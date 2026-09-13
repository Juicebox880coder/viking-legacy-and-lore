# Viking Legacy & Lore emblem

`originals/` preserves the four supplied PNG files unchanged: antique gold, warm ivory, deep charcoal, and the silver alternate. The existing podcast artwork in `public/cover.jpg` remains unchanged.

The editorial website uses flat antique gold (#9A8357). Warm ivory (#E8E1D3) on deep charcoal (#1C1B19) improves recognition for browser and bookmark icons. The silver alternate is retained for other brand applications.

Run `python3 brand/export_icons.py` with Pillow to reproduce the web assets. Exports retain the supplied gold mark's alpha silhouette, trim transparent padding, and normalize the ink color. They do not redraw the logo. Small raster exports serve navigation and dividers; the larger export serves the restrained homepage watermark. The SVG favicon is a self-contained wrapper around the supplied raster silhouette, not a vector tracing.

Website placements are shared through `homepage.template.html`, `build.py`, and `public/site.css`. Decorative images have empty alternative text; their adjacent wordmarks supply accessible link names. The homepage watermark is 4–4.5% opacity. Section dividers appear only before Explore and related episodes. The manifest provides bookmark icons, without adding offline behavior.
