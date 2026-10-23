# Rolling out to a fleet (Intune, Jamf, Homebrew)

Three steps for IT: put Squidbrake on every machine, connect each person's agents to the team's gateway, and lock the
agents so nobody can switch it off. One gateway and one `rules.yaml` then decide for every agent.

Before you start: run a team gateway (see [install.md](install.md)) and make one agent key per person in the
dashboard (*Team* → *Add someone*, type *AI agent*, *Works for* set to that person). Each agent key works for one person, so the
install is assigned per user, not once for all devices.

## 1. Install and connect

### Windows: Microsoft Intune

[`packaging/mdm/intune-install.ps1`](../packaging/mdm/intune-install.ps1) installs Squidbrake for the signed-in user
and connects their Claude Code, Cursor, Codex, Gemini CLI, VS Code Copilot and Antigravity, and the MCP servers
those agents use.

1. Wrap it as a Win32 app: `IntuneWinAppUtil.exe -c packaging\mdm -s intune-install.ps1 -o out`
2. Install command:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File intune-install.ps1 -Url https://gateway.yourcompany.com -Key gw_...`
3. **Install behavior: User.** Squidbrake and the agents' settings live in the user's profile.
4. Detection rule: file `%USERPROFILE%\.local\bin\squidbrake.exe` exists.
5. Assign it to each person with their own key.

The install log is `%TEMP%\squidbrake-intune.log`.

### macOS: Jamf Pro

[`packaging/mdm/jamf-install.sh`](../packaging/mdm/jamf-install.sh) does the same on a Mac. Jamf runs scripts as
root, so the script installs as the person logged in at the console.

1. Add the script in *Settings* → *Scripts*.
2. In the policy, set parameter 4 to the gateway URL and parameter 5 to the person's agent key.
3. Triggers: *Recurring Check-in* and *Login*. If nobody is logged in, the script exits and runs again at the next
   login.

### macOS and Linux: Homebrew

```bash
brew install batrapulkit/tap/squidbrake
squidbrake connect all --url https://gateway.yourcompany.com --key gw_YOUR_AGENT_KEY
```

The formula is [`packaging/homebrew/squidbrake.rb`](../packaging/homebrew/squidbrake.rb).

## 2. Lock it

```bash
squidbrake lockdown --url https://gateway.yourcompany.com --out squidbrake-lockdown
```

This writes each agent's managed-settings file (Claude Code, Codex, Gemini CLI, Cursor) and a README saying where each
one goes on macOS, Linux and Windows. Push those files with the same MDM. Each agent then must run Squidbrake's hook,
and `--dangerously-skip-permissions` / `--yolo` are off.

## 3. Check

- `squidbrake doctor` on any machine says what is connected, what each hook doesn't see, and which MCP servers don't
  go through Squidbrake.
- The dashboard's *Settings* → *Agents across the team* lists every computer that reported, with agents and MCP
  servers that aren't connected yet.

## Not done yet

- **One install for every device.** Each machine needs its person's own key. An enrollment key that makes a key per
  person on first run isn't built yet.
- **A signed MSI or .pkg.** The scripts above install from PyPI with the same installer as the one-line install.
