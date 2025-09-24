import json
import subprocess
import sys
from pathlib import Path


def run_cli(args):
    python = sys.executable
    cli = Path(__file__).resolve().parents[2] / "src" / "agent" / "cli" / "deepseek_travels_cli.py"
    cmd = [python, str(cli), "generate"] + args
    cp = subprocess.run(cmd, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout)


def test_llm_flag_adds_explanation_note():
    out = run_cli([
        "Paris", "2025-10-01", "2025-10-03", "3",
        "--tod", "day",
        "--use-llm",
    ])
    notes = out.get("notes", [])
    assert any(n.startswith("LLM: ") for n in notes)


def test_llm_detailed_style_includes_marker():
    out = run_cli([
        "Paris", "2025-10-01", "2025-10-03", "3",
        "--tod", "day",
        "--use-llm",
        "--llm-style", "detailed",
    ])
    notes = out.get("notes", [])
    assert any("(style=detailed)" in n for n in notes)