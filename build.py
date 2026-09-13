"""Build the homepage, archive and episode pages without network access or dependencies."""
from pathlib import Path
from datetime import datetime
import html, json, re
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
SITE='https://vikinglegacyandlore.com'
esc=lambda s:html.escape(str(s),quote=True)
def safe_url(value):
    if not isinstance(value,str) or urlparse(value).scheme!='https' or not urlparse(value).netloc:raise ValueError('Expected an absolute HTTPS URL: '+str(value))
    return value

def load_episodes():
    items=[];ids=set();slugs=set()
    for file in sorted((ROOT/'content/episodes').glob('*.json')):
        e=json.loads(file.read_text())
        for field in ('id','slug','title','published','duration','category','summary','notes','image','audio_url','sources','publication_url','draft'):
            if field not in e:raise ValueError(f'{file}: missing {field}')
        if e['id'] in ids or e['slug'] in slugs:raise ValueError('Duplicate episode ID or slug')
        ids.add(e['id']);slugs.add(e['slug'])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',e['slug']):raise ValueError('Unsafe slug')
        datetime.fromisoformat(e['published'])
        if type(e['duration']) is not int or e['duration']<0:raise ValueError('Invalid duration')
        if type(e['draft']) is not bool:raise ValueError('draft must be true or false')
        if not isinstance(e['notes'],list) or not all(isinstance(n,str) for n in e['notes']):raise ValueError('Notes must be plain text paragraphs')
        for key in ('audio_url','publication_url'):safe_url(e[key])
        for source in e['sources']:safe_url(source['url']);assert source['title']
        for key,pattern in [('spotify_id',r'[A-Za-z0-9]{22}'),('youtube_id',r'[A-Za-z0-9_-]{11}')]:
            if e.get(key) and not re.fullmatch(pattern,e[key]):raise ValueError('Invalid '+key)
        if e['image'].startswith('/'):
            image_path=(PUBLIC/e['image'].lstrip('/')).resolve()
            if not image_path.is_relative_to(PUBLIC.resolve()) or not image_path.is_file():raise ValueError('Missing or unsafe local image')
        else:safe_url(e['image'])
        if not e['draft']:items.append(e)
    return sorted(items,key=lambda x:datetime.fromisoformat(x['published']),reverse=True)

def path(e):return '/episodes/'+e['slug']+'/'
def date(e):return datetime.fromisoformat(e['published']).strftime('%B %d, %Y').replace(' 0',' ')
def duration(e):return f"{e['duration']//60}:{e['duration']%60:02d}"
def card(e):
    return f'<article class="card episode" data-episode data-category="{esc(e["category"])}"><div class="meta">{esc(e["category"])}</div><h3><a href="{path(e)}">{esc(e["title"])}</a></h3><p class="episode-date"><time datetime="{esc(e["published"])}">{date(e)}</time> · {duration(e)}</p><p>{esc(e["summary"][:220])}{"…" if len(e["summary"])>220 else ""}</p><a class="text-link" href="{path(e)}" aria-label="Explore episode: {esc(e["title"])}">Listen &amp; explore →</a></article>'

def platform_links(e):
    links=''
    if e.get('spotify_id'):links+=f'<a class="button button-primary" href="https://open.spotify.com/episode/{e["spotify_id"]}">Listen on Spotify</a>'
    if e.get('youtube_id'):links+=f'<a class="button button-secondary" href="https://www.youtube.com/watch?v={e["youtube_id"]}">Watch on YouTube</a>'
    return links

def latest(e):
    return f'''<section id="latest" aria-labelledby="latest-heading"><div class="section-head"><div><div class="eyebrow">The latest chapter</div><h2 id="latest-heading">New from the Viking world</h2></div><p class="meta">Latest podcast episode · {date(e)}</p></div><article class="feature"><img src="{esc(e['image'])}" width="300" height="300" loading="lazy" alt="Viking Legacy and Lore podcast artwork"><div><div class="meta">{esc(e['category'])} · {duration(e)}</div><h3><a href="{path(e)}">{esc(e['title'])}</a></h3><p>{esc(e['summary'])}</p><div class="buttons">{platform_links(e)}</div><a class="text-link" href="{path(e)}">Full episode, players &amp; notes →</a></div></article></section>'''

