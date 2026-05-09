---
name: pass-cli-secrets
description: Fonte canonica de segredos. Use pass-cli (Proton Pass CLI) para credenciais locais do usuario; use AWS Secrets Manager / SSM Parameter Store para workloads e IaC AWS. Acione esta skill SEMPRE que: (1) o usuario pedir uma senha/token/credencial, (2) o codigo/script/config/IaC gerado precisar de um segredo, (3) for necessario expor um segredo em variavel de ambiente, (4) o usuario mencionar Proton Pass, vault, cofre, secret, credential, Secrets Manager, SSM, parameter store. NUNCA escreva segredos literais em arquivos, commits, comandos ou respostas.
---

# pass-cli (Proton Pass CLI) — fonte unica de segredos

O usuario tem `pass-cli` instalado e logado. Todos os segredos (senhas, tokens, API keys, chaves SSH, certificados) **devem** ser obtidos via `pass-cli` em vez de:

- Hardcoded em codigo, scripts, configs, IaC
- Pedidos diretos ao usuario ("me passa a senha")
- Lidos de `.env` / `.envrc` versionados
- Copiados de password managers do navegador

Docs oficiais: https://protonpass.github.io/pass-cli/ — repo: https://github.com/protonpass/pass-cli

## Regras invioláveis

1. **Nunca** imprima, logue, comente ou escreva o valor de um segredo recuperado. Use-o apenas no comando final.
2. **Nunca** sugira `echo $TOKEN` ou similar para "verificar" um segredo. Para validar, use o segredo no comando real.
3. **Nunca** salve segredos em arquivos do projeto (`.env`, `secrets.yaml`, etc.) sem confirmar com o usuario que o arquivo esta no `.gitignore`.
4. **Nunca** use `pass-cli` com `--output json` enviando para um arquivo sem aviso explicito.
5. Em scripts, prefira **passar o segredo via stdin ou variavel de ambiente efemera** ao processo que precisa dele, nao persistir em disco.
6. Se for criar um segredo novo (gerar token, API key, senha de DB), ofereça **gravar no Proton Pass** ao final.

## Fluxo padrao para recuperar um segredo

### 1. Listar para encontrar o item
```bash
pass-cli item list --output json | jq '.[] | {title, item_id, share_id}'
```
Ou liste vaults primeiro:
```bash
pass-cli vault list --output json
pass-cli item list "Personal" --output json
```

### 2. Recuperar UM campo especifico (uso normal)
Use `--field` para extrair so o que precisa, sem expor o resto:
```bash
pass-cli item view --item-title "GitHub Token" --field password
pass-cli item view --vault-name "Work" --item-title "AWS prod" --field "access_key"
```

Ou via Pass URI (preferido em scripts — nao depende de match de titulo):
```bash
pass-cli item view "pass://SHARE_ID/ITEM_ID/password"
```

### 3. Usar em comandos sem expor no shell history

**Variavel local efemera (preferido):**
```bash
GITHUB_TOKEN="$(pass-cli item view --item-title 'GitHub Token' --field password)" \
  gh auth login --with-token <<< "$GITHUB_TOKEN"
unset GITHUB_TOKEN
```

**Pipe direto quando o comando aceita stdin:**
```bash
pass-cli item view --item-title 'DB Prod' --field password | \
  psql -h db.prod -U admin
```

**Sem mostrar no terminal:**
```bash
read -rs DB_PASS < <(pass-cli item view --item-title 'DB Prod' --field password)
```

## Padroes AI-blind (quando um agente esta executando o comando)

Quando voce (IA) executa `pass-cli` via tool de Bash, **tudo que sair em stdout/stderr volta como tool result e fica visivel pra voce e pro contexto**. Para usar segredos sem ve-los:

### Regra de ouro
**O segredo nunca pode aparecer no output final do comando.** Use pipe direto ou env var inline para o consumidor, em uma unica linha de Bash.

### Padroes seguros (segredo invisivel ao agente)

```bash
# Pipe direto para stdin do consumidor
pass-cli item view --field password --vault-name V --item-title T | \
  docker login -u user --password-stdin

pass-cli item view --field password --vault-name V --item-title T | \
  gh auth login --with-token

pass-cli item view --field password --vault-name V --item-title T | \
  psql -h db.host -U admin

# Env var inline, comando que nao ecoa o valor
PGPASSWORD="$(pass-cli item view --field password ... )" \
  psql -h db -U user -c '\dt'

# Process substitution para ferramentas que querem arquivo
kubectl create secret generic foo \
  --from-file=token=<(pass-cli item view --field password ... )

# Comando que so retorna exit code
PASS="$(pass-cli item view --field password ... )" \
  curl -fsS -u "user:$PASS" https://api.example.com/healthz -o /dev/null && echo OK
```

