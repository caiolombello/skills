#!/usr/bin/env python3
"""Read-only checks. Never installs, deletes, repairs or launches a provider."""
import sys

# Also prevent local helper/PyYAML bytecode writes when invoked without -B.
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

try:
    from skill_metadata import manifests, metadata, source_skills
    from install import PROVIDERS, fingerprint
except ImportError:
    sys.exit("Install check dependencies with: python3 -m pip install -r setup/requirements-checks.txt")


def add(report, level, code, path, message):
    report["findings"].append({"level": level, "code": code,
                               "path": str(path), "message": message})


def local_references(path, repo, report):
    """Check inline Markdown destinations, excluding fences/URLs/fragments/templates.

    This is deliberately not a Markdown renderer or a checker of prose/code paths.
    Missing references are warnings: some intentionally target optional/private skills.
    """
    fence = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        mark = re.match(r"^\s*(`{3,}|~{3,})", line)
        if mark:
            token = mark.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        for match in re.finditer(r"\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", line):
            value = match.group(1).strip("<>")
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
                continue
            relative = unquote(parsed.path)
            if any(c in relative for c in "{}*$`"):
                continue
            target = (path.parent / relative).resolve()
            if target != repo and repo not in target.parents:
                add(report, "warning", "external-reference", path,
                    f"line {number}: local target outside source repository: {value}")
            elif not target.exists():
                add(report, "warning", "reference", path,
                    f"line {number}: unavailable local target: {value}")


def evaluation(path, repo, report):
    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("evaluation must be a regular file")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("expected version 1 evaluation object")
        cases = data.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("cases must be a nonempty list")
        ids = set()
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError("each case must be an object")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id or case_id in ids:
                raise ValueError("case ids must be nonempty, unique strings")
            ids.add(case_id)
            if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                raise ValueError(f"{case_id}: missing prompt")
            expectations = case.get("expectations")
            primary = case.get("primary")
            if expectations is None:
                if primary not in [*report["skills"], "none"]:
                    raise ValueError(f"{case_id}: missing expectations or valid primary skill")
            elif not isinstance(expectations, list) or not expectations or any(
                    not isinstance(item, str) or not item.strip() for item in expectations):
                raise ValueError(f"{case_id}: invalid expectations")
            artifacts = case.get("artifacts", [])
            if not isinstance(artifacts, list):
                raise ValueError(f"{case_id}: artifacts must be a list")
            for artifact in artifacts:
                if not isinstance(artifact, str):
                    raise ValueError(f"{case_id}: artifact must be a relative path")
                target = (path.parent / artifact).resolve()
                if Path(artifact).is_absolute() or not inside(target, repo) or not target.is_file():
                    raise ValueError(f"{case_id}: missing or external artifact: {artifact}")
    except (ValueError, OSError) as error:
        add(report, "error", "evaluation", path, str(error))


def diagnose(repo):
    report = {"version": 1, "skills": [], "findings": [], "installed": [],
              "runtime_verified": False}
    for path in source_skills(repo):
        # Do not parse external sources reached via a skill or payload symlink.
        links = [path] if path.is_symlink() else [p for p in path.rglob("*") if p.is_symlink()]
        if links:
            for link in links:
                add(report, "error", "source-link", link, "source payload symlink; not inspected")
            continue
        try:
            metadata(path)
            report["skills"].append(path.name)
            for doc in sorted(path.rglob("*.md")):
                if doc.is_file():
                    local_references(doc, repo, report)
        except (ValueError, OSError) as error:
            add(report, "error", "metadata", path, str(error))
    if not report["skills"]:
        add(report, "error", "empty-source", repo, "no valid source skills found")
    try:
        for name, entries in manifests(repo).items():
            seen = set()
            for entry in entries:
                if entry not in report["skills"]:
                    add(report, "error", "manifest", repo / "install-manifests" / (name + ".txt"),
                        f"unknown or invalid skill: {entry}")
                elif entry in seen:
                    add(report, "warning", "manifest-duplicate", name, f"repeated entry: {entry}")
                seen.add(entry)
    except (OSError, ValueError) as error:
        add(report, "error", "manifest", repo / "install-manifests", str(error))
    for name in report["skills"]:
        path = repo / name / "evals/scenarios.json"
        if path.exists():
            evaluation(path, repo, report)
    routing = repo / "setup/evals/description-routing.json"
    if routing.exists():
        if any(p.is_symlink() for p in [routing, routing.parent, routing.parent.parent]):
            add(report, "error", "evaluation", routing, "aliased evaluation path; not inspected")
        else:
            evaluation(routing, repo, report)
    return report


