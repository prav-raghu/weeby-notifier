from utilities.manga_util import get_latest_chapter
from utilities.anime_util import get_latest_episode
from utilities.email_util import send_email, format_html
import json, os, sys
from datetime import datetime

# Some Windows consoles default to cp1252 and choke on emoji output.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MANGA_TITLES = ["One Piece", "Baki", "Dragon Ball Super", "Kengan Omega", "One Punch Man", "Black Clover", "Doctor Stone"]
ANIME_TITLES = ["One Piece", "Solo Leveling", "Dandadan", "Jujutsu Kaisen", "My Hero Academia"]
DATA_FILE = "data/last_manga_chapters.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # Empty or corrupt state file — treat as a fresh start rather than crash.
        print("⚠️  State file was empty or invalid; starting fresh.")
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def check_releases(titles, fetch, kind, last_data, new_data):
    """Check each title for a new release, collecting updates.

    Keys are namespaced by `kind` so a manga and anime sharing a title
    (e.g. One Piece) are tracked independently.
    """
    updates = []
    for title in titles:
        try:
            release = fetch(title)
        except Exception as e:
            print(f"⚠️  Failed to check {kind} '{title}': {e}")
            continue
        if not release:
            continue
        key = f"{kind}:{title}"
        if release["id"] != last_data.get(key, {}).get("id"):
            updates.append(release)
            new_data[key] = release
    return updates


def main():
    last_data = load_data()
    new_data = last_data.copy()

    updates = []
    updates += check_releases(MANGA_TITLES, get_latest_chapter, "manga", last_data, new_data)
    updates += check_releases(ANIME_TITLES, get_latest_episode, "anime", last_data, new_data)

    if updates:
        subject = f"Weeby Notifier — New Release(s)! - {datetime.now().strftime('%d/%m/%y')}"
        plain_text = "\n".join(
            f"[{c.get('kind', 'manga').title()}] {c['title']} - "
            f"{'Episode' if c.get('kind') == 'anime' else 'Chapter'} {c['number']}: {c['url']}"
            for c in updates
        )
        html_body = format_html(updates)
        send_email(subject, plain_text, html_body)
        save_data(new_data)
        print(f"📨 Sent notification for {len(updates)} new release(s).")
    else:
        print("📖 No new chapters or episodes yet.")


if __name__ == "__main__":
    main()
