#!/usr/bin/env python3
"""Flag stock AI-writing patterns in a blog post or article.

Usage:
    python3 blog_lint.py post.md
    python3 blog_lint.py --lang pt rascunho.md
    python3 blog_lint.py --format json post.md post2.md
    cat post.md | python3 blog_lint.py --stdin

Exit codes: 0 = clean (warnings allowed), 1 = error-level findings,
2 = usage or IO error.

Heuristic aid, not an AI detector. Tells are statistical: one flagged word
is a style choice, a pattern is a tell. Fix structure and substance first,
vocabulary last. The catalog with per-language rewrites is in
../references/ai-tells.md.
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ------------------------------------------------------------------ vocabulary

HARD_EN = {
    "in today's fast-paced": "delete",
    "in today's world": "delete",
    "in today's digital age": "delete",
    "in a world where": "delete, or ground it in one real fact",
    "ever-evolving": "say what actually changes",
    "delve": "dig into, look at",
    "delves": "dig into",
    "delved": "dug into",
    "delving": "looking at",
    "tapestry": "delete, or name the actual mix",
    "realm": "in, among",
    "in the realm of": "in, among",
    "unleash": "release, ship, let (literal)",
    "unleash the power": "use",
    "game-changer": "say what actually changed, with the number",
    "game changer": "say what actually changed, with the number",
    "a testament to": "shows, proves",
    "beacon of": "example of, model of",
    "embark on": "start",
    "embarking on": "start",
    "meticulously": "carefully, or show the care with a concrete detail",
    "plethora": "too many",
    "synergy": "good fit, or explain the actual interaction",
    "synergies": "good fit, or explain the actual interaction",
    "holistically": "end to end, or name the parts",
    "supercharge": "speed up, and by how much",
    "revolutionize": "change, and say how",
    "revolutionizes": "change, and say how",
    "revolutionized": "change, and say how",
    "skyrocket": "give the number",
    "it's important to note": "delete",
    "it is important to note": "delete",
    "it's worth noting": "delete",
    "it's worth mentioning": "delete",
    "let's dive in": "delete",
    "let's dive into": "delete",
    "let's dive deeper": "delete",
    "deep dive": "detailed look, walkthrough",
    "look no further": "delete",
    "whether you're a": "delete; name the reader",
    "whether you are a": "delete; name the reader",
    "at its core": "delete, or 'basically'",
    "the bottom line is": "delete, and state the point",
    "navigate the complexities": "deal with the hard parts",
    "unlock the potential": "say what becomes possible, concretely",
    "unlock the power": "say what becomes possible, concretely",
    "harness the power of": "use",
    "in conclusion": "delete the recap section",
    "to sum up": "delete the recap",
    "to summarize": "delete the recap",
    "in summary": "delete the recap",
    "in wrapping up": "delete the recap",
    "as we've seen": "delete the recap",
    "have you ever wondered": "open with the stakes of the answer",
    "ever wondered": "open with the stakes of the answer",
    "double-edged sword": "name the actual trade",
    "tip of the iceberg": "one visible part of a bigger problem",
    "bridge the gap": "connect, fix the mismatch",
    "level up your": "improve, and say what changes",
}

SOFT_EN = {
    "crucial": "important (once), or delete",
    "pivotal": "important (once), or delete",
    "paramount": "important (once), or delete",
    "robust": "solid; better, works under load / survives failure",
    "seamless": "delete, or 'without the user noticing'",
    "seamlessly": "delete",
    "comprehensive": "complete, or say what it covers",
    "extensive": "long, or say what it covers",
    "leverage": "use",
    "leveraging": "use",
    "utilize": "use",
    "utilizing": "use",
    "facilitate": "help",
    "facilitates": "help",
    "foster": "build, encourage",
    "fostering": "build, encourage",
    "empower": "rewrite with the actor: who now does what",
    "empowers": "rewrite with the actor",
    "empowering": "rewrite with the actor",
    "elevate": "improve",
    "unlock": "get, enable (literal)",
    "harness": "use",
    "navigate": "handle (metaphorical uses)",
    "journey": "the actual process, with a name",
    "landscape": "market, scene",
    "ecosystem": "community, market, set of tools",
    "myriad": "dozens, or the real number",
    "cutting-edge": "new; better, name the version and date",
    "state-of-the-art": "new; better, name the version and date",
    "best-in-class": "name the measurement",
    "vibrant": "active, busy",
    "transformative": "big; say what changed",
    "when it comes to": "for, about",
    "in this post": "delete the announcement; start doing it",
    "in this article": "delete the announcement; start doing it",
    "it goes without saying": "delete",
}

HARD_PT = {
    "mergulhe": "delete; comece pelo ponto",
    "vamos mergulhar": "delete; comece pelo ponto",
    "mergulho profundo": "análise detalhada",
    "desvendando": "entenda, veja como funciona",
    "desvende": "delete",
    "no cenário atual": "delete",
    "no mundo atual": "delete",
    "na era digital": "delete",
    "na era da ia": "delete",
    "em um mundo cada vez mais": "delete, ou um fato concreto",
    "num mundo cada vez mais": "delete, ou um fato concreto",
    "é importante ressaltar": "delete",
    "é importante destacar": "delete",
    "é fundamental destacar": "delete",
    "vale ressaltar": "delete",
    "vale destacar": "delete",
    "vamos explorar": "delete; faça",
    "vamos entender": "delete; faça",
    "de forma holística": "de ponta a ponta, ou nomeie as partes",
    "de maneira holística": "de ponta a ponta, ou nomeie as partes",
    "guia definitivo": "prometa o conteúdo específico no título",
    "guia completo": "prometa o conteúdo específico no título",
    "tudo que você precisa saber": "prometa o conteúdo específico",
    "tudo o que você precisa saber": "prometa o conteúdo específico",
    "de forma simples e descomplicada": "delete",
    "potencialize": "melhore, aumente",
    "potencializar": "melhore, aumente",
    "uma verdadeira jornada": "delete",
    "poderosa ferramenta": "diga o que a ferramenta faz",
    "aliada poderosa": "diga o que ela faz",
    "o segredo por trás": "a explicação real, ou delete",
    "seja você um": "delete; nomeie o leitor",
    "seja você uma": "delete; nomeie o leitor",
    "ao final deste artigo": "delete (anúncio de estrutura)",
    "ao final deste post": "delete (anúncio de estrutura)",
    "ao longo deste post": "delete (anúncio de estrutura)",
    "ao longo deste artigo": "delete (anúncio de estrutura)",
    "em conclusão": "delete o fecho",
    "em resumo": "delete o fecho",
    "para concluir": "delete o fecho",
    "você já se perguntou": "abra com o que está em jogo",
    "revolucionar a forma": "mude, melhore; diga o quê",
    "eleve seu": "melhore seu",
    "eleve o seu": "melhore o seu",
    "sem esforço algum": "diga o esforço real",
}

SOFT_PT = {
    "robusto": "sólido; melhor, sobrevive a falha / aguenta pico",
    "robusta": "sólida; melhor, diga o que ela aguenta",
    "robustos": "sólidos; seja específico",
    "robustas": "sólidas; seja específica",
    "sinergia": "boa combinação",
    "sinergias": "boa combinação",
    "ecossistema": "mercado, comunidade, conjunto de ferramentas",
    "cenário": "mercado, área",
    "cada vez mais": "delete, ou um número",
    "holístico": "de ponta a ponta",
    "holística": "de ponta a ponta",
    "papel fundamental": "parte importante",
    "papel crucial": "parte importante",
    "por fim": "delete (recapitulação)",
    "outrossim": "além disso (uma vez)",
    "ademais": "além disso (uma vez)",
    "dica valiosa": "diga por que vale",
    "de ponta a ponta": "nomeie o começo e o fim",
}

HARD = {"en": HARD_EN, "pt": HARD_PT}
SOFT = {"en": SOFT_EN, "pt": SOFT_PT}

NOT_JUST_PATTERNS = [
    r"\bnot just\b",
    r"\bnot only\b",
    r"\bmore than just\b",
    r"\bisn'?t just\b",
    r"\bwasn'?t just\b",
    r"\bnão apenas\b",
    r"\bnão é só\b",
    r"\bnão só\b",
    r"\bnem apenas\b",
]

TRANSITIONS = {
    "en": ["moreover", "furthermore", "additionally", "consequently", "in addition", "notably", "importantly"],
    "pt": ["além disso", "outrossim", "ademais", "sendo assim", "dessa forma", "por outro lado", "vale lembrar"],
}

HEADER_TEMPLATES = [
    r"^understanding\b",
    r"^the power of\b",
    r"^key takeaways\b",
    r"^conclusion\b",
    r"^final thoughts\b",
    r"^introduction\b",
    r"^overview\b",
    r"^best practices\b",
    r"^common pitfalls\b",
    r"^what is\b",
    r"^why .* matters\b",
    r"^the ultimate guide\b",
    r"^a comprehensive guide\b",
    r"^everything you need to know\b",
    r"^takeaways\b",
    r"^entendendo\b",
    r"^o que é\b",
    r"^conclusão\b",
    r"^introdução\b",
    r"^principais pontos\b",
    r"^principais dicas\b",
    r"^por que .* (importante|essencial)\b",
    r"^guia (definitivo|completo)\b",
    r"^tudo o que você precisa\b",
]

TITLE_TEMPLATES = [
    r"ultimate guide",
    r"comprehensive guide",
    r"complete guide",
    r"definitive guide",
    r"demystified",
    r"everything you need to know",
    r"things you need to know",
    r"^the power of\b",
    r"do zero ao (herói|expert|pro|mestre)",
    r"^guia (definitivo|completo)\b",
    r"^tudo sobre\b",
]

DEFINITION_RES = {
    "en": r"^[A-Z][\w'’-]+\s+(?:is|are)\s+(?:a|an|the)\s",
    "pt": r"^[A-ZÀ-Ü][\w'’-]+\s+(?:é|são)\s+(?:um|uma|o|a)\s",
}

EN_MARKERS = {"the", "and", "of", "to", "in", "is", "it", "you", "that", "was", "for",
              "are", "with", "this", "but", "they", "have", "has", "not", "from", "as"}
PT_MARKERS = {"de", "que", "não", "uma", "para", "com", "por", "dos", "das", "em",
              "você", "nós", "mais", "como", "mas", "seu", "sua", "foi", "são",
              "os", "as", "na", "no"}

WORD = re.compile(r"[^\W\d_]+(?:[’'\-][^\W\d_]+)*", re.UNICODE)
TRIAD = re.compile(r"\b([^\W\d_]+),\s+([^\W\d_]+),\s+(?:and|e|or|ou)\s+([^\W\d_]+)", re.IGNORECASE)
HEADER_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
STRUCT_PREFIX = re.compile(r"^(#{1,6}\s|>|[-*+]\s|\||</?\w+|\d+[.)]\s)")
ABBREV = {"mr", "dr", "etc", "vs", "sr", "jr", "st", "no", "fig", "mt", "ex",
          "e.g", "i.e", "p.ex", "prof", "sra", "pag", "pág"}

# ------------------------------------------------------------------ parsing


def term_regex(term):
    lead = r"(?<!\w)" if term[:1].isalnum() else ""
    trail = r"(?!\w)" if term[-1:].isalnum() else ""
    return re.compile(lead + re.escape(term) + trail, re.IGNORECASE)


def normalize(text):
    return text.replace("’", "'").replace("‘", "'")


def clean_lines_of(text):
    out = []
    fence = False
    for line in normalize(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = not fence
            out.append("")
            continue
        if fence or stripped.startswith("!["):
            out.append("")
            continue
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)  # links -> anchor text
        line = line.replace("`", "")
        out.append(line)
    return out


def prose_blocks(lines):
    blocks, current = [], []

    def flush():
        if current:
            blocks.append(" ".join(current))
            del current[:]

    for line in lines:
        stripped = line.strip()
        if not stripped or STRUCT_PREFIX.match(stripped):
            flush()
        else:
            current.append(stripped)
    flush()
    return blocks


def _tail_is_abbrev(sentence):
    tail = sentence.rstrip(" .!?…\"'”’)]")
    if not tail:
        return False
    return tail.split()[-1].lower().strip(".") in ABBREV


def split_sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if out and _tail_is_abbrev(out[-1]):
            out[-1] = out[-1] + " " + part
        else:
            out.append(part)
    return out


def detect_language(words):
    lowered = [w.lower() for w in words]
    en = sum(1 for w in lowered if w in EN_MARKERS)
    pt = sum(1 for w in lowered if w in PT_MARKERS)
    return "pt" if pt > en else "en"


def rate(count, words, base):
    return count * base / max(words, 1)


# ------------------------------------------------------------------ checks


def term_findings(lines, table, rule, hard):
    out = []
    for term, fix in table.items():
        rx = term_regex(term)
        hits, hit_lines = 0, []
        for number, line in enumerate(lines, 1):
            found = len(rx.findall(line))
            if found:
                hits += found
                if len(hit_lines) < 5:
                    hit_lines.append(number)
        if not hits:
            continue
        severity = "error" if hard or hits >= 3 else "warning"
        kind = "hard tell" if hard else "soft tell"
        out.append({"rule": rule, "severity": severity,
                    "message": f"{kind} '{term}' x{hits} (fix: {fix})",
                    "count": hits, "lines": hit_lines})
    return out


def finding(rule, severity, message, count=1, lines=None):
    return {"rule": rule, "severity": severity, "message": message,
            "count": count, "lines": lines or []}


def structure_findings(lines, blocks, sentences, lens, words, lang):
    out = []
    prose = " ".join(blocks)
    mean = statistics.mean(lens) if lens else 0
    sd = statistics.pstdev(lens) if len(lens) > 1 else 0

    dash_count = sum(line.count("—") + line.count("–") for line in lines)
    dash_lines = [n for n, line in enumerate(lines, 1) if "—" in line or "–" in line][:5]
    dash_rate = rate(dash_count, words, 300)
    if dash_count >= 3 and dash_rate > 1.4:
        out.append(finding("em-dash-density", "error",
                           f"{dash_count} em dashes in {words} words "
                           f"({dash_rate:.1f} per 300; budget about 1)", dash_count, dash_lines))
    elif dash_count >= 2 and dash_rate > 0.7:
        out.append(finding("em-dash-density", "warning",
                           f"{dash_count} em dashes in {words} words "
                           f"({dash_rate:.1f} per 300; budget about 1)", dash_count, dash_lines))

    semis = prose.count(";")
    if semis >= 4:
        out.append(finding("semicolon-overuse", "error",
                           f"{semis} semicolons in prose; rare in speech, prefer two sentences",
                           semis))
    elif semis >= 2:
        out.append(finding("semicolon-overuse", "warning",
                           f"{semis} semicolons in prose; rare in speech, prefer two sentences",
                           semis))

    triads = len(TRIAD.findall(prose))
    triad_rate = rate(triads, words, 250)
    if triads >= 2 and triad_rate > 1.5:
        out.append(finding("triad-overuse", "error",
                           f"{triads} 'A, B, and C' triples ({triad_rate:.1f} per 250 words); "
                           "keep the best one, write the rest as two or as one specific",
                           triads))
    elif triads >= 1 and triad_rate > 0.8:
        out.append(finding("triad-overuse", "warning",
                           f"{triads} 'A, B, and C' triples ({triad_rate:.1f} per 250 words)",
                           triads))

    not_just = sum(len(re.findall(p, prose, re.IGNORECASE)) for p in NOT_JUST_PATTERNS)
    if not_just >= 2:
        out.append(finding("not-just-but", "error",
                           f"{not_just} not-just / not-only constructions; "
                           "state one claim directly", not_just))
    elif not_just == 1:
        out.append(finding("not-just-but", "warning",
                           "one not-just / not-only construction; state one claim directly",
                           not_just))

    if len(lens) >= 10:
        if sd < 5.0:
            out.append(finding("low-burstiness", "error",
                               f"sentence words: mean {mean:.1f}, sd {sd:.1f} (n={len(lens)}); "
                               "low variance reads generated, mix short and long"))
        elif sd < 7.5:
            out.append(finding("low-burstiness", "warning",
                               f"sentence words: mean {mean:.1f}, sd {sd:.1f} (n={len(lens)}); "
                               "human variance is higher"))
        if min(lens) > 8:
            out.append(finding("no-short-sentence", "warning",
                               f"shortest sentence is {min(lens)} words; "
                               "no short beat anywhere in the post"))

    pcounts = [len(split_sentences(b)) for b in blocks]
    pcounts = [c for c in pcounts if c]
    if len(pcounts) >= 5:
        pmean = statistics.mean(pcounts)
        psd = statistics.pstdev(pcounts)
        cv = psd / pmean if pmean else 0
        if cv < 0.15:
            out.append(finding("uniform-paragraphs", "error",
                               f"{len(pcounts)} paragraphs, all near {pmean:.1f} sentences "
                               f"(size variance {cv:.0%}); vary one and five"))
        elif cv < 0.25:
            out.append(finding("uniform-paragraphs", "warning",
                               f"{len(pcounts)} paragraphs, all near {pmean:.1f} sentences "
                               f"(size variance {cv:.0%})"))

    if lang:
        trx = re.compile(r"^(?:" + "|".join(re.escape(t) for t in TRANSITIONS[lang]) + r")\b",
                         re.IGNORECASE)
        thits = [s for s in sentences if trx.match(s)]
        if len(thits) >= 3:
            out.append(finding("transition-opener", "error",
                               f"{len(thits)} sentences open with Moreover/Furthermore-class "
                               "connectors; link ideas by meaning instead", len(thits)))
        elif len(thits) == 2:
            out.append(finding("transition-opener", "warning",
                               "2 sentences open with Moreover/Furthermore-class connectors",
                               len(thits)))

        drx = re.compile(DEFINITION_RES[lang])
        dhits = [b for b in blocks if drx.match(b)]
        if len(dhits) >= 3:
            out.append(finding("definition-opener", "error",
                               f"{len(dhits)} paragraphs open with a dictionary definition",
                               len(dhits)))
        elif len(dhits) == 2:
            out.append(finding("definition-opener", "warning",
                               "2 paragraphs open with a dictionary definition", len(dhits)))

    if len(sentences) >= 8:
        openers = {}
        for s in sentences:
            key = " ".join(w.lower() for w in WORD.findall(s)[:2])
            if key:
                openers[key] = openers.get(key, 0) + 1
        top, count = max(openers.items(), key=lambda kv: kv[1]) if openers else ("", 0)
        if count >= 4:
            out.append(finding("repeated-opener", "error",
                               f"'{top}' opens {count} sentences", count))
        elif count == 3:
            out.append(finding("repeated-opener", "warning",
                               f"'{top}' opens {count} sentences", count))

    bullets = [n for n, line in enumerate(lines, 1) if BULLET.match(line)]
    bolds = [n for n in bullets if "**" in lines[n - 1][BULLET.match(lines[n - 1]).end():][:3]]
    if len(bullets) >= 5 and len(bolds) / len(bullets) > 0.6:
        out.append(finding("bold-bullet", "error",
                           f"{len(bolds)} of {len(bullets)} bullets carry a bold lead; "
                           "bold only real keys", len(bolds)))
    elif len(bullets) >= 5 and len(bolds) / len(bullets) > 0.4:
        out.append(finding("bold-bullet", "warning",
                           f"{len(bolds)} of {len(bullets)} bullets carry a bold lead", len(bolds)))
    return out


def header_findings(lines):
    out = []
    first_h1_done = False
    for number, line in enumerate(lines, 1):
        match = HEADER_LINE.match(line.strip())
        if not match:
            continue
        level, raw = len(match.group(1)), match.group(2)
        content = re.sub(r"[*_`]", "", raw).strip().rstrip("#").strip()
        if not content:
            continue
        if level == 1 and not first_h1_done:
            first_h1_done = True
            for pattern in TITLE_TEMPLATES:
                if re.search(pattern, content, re.IGNORECASE):
                    out.append(finding("title-template", "error",
                                       f"H1 '{content}' matches a template title "
                                       "('Ultimate Guide' class); use the actual promise"))
                    break
            continue
        for pattern in HEADER_TEMPLATES:
            if re.match(pattern, content, re.IGNORECASE):
                out.append(finding("header-template", "error",
                                   f"header '{content}' is a template header "
                                   "(Introduction/Conclusion class); say something specific"))
                break
    return out


# ------------------------------------------------------------------ driver


def analyze(text, forced_lang):
    lines = clean_lines_of(text)
    words = [w for line in lines for w in WORD.findall(line)]
    lang = forced_lang if forced_lang != "auto" else detect_language(words)
    blocks = prose_blocks(lines)
    sentences = [s for block in blocks for s in split_sentences(block)]
    lens = [len(WORD.findall(s)) for s in sentences]
    lens = [n for n in lens if n]
    findings = []
    findings += term_findings(lines, HARD[lang], "slop-hard", hard=True)
    findings += term_findings(lines, SOFT[lang], "slop-soft", hard=False)
    findings += structure_findings(lines, blocks, sentences, lens, len(words), lang)
    findings += header_findings(lines)
    mean = statistics.mean(lens) if lens else 0
    sd = statistics.pstdev(lens) if len(lens) > 1 else 0
    stats = {
        "language": lang,
        "words": len(words),
        "sentences": len(lens),
        "sentence_words_mean": round(mean, 1),
        "sentence_words_sd": round(sd, 1),
        "paragraphs": len(blocks),
        "em_dashes": sum(line.count("—") + line.count("–") for line in lines),
    }
    return stats, findings


def report_text(reports, errors, warnings):
    for name, stats, findings in reports:
        print(f"blog_lint: {name}")
        print(f"  language: {stats['language']} | words: {stats['words']} | "
              f"sentences: {stats['sentences']} | sentence words: mean "
              f"{stats['sentence_words_mean']} sd {stats['sentence_words_sd']} | "
              f"paragraphs: {stats['paragraphs']} | em dashes: {stats['em_dashes']}")
        for f in sorted(findings, key=lambda f: (f["severity"] != "error", f["rule"])):
            lines = f", ".join(str(n) for n in f["lines"][:5])
            where = f" | lines {lines}" if lines else ""
            print(f"  {f['severity'].upper():7} {f['rule']}: {f['message']}{where}")
        print()
    print(f"findings: {errors} errors, {warnings} warnings")
    if errors:
        print("fix the errors; review the warnings (keep one only when it is deliberate voice).")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag stock AI-writing patterns in a blog post or article.")
    parser.add_argument("files", nargs="*", help="markdown or text files")
    parser.add_argument("--stdin", action="store_true", help="read the document from stdin")
    parser.add_argument("--lang", choices=("auto", "en", "pt"), default="auto")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    documents = []
    if args.stdin:
        documents.append(("<stdin>", sys.stdin.read()))
    for path in args.files:
        target = Path(path)
        if not target.is_file():
            parser.exit(2, f"error: not a readable file: {path}\n")
        documents.append((str(path), target.read_text(encoding="utf-8", errors="replace")))
    if not documents:
        parser.exit(2, "error: pass files or --stdin\n")

    reports, all_findings, stats_by_name = [], [], {}
    for name, text in documents:
        stats, findings = analyze(text, args.lang)
        for f in findings:
            f["file"] = name
        stats_by_name[name] = stats
        reports.append((name, stats, findings))
        all_findings.extend(findings)
    errors = sum(1 for f in all_findings if f["severity"] == "error")
    warnings = sum(1 for f in all_findings if f["severity"] == "warning")

    if args.format == "json":
        print(json.dumps({"files": len(documents), "errors": errors, "warnings": warnings,
                          "findings": all_findings, "stats": stats_by_name}, indent=2))
    else:
        report_text(reports, errors, warnings)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
