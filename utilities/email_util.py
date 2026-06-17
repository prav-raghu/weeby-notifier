import os, requests
from dotenv import load_dotenv
load_dotenv()
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
EMAIL_TO = os.getenv("EMAIL_TO")

def send_email(subject, plain_text, html_body):
    res = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Manga Notifier <mailgun@{MAILGUN_DOMAIN}>",
            "to": EMAIL_TO,
            "subject": subject,
            "text": plain_text,
            "html": html_body
        }
    )
    return res

def format_html(releases):
    with open("templates/notification_email.html", "r") as f:
        template = f.read()

    card_html = ""
    for c in releases:
        is_anime = c.get("kind") == "anime"
        unit = "Episode" if is_anime else "Chapter"
        action = "Watch now" if is_anime else "Read now"
        badge = "ANIME" if is_anime else "MANGA"

        # Flat solid accents: anime = teal, manga = indigo.
        accent = "#0d9488" if is_anime else "#4338ca"
        badge_bg = "#e6f4f1" if is_anime else "#eaeaf6"

        card_html += f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 14px 0; background-color: #ffffff; border: 1px solid #e3e5e9; border-left: 3px solid {accent}; border-radius: 6px;">
          <tr>
            <td style="padding: 16px 20px;">
              <span style="display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {accent}; background-color: {badge_bg}; padding: 3px 9px; border-radius: 4px;">{badge}</span>
              <div style="font-size: 17px; font-weight: 700; color: #1f2937; margin: 10px 0 2px 0;">{c['title']}</div>
              <div style="font-size: 14px; color: #6b7280; margin-bottom: 14px;">{unit} {c['number']}</div>
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-radius: 5px; background-color: {accent};">
                    <a href="{c['url']}" style="display: inline-block; padding: 9px 20px; font-size: 14px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 5px;">{action}</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
        """

    return template.replace("{{CHAPTERS}}", card_html)
