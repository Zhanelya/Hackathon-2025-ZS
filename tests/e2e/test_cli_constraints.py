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
    return cp.stdout


def test_cli_with_constraints_applies_fitter():
    out = run_cli([
        "Paris", "2025-10-01", "2025-10-03", "3",
        "--activities", "beach",
        "--tod", "day", "night",
        "--weather", "cold", "rain",
        "--capacity-liters", "8.0",
        "--max-weight-kg", "3.0",
    ])
    data = json.loads(out)
    notes = data.get("notes", [])
    assert any("fitter applied" in n for n in notes)