### Antipadroes (vaza para o agente)

```bash
# stdout direto: secret vira tool result
pass-cli item view --field password ...

# Atribuir a variavel e depois "checar" — echo/printf vaza
TOKEN="$(pass-cli item view --field password ... )"
echo "$TOKEN"          # ❌
printenv TOKEN         # ❌

# set -x / bash -x expande comandos no stderr
set -x; CMD="$(pass-cli item view --field password ...)"  # ❌ vaza no trace

# Passar como argv — fica em ps, history, logs do programa
mysql --password="$(pass-cli item view --field password ...)"  # ❌
# Use --password-stdin ou MYSQL_PWD env var
```

### Pegadinhas adicionais

- **`curl -v` / `-vvv`** loga headers, incluindo `Authorization`
- **`docker run -e SECRET=$X`** aparece em `docker inspect`
- **Mensagens de erro**: muitas ferramentas ecoam a connection string completa (com senha) em falha — redirecione `2>&1 | grep -v -i password` ou `2>/dev/null` quando for seguro
- **`tee`, `>>` para arquivo** que voce depois vai ler com `Read` ou `cat`
- **History**: comandos com segredo em argv ficam em `~/.zsh_history`. Use env var ou pipe.

### Quando voce precisa ver o valor (criar config, popular outro storage)

Se a tarefa **exige** que voce manipule o valor (ex.: bootstrap inicial pra Secrets Manager, gerar `.env.local` para dev), avise o usuario antes de executar:

> "Vou recuperar o segredo X via pass-cli — o valor vai aparecer no meu contexto. Confirma?"

Apos usar, sugira limpar:
```bash
history -d $(history 1)   # remove ultimo comando do history
```

### Limite real

Mesmo com pipe direto, o segredo existe descriptografado na memoria do shell que voce disparou. O sandbox roda como o usuario — entao tecnicamente um agente malicioso poderia ler `/proc/<pid>/environ`. A garantia aqui eh "agente honesto + nao-vazamento acidental no contexto", nao "agente sem acesso possivel". Para garantia forte (segredo nunca toca a maquina do agente), use IRSA/OIDC para workloads AWS ou exija approval humano no comando final.

## Padroes por contexto

### Terraform / IaC
NUNCA coloque segredos em `.tfvars`. Em vez disso, exporte antes de rodar:
```bash
export TF_VAR_db_password="$(pass-cli item view --item-title 'RDS prod' --field password)"
terraform apply
```
Marque a variavel como `sensitive = true` no `.tf`.

### Docker / docker-compose
Use `--env-file` apontando para arquivo gerado on-the-fly e deletado, ou:
```bash
docker run -e API_KEY="$(pass-cli item view --item-title 'X' --field password)" image
```
Para compose, prefira `secrets:` apontando para arquivo temporario gerado de pass-cli.

### CI/CD (GitHub Actions, GitLab CI)
NAO sugira commitar segredos. Recomende:
- GitHub Actions: `secrets.NAME` no repo settings
- Para popular esses secrets a partir de pass-cli localmente:
  ```bash
  gh secret set MY_SECRET --body "$(pass-cli item view --item-title 'X' --field password)"
  ```

### Codigo de aplicacao (Python, Node, Go)
NAO embuta segredo no codigo. Sempre via env var, e instrua o usuario a popular a env var via pass-cli no shell antes de rodar:
```bash
export OPENAI_API_KEY="$(pass-cli item view --item-title 'OpenAI' --field password)"
python app.py
```

### SSH / chaves privadas
Use o ssh-agent embutido do pass-cli em vez de copiar a chave para `~/.ssh/`:
```bash
pass-cli ssh-agent start          # inicia agent
pass-cli ssh-agent load --item-title "GitHub Deploy"
```

## Criar segredos novos no Proton Pass

Quando voce gerar um token/senha/chave nova (ex.: rotacao de API key, novo IAM user, novo deploy key), oferecer salvar:

```bash
# Gerar e salvar uma senha forte direto no Pass
pass-cli item create login \
  --vault-name "Work" \
  --title "Servico X - prod" \
  --username "svc-account" \
  --generate-password="32,uppercase,symbols" \
  --url "https://servicox.com"

# Salvar segredo ja gerado externamente
pass-cli item create login \
  --vault-name "Work" \
  --title "AWS access key - userY" \
  --username "AKIA..." \
  --password "$(cat /tmp/secret)" && shred -u /tmp/secret
```

## Excecao: contexto AWS — Secrets Manager / SSM Parameter Store tem prioridade

