# Manga & Anime Release Email Notifier

Stay ahead of your favorite manga **and** anime releases — automatically get notified via email whenever a new chapter or episode drops.

This Python-based project checks for the latest manga chapters of selected titles (like **One Piece**, **Baki**, **Dragon Ball Super**, and **Kengan Omega**) using the [MangaDex API](https://api.mangadex.org), and the latest aired anime episodes (like **Solo Leveling**, **Dandadan**, and **Jujutsu Kaisen**) using the free [AniList GraphQL API](https://anilist.gitbook.io/anilist-apiv2-docs/). When new releases are available, a clean HTML email is sent to your inbox using [Mailgun](https://mailgun.com).

## Features

- Monitor multiple manga **and** anime series
- Detects new chapters/episodes only (no spam)
- Manga and anime tracked independently — a title can be both (e.g. One Piece)
- Sends a clean, flat HTML email with anime/manga badges and per-release links
- No API key needed for release lookups (MangaDex and AniList are public)
- Secured with Mailgun credentials in a `.env` file
- Pythonic and cleanly modular

## Project Structure

```text
manga-notifier/
├── main.py                   # Main controller (manga + anime)
├── requirements.txt          # Pip dependencies
├── .env                      # Your Mailgun credentials
├── data/
│   └── last_manga_chapters.json   # Tracks last seen chapters & episodes
├── templates/
│   └── notification_email.html    # HTML email template
└── utilities/
    ├── manga_util.py         # MangaDex chapter lookup
    ├── anime_util.py         # AniList episode lookup
    └── email_util.py         # Mailgun integration & formatter
```

## Configuring Titles

Edit the two lists at the top of `main.py`:

```python
MANGA_TITLES = ["One Piece", "Baki", "Dragon Ball Super", ...]
ANIME_TITLES = ["One Piece", "Solo Leveling", "Dandadan", ...]
```

Manga is matched against MangaDex; anime is matched against AniList. The two are
tracked separately, so a title that is both a manga and an anime (e.g. One Piece)
is notified independently for each.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env`

```env
MAILGUN_API_KEY=key-xxxxxx
MAILGUN_DOMAIN=sandbox12345.mailgun.org
EMAIL_TO=you@example.com
```

> If you're using a Mailgun sandbox domain, be sure to verify the recipient email.

### 3. Run It

```bash
python main.py
```

If new chapters or episodes are available, you will receive an email.

### 4. Automate It (Optional)

The included GitHub Actions workflow (`.github/workflows/checker.yaml`) runs the
checker every 6 hours and commits updated state back to the repo so you don't get
duplicate notifications. Add `MAILGUN_DOMAIN`, `MAILGUN_API_KEY`, and `EMAIL_TO`
as repository secrets to enable it. You can also run it on demand via the
**Run workflow** button (workflow_dispatch), or use cron / Task Scheduler locally.

## Testing

You can verify the project without sending real email or waiting for a new release.

**1. Check the release lookups only (no email, no credentials needed).**
This confirms MangaDex and AniList are returning data:

```bash
python -c "from utilities.manga_util import get_latest_chapter; print(get_latest_chapter('One Piece'))"
python -c "from utilities.anime_util import get_latest_episode; print(get_latest_episode('Solo Leveling'))"
```

**2. Preview the email HTML in your browser (no credentials needed).**
This renders the template with sample data so you can see the layout:

```bash
python -c "from utilities.email_util import format_html; open('preview.html','w',encoding='utf-8').write(format_html([{'title':'One Piece','number':'1185','url':'https://mangadex.org','kind':'manga'},{'title':'Solo Leveling','number':12,'url':'https://anilist.co','kind':'anime'}]))"
```

Then open `preview.html` in any browser. (Delete it afterwards — it's just a scratch file.)

**3. Force a full run as if everything were new (sends a real email).**
The notifier only emails about releases it hasn't seen before. To re-trigger a
notification for testing, clear the saved state first:

```bash
echo "{}" > data/last_manga_chapters.json
python main.py
```

With valid `.env` credentials this sends one email containing the current latest
chapters/episodes. Running `python main.py` again immediately should print
`No new chapters or episodes yet.` — confirming the de-duplication works.

## Coming Soon

- Discord notifications
- Pushbullet / Pushover integration
- Custom release day configs (e.g., "One Piece = Wednesday")

## Credits & Inspiration

- Manga powered by the [MangaDex API](https://api.mangadex.org)
- Anime powered by the [AniList API](https://anilist.gitbook.io/anilist-apiv2-docs/)
- Email handled via [Mailgun](https://www.mailgun.com/)
