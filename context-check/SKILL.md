---
name: context-check
description: "Verifique o uso atual de contexto usando /context internamente."
---

Verifique o uso atual de contexto usando /context internamente.

Com base no resultado, sugira uma das acoes:

1. **Continuar normalmente** - Se o contexto estiver abaixo de 40%
2. **Fazer /compact** - Se estiver entre 40-60% e a tarefa atual for complexa
3. **Iniciar nova conversa** - Se estiver acima de 60% ou se a qualidade das respostas parecer estar degradando

Explique brevemente o motivo da recomendacao.
