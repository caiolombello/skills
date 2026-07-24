---
name: review-code
description: "Revise o codigo que acabei de escrever/modificar com foco em:"
---

Revise o codigo que acabei de escrever/modificar com foco em:

1. **Bugs potenciais** - Logica incorreta, null pointers, race conditions
2. **Seguranca** - OWASP top 10, injection, autenticacao, autorizacao
3. **Performance** - Complexidade, queries N+1, memory leaks
4. **Legibilidade** - Naming, estrutura, comentarios necessarios
5. **Manutencao** - Duplicacao, acoplamento, testabilidade

Classifique cada problema encontrado por severidade:
- **P1**: Critico - deve ser corrigido antes de deploy
- **P2**: Importante - deve ser corrigido em breve
- **P3**: Menor - melhoria nice-to-have

Se nao encontrar problemas significativos, diga "LGTM" com breve explicacao.
