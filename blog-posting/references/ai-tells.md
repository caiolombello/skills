# AI tells catalog

The words, constructions, structures, and rhythms that make a draft read generated. Two languages: English and Brazilian Portuguese. Use it during the anti-tell pass in [SKILL.md](../SKILL.md); `scripts/blog_lint.py` automates most of this catalog.

Calibration first: tells are statistical. A single soft hit is a style choice, not a finding. Hard hits and repeated soft hits are the tells. When a word is the right word, keep it. Kill patterns, not vocabulary.

## Contents

- [Calibration](#calibration)
- [English vocabulary](#english-vocabulary)
- [Portuguese vocabulary (PT-BR)](#portuguese-vocabulary-pt-br)
- [Constructions](#constructions)
- [Structure tells](#structure-tells)
- [Rhythm and punctuation](#rhythm-and-punctuation)
- [Titles and headers](#titles-and-headers)
- [Before and after](#before-and-after)

## Calibration

| Level | Meaning | Action |
|---|---|---|
| Hard | Almost never justified in a blog post | Rewrite every hit |
| Soft | Fine once; a pattern at three or more hits, or dense repetition | Rewrite when repeated; keep single justified uses |

## English vocabulary

### Hard

| Tell | Fix |
|---|---|
| delve (into) | dig into, look at |
| tapestry | delete, or name the actual mix |
| realm, in the realm of | in, among |
| unleash | release, ship, let (literal) |
| game-changer | say what actually changed, with the number |
| a testament to | shows, proves |
| beacon of | example of, model of |
| embark on | start |
| meticulously | carefully (or show the care with a concrete detail) |
| plethora | too many |
| synergy, synergies | good fit (or explain the actual interaction) |
| holistically | end to end, or name the parts |
| supercharge | speed up (by how much) |
| revolutionize | change (say how) |
| skyrocket | give the number |
| in today's fast-paced world / digital age | delete |
| in the ever-evolving X landscape | delete, or say what actually changed |
| in a world where | delete, or ground it in one real fact |
| it's important to note / it's worth noting | delete |
| let's dive in / dive deeper | delete |
| deep dive (noun) | detailed look, walkthrough |
| look no further | delete |
| whether you're a beginner or a... | delete; name the reader |
| at its core | delete, or "basically" |
| the bottom line is | delete (just state the point) |
| navigate the complexities | deal with the hard parts |
| unlock the potential / the power of | say what becomes possible, concretely |
| harness the power of | use |
| in conclusion / to sum up / in summary / in wrapping up / as we've seen | delete the recap section |
| have you ever wondered | delete; open with the stakes of the answer |
| double-edged sword | name the actual trade |
| tip of the iceberg | one visible part of a bigger problem |
| bridge the gap | connect, fix the mismatch |
| level up your X | improve (say what changes) |

### Soft

| Tell | Fix |
|---|---|
| crucial, pivotal, paramount | important (once), or delete |
| robust | solid; better: works under load, survives failure (be specific) |
| seamless | delete, or "without the user noticing" |
| comprehensive, extensive | complete, long (or say what it covers) |
| leverage (verb) | use |
| utilize | use |
| facilitate | help |
| foster | build, encourage |
| empower / empowering | rewrite with the actor: who now does what |
| elevate | improve |
| unlock | get, enable (literal) |
| harness | use |
| navigate (metaphor) | handle, deal with |
| journey | the actual process, with a name |
| landscape (the X landscape) | market, scene, mess of tools |
| ecosystem | community, market, set of tools |
| myriad | dozens of (or the real number) |
| cutting-edge, state-of-the-art, best-in-class | new; better: name the version and date |
| vibrant | active, busy |
| transformative | big (say what changed) |
| when it comes to | for, about |
| in this post, in this article | delete the announcement; start doing it |
| it goes without saying | delete |

## Portuguese vocabulary (PT-BR)

### Hard

| Tell | Fix |
|---|---|
| mergulhe (no mundo de) / vamos mergulhar | delete; comece pelo ponto |
| mergulho profundo | análise detalhada |
| desvendando / desvende | entenda, veja como funciona |
| no cenário atual / no mundo atual | delete |
| na era digital / na era da IA | delete |
| em um mundo cada vez mais... | delete, ou um fato concreto |
| é importante ressaltar que / vale ressaltar / é fundamental destacar | delete |
| vamos explorar / vamos entender (como anunciado de estrutura) | delete a frase; faça |
| de forma holística | de ponta a ponta, ou nomeie as partes |
| guia definitivo / guia completo / tudo que você precisa saber | prometa o conteúdo específico no título |
| de forma simples e descomplicada | delete |
| potencialize / potencializar | melhore, aumente |
| uma verdadeira jornada | delete |
| poderosa ferramenta / aliada poderosa | diga o que a ferramenta faz |
| o segredo por trás de | delete, ou a explicação real |
| seja você um(a)... | delete; nomeie o leitor |
| ao final deste artigo / ao longo deste post | delete (anúncio de estrutura) |
| em conclusão / em resumo / para concluir | delete a seção de recapitulação |
| você já se perguntou | delete; abra com a resposta e o que está em jogo |
| revolucionar a forma como você... | mude, melhore (diga o quê) |
| eleve seu... | melhore seu |
| sem esforço algum | diga o esforço real |

### Soft

| Tell | Fix |
|---|---|
| robusto(a) | sólido; melhor: sobrevive a falha, aguenta pico |
| dinâmico(a) (enchimento) | delete ou diga o que muda |
| sinergia | boa combinação |
| ecossistema | mercado, comunidade, conjunto de ferramentas |
| cenário (o cenário de X) | mercado, área |
| cada vez mais | delete (ou um número) |
| de forma X (de forma eficiente, simples...) | direto: "com menos memória", "em uma linha" |
| holístico | de ponta a ponta |
| papel fundamental / papel crucial | parte importante |
| além disso (conectivo repetido) | reestruture, ou delete |
| outrossim, ademais | além disso (uma vez), ou reestruture |
| por fim (recapitulação) | delete |
| dica valiosa | dica (diga por que vale) |
| de ponta a ponta (enchimento) | delete ou nomeie o começo e o fim |

## Constructions

Language-independent shapes. The `not-just` family is the most recognizable single construction in AI drafts.

| Construction | Tell | Fix |
|---|---|---|
| not just X, but Y — it's not about X, it's about Y — more than just X — não apenas X, mas também Y — não é só X, é Y | The contrast does the argument's work without saying anything | State one claim directly, with evidence |
| Rule of three: fast, flexible, and reliable — claro, conciso e completo | One triad is rhetoric; one per paragraph is a drumbeat | Keep your best one; write the rest as two, or as one specific |
| Rhetorical question opener | Announces a school essay | Open with the answer or the stakes |
| First... Second... Third... visible scaffolding | Essay skeleton shows through the skin | Order by the argument; let one point grow from the previous |
| Announced structure ("In this post, we'll cover...", "Neste artigo, vamos...") | Throat-clearing | Delete; the headers already do this job |
| Definition opener every section ("X is a Y that does Z") | Wikipedia voice | Start with why the reader cares, or a scene |
| Every section ends with a wrap-up sentence | Mini-recaps pile up | Trust the section; stop |
| Parallel bullets with identical grammar ("**Fast:** does X... **Flexible:** does Y") | Table energy in prose | Vary the shapes; merge into sentences |

## Structure tells

| Tell | Fix |
|---|---|
| Uniform paragraphs, all three to four sentences | Vary: one sentence, then five |
| Every H2 at the same level of abstraction | Mix a scene, a how-to, a caveat |
| Bullet lists where prose belongs | Restore argument prose; keep lists for genuine lists |
| Bold lead on every bullet | Plain bullets; bold only real keys |
| Bold and italics sprinkled for emphasis | Emphasis in the sentence itself, or delete |
| Emoji in headers | Delete (unless the platform's style really uses them) |
| Table of contents in a 600-word post | Delete (or the post is bloated) |
| A recap/"Key takeaways" section at the end | Delete the section; the reader just read it |

## Rhythm and punctuation

Human writing has high burstiness: sentence length swings widely (a four-word sentence next to a forty-word one; typical sentence-length standard deviation is around 8 words). Model prose clusters in a narrow 15-to-25-word band. Detect: `blog_lint.py` reports mean and standard deviation.

| Tell | Budget / fix |
|---|---|
| Em dashes as the default connector | About one per 300 words; the rest become commas, periods, parentheses, or two sentences |
| Em dash doing the "not X — but Y" move | Pick one side and commit |
| Semicolons joining clauses in casual prose | Two sentences; semicolons are rare in speech |
| Parenthetical definition after every term | Define once, in a sentence, when the reader actually needs it |
| No sentence fragments anywhere | Allow one or two. They are how people actually talk. |
| Every sentence a complete clause with a comma-connector | Let a "Because." follow a long sentence |
| Rhetorical triple punctuation ("...fast. Flexible. Reliable.") | Once, at most, when the rhythm is earned |

## Titles and headers

| Tell | Fix |
|---|---|
| The Ultimate Guide to X / X: A Comprehensive Guide | A title with the actual promise or number |
| X Demystified / Understanding X / The Power of X | What the reader gets or does |
| 10 Things You Need to Know About X | Name the one thing, or the specific ten |
| From Zero to Hero / do zero ao herói | The real outcome, with a timeframe |
| Headers: Introduction / Overview / Conclusion / Key Takeaways / Best Practices / Common Pitfalls / What Is X? / Why X Matters | Statements, questions, or short commands that carry content |
| Headers: Entendendo X / O que é X? / Conclusão / Principais pontos / Por que X é importante | Idem, em português |
| Numbered H2s in a non-list post ("## 1. Setup") | Delete the numbers; the order is already the order |

## Before and after

### English

Before (tell-dense: reads generated):

> In today's fast-paced development landscape, delivering robust and seamless experiences has become more crucial than ever. Whether you're a seasoned engineer or just embarking on your journey, understanding the power of observability is a game-changer. It's not just about collecting metrics — it's about weaving a rich tapestry of logs, traces, and events that empowers teams to delve into issues with confidence. In conclusion, observability is truly pivotal.

After (specifics, stance, varied rhythm):

> Observability paid for itself the first time production broke at 2am and nobody had to guess. The trace was open before the pager stopped vibrating: one request stuck for 40 seconds in the payment service, retrying against a dead connection pool. One log line, one metric, one trace. Ten minutes to an answer that used to cost an afternoon of ssh and grep. I would not go back.

What changed: a scene instead of a claim, a number instead of "fast-paced", one stance ("I would not go back"), sentence lengths from three words to nineteen, and no recap.

### Portuguese

Antes (denso em tells):

> No cenário atual, garantir entregas robustas e dinâmicas tornou-se cada vez mais essencial. Seja você um desenvolvedor experiente ou alguém que está começando, vamos mergulhar no fascinante universo dos logs e explorar como essa poderosa ferramenta pode revolucionar a forma como você depura problemas em produção.

Depois (com contexto e detalhes reais):

> Log estruturado salvou meu plantão numa sexta. O build quebrou às 19h40 e a única pista era um "timeout" no console. Com log, dois minutos: a chamada do banco expirava porque o pool estava travado desde o deploy das 18h. Sem log, eu ainda estaria às 21h imprimindo variável com console.log.

O que mudou: uma cena em vez de um cenário abstrato, horários e nomes reais em vez de adjetivos, uma opinião em primeira pessoa, e frases de comprimentos bem diferentes.
