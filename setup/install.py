#!/usr/bin/env python3
"""Selective, offline Agent Skills installer. Python 3.9+, standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

PROVIDERS = {
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "opencode": ".config/opencode/skills",
    "gemini": ".gemini/skills",
    "kiro": ".kiro/skills",
    "cursor": ".cursor/skills",
    "antigravity": ".gemini/config/skills",
    "antigravity-cli": ".gemini/antigravity-cli/skills",
}
REPO = Path(__file__).resolve().parents[1]
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fingerprint(path):
    """Snapshot a tree without following symlinks (including broken links)."""
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if not path.exists():
        return {"kind": "absent"}
    if not path.is_dir():
        return {"kind": "file", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    files = {}
    for child in sorted(path.rglob("*")):
        rel = child.relative_to(path).as_posix()
        if child.is_symlink():
            files[rel] = {"link": os.readlink(child)}
        elif child.is_file():
            files[rel] = {"sha256": hashlib.sha256(child.read_bytes()).hexdigest()}
        elif child.is_dir():
            files[rel] = {"directory": True}
        else:
            raise ValueError(f"Unsupported special file: {child}")
    return {"kind": "directory", "files": files}


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def bounded(path, home):
    resolved = path.resolve()
    if resolved != home and home not in resolved.parents:
        raise ValueError(f"Destination escapes selected home: {path}")
    return resolved


def check_state_paths(state):
    # Refuse aliases in state ancestors and descendants, including temporary files.
    for path in [state, *state.parents]:
        if path.is_symlink():
            raise ValueError(f"State path contains symlink: {path}")
    if state.exists():
        for path in state.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"State contains symlink: {path}")


def native_target(value, home):
    if not isinstance(value, str):
        raise ValueError("Invalid target")
    target = Path(value)
    if (not target.is_absolute() or str(target) != value or
            not NAME.fullmatch(target.name) or
            target.parent not in {home / p for p in PROVIDERS.values()} or
            bounded(target.parent, home) != target.parent):
        raise ValueError(f"Invalid native skill target: {value}")
    return target


def check_snapshot(value, absent=False):
    if absent and value == {"kind": "absent"}:
        return
    if not isinstance(value, dict) or set(value) != {"kind", "files"} or value["kind"] != "directory" or not isinstance(value["files"], dict):
        raise ValueError("Invalid directory snapshot")
    for name, entry in value["files"].items():
        if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("Invalid snapshot path")
        if entry != {"directory": True} and not (isinstance(entry, dict) and set(entry) == {"sha256"} and isinstance(entry["sha256"], str) and re.fullmatch(r"[a-f0-9]{64}", entry["sha256"])):
            raise ValueError("Invalid snapshot entry")


def check_owner(value):
    if not isinstance(value, dict) or set(value) != {"fingerprint", "transaction"} or not isinstance(value["transaction"], str) or not re.fullmatch(r"[a-f0-9]{32}", value["transaction"]):
        raise ValueError("Invalid ownership record")
    check_snapshot(value["fingerprint"])


def load_installed(state, home):
    installed = read_json(state / "installed.json", {})
    if not isinstance(installed, dict):
        raise ValueError("Invalid installed state: expected object")
    for target, owner in installed.items():
        native_target(target, home)
        check_owner(owner)
    return installed


def selection(args):
    names = []
    if args.manifest:
        for line in Path(args.manifest).read_text().splitlines():
            name = line.split("#", 1)[0].strip()
            if name:
                names.append(name)
    names.extend(args.skill or [])
    if not names:
        raise ValueError("Select --skill NAME (repeatable) or --manifest PATH; no bulk default")
    sources = []
    for name in dict.fromkeys(names):
        if not NAME.fullmatch(name) or name in {"synced", "anthropic-skills"}:
            raise ValueError(f"Invalid/reserved skill name: {name}")
        source = REPO / name
        if source.is_symlink() or not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing ordinary source skill: {name}")
        snapshot = fingerprint(source)
        if any("link" in value for value in snapshot["files"].values()):
            raise ValueError(f"Source contains symlinks; inspect separately: {name}")
        sources.append((name, source, snapshot))
    return sources


def plan(args, home, state):
    if not args.provider:
        raise ValueError("Select --provider NAME (repeatable); use --list-providers")
    installed = load_installed(state, home)
    operations = []
    seen = set()
    sources = selection(args)
    for provider in args.provider:
        # Resolve an existing provider-root alias, but never a skill-name alias.
        root = bounded(home / PROVIDERS[provider], home)
        if root not in {home / path for path in PROVIDERS.values()}:
            raise ValueError(f"Provider root redirects outside native skill roots: {root}")
        for name, source, after in sources:
            target = root / name
            key = str(target)
            if key in seen:
                continue
            seen.add(key)
            before = fingerprint(target)
            managed = installed.get(key)
            if managed:
                if before != managed["fingerprint"]:
                    raise ValueError(f"Managed destination changed locally; preserve it: {target}")
                action = "unchanged" if before == after else "update"
            elif before["kind"] == "absent":
                action = "install"
            elif before["kind"] == "symlink" and target.resolve() == source.resolve():
                # An existing live checkout link needs neither adoption nor copying.
                action = "existing-link"
            else:
                raise ValueError(f"Unmanaged destination exists; no overwrite: {target}")
            operations.append({"action": action, "target": key, "source": str(source),
                               "before": before, "after": after})
    return operations, installed


def restore_paths(op, journal):
    target = Path(op["target"])
    prefix = ".caio-rollback-" + journal + "-" + op["backup"]
    return target.parent / (prefix + "-stage"), target.parent / (prefix + "-retired")


def check_restore_scratch(op, journal, backup_root):
    stage, retired = restore_paths(op, journal)
    for scratch in (stage, retired):
        if scratch.is_symlink():
            raise ValueError(f"Rollback scratch is a symlink: {scratch}")
        if scratch.exists() and op["phase"] != "restoring":
            raise ValueError(f"Unowned rollback scratch exists: {scratch}")
    if retired.exists() and fingerprint(retired) != op["after"]:
        raise ValueError(f"Retired destination changed; preserve it: {retired}")
    if stage.exists():
        partial = fingerprint(stage)
        expected = op["before"]
        if partial["kind"] != "directory" or expected["kind"] != "directory":
            raise ValueError(f"Invalid rollback staging: {stage}")
        for name, entry in partial["files"].items():
            wanted = expected["files"].get(name)
            if entry == wanted:
                continue
            # A killed file copy may have written only a byte prefix. This
            # allowance applies only to journal-owned scratch, never live work.
            if (wanted and "sha256" in wanted and "sha256" in entry and
                    (backup_root / op["backup"] / name).read_bytes().startswith((stage / name).read_bytes())):
                continue
            raise ValueError(f"Rollback staging changed; preserve it: {stage}")


def restore_operation(op, journal, record, journal_path, backup_root):
    """Copy before retiring live content; publish with same-filesystem rename."""
    target = Path(op["target"])
    stage, retired = restore_paths(op, journal)
    check_restore_scratch(op, journal, backup_root)
    op["phase"] = "restoring"
    save_json(journal_path, record)
    current = fingerprint(target)
    if current != op["before"]:
        if op["before"]["kind"] != "absent":
            # An interrupted partial staging tree is replaceable only after its
            # existing entries have been checked against the immutable backup.
            remove(stage)
            shutil.copytree(backup_root / op["backup"], stage)
            if fingerprint(stage) != op["before"]:
                raise ValueError("Rollback backup changed during staging")
        if fingerprint(target) != current:
            raise ValueError(f"Destination changed during rollback: {target}")
        if current["kind"] != "absent":
            if retired.exists():
                raise ValueError(f"Both live and retired destinations exist: {target}")
            target.rename(retired)
        if op["before"]["kind"] != "absent":
            stage.rename(target)
    # Scratch is retained until ownership and journal completion are recorded.


def rollback(journal, state, home, apply):
    path = state / "transactions" / (journal + ".json")
    record = read_json(path, None)
    if not isinstance(record, dict) or record.get("status") not in ("applied", "prepared"):
        raise ValueError("Rollback requires an applied or interrupted prepared transaction")
    if set(record) != {"status", "operations"} or not isinstance(record["operations"], list) or not record["operations"]:
        raise ValueError("Invalid transaction journal")
    installed = load_installed(state, home)
    seen = set()
    for index, op in enumerate(record["operations"]):
        fields = {"action", "target", "source", "before", "after", "backup", "previous_record", "phase"}
        if not isinstance(op, dict) or set(op) != fields:
            raise ValueError("Invalid transaction operation")
        target = native_target(op["target"], home)
        if str(target) in seen or op["backup"] != str(index) or op["phase"] not in {"ready", "publishing", "restoring"}:
            raise ValueError("Invalid transaction paths or phase")
        seen.add(str(target))
        if op["source"] != str(REPO / target.name):
            raise ValueError("Invalid transaction source")
        check_snapshot(op["before"], absent=True)
        check_snapshot(op["after"])
        previous = op["previous_record"]
        if previous is not None:
            check_owner(previous)
        if (op["action"] == "install" and (op["before"] != {"kind": "absent"} or previous is not None)) or (op["action"] == "update" and (previous is None or previous["fingerprint"] != op["before"])) or op["action"] not in {"install", "update"}:
            raise ValueError("Inconsistent transaction operation")
        owner = installed.get(str(target))
        after_owner = {"fingerprint": op["after"], "transaction": journal}
        if owner != after_owner and not (record["status"] == "prepared" and owner == previous):
            raise ValueError(f"Later or inconsistent transaction owns destination: {target}")
        check_restore_scratch(op, journal, state / "backups" / journal)
        current = fingerprint(target)
        recoverable = record["status"] == "prepared" and (current == op["before"] or (current == {"kind": "absent"} and op["phase"] in {"publishing", "restoring"}))
        if current != op["after"] and not recoverable:
            raise ValueError(f"Changed since install; rollback would overwrite work: {target}")
        if op["before"]["kind"] != "absent":
            if fingerprint(state / "backups" / journal / op["backup"]) != op["before"]:
                raise ValueError(f"Missing or changed backup; not restored: {target}")
        print(f"restore: {target}")
    if not apply:
        return
    record["status"] = "prepared"
    save_json(path, record)
    for op in reversed(record["operations"]):
        target = Path(op["target"])
        restore_operation(op, journal, record, path, state / "backups" / journal)
        if op["previous_record"] is None:
            installed.pop(str(target), None)
        else:
            installed[str(target)] = op["previous_record"]
    save_json(state / "installed.json", installed)
    record["status"] = "rolled-back"
    save_json(path, record)
    for op in record["operations"]:
        for scratch in restore_paths(op, journal):
            remove(scratch)


def install(operations, installed, state):
    changes = [op for op in operations if op["action"] in {"install", "update"}]
    if not changes:
        print("No changes; already installed or linked.")
        return
    transaction = uuid.uuid4().hex
    backup_root = state / "backups" / transaction
    backup_root.mkdir(parents=True)
    record = {"status": "prepared", "operations": []}
    journal = state / "transactions" / (transaction + ".json")
    journal.parent.mkdir(parents=True, exist_ok=True)
    # Back up and verify every operation before the first destination write.
    for index, op in enumerate(changes):
        target = Path(op["target"])
        if fingerprint(target) != op["before"] or fingerprint(Path(op["source"])) != op["after"]:
            raise ValueError("Source or destination changed during planning; rerun")
        op = dict(op, phase="ready", backup=str(index), previous_record=installed.get(str(target)))
        if op["before"]["kind"] != "absent":
            shutil.copytree(target, backup_root / str(index))
        record["operations"].append(op)
    save_json(journal, record)
    written = []
    try:
        for op in record["operations"]:
            target = Path(op["target"])
            if fingerprint(target) != op["before"]:
                raise ValueError(f"Destination changed during transaction: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            staged = backup_root / ("staged-" + op["backup"])
            shutil.copytree(op["source"], staged)
            if fingerprint(staged) != op["after"]:
                raise ValueError("Source changed during copy; rerun")
            op["phase"] = "publishing"
            save_json(journal, record)
            remove(target)
            written.append(op)
            shutil.move(str(staged), str(target))
            installed[str(target)] = {"fingerprint": op["after"], "transaction": transaction}
        save_json(state / "installed.json", installed)
        record["status"] = "applied"
        save_json(journal, record)
    except Exception:
        # Reuse the recoverable rollback path, including atomic publication.
        rollback(transaction, state, state.parents[2], True)
        raise
    print(f"Applied transaction: {transaction}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=PROVIDERS, action="append")
    parser.add_argument("--skill", action="append")
    parser.add_argument("--manifest")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Override only for isolated tests")
    parser.add_argument("--apply", action="store_true", help="Write; default is dry-run")
    parser.add_argument("--rollback", help="Transaction ID; preview unless --apply")
    parser.add_argument("--list-providers", action="store_true")
    args = parser.parse_args()
    if args.list_providers:
        for name, path in PROVIDERS.items():
            print(f"{name}: ~/{path}")
        return
    if args.rollback and not re.fullmatch(r"[a-f0-9]{32}", args.rollback):
        parser.error("Invalid transaction ID")
    home = args.home.expanduser().resolve()
    state = home / ".local/state/caiolombello-skills"
    lock = state / "lock"
    locked = False
    try:
        check_state_paths(state)
        if args.apply:
            state.mkdir(parents=True, exist_ok=True)
            lock.mkdir()  # Concurrent apply/rollback must not share a transaction.
            locked = True
        if args.rollback:
            rollback(args.rollback, state, home, args.apply)
        else:
            operations, installed = plan(args, home, state)
            for op in operations:
                print(f"{op['action']}: {op['target']}")
            if args.apply:
                install(operations, installed, state)
            else:
                print("Dry-run; nothing written. Add --apply after reviewing.")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"{exc}\n")
    finally:
        if locked:
            lock.rmdir()


if __name__ == "__main__":
    main()
