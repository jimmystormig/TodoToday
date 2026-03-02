from dotenv import load_dotenv
from fastmcp import FastMCP

from todotoday.tools.email_tools import check_email, send_email_report
from todotoday.tools.calendar_tools import get_todays_calendar_events
from todotoday.tools.reminders_tools import get_pending_reminders

load_dotenv()

mcp = FastMCP("todotoday")


@mcp.tool
def tool_check_email(hours_back: int = 24) -> str:
    """Check iCloud email for recent messages. Returns sender, subject, and date for each message from the last N hours."""
    return check_email(hours_back)


@mcp.tool
def tool_send_email_report(subject: str, html_body: str) -> str:
    """Send an HTML email report to the user's iCloud address. Use this to deliver the daily briefing."""
    return send_email_report(subject, html_body)


@mcp.tool
def tool_get_todays_calendar_events() -> str:
    """Get all calendar events scheduled for today from Apple Calendar."""
    return get_todays_calendar_events()


@mcp.tool
def tool_get_pending_reminders() -> str:
    """Get all pending (incomplete) reminders from Apple Reminders."""
    return get_pending_reminders()


if __name__ == "__main__":
    mcp.run()
