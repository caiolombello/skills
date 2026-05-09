from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


TITLE_FIELDS = ("title", "sessionTitle", "customTitle", "name", "session_name")
COMMAND_PATTERN = re.compile(r"\b(make|npm|pnpm|yarn|python3?|docker|git|pytest|uv)\s+[^\n`]+")
PATH_PATTERN = re.compile(r"(?<!\w)([~/]?[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)+)")
NEXT_STEP_PATTERN = re.compile(r"(?:next step|pr[oó]ximo passo)\s*:\s*([^\n]+)", re.IGNORECASE)
SESSION_NAME_PATTERN = re.compile(r'The user named this session "([^"]+)"')


class ClaudeResumeError(Exception):
    pass


class SessionNotFoundError(ClaudeResumeError):
    pass


class AmbiguousSessionError(ClaudeResumeError):
    def __init__(self, message: str, candidates: Sequence["SessionRecord"]) -> None:
        super().__init__(message)
        self.candidates = list(candidates)


@dataclass
class SessionRecord:
    session_id: str
    full_path: str
    project_path: str
    title: str | None
    summary: str | None
    created: str | None
    modified: str | None
    message_count: int | None
    git_branch: str | None
    last_message_preview: str
    first_prompt: str | None
    slug: str | None = None

    @property
    def display_title(self) -> str:
        for value in (self.title, self.summary, self.slug, self.first_prompt):
            if value:
                return clean_preview(value)
        return self.session_id

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["display_title"] = self.display_title
        data["relative_modified"] = humanize_relative_time(self.modified)
        return data


def clean_preview(text: str, limit: int = 160) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.casefold().split())


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def humanize_relative_time(value: str | None, now: datetime | None = None) -> str:
    timestamp = parse_timestamp(value)
    if not timestamp:
        return "unknown"
    current = now or datetime.now(timezone.utc)
    seconds = max(0, int((current - timestamp).total_seconds()))
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = months // 12
    return f"{years}y ago"


def normalize_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def path_matches_cwd(project_path: str | None, cwd: Path) -> bool:
    if not project_path:
        return False
    project = normalize_path(project_path)
    current = normalize_path(cwd)
    return project == current or current.is_relative_to(project) or project.is_relative_to(current)


