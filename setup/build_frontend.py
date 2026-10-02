#!/usr/bin/env python3
"""Synchronize the versioned frontend bundle; preview/check by default."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("frontend-design", "frontend-development", "ai-interface-design")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    package = ROOT / "plugins/caio-frontend"
    changes = []
    for name in SKILLS:
        source = ROOT / name
        destination = package / "skills" / name
        for tree in (source, destination):
            if tree.is_symlink() or any(p.is_symlink() for p in tree.rglob("*")):
                raise SystemExit(f"Bundle tree contains symlink; inspect separately: {tree}")
        expected = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
        actual = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*") if p.is_file()}
        if expected != actual:
            changes.append((source, destination))
    for name in ("LICENSE",):
        source, target = ROOT / name, package / name
        if source.is_symlink() or target.is_symlink():
            raise SystemExit("Bundle license contains symlink; inspect separately")
        if not target.exists() or target.read_bytes() != source.read_bytes():
            changes.append((source, target))
    if not changes:
        print("Bundle sources, references and licenses are in sync.")
        return
    for source, target in changes:
        print(f"sync: {source.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
    if not args.apply:
        raise SystemExit("Bundle out of date; review then run with --apply")
    # Only generated payloads are replaced; manifests and settings are untouched.
    with tempfile.TemporaryDirectory(prefix="frontend-bundle-") as tmp:
        staging = Path(tmp)
        for index, (source, target) in enumerate(changes):
            item = staging / str(index)
            if source.is_dir():
                shutil.copytree(source, item)
            else:
                shutil.copy2(source, item)
        for index, (source, target) in enumerate(changes):
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_dir():
                shutil.rmtree(target)
            shutil.move(str(staging / str(index)), str(target))
    print("Generated payload updated; commit it together with its source changes.")


if __name__ == "__main__":
    main()
