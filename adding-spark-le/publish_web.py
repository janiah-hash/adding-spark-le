"""
Publishes the rendered newsletter as a webpage instead of emailing it.

Writes:
  docs/index.html              <- always the latest edition (what you bookmark)
  docs/archive/YYYY-MM-DD.html <- a permanent copy of each day's edition
  docs/archive/index.html      <- a simple list of past editions

The GitHub Actions workflow commits and pushes the "docs/" folder after
each run. GitHub Pages (configured once in your repo settings to serve
from the "docs" folder) picks up the change automatically — no server,
no email, no extra accounts.
"""

from datetime import datetime
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"
ARCHIVE_DIR = DOCS_DIR / "archive"

ARCHIVE_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Adding Spark-le ✨ — Archive</title>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background:#f4f1ea; color:#3d2f1f; max-width:640px; margin:40px auto; padding:0 20px; }}
  h1 {{ color:#6b4423; }}
  a {{ color:#b5562c; text-decoration:none; }}
  li {{ margin-bottom:8px; }}
  .back {{ display:inline-block; margin-bottom:20px; }}
</style>
</head>
<body>
  <a class="back" href="../index.html">&larr; Back to latest edition</a>
  <h1>Adding Spark-le ✨ — Past Editions</h1>
  <ul>
    {items}
  </ul>
</body>
</html>
"""


def publish(html_content, today=None):
    """Writes today's edition to docs/index.html + docs/archive/, and
    refreshes the archive index list."""
    today = today or datetime.now()
    date_str = today.strftime("%Y-%m-%d")

    DOCS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    # Always-current latest edition
    (DOCS_DIR / "index.html").write_text(html_content, encoding="utf-8")

    # Permanent dated copy
    (ARCHIVE_DIR / f"{date_str}.html").write_text(html_content, encoding="utf-8")

    # Rebuild the archive index from whatever dated files exist
    dated_files = sorted(ARCHIVE_DIR.glob("*.html"), reverse=True)
    dated_files = [f for f in dated_files if f.name != "index.html"]
    items = "\n    ".join(
        f'<li><a href="{f.name}">{f.stem}</a></li>' for f in dated_files
    )
    (ARCHIVE_DIR / "index.html").write_text(
        ARCHIVE_INDEX_TEMPLATE.format(items=items), encoding="utf-8"
    )

    print(f"Published: docs/index.html and docs/archive/{date_str}.html")


if __name__ == "__main__":
    publish("<h1>Test edition</h1>")