Quando o trabalho envolve **runtime AWS** (Lambda, ECS, EKS, EC2, CodeBuild, App Runner, Glue, etc.) ou **IaC AWS** (Terraform, CDK, CloudFormation, SAM), a fonte canonica de segredos passa a ser:

- **AWS Secrets Manager** — credenciais com rotacao, JSON estruturado, segredos de DB/API com versionamento
- **AWS Systems Manager Parameter Store (SecureString)** — config + segredos simples, mais barato, integrado com SSM

Motivo: workloads AWS ja tem IAM/IRSA para acessar esses servicos nativamente, sem expor segredo em env var no manifesto, sem dependencia de pass-cli no runtime, com auditoria via CloudTrail e rotacao automatica.

### Como decidir entre pass-cli vs AWS Secrets/SSM

| Cenario | Fonte canonica |
|---------|----------------|
| Segredo consumido por workload rodando **dentro da AWS** | Secrets Manager / SSM SecureString |
| Segredo de **infra AWS** referenciado em IaC (RDS password, API key de provider) | Secrets Manager / SSM (data source no Terraform) |
| Credencial pessoal do **usuario na maquina local** (gh token, kubeconfig token, npm token) | pass-cli |
| Credencial de **acesso a AWS em si** (AWS access keys, SSO refresh) | AWS CLI profiles / SSO — nao ambos |
| Segredo usado em **CI** que faz deploy AWS | GitHub Actions secrets (populados via pass-cli localmente OU via OIDC para AWS) |
| Segredo precisa ser **bootstrappado** no Secrets Manager pela primeira vez | pass-cli local → script que faz `aws secretsmanager create-secret` |

### Padroes AWS

**Terraform — referenciar Secrets Manager:**
```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/rds/master"
}

resource "aws_db_instance" "this" {
  password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

**Terraform — referenciar SSM SecureString:**
```hcl
data "aws_ssm_parameter" "api_key" {
  name            = "/prod/external-api/key"
  with_decryption = true
}
# usar data.aws_ssm_parameter.api_key.value (marcar variavel como sensitive)
```

**EKS — montar via Secrets Store CSI Driver (sem expor em manifesto):**
Use `SecretProviderClass` apontando para Secrets Manager via IRSA. NUNCA `kubectl create secret` com valor literal.

**Bootstrap inicial (pass-cli → AWS):**
```bash
aws secretsmanager create-secret \
  --name prod/external-api/key \
  --secret-string "$(pass-cli item view --item-title 'External API prod' --field password)"
```

**Rotacao — gerar nova credencial e gravar em ambos:**
```bash
NEW_PASS="$(openssl rand -base64 32)"
aws secretsmanager put-secret-value --secret-id prod/rds/master \
  --secret-string "{\"password\":\"$NEW_PASS\"}"
pass-cli item update --item-title "RDS prod backup" --field password --value "$NEW_PASS"
unset NEW_PASS
```

### Regras AWS

1. **Nunca** ponha segredo literal em `*.tfvars`, manifesto k8s, task definition do ECS, ou env do Lambda.
2. Em Terraform, sempre marque `sensitive = true` em outputs/variables que tocam segredos.
3. Para Lambda/ECS, prefira `secrets:` (referencia direta a Secrets Manager) em vez de `environment:` com valor.
4. Para EKS, use IRSA + Secrets Store CSI Driver, nao `Secret` k8s populado manualmente.
5. Tags obrigatorias do usuario (`Environment`, `Project`, `Owner`) tambem se aplicam a secrets criados.

## Quando o pass-cli nao esta disponivel

Se `pass-cli` falhar (sessao expirada, sem rede), pare e avise o usuario:
- `pass-cli login` para reautenticar
- NAO caia em fallback de pedir o segredo em texto plano no chat sem aviso explicito

## Variaveis de ambiente uteis (ja documentadas em memory)

- `PROTON_PASS_LINUX_KEYRING=dbus` — usuario ja tem isso configurado (chave persiste entre reboots via GNOME Keyring)
- `PROTON_PASS_PERSONAL_ACCESS_TOKEN=pst_xxx::KEY` — usar PAT em scripts/CI

## Auto-check antes de responder

Antes de qualquer resposta que envolva senha/token/credencial, pergunte-se:
- [ ] Estou prestes a escrever um segredo literal? → Pare. Use `pass-cli item view --field`.
- [ ] Vou pedir o segredo ao usuario? → Pare. Sugira `pass-cli item view ...`.
- [ ] O segredo vai parar em arquivo versionado? → Pare. Use env var via pass-cli no momento da execucao.
- [ ] Estou gerando um segredo novo? → Ofereca salvar no Pass ao final.
