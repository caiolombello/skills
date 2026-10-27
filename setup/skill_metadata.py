"""Read source metadata without importing or executing skill payloads."""
import re
from pathlib import Path

import yaml

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def source_skills(repo):
    return [p for p in sorted(repo.iterdir()) if not p.name.startswith(".")
            and (p / "SKILL.md").exists()]


def metadata(skill):
    if not (skill / "SKILL.md").is_file():
        raise ValueError("SKILL.md must be a regular file")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as error:
        raise ValueError("invalid or unsupported YAML frontmatter") from error
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    if any(not isinstance(key, str) for key in data):
        raise ValueError("frontmatter keys must be strings")
    name, description = data.get("name"), data.get("description")
    if (not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name)
            or name != skill.name):
        raise ValueError("name must match the kebab-case folder (max 64 characters)")
    if (not isinstance(description, str) or not description.strip()
            or len(description) > 1024 or "<" in description or ">" in description):
        raise ValueError("description must be a nonempty string, max 1024 characters, without angle brackets")
    if set(data) - FIELDS:
        raise ValueError("unsupported frontmatter fields: " + ", ".join(sorted(set(data) - FIELDS)))
    return data


def manifests(repo):
    """Public profiles only. Private/local selections are deliberately excluded."""
    folder = repo / "install-manifests"
    if folder.is_symlink():
        raise ValueError(f"profile directory is a symlink: {folder}")
    if not folder.exists():
        return {}
    result = {}
    for path in sorted(folder.glob("*.txt")):
        if ".local" in path.name:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"profile must be a regular file: {path}")
        result[path.stem] = [line.split("#", 1)[0].strip()
                             for line in path.read_text(encoding="utf-8").splitlines()
                             if line.split("#", 1)[0].strip()]
    return result
