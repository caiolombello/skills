"""Check local media inspection against disposable real media; no provider calls."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[2] / "content-production/scripts/probe_media.py"


class MediaProbeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffprobe"), "ffprobe unavailable")
    def test_audio_only_metadata_and_original_are_preserved(self):
        with tempfile.TemporaryDirectory(prefix="audio probe ") as folder:
            media = Path(folder) / "narration fixture.wav"
            with wave.open(str(media), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(16000)
                output.writeframes(b"".join(struct.pack("<h", int(4000 * math.sin(2 * math.pi * 440 * i / 16000))) for i in range(4000)))
            before = hashlib.sha256(media.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(media)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(len(report["streams"]), 1)
            stream = report["streams"][0]
            self.assertEqual((stream["codec_type"], stream["channels"], stream["sample_rate"]), ("audio", 1, "16000"))
            self.assertAlmostEqual(float(report["format"]["duration"]), 0.25, places=3)
            self.assertIn("audio quality", report["verification"])
            self.assertEqual(hashlib.sha256(media.read_bytes()).hexdigest(), before)

    def test_missing_and_remote_inputs_are_rejected(self):
        for value in ("/nonexistent/caio-content-absent.mp4", "https://example.com/clip.mp4"):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), value],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("existing local media file", json.loads(result.stderr)["error"])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/ffprobe unavailable")
    def test_real_media_is_inspected_without_modification(self):
        with tempfile.TemporaryDirectory(prefix="content probe ") as folder:
            root = Path(folder)
            media = root / "clip $literal;not-shell.mkv"
            subprocess.run([
                "ffmpeg", "-v", "error", "-nostdin", "-n", "-f", "lavfi",
                "-i", "color=c=blue:s=160x90:r=10", "-t", "0.3", "-an",
                "-c:v", "ffv1", str(media),
            ], check=True, capture_output=True)
            before = (hashlib.sha256(media.read_bytes()).hexdigest(), media.stat().st_mtime_ns)
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(media)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            video = next(s for s in report["streams"] if s["codec_type"] == "video")
            self.assertEqual((video["width"], video["height"], video["codec_name"]), (160, 90, "ffv1"))
            self.assertFalse(any(s["codec_type"] == "audio" for s in report["streams"]))
            self.assertIn("metadata only", report["verification"])
            self.assertEqual(before, (hashlib.sha256(media.read_bytes()).hexdigest(), media.stat().st_mtime_ns))
            self.assertEqual(list(root.iterdir()), [media])

    @unittest.skipUnless(shutil.which("ffprobe"), "ffprobe unavailable")
    def test_corrupt_file_is_not_reported_as_verified(self):
        with tempfile.TemporaryDirectory(prefix="content corrupt ") as folder:
            media = Path(folder) / "bad.mp4"
            media.write_bytes(b"not a video")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(media)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["error"], "ffprobe failed")
            self.assertFalse(result.stdout)
            self.assertEqual(media.read_bytes(), b"not a video")


if __name__ == "__main__":
    unittest.main()
