"""Render the Stage 1A homepage using only Python's standard library."""
from pathlib import Path
import html, json
root = Path(__file__).resolve().parent
data = json.loads((root / "homepage.json").read_text())
page = (root / "homepage.template.html").read_text()
for key in ("start", "episodes"):
    cards = []
    for i, item in enumerate(data[key], 1):
        category, title, hook, url = [html.escape(item[k], quote=True) for k in ("category", "title", "hook", "url")]
        if not url.startswith("https://"):
            raise ValueError("Episode links must use HTTPS")
        number = f'<span class="number" aria-hidden="true">0{i}</span>' if key == "start" else ""
        label = "Listen on Spotify" if "spotify.com/" in url else "Watch on YouTube"
        cards.append(f'<article class="card {"episode" if key == "episodes" else ""}">{number}<div class="meta">{category}</div><h3>{title}</h3><p>{hook}</p><a class="text-link" href="{url}" aria-label="{label}: {title}">{label} ↗</a></article>')
    page = page.replace("{{" + key.upper() + "}}", "\n".join(cards))
(root / "public" / "index.html").write_text(page)
print("Rendered public/index.html")
