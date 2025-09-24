from src.agent.cli.deepseek_travels_cli import build_parser, main


def test_cli_requires_command():
    parser = build_parser()
    try:
        parser.parse_args([])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover - unreachable branch
        raise AssertionError("CLI should require a subcommand")


def test_cli_main_prints_placeholder(capsys):
    exit_code = main(["simple", "Paris"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Quick checklist" in captured.out


def test_cli_assist_loop(monkeypatch, capsys):
    inputs = iter(["What should I pack?", "exit"])

    monkeypatch.setenv("DEEPSEEKTRAVELS_USE_MOCKS", "true")
    monkeypatch.setenv("DEEPSEEKTRAVELS_OFFLINE", "true")
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    exit_code = main(["assist", "Berlin", "3"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "DeepseekTravels" in captured.out