def list_sessions(claude_root: Path, cwd: Path) -> list[SessionRecord]:
    projects_root = claude_root / "projects"
    if not projects_root.exists():
        return []

    records_by_id: dict[str, SessionRecord] = {}

    for index_path in projects_root.rglob("sessions-index.json"):
        for record in load_index_entries(index_path):
            if not path_matches_cwd(record.project_path, cwd):
                continue
            hydrated = hydrate_record(record)
            records_by_id[hydrated.session_id] = hydrated

    for transcript_path in projects_root.rglob("*.jsonl"):
        if "subagents" in transcript_path.parts:
            continue
        record = load_transcript_entry(transcript_path)
        if not record or not path_matches_cwd(record.project_path, cwd):
            continue
        records_by_id.setdefault(record.session_id, record)

    return sorted(
        records_by_id.values(),
        key=lambda item: parse_timestamp(item.modified) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


def hydrate_record(record: SessionRecord) -> SessionRecord:
    transcript_path = Path(record.full_path)
    if not transcript_path.exists():
        return record
    transcript_record = load_transcript_entry(transcript_path)
    if not transcript_record:
        return record
    return SessionRecord(
        session_id=record.session_id,
        full_path=record.full_path,
        project_path=record.project_path or transcript_record.project_path,
        title=record.title or transcript_record.title,
        summary=record.summary or transcript_record.summary,
        created=record.created or transcript_record.created,
        modified=record.modified or transcript_record.modified,
        message_count=record.message_count or transcript_record.message_count,
        git_branch=record.git_branch or transcript_record.git_branch,
        last_message_preview=transcript_record.last_message_preview or record.last_message_preview,
        first_prompt=record.first_prompt or transcript_record.first_prompt,
        slug=record.slug or transcript_record.slug,
    )


def load_index_entries(index_path: Path) -> list[SessionRecord]:
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    entries = payload.get("entries", [])
    records: list[SessionRecord] = []
    for entry in entries:
        if entry.get("isSidechain"):
            continue
        title = first_nonempty(entry.get(field) for field in TITLE_FIELDS)
        summary = entry.get("summary")
        first_prompt = entry.get("firstPrompt")
        record = SessionRecord(
            session_id=entry.get("sessionId", ""),
            full_path=entry.get("fullPath", str(index_path.parent / f"{entry.get('sessionId', '')}.jsonl")),
            project_path=entry.get("projectPath") or payload.get("originalPath") or "",
            title=title,
            summary=summary,
            created=entry.get("created"),
            modified=entry.get("modified"),
            message_count=entry.get("messageCount"),
            git_branch=entry.get("gitBranch"),
            last_message_preview="",
            first_prompt=first_prompt,
            slug=entry.get("slug"),
        )
        if record.session_id:
            records.append(record)
    return records


def load_transcript_entry(jsonl_path: Path) -> SessionRecord | None:
    all_turns = read_turn_payloads(jsonl_path)
    useful_turns = filter_useful_turns(all_turns)
    if not useful_turns:
        return None

    first = useful_turns[0]
    last = useful_turns[-1]
    session_id = first.get("sessionId") or last.get("sessionId") or jsonl_path.stem
    project_path = first_nonempty(turn.get("cwd") for turn in useful_turns) or ""
    title = extract_session_name(all_turns) or first_nonempty(
        turn.get(field)
        for turn in useful_turns
        for field in TITLE_FIELDS
    )
    slug = first_nonempty(turn.get("slug") for turn in useful_turns)
    git_branch = first_nonempty(reversed([turn.get("gitBranch") for turn in useful_turns]))
    first_prompt = first_nonempty(
        extract_message_text(turn)
        for turn in useful_turns
        if extract_role(turn) == "user"
    )
    last_message = first_nonempty(
        extract_message_text(turn)
        for turn in reversed(useful_turns)
    ) or ""

    return SessionRecord(
        session_id=session_id,
        full_path=str(jsonl_path),
        project_path=project_path,
        title=title,
        summary=None,
        created=first.get("timestamp"),
        modified=last.get("timestamp"),
        message_count=len(useful_turns),
        git_branch=git_branch,
        last_message_preview=clean_preview(last_message),
        first_prompt=first_prompt,
        slug=slug,
    )


def read_useful_turns(jsonl_path: Path) -> list[dict[str, Any]]:
    return filter_useful_turns(read_turn_payloads(jsonl_path))


def read_turn_payloads(jsonl_path: Path) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    try:
        for raw_line in jsonl_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            turns.append(payload)
    except OSError:
        return []
    return turns


def filter_useful_turns(turns: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for payload in turns:
        if payload.get("isSidechain"):
            continue
        role = extract_role(payload)
        text = extract_message_text(payload)
        if role not in {"user", "assistant"} or not text or is_noise_text(text):
            continue
        filtered.append(payload)
    return filtered


def extract_role(payload: dict[str, Any]) -> str | None:
    if payload.get("type") in {"user", "assistant"}:
        return payload.get("type")
    message = payload.get("message")
    if isinstance(message, dict):
        role = message.get("role")
        if isinstance(role, str):
            return role
    return None


def extract_message_text(payload: dict[str, Any]) -> str:
    message = payload.get("message")
    content = message.get("content") if isinstance(message, dict) else payload.get("content")
    if isinstance(content, str):
        return clean_preview(content, limit=500)
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    chunks.append(item["text"])
                elif isinstance(item.get("content"), str):
                    chunks.append(item["content"])
        return clean_preview(" ".join(chunks), limit=500)
    return ""


def extract_session_name(turns: Sequence[dict[str, Any]]) -> str | None:
    for turn in turns:
        text = extract_message_text(turn)
        if not text:
            continue
        match = SESSION_NAME_PATTERN.search(text)
        if match:
            return match.group(1).strip()
    return None


def first_nonempty(values: Iterable[Any]) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def resolve_session(
    records: Sequence[SessionRecord],
    session_id: str | None = None,
    name: str | None = None,
) -> SessionRecord:
    if session_id:
        exact = [record for record in records if record.session_id == session_id]
        if len(exact) == 1:
            return exact[0]
        prefix_matches = [record for record in records if record.session_id.startswith(session_id)]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        if prefix_matches:
            raise AmbiguousSessionError("Multiple sessions match the id prefix.", prefix_matches)
        raise SessionNotFoundError("No session matched the provided id.")

    if name:
        target = normalize_text(name)
        scored: dict[int, list[SessionRecord]] = {}
        for record in records:
            fields = [
                normalize_text(record.display_title),
                normalize_text(record.summary),
                normalize_text(record.title),
                normalize_text(record.first_prompt),
            ]
            score: int | None = None
            if target in fields:
                score = 0
            elif any(target and target in field for field in fields if field):
                score = 1
            if score is not None:
                scored.setdefault(score, []).append(record)
        if not scored:
            raise SessionNotFoundError("No session matched the provided name.")
        best_score = min(scored)
        if len(scored[best_score]) > 1:
            raise AmbiguousSessionError("Multiple sessions match the provided name.", scored[best_score])
        return scored[best_score][0]

    raise SessionNotFoundError("A session selector is required.")


def build_import_brief(
    record: SessionRecord,
    cwd: Path | None = None,
    max_recent_turns: int = 6,
) -> dict[str, Any]:
    turns = read_useful_turns(Path(record.full_path))
    extracted_turns = [
        {
            "role": extract_role(turn),
            "timestamp": turn.get("timestamp"),
            "text": extract_message_text(turn),
        }
        for turn in turns
    ]

    goal = first_nonempty(
        turn["text"]
        for turn in extracted_turns
        if turn["role"] == "user"
    ) or record.first_prompt or record.display_title

    files = extract_paths(turn["text"] for turn in extracted_turns)
    commands = extract_commands(turn["text"] for turn in extracted_turns)
    next_steps = extract_next_steps(turn["text"] for turn in extracted_turns)
    if not next_steps and commands:
        next_steps = [f"Run or verify: {command}" for command in commands[:3]]

    decisions = [
        turn["text"]
        for turn in extracted_turns
        if turn["role"] == "assistant"
        and contains_decision_signal(turn["text"])
    ][:8]

    unresolved = [
        turn["text"]
        for turn in extracted_turns
        if turn["text"].rstrip().endswith("?")
    ][:5]

    alignment = None
    if cwd is not None:
        alignment = {
            "cwd": str(normalize_path(cwd)),
            "session_project_path": record.project_path,
            "matches_current_repo": path_matches_cwd(record.project_path, cwd),
        }

    brief = {
        "session": record.to_dict(),
        "repository_alignment": alignment,
        "goal": goal,
        "important_decisions": decisions,
        "files_referenced": files,
        "commands_referenced": commands,
        "unresolved_questions": unresolved,
        "next_steps": next_steps,
        "recent_turns": extracted_turns[-max_recent_turns:],
    }
    return brief


def extract_paths(texts: Iterable[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for match in PATH_PATTERN.findall(text):
            cleaned = match.rstrip(".,:;)")
            if "/" not in cleaned or cleaned in seen or not is_probable_path(cleaned):
                continue
            seen.add(cleaned)
            found.append(cleaned)
    return found


def extract_commands(texts: Iterable[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for match in COMMAND_PATTERN.findall(text):
            # findall returns only first group when pattern has groups, so use finditer below
            pass
        for match in COMMAND_PATTERN.finditer(text):
            command = clean_preview(match.group(0), limit=200)
            if command not in seen:
                seen.add(command)
                found.append(command)
    return found


def extract_next_steps(texts: Iterable[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for match in NEXT_STEP_PATTERN.finditer(text):
            step = clean_preview(match.group(1), limit=200)
            if step not in seen:
                seen.add(step)
                found.append(step)
    return found


def contains_decision_signal(text: str) -> bool:
    normalized = normalize_text(text)
    keywords = (
        "ajustei",
        "corrigi",
        "mudei",
        "adicionei",
        "implementei",
        "removi",
        "fix",
        "fixed",
        "updated",
        "changed",
        "next step",
        "próximo passo",
    )
    return any(keyword in normalized for keyword in keywords)


def is_noise_text(text: str) -> bool:
    normalized = text.strip()
    if normalized.startswith("<system-reminder>"):
        return True
    if normalized.startswith("<command-message>"):
        return True
    if normalized.startswith("API Error:"):
        return True
    return False


def is_probable_path(candidate: str) -> bool:
    if candidate.startswith(("/", "~/", "./", "../")):
        return True
    if "." in candidate:
        return True
    return candidate.count("/") >= 2


def format_list_output(records: Sequence[SessionRecord]) -> str:
    lines = []
    for index, record in enumerate(records, start=1):
        lines.append(
            f"{index}. {record.display_title} [{humanize_relative_time(record.modified)}] "
            f"{record.session_id} - {record.last_message_preview}"
        )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List and import Claude Code sessions for Codex.")
    parser.add_argument("command", nargs="?", choices=("list", "show", "import"), default="list")
    parser.add_argument("--cwd", default=str(Path.cwd()))
    parser.add_argument("--claude-root", default=str(Path("~/.claude").expanduser()))
    parser.add_argument("--id", dest="session_id")
    parser.add_argument("--name")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-recent-turns", type=int, default=6)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    claude_root = normalize_path(args.claude_root)
    cwd = normalize_path(args.cwd)
    records = list_sessions(claude_root=claude_root, cwd=cwd)

    try:
        if args.command == "list":
            payload = {"status": "ok", "sessions": [record.to_dict() for record in records]}
        else:
            record = resolve_session(records, session_id=args.session_id, name=args.name)
            if args.command == "show":
                payload = {"status": "ok", "session": record.to_dict()}
            else:
                payload = {
                    "status": "ok",
                    "brief": build_import_brief(record, cwd=cwd, max_recent_turns=args.max_recent_turns),
                }
    except ClaudeResumeError as exc:
        payload = {"status": "error", "message": str(exc)}
        if isinstance(exc, AmbiguousSessionError):
            payload["candidates"] = [candidate.to_dict() for candidate in exc.candidates]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1
        print(payload["message"])
        return 1

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.command == "list":
        print(format_list_output(records))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
