import imaplib
import smtplib
import email
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header


IMAP_HOST = "imap.mail.me.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.mail.me.com"
SMTP_PORT = 587


def _get_credentials() -> tuple[str, str]:
    addr = os.environ["ICLOUD_EMAIL"]
    password = os.environ["ICLOUD_APP_PASSWORD"]
    return addr, password


def _decode_header_value(value: str) -> str:
    if value is None:
        return ""
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def check_email(hours_back: int = 24) -> str:
    """Check iCloud email for recent messages. Returns sender, subject, and date for each message."""
    addr, password = _get_credentials()

    since_date = (datetime.now() - timedelta(hours=hours_back)).strftime("%d-%b-%Y")

    conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    try:
        conn.login(addr, password)
        conn.select("INBOX", readonly=True)

        _, msg_ids = conn.search(None, f'(SINCE "{since_date}")')
        ids = msg_ids[0].split()

        if not ids:
            return "No emails found in the last {} hours.".format(hours_back)

        results = []
        # Fetch most recent 50 max
        for msg_id in ids[-50:]:
            _, data = conn.fetch(msg_id, "(RFC822.HEADER)")
            header_data = data[0][1]
            msg = email.message_from_bytes(header_data)

            sender = _decode_header_value(msg.get("From", ""))
            subject = _decode_header_value(msg.get("Subject", "(no subject)"))
            date = msg.get("Date", "")

            results.append(f"From: {sender}\nSubject: {subject}\nDate: {date}")

        return f"Found {len(results)} emails in the last {hours_back} hours:\n\n" + "\n---\n".join(results)
    finally:
        conn.logout()


def send_email_report(subject: str, html_body: str) -> str:
    """Send an HTML email report to self via iCloud SMTP."""
    addr, password = _get_credentials()

    msg = MIMEMultipart("alternative")
    msg["From"] = addr
    msg["To"] = addr
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(addr, password)
        server.send_message(msg)

    return f"Email sent successfully to {addr} with subject: {subject}"
