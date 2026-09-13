# Viking Legacy & Lore

Stages 1A–1D: a static media site served by Cloudflare Workers Static Assets. Plain HTML/CSS, a small progressive-enhancement script, and a Python standard-library builder. No frontend framework, database, paid CMS, or runtime API.

Live: https://vikinglegacyandlore.com/
Archive: https://vikinglegacyandlore.com/episodes/

## Development

```sh
python3 build.py
python3 -m unittest -v test_site.py
python3 -m http.server 8766 --directory public
```

See [PUBLISHING.md](PUBLISHING.md) for importing episodes, editing content, adding sources and publishing.

- `content/episodes/*.json`: stable episode records; plain-text notes, optional platform IDs and reading sources.
- `build.py`: reusable homepage, archive and episode rendering; validation and generated-page cleanup.
- `homepage.template.html`: existing brand, homepage structure, shared head/navigation/footer.
- `homepage.json`: curated Start Here choices (legacy recent-card data retained for reference).
- `public/site.css`: shared styles.
- `public/episodes.js`: archive filtering and click-to-load platform players. Direct audio and all content work without JavaScript.
- `.generated-pages.json`: builder-owned page manifest; prevents cleanup from touching unrelated files.

## Deployment

GitHub `main` triggers Cloudflare Workers Builds. Existing dashboard settings: build command `exit 0`, deploy command `npx wrangler deploy`, root `/`. Wrangler's repository configuration runs `python3 build.py` before publishing `public/`. Commit generated files too so repository review and local previews match production. No network is required during rendering.

The existing unpinned Wrangler command is retained. The production configuration introduced in Stage 1A declares static assets and custom 404 handling. DNS, custom domains, routes and permissions remain managed as before.

## Content provenance and scope

The initial 52 episode/trailer entries were imported from https://feeds.buzzsprout.com/2459523.rss on September 13, 2026. Published titles and notes were retained as plain text, with promotional boilerplate removed. Existing short homepage hooks were reused, and one obvious missing initial letter was corrected. The newest feed entry remains Hervor, July 6, 2026. Platform IDs were checked against Spotify/YouTube oEmbed titles. Existing show artwork is reused rather than generating new images. Topic categories are editorial navigation, not evidence ratings.

No researched bibliographies were present in the feed. The template supports verified sources and further reading when supplied; it does not fabricate citations. Original episode notes link to their publisher. Original Tora stories have their own category. Advanced history/saga/myth distinctions belong to the later archive stage.

Direct audio uses the RSS enclosure with `preload="none"`. Third-party episode embeds load only on click. External providers may restrict playback by browser, region or account; direct audio, platform links and the podcast-host page offer alternatives. The homepage show embed also loads only on click.

## Next stages

2: articles and contributor/editorial workflow.
3: curated Norse library, archaeology and research resources.
4: linked sagas, Eddas, translations, people, places, maps and archive tools.

Do not advance stages without the owner's request.

## Stage 1B validation

Offline tests cover generated internal links/headings, reproducible builds, invalid slugs, escaped content, and unpublishing cleanup. Browser checks covered search, topic filtering, empty results, clearing filters, mobile/tablet overflow and loading both platform embeds. Direct Hervor audio played successfully with the expected duration. All 52 publisher-page URLs responded successfully. Automated audio probes were partially rejected with HTTP 403 even though browser playback worked; do not interpret command-line audio probes as a guarantee of availability for every listener. All 22 configured platform IDs matched the expected titles through provider oEmbed metadata.

## Stages 1C and 1D

Supporting pages live in `content/pages/*.json` and render through the same site shell. Edit their copy and links there, then run `python3 build.py`. Articles and Library are honest introductions to future collections. No articles, research sources, host credentials or contribution agreements have been invented. Contact and pitches use email; no form, account or upload service has been added.

All pages include shared website/podcast identity data. Episode pages identify audio, duration and series; the archive lists actual published episodes. Breadcrumbs and canonical URLs follow generated routes. The sitemap includes every indexable page, excluding the shared custom 404. The builder removes only paths previously recorded as generated when content is removed.

The homepage now uses the same deliberate player loading as episode pages. Native audio uses `preload="none"`, with an accessible failure message and persistent host/file links. The embedded SVG favicon uses the smaller original-silhouette export, reducing it from about 123 KB to 32 KB. No new runtime dependency was added.

Cloudflare Web Analytics was already enabled for `vikinglegacyandlore.com`, with automatic setup excluding EU visitors. The dashboard showed recorded visits on September 13, 2026. Preserve that account configuration; do not add another beacon to the template. Cloudflare supplies traffic and real-user performance metrics, not a custom click-event dashboard.

`episodes.js` emits `viking:interaction` DOM events for selected outgoing links, player loads and the first actual audio playback. Payloads contain only action and a fixed destination category. These events stay in the browser: no storage, no transport, and no email addresses, search queries or full URLs. A separately approved analytics adapter would be needed to collect custom events remotely. See `/privacy/` for visitor-facing details.

Validation: run `python3 build.py`, `python3 test_site.py`, `node --check public/episodes.js`, and `git diff --check`. Browser checks cover all generated pages at desktop, tablet, narrow mobile and landscape widths. Physical phones and a real screen-reader session require manual follow-up; browser viewport and accessibility-tree checks are not equivalent to those tests. Existing audio does not have full transcripts, so these changes do not establish full WCAG conformance.
