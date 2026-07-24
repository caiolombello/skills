import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

import claude_resume  # type: ignore  # noqa: E402


class ClaudeResumeTests(unittest.TestCase):
    def test_list_prefers_sessions_index_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude_root = Path(tmp) / ".claude"
            projects_root = claude_root / "projects"
            project_dir = projects_root / "-Users-test-demo"
            project_dir.mkdir(parents=True)

            session_path = project_dir / "11111111-1111-1111-1111-111111111111.jsonl"
            session_path.write_text("", encoding="utf-8")

            index_payload = {
                "version": 1,
                "entries": [
                    {
                        "sessionId": "11111111-1111-1111-1111-111111111111",
                        "fullPath": str(session_path),
                        "summary": "Infra deploy fix",
                        "messageCount": 14,
                        "created": "2026-04-28T10:00:00Z",
                        "modified": "2026-04-28T12:00:00Z",
                        "projectPath": "/work/demo",
                        "gitBranch": "main",
                        "isSidechain": False,
                    },
                    {
                        "sessionId": "22222222-2222-2222-2222-222222222222",
                        "fullPath": str(project_dir / "22222222-2222-2222-2222-222222222222.jsonl"),
                        "summary": "Other repo session",
                        "messageCount": 3,
                        "created": "2026-04-27T10:00:00Z",
                        "modified": "2026-04-27T12:00:00Z",
                        "projectPath": "/work/other",
                        "gitBranch": "main",
                        "isSidechain": False,
                    },
                ],
                "originalPath": "/work/demo",
            }
            (project_dir / "sessions-index.json").write_text(
                json.dumps(index_payload),
                encoding="utf-8",
            )

            sessions = claude_resume.list_sessions(
                claude_root=claude_root,
                cwd=Path("/work/demo"),
            )

            self.assertEqual(1, len(sessions))
            self.assertEqual("11111111-1111-1111-1111-111111111111", sessions[0].session_id)
            self.assertEqual("Infra deploy fix", sessions[0].display_title)
            self.assertEqual(14, sessions[0].message_count)

    def test_list_falls_back_to_jsonl_when_index_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude_root = Path(tmp) / ".claude"
            project_dir = claude_root / "projects" / "-Users-test-demo"
            project_dir.mkdir(parents=True)

            transcript_path = project_dir / "33333333-3333-3333-3333-333333333333.jsonl"
            transcript = [
                {
                    "type": "user",
                    "timestamp": "2026-04-28T10:00:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "33333333-3333-3333-3333-333333333333",
                    "message": {"role": "user", "content": "analise o deploy do traefik"},
                },
                {
                    "type": "assistant",
                    "timestamp": "2026-04-28T10:05:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "33333333-3333-3333-3333-333333333333",
                    "gitBranch": "main",
                    "slug": "kind-river",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Encontrei o problema no docker-compose.yml"}],
                    },
                },
            ]
            transcript_path.write_text(
                "\n".join(json.dumps(line) for line in transcript) + "\n",
                encoding="utf-8",
            )

            sessions = claude_resume.list_sessions(
                claude_root=claude_root,
                cwd=Path("/work/demo"),
            )

            self.assertEqual(1, len(sessions))
            self.assertEqual("33333333-3333-3333-3333-333333333333", sessions[0].session_id)
            self.assertIn("docker-compose.yml", sessions[0].last_message_preview)
            self.assertEqual("kind-river", sessions[0].display_title)

    def test_resolve_unique_session_by_id_prefix(self):
        records = [
            claude_resume.SessionRecord(
                session_id="aaaaaaaa-1111-1111-1111-111111111111",
                full_path="/tmp/a.jsonl",
                project_path="/work/demo",
                title="Deploy fix",
                summary="Deploy fix",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="fix deploy",
            ),
            claude_resume.SessionRecord(
                session_id="bbbbbbbb-2222-2222-2222-222222222222",
                full_path="/tmp/b.jsonl",
                project_path="/work/demo",
                title="Other issue",
                summary="Other issue",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="other",
            ),
        ]

        match = claude_resume.resolve_session(records, session_id="aaaaaaaa")

        self.assertEqual("aaaaaaaa-1111-1111-1111-111111111111", match.session_id)

    def test_resolve_unique_session_by_name(self):
        records = [
            claude_resume.SessionRecord(
                session_id="aaaaaaaa-1111-1111-1111-111111111111",
                full_path="/tmp/a.jsonl",
                project_path="/work/demo",
                title="Traefik deploy regression",
                summary="Traefik deploy regression",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="fix deploy",
            ),
            claude_resume.SessionRecord(
                session_id="bbbbbbbb-2222-2222-2222-222222222222",
                full_path="/tmp/b.jsonl",
                project_path="/work/demo",
                title="Chatwoot note",
                summary="Chatwoot note",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="other",
            ),
        ]

        match = claude_resume.resolve_session(records, name="traefik deploy")

        self.assertEqual("aaaaaaaa-1111-1111-1111-111111111111", match.session_id)

    def test_resolve_reports_ambiguity_for_name_conflict(self):
        records = [
            claude_resume.SessionRecord(
                session_id="aaaaaaaa-1111-1111-1111-111111111111",
                full_path="/tmp/a.jsonl",
                project_path="/work/demo",
                title="Deploy fix traefik",
                summary="Deploy fix traefik",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="fix deploy",
            ),
            claude_resume.SessionRecord(
                session_id="bbbbbbbb-2222-2222-2222-222222222222",
                full_path="/tmp/b.jsonl",
                project_path="/work/demo",
                title="Deploy fix chatwoot",
                summary="Deploy fix chatwoot",
                created="2026-04-28T10:00:00Z",
                modified="2026-04-28T11:00:00Z",
                message_count=4,
                git_branch="main",
                last_message_preview="done",
                first_prompt="other",
            ),
        ]

        with self.assertRaises(claude_resume.AmbiguousSessionError):
            claude_resume.resolve_session(records, name="deploy fix")

    def test_import_builds_continuation_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript_path = Path(tmp) / "44444444-4444-4444-4444-444444444444.jsonl"
            transcript = [
                {
                    "type": "user",
                    "timestamp": "2026-04-28T09:00:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "44444444-4444-4444-4444-444444444444",
                    "message": {"role": "user", "content": "corrija o deploy do traefik em servers/oci1-oci.devbeuni.xyz/traefik-portainer"},
                },
                {
                    "type": "assistant",
                    "timestamp": "2026-04-28T09:05:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "44444444-4444-4444-4444-444444444444",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Vou revisar o docker-compose.yml e o Makefile antes do deploy."}],
                    },
                },
                {
                    "type": "assistant",
                    "timestamp": "2026-04-28T09:10:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "44444444-4444-4444-4444-444444444444",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Ajustei a porta do Traefik. Próximo passo: rodar make deploy e confirmar o healthcheck.",
                            }
                        ],
                    },
                },
            ]
            transcript_path.write_text(
                "\n".join(json.dumps(line) for line in transcript) + "\n",
                encoding="utf-8",
            )

            record = claude_resume.load_transcript_entry(transcript_path)
            brief = claude_resume.build_import_brief(record, max_recent_turns=2)

            self.assertEqual("44444444-4444-4444-4444-444444444444", brief["session"]["session_id"])
            self.assertIn("traefik", brief["goal"].lower())
            self.assertIn("make deploy", brief["next_steps"][0].lower())
            self.assertIn("servers/oci1-oci.devbeuni.xyz/traefik-portainer", brief["files_referenced"][0])
            self.assertEqual(2, len(brief["recent_turns"]))

    def test_transcript_extracts_session_name_from_system_reminder(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript_path = Path(tmp) / "55555555-5555-5555-5555-555555555555.jsonl"
            transcript = [
                {
                    "type": "user",
                    "timestamp": "2026-04-28T18:00:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "55555555-5555-5555-5555-555555555555",
                    "message": {"role": "user", "content": "preciso reiniciar o servico"},
                },
                {
                    "type": "user",
                    "timestamp": "2026-04-28T18:01:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "55555555-5555-5555-5555-555555555555",
                    "message": {
                        "role": "user",
                        "content": '<system-reminder> The user named this session "my-generic-session". This may indicate the session\'s focus or intent. </system-reminder>',
                    },
                },
                {
                    "type": "assistant",
                    "timestamp": "2026-04-28T18:02:00Z",
                    "cwd": "/work/demo",
                    "sessionId": "55555555-5555-5555-5555-555555555555",
                    "message": {"role": "assistant", "content": [{"type": "text", "text": "Vou verificar o serviço systemd."}]},
                },
            ]
            transcript_path.write_text(
                "\n".join(json.dumps(line) for line in transcript) + "\n",
                encoding="utf-8",
            )

            record = claude_resume.load_transcript_entry(transcript_path)
            brief = claude_resume.build_import_brief(record, max_recent_turns=3)

            self.assertEqual("my-generic-session", record.title)
            self.assertEqual("my-generic-session", record.display_title)
            self.assertTrue(all("system-reminder" not in turn["text"] for turn in brief["recent_turns"]))


if __name__ == "__main__":
    unittest.main()
