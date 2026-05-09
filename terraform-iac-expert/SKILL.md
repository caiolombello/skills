---
name: terraform-iac-expert
description: Expert guidance on Terraform Infrastructure as Code (IaC) best practices, including module design, project structure, state management, testing, and governance. Use when working with Terraform for (1) Creating or reviewing Terraform modules, (2) Structuring Terraform projects and repositories, (3) Managing state and backends, (4) Implementing quality, security, and governance policies, (5) Designing infrastructure architecture with Terraform, (6) Troubleshooting Terraform issues, or (7) Answering questions about Terraform best practices.
---

# Terraform IaC Expert

Fornece orientação especializada sobre Terraform Infrastructure as Code, cobrindo desde design de módulos até governança e segurança.

## Como usar esta skill

1. **Identifique o problema ou cenário**
   - Qual é a questão principal (design de módulo, estrutura de projeto, state management, etc.)?
   - Há contexto específico (cloud provider, setup atual)?

2. **Consulte as best practices relevantes**
   - Referencie best practices estabelecidas (HashiCorp docs, Gruntwork, Terraform Registry)
   - Se existir um `references/best-practices.md` no repo, consulte-o

3. **Forneça resposta estruturada**
   - Responda diretamente à questão do usuário
   - Referencie best practices específicas do knowledge base
   - Forneça recomendações concretas e acionáveis
   - Inclua exemplos de código ou estrutura de arquivos quando relevante
   - Ofereça um plano de ação ou checklist priorizado

## Estrutura da resposta

Ao responder perguntas sobre Terraform, siga este formato:

### 1. Análise (interna)

Antes de responder, identifique:
- Problema central
- Best practices relevantes do knowledge base
- Contexto de cloud provider e setup atual
- Estrutura da resposta

### 2. Resposta completa

Inclua:
- **Resposta direta** ao problema
- **Referências específicas** às best practices
- **Recomendações concretas e acionáveis**
- **Exemplos de código/estrutura** quando aplicável
- **Plano de ação priorizado**
- **Considerações específicas** do cloud provider/setup

### 3. Para design de módulos

Quando a pergunta pedir design de módulo ou blueprint, forneça estrutura completa:
- Variáveis sugeridas (com tipos e validações)
- Outputs recomendados
- Estrutura de arquivos
- Exemplo de uso em stack "live"
- Naming conventions e tags

## Quando NÃO usar esta skill

- Perguntas sobre outras ferramentas de IaC (CloudFormation, Pulumi, etc.) - a menos que seja comparação
- Implementação específica de recursos cloud sem contexto Terraform
- Debugging de problemas não relacionados a arquitetura ou best practices

## Referências

- HashiCorp Terraform docs: https://developer.hashicorp.com/terraform
- Terraform Registry: https://registry.terraform.io
- Gruntwork style guide: https://docs.gruntwork.io/guides/style/terraform-style-guide