def page_shell(template,title,description,url,body,image='/cover.jpg',schema=None):
    head=template.split('</head>')[0]+'</head>'
    head=re.sub(r'<title>.*?</title>',f'<title>{esc(title)} | Viking Legacy &amp; Lore</title>',head)
    head=re.sub(r'<meta name="description"[^>]*>',f'<meta name="description" content="{esc(description)}">',head)
    head=re.sub(r'<link rel="canonical"[^>]*>',f'<link rel="canonical" href="{SITE+url}">',head)
    for key,value in [('og:title',title),('og:description',description),('og:url',SITE+url),('og:image',SITE+image if image.startswith('/') else image)]:
        head=re.sub(fr'<meta property="{key}"[^>]*>',f'<meta property="{key}" content="{esc(value)}">',head)
    for key,value in [('twitter:title',title),('twitter:description',description),('twitter:image',SITE+image if image.startswith('/') else image)]:
        head=re.sub(fr'<meta name="{key}"[^>]*>',f'<meta name="{key}" content="{esc(value)}">',head)
    if schema:head=head.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
    nav=template[template.index('<nav class="site-nav"'):template.index('<header>')]
    footer=template[template.index('<footer>'):].split('</body>')[0]
    for anchor in ('home','about','explore'):
        nav=nav.replace(f'href="#{anchor}"',f'href="/{"#"+anchor if anchor!="home" else ""}"')
        footer=footer.replace(f'href="#{anchor}"',f'href="/{"#"+anchor if anchor!="home" else ""}"')
    return head+'<body><a class="skip" href="#main">Skip to content</a>'+nav+'<main id="main" class="episode-main">'+body+'</main>'+footer+'<script src="/episodes.js" defer></script></body></html>'

def player(e,kind):
    if kind=='spotify':src='https://open.spotify.com/embed/episode/'+e['spotify_id'];label='Spotify';height=352
    else:src='https://www.youtube-nocookie.com/embed/'+e['youtube_id'];label='YouTube';height=360
    return f'<div class="embed-shell {kind}"><button class="button button-secondary" type="button" data-embed="{src}" data-title="{esc(e["title"])} on {label}" data-height="{height}" hidden>Load {label} player</button><p class="embed-note">Loading this player connects to {label}.</p><noscript><p>Use the {label} link above to open this episode.</p></noscript></div>'

