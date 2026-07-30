"""
Uses the Anthropic API to turn the day's raw pulled stories into the
editorial sections that need judgment: "why it matters" blurbs, Follow of
the Day, Pitch Angle of the Day, Event Spotlight, and a best-effort
Reporter Radar.

IMPORTANT on Reporter Radar: journalist moves, beat changes, and open
records requests aren't reliably detectable from RSS/News API content
alone. This step asks the model to flag anything suggestive it sees in
the pulled articles or their bylines, but treat its output as a lead to
verify yourself, not a confirmed fact. Manually checking Twitter/X,
LinkedIn, and Muck Rack for your tracked reporters weekly is still the
most reliable source for this section.
"""

import json
import os

import anthropic

import config

MODEL = "claude-sonnet-5"


def _flatten_stories_for_prompt(stories_by_vertical):
    lines = []
    for vkey, stories in stories_by_vertical.items():
        label = config.VERTICALS[vkey]["label"]
        for s in stories:
            lines.append(
                f"[{label}] \"{s['title']}\" — {s['source']} — {s['link']}\n"
                f"  Summary: {s['summary'][:300]}"
            )
    return "\n".join(lines) if lines else "(No stories were pulled today.)"


def enrich(stories_by_vertical, api_key=None):
    """
    Returns a dict:
    {
      "why_it_matters": { "<link>": "one-sentence reason" },
      "follow_of_the_day": {"name": ..., "affiliation": ..., "reason": ...},
      "pitch_angle": {"title": ..., "text": ...},
      "event_spotlight": {"name": ..., "date": ..., "text": ...},
      "reporter_radar": [ {"type": "move|beat|foia", "text": ...}, ... ]
    }
    Falls back to safe empty defaults if the API call fails or no key is set.
    """
    fallback = {
        "why_it_matters": {},
        "follow_of_the_day": None,
        "pitch_angle": None,
        "event_spotlight": None,
        "reporter_radar": [],
    }

    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  [warn] No ANTHROPIC_API_KEY set — skipping AI enrichment.")
        return fallback

    stories_text = _flatten_stories_for_prompt(stories_by_vertical)
    reporters_text = ", ".join(config.TRACKED_REPORTERS)

    prompt = f"""You are helping a PR professional build their daily energy-industry
newsletter, "Adding Spark-le". Their clients are: virtual power plants (VPPs),
a regulatory intelligence platform, a hyperlocal air quality monitoring company,
a compartmentalized/modular data center company, and a company that optimizes
building energy using AI occupancy sensing.

Here are today's pulled stories, grouped by client vertical:

{stories_text}

Reporters they track closely: {reporters_text}

Based ONLY on the stories above (do not invent facts not supported by them),
return a single JSON object with this exact shape and nothing else — no
markdown fences, no preamble:

{{
  "why_it_matters": {{ "<exact story link>": "<one sentence on why this matters to the relevant client>" }},
  "follow_of_the_day": {{"name": "<person>", "affiliation": "<outlet/org>", "reason": "<1-2 sentences>"}} or null if no clear candidate,
  "pitch_angle": {{"title": "<short pitch title>", "text": "<1-2 sentence pitch angle tying today's news to a client>"}} or null,
  "event_spotlight": {{"name": "<event name>", "date": "<date if inferable, else 'TBD'>", "text": "<1-2 sentences on relevance>"}} or null,
  "reporter_radar": [ {{"type": "move|beat|foia", "text": "<1 sentence, only if genuinely suggested by the source material>"}} ]
}}

Only include a "why_it_matters" entry for stories where there's a real, specific
connection to one of the client verticals — skip generic ones. If you don't have
a confident answer for follow_of_the_day, pitch_angle, or event_spotlight, use
null rather than guessing. reporter_radar should usually be an empty list unless
the story text itself mentions a byline change, beat shift, or records request —
do not fabricate reporter moves."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        raw_text = raw_text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        parsed = json.loads(raw_text)
        # Merge with fallback so missing keys don't break rendering
        fallback.update(parsed)
        return fallback
    except Exception as e:
        print(f"  [warn] AI enrichment failed, using fallback: {e}")
        return fallback


if __name__ == "__main__":
    # Quick manual test with fake data
    fake_stories = {
        "vpp": [{
            "title": "Test VPP story",
            "link": "https://example.com/1",
            "source": "Test Source",
            "summary": "A test summary about virtual power plants.",
        }]
    }
    print(json.dumps(enrich(fake_stories), indent=2))
