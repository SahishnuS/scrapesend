import email.mime.text
import email.mime.multipart
import aiosmtplib
import httpx
import structlog
from app.core.config import settings

log = structlog.get_logger(__name__)


class NotificationService:
    """
    Service responsible for dispatching push notifications via Telegram Bot API
    and emails via Gmail SMTP.
    """

    def __init__(self):
        self.telegram_token = settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = settings.TELEGRAM_CHAT_ID
        self.smtp_email = settings.SMTP_EMAIL
        self.smtp_password = (settings.SMTP_APP_PASSWORD or "").replace(" ", "")

    async def send_telegram(self, message: str) -> bool:
        """
        Send a Markdown message to Telegram via Bot API.
        Returns True if successful, False otherwise.
        """
        if not self.telegram_token or "your_" in self.telegram_token.lower():
            log.warning("Telegram Bot token not set or placeholder. Skipping Telegram send.")
            return False

        if not self.telegram_chat_id or "your_" in str(self.telegram_chat_id).lower():
            log.warning("Telegram Chat ID not set or placeholder. Skipping Telegram send.")
            return False

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }

        try:
            log.info("Connecting to Telegram API... (Timeout set to 3s to prevent hanging)")
            transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
            async with httpx.AsyncClient(transport=transport, timeout=3.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    log.info("Telegram notification sent successfully.")
                    return True
                else:
                    log.error(
                        "Telegram API error",
                        status=response.status_code,
                        body=response.text,
                    )
                    return False
        except Exception as exc:
            log.error("Failed to send Telegram notification", error=str(exc))
            return False

    async def send_email(self, subject: str, body_text: str, recipient_email: str = None) -> bool:
        """
        Send an email via Gmail SMTP using aiosmtplib.
        Returns True if successful, False otherwise.
        """
        if not self.smtp_email or "your_" in self.smtp_email.lower():
            log.warning("SMTP_EMAIL not set or placeholder. Skipping Email send.")
            return False

        if not self.smtp_password or "your_" in self.smtp_password.lower():
            log.warning("SMTP_APP_PASSWORD not set or placeholder. Skipping Email send.")
            return False

        target = recipient_email or self.smtp_email

        msg = email.mime.multipart.MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"InternHunt <{self.smtp_email}>"
        msg["To"] = target

        msg.attach(email.mime.text.MIMEText(body_text, "plain"))

        try:
            log.info("Connecting to Gmail SMTP server (smtp.gmail.com:587)...")
            await aiosmtplib.send(
                msg,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username=self.smtp_email,
                password=self.smtp_password,
                timeout=15.0,
            )
            log.info(f"Email notification sent successfully to {target}.")
            return True
        except Exception as exc:
            log.error("Failed to send Email notification", error=str(exc))
            return False
