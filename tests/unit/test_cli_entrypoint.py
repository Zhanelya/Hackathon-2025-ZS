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
    assert "DeepseekTravels packing list" in captured.out

