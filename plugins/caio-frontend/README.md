# Caio Frontend

Three skills: `frontend-design`, `frontend-development`, and `ai-interface-design`.
Choose design for unresolved flow/visual decisions, development for authorized
implementation, and pair AI design with the design baseline for model behavior.

This skills-only package includes distinct Codex, Claude, and Cursor manifests
and a root Agent Plugins manifest for Kiro Powers and supporting runtimes.
It contains no hooks, MCP servers, credentials, or automatic installation actions.
Installation is optional and must use the target provider's own mechanism.
See [provider setup](https://github.com/caiolombello/skills/blob/main/setup/README.md) in the source repository for commands,
update behavior, compatibility boundaries, and validation evidence.

The three skill folders and their references are included. Links to other skills
in the wider library describe optional adjacent workflows; they are not bundled
or automatically installed. Inspect the corresponding folder in
[the source library](https://github.com/caiolombello/skills) when needed, or use
the runtime's available equivalent. Do not assume those sibling skills exist.

The included `ai-interface-design/LICENSE` has source-available terms including
a gambling field-of-use exclusion. Root MIT terms must not be applied to that
skill or its third-party influences. See the bundled LICENSE and CREDITS.md.

Payloads are generated from the root skills with `python3 setup/build_frontend.py
--apply`; changes should be made to the root sources and regenerated. Package
metadata is maintained separately; bump all manifests together when releasing.
