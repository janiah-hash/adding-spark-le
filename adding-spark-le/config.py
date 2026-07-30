"""
Adding Spark-le ✨ — Configuration
Edit this file to change client verticals, sources, and keywords.
No code changes needed elsewhere for basic tuning.
"""

# ---------------------------------------------------------------------------
# CLIENT VERTICALS
# Each vertical = one section of the newsletter.
# - "feeds": RSS feed URLs to pull from directly (fast, reliable, free)
# - "keywords": used both to (a) score/filter RSS items for relevance and
#               (b) query the News API for broader discovery
# - "color": hex color for that section's header band in the email
# - "emoji": section icon
# ---------------------------------------------------------------------------

VERTICALS = {
    "vpp": {
        "label": "Virtual Power Plants",
        "emoji": "🔋",
        "color": "#6b7a4f",
        "feeds": [
            "https://www.canarymedia.com/rss-feed",
            "https://www.utilitydive.com/feeds/news/",
            "https://www.greentechmedia.com/rss/all",  # verify/replace if dead
        ],
        "keywords": [
            "virtual power plant", "VPP", "distributed energy resources",
            "DER aggregation", "demand response", "grid flexibility",
            "residential battery aggregation",
        ],
    },
    "regulatory": {
        "label": "Regulatory Intelligence",
        "emoji": "📜",
        "color": "#b5562c",
        "feeds": [
            "https://www.utilitydive.com/feeds/news/",
            "https://www.rtoinsider.com/feed/",  # verify/replace if dead
        ],
        "keywords": [
            "FERC", "public utility commission", "PUC ruling",
            "interconnection rule", "energy regulation", "docket",
            "rate case", "building performance standard",
        ],
    },
    "air_quality": {
        "label": "Hyperlocal Air Quality Monitoring",
        "emoji": "🌬️",
        "color": "#c1943a",
        "feeds": [
            "https://www.epa.gov/newsreleases/search/rss",
            "https://grist.org/feed/",
        ],
        "keywords": [
            "air quality monitoring", "air sensor network", "EPA air quality",
            "hyperlocal pollution", "environmental justice air",
            "PM2.5 monitoring",
        ],
    },
    "data_centers": {
        "label": "Compartmentalized Data Centers",
        "emoji": "🖥️",
        "color": "#6b4423",
        "feeds": [
            "https://www.datacenterdynamics.com/en/rss/",
            "https://www.datacenterfrontier.com/rss.xml",
        ],
        "keywords": [
            "modular data center", "compartmentalized data center",
            "data center interconnection", "co-located load",
            "data center power constraint", "edge data center",
        ],
    },
    "ai_buildings": {
        "label": "AI-Driven Building Energy Optimization",
        "emoji": "🏢",
        "color": "#7a3b3b",
        "feeds": [
            "https://www.greenbiz.com/rss.xml",
            "https://www.energymanagertoday.com/feed",  # verify/replace if dead
        ],
        "keywords": [
            "AI building energy", "smart building HVAC", "occupancy sensor",
            "building energy optimization", "commercial building efficiency AI",
        ],
    },
}

# ---------------------------------------------------------------------------
# REPORTERS TO TRACK
# Add reporters whose bylines/beats matter to your clients. The enrichment
# step will flag when their name shows up in a pulled article, and the AI
# pass will do a best-effort scan for public "I've moved" / "new beat" /
# open-records signals. This is NOT a guaranteed detector — treat radar
# output as a lead to verify, not a confirmed fact.
# ---------------------------------------------------------------------------
TRACKED_REPORTERS = [
    "Jeff St. John", "Jason Plautz", "Robert Walton", "Catherine Morehouse",
    "Sebastian Moss", "Rich Heidorn Jr.", "Kate Winston", "Sara Heegaard",
    "Deonna Anderson",
]

# ---------------------------------------------------------------------------
# NEWS API (for broader discovery beyond your known RSS feeds)
# Uses NewsAPI.org's /v2/everything endpoint. Free tier: 100 req/day,
# https://newsapi.org (sign up for NEWSAPI_KEY)
# ---------------------------------------------------------------------------
NEWSAPI_URL = "https://newsapi.org/v2/everything"
NEWSAPI_PAGE_SIZE = 10

# How many hours back to search. The run script auto-widens this on Mondays
# to cover the weekend (see main.py).
LOOKBACK_HOURS_WEEKDAY = 24
LOOKBACK_HOURS_MONDAY = 72

# Max stories to include per vertical section in the final email
MAX_STORIES_PER_VERTICAL = 2

# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------
EMAIL_SUBJECT_PREFIX = "Adding Spark-le ✨ —"
NEWSLETTER_NAME = "Adding Spark-le ✨"
