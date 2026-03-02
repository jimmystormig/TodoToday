# TodoToday

Automated daily briefing agent for macOS. Gathers data from Apple Calendar, Apple Reminders, and iCloud email each morning, then uses Claude to compose and send a summary email.

Built with the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python), a local [FastMCP](https://github.com/jlowin/fastmcp) server providing Apple ecosystem tools, and a macOS LaunchAgent for daily scheduling.

## Architecture

```
LaunchAgent (7:00 AM daily)
  └─> run_briefing.py (Claude Agent SDK)
        └─> Claude Code (Pro subscription)
              └─> FastMCP server (stdio)
                    ├── check_email (IMAP)
                    ├── send_email_report (SMTP)
                    ├── get_todays_calendar_events (EventKit)
                    └── get_pending_reminders (EventKit)
```

## Requirements

- macOS (uses EventKit via pyobjc for Calendar/Reminders access)
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with an active Pro subscription
- An iCloud account with an [app-specific password](https://support.apple.com/en-us/102654)

## Setup

1. **Clone and install dependencies:**

   ```bash
   git clone https://github.com/yourusername/TodoToday.git
   cd TodoToday
   uv sync
   ```

2. **Configure credentials:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your iCloud email and app-specific password:

   ```
   ICLOUD_EMAIL=you@icloud.com
   ICLOUD_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

   Generate an app-specific password at [account.apple.com](https://account.apple.com) > Sign-In and Security > App-Specific Passwords.

3. **First run (interactive — required for macOS permissions):**

   ```bash
   uv run todotoday
   ```

   macOS will prompt you to grant Calendar and Reminders access. You must approve these for the tool to work.

4. **Install the LaunchAgent (optional — for daily scheduling):**

   ```bash
   ./launchagent/install.sh
   ```

   This installs a LaunchAgent that runs the briefing daily at 7:00 AM. Test it with:

   ```bash
   launchctl start com.todotoday.briefing
   ```

   Check logs at `logs/briefing.stdout.log` and `logs/briefing.stderr.log`.

## Project Structure

```
src/todotoday/
├── run_briefing.py           # Agent orchestrator (Claude Agent SDK)
├── mcp_server.py             # FastMCP server registering all tools
└── tools/
    ├── email_tools.py        # IMAP check + SMTP send (iCloud)
    ├── calendar_tools.py     # Apple Calendar via EventKit
    └── reminders_tools.py    # Apple Reminders via EventKit
launchagent/
├── com.todotoday.briefing.plist  # LaunchAgent template
└── install.sh                     # Installer (fills in paths)
```

## How It Works

1. The agent orchestrator launches a FastMCP server as a subprocess, providing four tools
2. Claude Code (via the Agent SDK) calls the data-gathering tools to fetch today's calendar events, pending reminders, and recent emails
3. Claude composes an HTML briefing email with sections for schedule, reminders, emails, and a daily focus suggestion
4. The briefing is sent to your iCloud email via SMTP

Calendar and Reminders are accessed through Apple's EventKit framework (via pyobjc), which uses native predicate queries — fast even with hundreds of calendars and thousands of reminders.

## License

MIT
