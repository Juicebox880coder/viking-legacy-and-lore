# Maintaining the Norse Library

Edit content/research/resources.json, paths.json and discoveries.json, then run:

```sh
python3 build.py
python3 -m unittest -v test_site.py
python3 tools/check_resources.py
```

Resources require an identifiable creator/institution, legitimate HTTPS destination, original summary, reading context, edition-specific citation, language/access/rights notes and editorial review date. Free access is not a reuse licence. Link to lawful originals; do not upload third-party books, translations, photographs or scans without applicable permission. Credit translators and edition information, not just medieval authors.

Use the existing controlled topic/type/level/access labels so filters stay useful. Learning paths reference resource IDs in reading order with one original prompt per step. Archaeology entries require Evidence, Interpretation and What remains open, each with explicit resource references. Distinguish ancient dates, discovery dates and publication dates. Older findings must be labelled as milestones rather than latest news.

Related episode IDs express a topic connection, not evidence that an episode cited a work. Unpublished episodes automatically disappear from related listening. Do not add article connections until the articles exist.

The checker writes .cache/research-links.json and flags HTTP failures and editorial reviews older than 180 days. A successful HTTP response never updates the editorial review date. Rate limits and bot restrictions require a normal browser check, not a security bypass. Re-read changed sources, check author/edition/licence details and revise affected claims before updating reviewed. Review at least every six months and when a reader reports a problem; this tool does not schedule monitoring.

For an unavailable resource, set status to unavailable while investigating. Keep its bibliographic record for transparency. Learning paths and catalogue cards suppress its reading link; historical case-study citations retain the original destination so readers can identify the cited work. Replace or remove an unsuitable source and update every path/citation referring to it. The build rejects missing references. Use git history to document substantial corrections and publish a correction in the entry when its meaning changes.

## Initial verification — September 13, 2026

25 resource destinations reviewed. Automated GET checks succeeded for 22. Open Book Publishers returned 429; UNESCO Hedeby and Jelling returned 403 to the checker. All three loaded their correct source records in Chrome and were manually verified. These browser checks do not overwrite the raw automated results. No 404/410 responses. No full texts or third-party research images are mirrored on the site. Original annotations link outward with credits and edition/access information.
