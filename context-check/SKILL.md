---
name: context-check
description: "Compatibilidade: encaminha à orientação de context-engineering para avaliar contexto com métricas disponíveis."
---

Este nome é mantido como alias para compatibilidade. Siga [`context-engineering`](../context-engineering) para avaliar e reduzir o contexto.

Use apenas métricas expostas pela superfície e ferramentas disponíveis nesta sessão. Se a interface mostrar uma medida de uso, informe o valor observado e sua fonte. Não presuma que exista um comando `/context` nem invente percentuais. Se não houver métrica acessível, diga que o uso exato está indisponível e faça uma recomendação qualitativa baseada em sinais observáveis, como repetição de contexto, referências obsoletas ou perda de foco.

Quando a superfície fornecer ações suportadas de compactação ou nova conversa, sugira-as apenas se os sinais justificarem. Limiares numéricos são heurísticas específicas da superfície, não regras universais; não recomende um comando que não esteja disponível.

Explique brevemente a evidência e a recomendação.
