#!/bin/sh
# Jamf Pro: install Squidbrake for the person logged in on this Mac and connect their agents to the team's gateway.
# Add it as a script, and in the policy set:
#   Parameter 4   the gateway URL, e.g. https://gateway.yourcompany.com
#   Parameter 5   the person's own agent key (dashboard > Team > Add someone, type AI agent, "Works for" that person)
# Jamf runs scripts as root; Squidbrake and the agents' settings live in the user's home, so it installs as them.
# Each key works for one person: scope the policy per user (or per Mac with one owner). See docs/mdm.md.
set -eu
URL=${4:?parameter 4: the gateway URL}
KEY=${5:?parameter 5: the agent key}
USER_NAME=$(stat -f%Su /dev/console)
if [ -z "$USER_NAME" ] || [ "$USER_NAME" = "root" ] || [ "$USER_NAME" = "loginwindow" ]; then
  echo "Nobody is logged in; run the policy again at next login (trigger: login)."
  exit 1
fi
sudo -u "$USER_NAME" -H env SQUIDBRAKE_URL="${URL%/}" SQUIDBRAKE_AGENT_KEY="$KEY" SQUIDBRAKE_SEND_REPORT=no \
  SQUIDBRAKE_REF=mdm sh -c 'curl -fsSL https://pilots.squidbrake.com/install.sh | sh'
sudo -u "$USER_NAME" -H sh -c '"$HOME/.local/bin/squidbrake" --version'
