import os
import sys
import anyio
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)

BRIEFING_PROMPT = """\
You are a daily briefing assistant. Gather information and compose a morning briefing email.

Steps:
1. Call tool_get_todays_calendar_events to get today's calendar events
2. Call tool_get_pending_reminders to get outstanding reminders
3. Call tool_check_email to get recent emails from the last 24 hours
4. Compose an HTML email with these sections:
   - **Today's Schedule**: Calendar events formatted as a timeline
   - **Outstanding Reminders**: Pending tasks grouped by list
   - **Recent Emails**: Summary of incoming messages
   - **Daily Focus**: A brief 2-3 sentence suggestion for the day's priorities based on the above
5. Call tool_send_email_report with subject "Daily Briefing - <today's date>" and the HTML body

Use clean, readable HTML with inline styles. Keep it concise and scannable.
"""


async def run() -> None:
    # Allow running from within a Claude Code session (e.g. during development)
    os.environ.pop("CLAUDECODE", None)

    load_dotenv(Path(PROJECT_ROOT) / ".env")

    env_vars = {}
    for key in ("ICLOUD_EMAIL", "ICLOUD_APP_PASSWORD"):
        val = os.environ.get(key)
        if not val:
            print(f"Error: {key} not set in environment or .env file", file=sys.stderr)
            sys.exit(1)
        env_vars[key] = val

    mcp_server_path = str(Path(__file__).resolve().parent / "mcp_server.py")

    async for message in query(
        prompt=BRIEFING_PROMPT,
        options=ClaudeAgentOptions(
            allowed_tools=["mcp__todotoday__*"],
            permission_mode="bypassPermissions",
            max_turns=10,
            mcp_servers={
                "todotoday": {
                    "command": "uv",
                    "args": [
                        "run",
                        "--project", PROJECT_ROOT,
                        "python", mcp_server_path,
                    ],
                    "env": {
                        **env_vars,
                        "PATH": os.environ.get("PATH", ""),
                        "HOME": os.environ.get("HOME", ""),
                    },
                }
            },
        ),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


def main() -> None:
    anyio.run(run)


if __name__ == "__main__":
    main()
