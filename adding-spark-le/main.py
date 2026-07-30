"""
Adding Spark-le ✨ — daily orchestration script.

Run manually:  python main.py
Run for real via GitHub Actions (see .github/workflows/send-newsletter.yml),
which runs this automatically Monday–Friday mornings.

No email credentials needed. Output is published as a webpage via GitHub
Pages (see publish_web.py and the GitHub Actions workflow).

Optional environment variables (set as GitHub Secrets for automated runs,
or a local .env file for manual testing — see README.md):
  NEWSAPI_KEY        (optional but recommended — broadens discovery)
  ANTHROPIC_API_KEY  (optional — without it, "why it matters", Follow of
                      the Day, Pitch Angle, Event Spotlight, and Reporter
                      Radar are skipped and only raw headlines are shown)
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

import fetch_content
import enrich
import render
import publish_web

load_dotenv()  # loads a local .env file if present; no-op on GitHub Actions

# Skip weekends even if the scheduler misfires
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def main():
    today = datetime.now()
    if today.weekday() >= 5:  # 5=Saturday, 6=Sunday
        print(f"Today is {WEEKDAY_NAMES[today.weekday()]} — no newsletter on weekends. Exiting.")
        sys.exit(0)

    newsapi_key = os.environ.get("NEWSAPI_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    print("Step 1/4: Fetching stories from RSS + NewsAPI...")
    stories_by_vertical = fetch_content.fetch_all_verticals(newsapi_key=newsapi_key)

    print("Step 2/4: Running AI enrichment (why it matters, follow, pitch, event, radar)...")
    enrichment = enrich.enrich(stories_by_vertical, api_key=anthropic_key)

    print("Step 3/4: Rendering HTML...")
    # Simple issue counter based on day-of-year so it's stable without needing storage
    issue_number = today.timetuple().tm_yday
    html = render.render_newsletter(stories_by_vertical, enrichment, issue_number=issue_number)

    print("Step 4/4: Publishing to the webpage...")
    publish_web.publish(html, today=today)

    print("Done! ✨ Check your GitHub Pages URL for today's edition.")


if __name__ == "__main__":
    main()
