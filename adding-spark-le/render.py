"""
Combines fetched stories + AI enrichment into the final HTML email body,
using template.html as the base.
"""

from datetime import datetime
from pathlib import Path

from jinja2 import Template

import config

TAG_LABELS = {"move": "Moved", "beat": "New Beat", "foia": "Open Request"}


def _format_story_date(published):
    if not published:
        return "date unavailable"
    return published.strftime("%B %-d, %Y") if hasattr(published, "strftime") else str(published)


def render_newsletter(stories_by_vertical, enrichment, issue_number=1):
    template_path = Path(__file__).parent / "template.html"
    template = Template(template_path.read_text())

    verticals = {}
    for vkey, vconf in config.VERTICALS.items():
        stories = stories_by_vertical.get(vkey, [])
        rendered_stories = []
        for s in stories:
            rendered_stories.append({
                "title": s["title"],
                "link": s["link"],
                "summary": s["summary"] or "(No summary available — click through to read.)",
                "source": s["source"],
                "date_display": _format_story_date(s.get("published")),
                "why_it_matters": enrichment.get("why_it_matters", {}).get(s["link"]),
            })
        verticals[vkey] = {
            "label": vconf["label"],
            "emoji": vconf["emoji"],
            "color": vconf["color"],
            "stories": rendered_stories,
        }

    reporter_radar = []
    for item in enrichment.get("reporter_radar") or []:
        reporter_radar.append({
            "type": item.get("type", "beat"),
            "type_label": TAG_LABELS.get(item.get("type", "beat"), "Update"),
            "text": item.get("text", ""),
        })

    context = {
        "newsletter_name": config.NEWSLETTER_NAME,
        "display_date": datetime.now().strftime("%A, %B %-d, %Y"),
        "issue_number": issue_number,
        "intro_line": (
            "Good morning! Here's what's electrifying the energy world today — "
            "sorted by beat, flagged by relevance, and ready for your client check-ins. ☕⚡"
        ),
        "verticals": verticals,
        "reporter_radar": reporter_radar,
        "follow_of_the_day": enrichment.get("follow_of_the_day"),
        "pitch_angle": enrichment.get("pitch_angle"),
        "event_spotlight": enrichment.get("event_spotlight"),
    }

    return template.render(**context)


if __name__ == "__main__":
    # Quick manual test with fake data
    fake_stories = {"vpp": [], "regulatory": [], "air_quality": [], "data_centers": [], "ai_buildings": []}
    fake_enrichment = {"why_it_matters": {}, "reporter_radar": [], "follow_of_the_day": None,
                        "pitch_angle": None, "event_spotlight": None}
    html = render_newsletter(fake_stories, fake_enrichment)
    Path("preview.html").write_text(html)
    print("Wrote preview.html")
