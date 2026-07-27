"""
Email Notification Bridge — Zero 3rd-Party APIs, 100% Free
Sends opportunity alerts via Gmail SMTP using Python's built-in smtplib.
No API keys required — uses your existing Gmail account with an App Password.
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(self, sender_email: str = None, app_password: str = None, recipient_email: str = None):
        self.sender_email = sender_email or self._load_env_var("NOTIFY_EMAIL_FROM")
        self.app_password = app_password or self._load_env_var("NOTIFY_EMAIL_PASSWORD")
        self.recipient_email = recipient_email or self._load_env_var("NOTIFY_EMAIL_TO")

    def _load_env_var(self, key: str) -> str:
        """Load variable from environment or .env file."""
        val = os.getenv(key, "")
        if val:
            return val
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        return ""

    def format_immediate_alert(self, opp: Dict[str, Any]) -> tuple:
        """Format urgent high-score opportunity as HTML email."""
        scores = opp.get("scores", {})
        subject = f"🚨 UNICORN B2B OPPORTUNITY [{scores.get('composite')}/10] — {opp.get('title')[:60]}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 32px; border-radius: 12px;">
            <div style="background: linear-gradient(135deg, #6366f1, #ec4899); padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                <h1 style="margin:0; font-size: 20px;">🚨 UNICORN B2B OPPORTUNITY ALERT</h1>
                <p style="margin:4px 0 0 0; opacity:0.85;">AI Business Opportunity Hunter — Score: <strong>{scores.get('composite')}/10</strong></p>
            </div>

            <h2 style="color:#818cf8; font-size:18px;">{opp.get('title')}</h2>

            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr>
                    <td style="padding:10px; background:#1e293b; border-radius:6px; margin:4px;">
                        <div style="color:#94a3b8; font-size:12px;">MARKET GAP SCORE</div>
                        <div style="font-size:22px; font-weight:800; color:#ec4899;">{scores.get('composite')}/10</div>
                    </td>
                    <td style="width:12px;"></td>
                    <td style="padding:10px; background:#1e293b; border-radius:6px;">
                        <div style="color:#94a3b8; font-size:12px;">2-YEAR ARR POTENTIAL</div>
                        <div style="font-size:16px; font-weight:700; color:#10b981;">{opp.get('financial_projection')}</div>
                    </td>
                    <td style="width:12px;"></td>
                    <td style="padding:10px; background:#1e293b; border-radius:6px;">
                        <div style="color:#94a3b8; font-size:12px;">BUILD EFFORT</div>
                        <div style="font-size:14px; font-weight:600; color:#f59e0b;">{opp.get('build_effort')}</div>
                    </td>
                </tr>
            </table>

            <div style="background:#1e293b; padding:16px; border-radius:8px; margin-bottom:16px; border-left: 4px solid #6366f1;">
                <div style="color:#94a3b8; font-size:12px; margin-bottom:6px;">🎯 THE PROBLEM / MARKET DEMAND</div>
                <p style="margin:0; line-height:1.6;">{opp.get('description')}</p>
            </div>

            <div style="background:#1e293b; padding:16px; border-radius:8px; margin-bottom:16px; border-left: 4px solid #10b981;">
                <div style="color:#94a3b8; font-size:12px; margin-bottom:6px;">🛠️ SUGGESTED MVP EXECUTION PLAN</div>
                <p style="margin:0; line-height:1.6;">{opp.get('suggested_mvp_concept')}</p>
            </div>

            <div style="background:#1e293b; padding:12px; border-radius:8px; font-size:12px; color:#64748b;">
                Source: {opp.get('source')} | Antigravity AI Opportunity Hunter
            </div>
        </div>
        """
        return subject, html

    def format_bidaily_digest(self, opps: List[Dict[str, Any]]) -> tuple:
        """Format 48-hour digest as HTML email."""
        subject = f"📊 Bi-Daily AI Opportunity Digest — {len(opps)} Opportunities Found"
        rows = ""
        for idx, opp in enumerate(opps[:5], 1):
            scores = opp.get("scores", {})
            rows += f"""
            <div style="background:#1e293b; padding:16px; border-radius:8px; margin-bottom:12px; border-left:4px solid {'#ec4899' if idx == 1 else '#6366f1'};">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <strong style="font-size:15px;">{idx}. {opp.get('title')}</strong>
                    <span style="background:#6366f1; color:#fff; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:700;">{scores.get('composite')}/10</span>
                </div>
                <div style="color:#10b981; font-size:13px; margin-bottom:4px;">📈 {opp.get('financial_projection')}</div>
                <div style="color:#94a3b8; font-size:12px;">{opp.get('suggested_mvp_concept')[:140]}...</div>
            </div>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 32px; border-radius: 12px;">
            <div style="background: linear-gradient(135deg, #6366f1, #10b981); padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                <h1 style="margin:0; font-size: 20px;">📊 Bi-Daily AI Opportunity Digest</h1>
                <p style="margin:4px 0 0 0; opacity:0.85;">Top {len(opps)} high-demand B2B opportunities from the last 48 hours</p>
            </div>
            {rows}
            <div style="background:#1e293b; padding:12px; border-radius:8px; font-size:12px; color:#64748b; margin-top:16px;">
                Full research dossiers saved to Obsidian Second Brain → 02 My Businesses/Opportunities/
            </div>
        </div>
        """
        return subject, html

    def send(self, subject: str, html_body: str) -> bool:
        """Send email via Gmail SMTP."""
        sender = self.sender_email or self._load_env_var("NOTIFY_EMAIL_FROM")
        password = self.app_password or self._load_env_var("NOTIFY_EMAIL_PASSWORD")
        recipient = self.recipient_email or self._load_env_var("NOTIFY_EMAIL_TO")

        if not all([sender, password, recipient]):
            logger.warning("Email credentials incomplete. Skipping email dispatch.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())

            logger.info(f"✅ Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    def send_immediate_alert(self, opp: Dict[str, Any]) -> bool:
        subject, html = self.format_immediate_alert(opp)
        return self.send(subject, html)

    def send_bidaily_digest(self, opps: List[Dict[str, Any]]) -> bool:
        subject, html = self.format_bidaily_digest(opps)
        return self.send(subject, html)

if __name__ == "__main__":
    notifier = EmailNotifier()
    print("Email notifier initialized.")