def inside(path, parent):
    return path == parent or parent in path.parents


def installed(report, repo, home, providers):
    state = home / ".local/state/caiolombello-skills/installed.json"
    owned = {}
    if any(p.is_symlink() for p in [state, *state.parents]):
        add(report, "warning", "state", state, "aliased state not inspected")
    elif state.exists():
        try:
            owned = json.loads(state.read_text(encoding="utf-8"))
            if not isinstance(owned, dict):
                raise ValueError("state must be a mapping")
        except (ValueError, OSError):
            owned = {}
            add(report, "warning", "state", state, "invalid or unreadable ownership state")
    source = {name: (repo / name).resolve() for name in report["skills"]}
    for provider in providers:
        roots = [home / PROVIDERS[provider]]
        if provider in {"codex", "opencode", "gemini", "cursor"}:
            roots.append(home / ".agents/skills")
        if provider == "codex":
            roots.append(home / ".codex/skills")
        seen_roots, seen_skills = set(), {}
        for root in roots:
            resolved = root.resolve()
            if not inside(resolved, home):
                add(report, "warning", "external-root", root, "root escapes selected home; not inspected")
                continue
            if resolved in seen_roots:
                continue
            seen_roots.add(resolved)
            if not root.exists():
                if root.is_symlink():
                    add(report, "error", "broken-link", root, "provider root link has no target")
                continue
            if not root.is_dir():
                add(report, "error", "provider-root", root, "provider root is not a directory")
                continue
            for target in sorted(root.iterdir()):
                if target.name.startswith("."):
                    continue
                status, skill_name = "foreign-entry", target.name
                actual = target.resolve()
                if target.is_symlink():
                    if not target.exists():
                        status = "broken-link"
                        add(report, "error", status, target, "link has no target")
                    elif actual in source.values():
                        skill_name = next(n for n, p in source.items() if p == actual)
                        status = "source-link"
                    else:
                        status = "foreign-link"  # No content read through unknown links.
                elif skill_name in source and target.is_dir():
                    current, desired = fingerprint(target), fingerprint(source[skill_name])
                    record = owned.get(str(target), owned.get(str(actual), {}))
                    recorded = record.get("fingerprint") if isinstance(record, dict) else None
                    if recorded is not None and current != recorded:
                        status = "locally-edited-copy"
                    elif current == desired:
                        status = "matching-copy" if recorded is not None else "unmanaged-matching-copy"
                    else:
                        status = "outdated-copy" if recorded is not None else "unmanaged-divergent-copy"
                    if status in {"locally-edited-copy", "outdated-copy", "unmanaged-divergent-copy"}:
                        add(report, "warning", status, target, "content differs; no changes made")
                if status in {"source-link", "matching-copy", "unmanaged-matching-copy",
                              "locally-edited-copy", "outdated-copy", "unmanaged-divergent-copy"}:
                    if skill_name in seen_skills:
                        add(report, "warning", "duplicate", target,
                            f"same skill also present for {provider}: {seen_skills[skill_name]}")
                    seen_skills[skill_name] = str(target)
                report["installed"].append({"provider": provider, "path": str(target),
                                             "skill": skill_name, "status": status})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--installed", action="store_true", help="also inspect known local provider roots")
    parser.add_argument("--provider", choices=PROVIDERS, action="append")
    parser.add_argument("--strict", action="store_true", help="also fail on warnings")
    args = parser.parse_args()
    if args.provider and not args.installed:
        parser.error("--provider requires --installed")
    try:
        report = diagnose(args.repo.resolve())
        if args.installed:
            installed(report, args.repo.resolve(), args.home.resolve(), args.provider or list(PROVIDERS))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot inspect repository: {error}\n")
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Source skills: {len(report['skills'])}; runtime verification: not performed")
        print(f"Installed entries inspected: {len(report['installed'])}")
        for item in report["findings"]:
            print(f"{item['level'].upper()} {item['code']}: {item['path']}: {item['message']}")
    return int(any(item["level"] == "error" or args.strict for item in report["findings"]))


if __name__ == "__main__":
    sys.exit(main())
