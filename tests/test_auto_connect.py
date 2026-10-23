"""Install once, covered everywhere: an agent installed after setup gets the hook from the gateway on its own, an agent a
person took out stays out, and the first `squidbrake` after pip install does the whole setup."""
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import connect  # noqa: E402


@pytest.fixture()
def machine(monkeypatch, tmp_path):
    """Claude Code connected to the gateway; Cursor installed later; Codex installed and taken out by hand."""
    monkeypatch.setenv("SQUIDBRAKE_AGENTS_OFF", str(tmp_path / "agents-off.json"))
    connected = {"claude-code"}
    monkeypatch.setattr(connect, "_hooked_gateway", lambda: ("http://localhost:8080", "gw_agents"))
    monkeypatch.setattr(connect, "local_agents", lambda: [
        {"name": n, "present": True, "connected": n in connected} for n in ("claude-code", "cursor", "codex")])
    done = []
    monkeypatch.setattr(connect, "claude_code", lambda a: done.append(("claude-code", a.remove)))
    monkeypatch.setattr(connect, "agents", lambda a: done.append((a.agent, a.remove)))
    monkeypatch.setattr(connect, "guard", lambda a: None)
    return done


def test_an_agent_installed_later_is_connected_one_taken_out_stays_out(machine):
    connect.set_agent("codex", False, "http://localhost:8080")          # a person took Codex out (dashboard toggle)
    machine.clear()
    assert connect.auto_connect() == ["cursor"]
    assert machine == [("cursor", False)]
    connect.set_agent("codex", True, "http://localhost:8080")           # and put it back: auto-connect may again
    assert "codex" not in connect.agents_off()


def test_connect_all_remove_keeps_every_agent_out(machine, monkeypatch):
    monkeypatch.setattr(connect, "connected_agents", lambda: [])
    connect.connect_all(Namespace(url="http://localhost:8080", key=None, remove=True, yes=True, only=None))
    assert {"claude-code", "cursor", "codex"} <= connect.agents_off()
    machine.clear()
    assert connect.auto_connect() == []


def test_nothing_happens_where_squidbrake_was_never_set_up(machine, monkeypatch):
    monkeypatch.setattr(connect, "_hooked_gateway", lambda: None)
    assert connect.auto_connect() == [] and machine == []


def test_the_first_squidbrake_after_pip_install_is_the_whole_setup(monkeypatch):
    import onboard
    import service
    from squidbrake import cli
    ran = []
    monkeypatch.setattr(onboard, "main", lambda argv: ran.append(("setup", argv)) or 0)
    monkeypatch.setattr(service, "main", lambda argv: ran.append(("start", argv)) or 0)
    monkeypatch.setattr(sys, "argv", ["squidbrake"])
    monkeypatch.setattr(service, "is_first_start", lambda argv: True)
    assert cli.main() == 0 and ran[-1] == ("setup", [])
    monkeypatch.setattr(service, "is_first_start", lambda argv: False)   # every later `squidbrake`: just a start
    cli.main()
    assert ran[-1] == ("start", ["start"])
