# Viking Legacy & Lore

Stages 1A and 1B: a static media site served by Cloudflare Workers Static Assets. Plain HTML/CSS, a small progressive-enhancement script, and a Python standard-library builder. No frontend framework, database, paid CMS, or runtime API.

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

Direct audio uses the RSS enclosure with `preload="none"`. Third-party episode embeds load only on click. External providers may restrict playback by browser, region or account; direct audio, platform links and the podcast-host page offer alternatives. The pre-existing homepage show embed remains lazy-loaded.

## Next stages

1C: dedicated About, Articles, Library, Contribute and Contact pages.
1D: broader accessibility, performance, metadata, physical-device testing and deliberate analytics choices.
2: articles and contributor/editorial workflow.
3: curated Norse library, archaeology and research resources.
4: linked sagas, Eddas, translations, people, places, maps and archive tools.

Do not advance stages without the owner's request.

## Stage 1B validation

Offline tests cover generated internal links/headings, reproducible builds, invalid slugs, escaped content, and unpublishing cleanup. Browser checks covered search, topic filtering, empty results, clearing filters, mobile/tablet overflow and loading both platform embeds. Direct Hervor audio played successfully with the expected duration. All 52 publisher-page URLs responded successfully. Automated audio probes were partially rejected with HTTP 403 even though browser playback worked; do not interpret command-line audio probes as a guarantee of availability for every listener. All 22 configured platform IDs matched the expected titles through provider oEmbed metadata.
