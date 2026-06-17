import time

import requests

ANILIST_URL = "https://graphql.anilist.co"

# Look up the anime by title to resolve its canonical id, title and site url.
_SEARCH_QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    id
    title { romaji english }
    siteUrl
  }
}
"""

# Fetch the most recently aired episode for a given anime id.
_LATEST_EPISODE_QUERY = """
query ($id: Int, $now: Int) {
  Page(perPage: 1) {
    airingSchedules(mediaId: $id, sort: TIME_DESC, airingAt_lesser: $now) {
      episode
      airingAt
    }
  }
}
"""


def get_latest_episode(title):
    """Return info about the latest aired episode of `title`, or None.

    Uses the public AniList GraphQL API (no API key required).
    """
    search = requests.post(
        ANILIST_URL,
        json={"query": _SEARCH_QUERY, "variables": {"search": title}},
        timeout=30,
    ).json()

    media = (search.get("data") or {}).get("Media")
    if not media:
        return None

    episodes = requests.post(
        ANILIST_URL,
        json={
            "query": _LATEST_EPISODE_QUERY,
            "variables": {"id": media["id"], "now": int(time.time())},
        },
        timeout=30,
    ).json()

    schedules = (
        ((episodes.get("data") or {}).get("Page") or {}).get("airingSchedules") or []
    )
    if not schedules:
        return None

    latest = schedules[0]
    canonical_title = media["title"].get("english") or media["title"].get("romaji") or title

    return {
        # AniList has no per-episode id, so build a stable key from media + episode.
        "id": f"{media['id']}-{latest['episode']}",
        "title": canonical_title,
        "number": latest["episode"],
        "url": media.get("siteUrl") or f"https://anilist.co/anime/{media['id']}",
        "kind": "anime",
    }
