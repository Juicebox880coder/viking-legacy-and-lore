# Viking Legacy & Lore

Stage 1A: foundation and homepage. Plain HTML/CSS served by Cloudflare Workers Static Assets. No frontend framework, application JavaScript, database, or paid CMS.

## Publishing

`main` is the production branch. Cloudflare Workers Builds watches the connected GitHub repository. Its current build command is `exit 0`, deploy command is `npx wrangler deploy`, and root is `/`. `wrangler.jsonc` declares `public/` as the asset directory. Only that directory is published.

Preview locally: `python3 -m http.server 8765 --directory public`.

Homepage card content lives in `homepage.json`; layout lives in `homepage.template.html`. After changing either, run `python3 build.py`, inspect the result, and commit the sources **and** generated `public/index.html`. The committed HTML works without Python or JavaScript in production. The featured episode remains in the template until Stage 1B adds the full episode model. Never deploy source changes without regenerating HTML.

## Content provenance

Verified September 11, 2026 against the show's RSS feed at https://feeds.buzzsprout.com/2459523.rss, Spotify episode pages, and https://www.youtube.com/@VikingLegacyandLore. July 6, 2026 Hervor is the latest podcast episode in the feed. Titles retain published spelling. Homepage hooks summarize the published descriptions. `public/cover.jpg` is the existing show artwork supplied by Spotify's Hervor oEmbed response, not a newly generated image.

Instagram and email were confirmed by the owner. The About section uses the host name from the podcast's public profile. No fictitious episodes or articles.

## Scope and next step

Navigation uses homepage anchors until real supporting pages exist. All Episodes and Episode Details point to Spotify. Future topic previews are intentionally not links. Stage 1B should add an episode data model and static episode/archive templates; retain optional Spotify/YouTube URLs, image, publication date, sources and slug. Then replace the external detail links with actual published episode routes. Do not publish nonexistent routes.

## Audit and deployment risks

Initial repository: two commits, README and one public/index.html file. No package manifest, Actions workflow, Wrangler configuration, or existing CMS. Production HTML matched commit 97e530f. The active Cloudflare version had been manually deployed despite GitHub being connected. Added explicit asset configuration so the dashboard command can reproduce deployment from GitHub. No DNS, routes, permissions or domain registrations changed.

Wrangler currently resolves through the existing unpinned `npx` command; pinning a tested CLI version can be considered separately. Runtime assets remain very small. Spotify is an external dependency and its player can fail or be blocked, so direct listening links remain available. No autoplay or custom analytics added.

## Validation

Homepage inspected in Chrome at desktop, 768px, 390px and 320px; no horizontal overflow. Navigation stays visible without a JavaScript menu. Anchor targets and artwork verified. Meta description, canonical, Open Graph, Twitter card, favicon, robots and sitemap included. A branded 404 page avoids treating missing archive pages as the homepage. Built-in keyboard focus styles, skip link, semantic headings, descriptive links, iframe title and reduced-motion handling included.

Stop after Stage 1A. Full archive, episode pages and dedicated supporting pages belong to subsequent stages.
