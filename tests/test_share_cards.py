"""Share cards: what the dashboard puts in a public squidbrake.com link is a program's name, a known agent and a rule,
never a command's arguments or a key name; the cards take only short words and numbers."""
import json
import time

from test_pilot import insights  # noqa: F401
from test_server import BOSS, H, c, server  # noqa: F401


def post(c, source, command):
    return c.post("/v1/events", headers=H, json={"name": "Bash", "input": {"command": command},
                                                 "session_id": f"share-{time.time_ns()}", "source": source}).json()


def test_a_catch_shares_the_program_never_its_arguments_or_a_key_name(c):
    me = f"alice-laptop-{time.time_ns()}"                                  # not an agent we know: could be a person's name
    post(c, me, "cd /tmp && rm -rf ~/")
    held = post(c, "claude-code", "git push --force origin main")
    c.post(f"/v1/events/{held['event_id']}/reject", headers=BOSS, json={"note": "no"})
    caught = server.caught(7, limit=1000)
    mine = next(x for x in caught if x["agent"] == me)
    assert mine["share"]["what"] == "rm" and mine["share"]["agent"] is None and mine["share"]["rule"]
    assert "~/" not in json.dumps(mine["share"]) and me not in json.dumps(mine["share"])
    push = next(x for x in caught if x["agent"] == "claude-code" and x["outcome"] == "rejected")
    assert push["share"]["what"] == "git" and push["share"]["agent"] == "claude-code"
    assert isinstance(push["share"]["decide_s"], int)


def test_cards_render_from_short_words_and_numbers_only(insights):  # noqa: F811
    r = insights.get("/caught", params={"what": "rm", "outcome": "blocked", "agent": "claude-code", "rule": "irreversible"})
    assert r.status_code == 200 and "Claude Code tried to run rm. Squidbrake blocked it." in r.text
    assert 'property="og:title"' in r.text and "/go/share-caught" in r.text
    for bad in ({"what": "rm -rf ~/", "outcome": "blocked"}, {"what": "<script>", "outcome": "blocked"},
                {"what": "rm", "outcome": "pwned"}, {"what": "rm", "outcome": "blocked", "rule": "a b"}):
        assert insights.get("/caught", params=bad).status_code == 404
    who = insights.get("/caught", params={"what": "terraform", "outcome": "rejected", "agent": "bob", "s": 40})
    assert "An AI agent tried to run terraform" in who.text and "bob" not in who.text and "decided in 40 s" in who.text
    week = insights.get("/week", params={"e": 1240, "h": 37, "b": 2, "r": 1})
    assert "1,240 actions" in week.text and "39 of them needed a brake" in week.text
    assert insights.get("/week", params={"e": -1}).status_code == 422
    assert "14 of 15 harmful actions" in insights.get("/score", params={"n": 14, "of": 15}).text
    assert insights.get("/score", params={"n": 16, "of": 15}).status_code == 404
