import json
from src.agent.cli.deepseek_travels_cli import main


def test_cli_simple_mode_smoke(capsys):
    argv = [
        "simple",
        "Paris",
        "2025-10-01",
        "2025-10-03",
        "3",
        "--activities",
        "museum",
        "--tod",
        "day",
    ]
    rc = main(argv)
    assert rc == 0
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "checklist" in data
    assert isinstance(data["checklist"], list)
    assert any(i["name"] == "Passport" for i in data["checklist"])