def build():
    episodes=load_episodes()
    if not episodes:raise ValueError('No published episodes')
    template=(ROOT/'homepage.template.html').read_text();home=template.replace('{{LATEST}}',latest(episodes[0]))
    original=json.loads((ROOT/'homepage.json').read_text())
    for key in ('start','episodes'):
        if key=='episodes':cards=[card(e) for e in episodes[1:4]]
        else:
            cards=[]
            for i,item in enumerate(original[key],1):
                e=next((e for e in episodes if e['title']==item['title']),None)
                if not e:raise ValueError('Start Here selection is missing: '+item['title'])
                cards.append(f'<article class="card"><span class="number" aria-hidden="true">0{i}</span><div class="meta">{esc(item["category"])}</div><h3>{esc(e["title"])}</h3><p>{esc(item["hook"])}</p><a class="text-link" href="{path(e)}" aria-label="Explore episode: {esc(e["title"])}">Listen &amp; explore →</a></article>')
        home=home.replace('{{'+key.upper()+'}}','\n'.join(cards))
    generated={ 'index.html':home }
    categories=sorted({e['category'] for e in episodes})
    filters='<form class="archive-filters" role="search" hidden><div><label for="episode-search">Search episodes</label><input id="episode-search" type="search" placeholder="Try Odin, longships, or Viking food"></div><div><label for="episode-topic">Topic</label><select id="episode-topic"><option value="">All topics</option>'+''.join(f'<option>{esc(c)}</option>' for c in categories)+'</select></div><button type="reset" class="button button-secondary">Clear filters</button></form>'
    archive=f'<section><div class="eyebrow">The listening room</div><h1 class="page-title">Every story is a way in.</h1><p class="section-intro">Explore the Viking Legacy &amp; Lore episode archive: history, mythology, sagas and the lives behind the legends.</p>{filters}<p id="result-count" role="status" aria-live="polite">{len(episodes)} episodes and trailers · newest first</p><p id="no-results" hidden>No episodes match your search. Try a different word or clear the filters.</p><div class="grid archive-grid">'+''.join(card(e).replace('<h3>', '<h2>').replace('</h3>', '</h2>') for e in episodes)+'</div></section>'
    generated['episodes/index.html']=page_shell(template,'Episode archive','Listen to Viking Legacy & Lore: browse episodes about Viking history, Norse mythology, sagas, voyages and everyday life.','/episodes/',archive)
    for e in episodes:
        notes=''.join('<p>'+esc(n)+'</p>' for n in e['notes'])
        media=f'<section id="listen" aria-labelledby="listen-heading"><h2 id="listen-heading">Listen to this episode</h2><audio controls preload="none" aria-label="{esc(e["title"])}"><source src="{esc(e["audio_url"])}" type="audio/mpeg">Your browser does not support audio playback.</audio><p class="note"><a href="{esc(e["audio_url"])}">Open the audio file</a> · <a href="{esc(e["publication_url"])}">Listen on the podcast host</a></p><div class="buttons">{platform_links(e)}</div>'
        if e.get('spotify_id'):media+=player(e,'spotify')
        if e.get('youtube_id'):media+=player(e,'youtube')
        media+='</section>'
        reading=''
        if e['sources']:reading='<h3>Sources &amp; further reading</h3><ul>'+''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a>{" — "+esc(s["note"]) if s.get("note") else ""}</li>' for s in e['sources'])+'</ul>'
        preferred=e.get('related_ids',[])
        related=sorted((x for x in episodes if x['id']!=e['id']),key=lambda x:(preferred.index(x['id']) if x['id'] in preferred else len(preferred),0 if x['category']==e['category'] else 1))[:3]
        body=f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/episodes/">Episodes</a></nav><section class="episode-heading"><div class="eyebrow">{esc(e["category"])}</div><h1 class="page-title">{esc(e["title"])}</h1><p class="meta"><time datetime="{esc(e["published"])}">{date(e)}</time> · {duration(e)} · {"Trailer" if e.get("type")=="trailer" else "Podcast"}</p><p class="section-intro">{esc(e["summary"])}</p></section><div class="episode-layout"><div>{media}<section id="notes"><h2>About this episode</h2><div class="show-notes">{notes}</div></section><section class="source-note"><h2>Episode notes &amp; reading</h2><p>These are the show’s published episode notes. <a href="{esc(e["publication_url"])}">View the original episode on Buzzsprout</a>.</p>{reading}</section></div><aside class="episode-aside"><img src="{esc(e["image"])}" width="300" height="300" alt="Viking Legacy and Lore podcast artwork" loading="lazy"><p class="eyebrow">Keep exploring</p><p>Stories of the Viking world, wherever you listen.</p><a class="text-link" href="/episodes/">Browse all episodes →</a><a class="text-link" href="https://open.spotify.com/show/7ocooMGKkr9oTVeggU237S">Follow the show on Spotify ↗</a></aside></div><section><div class="eyebrow">Continue your journey</div><h2>More to explore</h2><div class="grid">'+''.join(card(x) for x in related)+'</div></section>'
        schema={'@context':'https://schema.org','@type':'PodcastEpisode','name':e['title'],'url':SITE+path(e),'datePublished':e['published'],'description':e['summary'],'timeRequired':f'PT{e["duration"]}S','partOfSeries':{'@type':'PodcastSeries','name':'Viking Legacy & Lore','url':SITE},'associatedMedia':{'@type':'AudioObject','contentUrl':e['audio_url']}}
        generated[path(e).lstrip('/')+'index.html']=page_shell(template,e['title'],e['summary'][:160],path(e),body,e['image'],schema)
    # Remove only pages generated by this builder on the previous run.
    manifest=ROOT/'.generated-pages.json'
    previous=json.loads(manifest.read_text()) if manifest.exists() else []
    for old in set(previous)-set(generated):
        candidate=(PUBLIC/old).resolve()
        if candidate.is_relative_to((PUBLIC/'episodes').resolve()) and candidate.name=='index.html':candidate.unlink(missing_ok=True)
    for name,content in generated.items():
        target=PUBLIC/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
    manifest.write_text(json.dumps(sorted(generated),indent=2)+'\n')
    urls=['/','/episodes/']+[path(e) for e in episodes]
    (PUBLIC/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+SITE+esc(u)+'</loc></url>' for u in urls)+'</urlset>\n')
    print(f'Built homepage, archive and {len(episodes)} episode pages.')
if __name__=='__main__':build()
