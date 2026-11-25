"""Publish short author-led manuscript excerpts with explicit context and provenance."""
import html,json,re,math
from datetime import date
from urllib.parse import urlsplit
SITE='https://vikinglegacyandlore.com'
esc=lambda value:html.escape(str(value),quote=True)
LABELS={'blog':'Blog','stories':'Stories'}
def url(p):return '/'+p['kind']+'/'+p['slug']+'/'
def minutes(p):return max(1,math.ceil(len(' '.join(p['paragraphs']).split())/220))
def load(root,episodes):
    posts=[];episode_ids={e['id'] for e in episodes}
    for kind in LABELS:
        for file in sorted((root/'content'/kind).glob('*.json')):
            p=json.loads(file.read_text())
            for key in ('kind','slug','title','summary','category','author','published','source_title','paragraphs','context','editorial_note','sources','related'):
                if not p.get(key) and key not in ('sources','related'):raise ValueError(f'{file}: missing {key}')
            if p['kind']!=kind or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',p['slug']):raise ValueError('Unsafe editorial path')
            date.fromisoformat(p['published'])
            if not isinstance(p['paragraphs'],list) or not all(isinstance(x,str) and x.strip() for x in p['paragraphs']):raise ValueError('Invalid editorial paragraphs')
            if kind=='blog' and not p['sources']:raise ValueError('Blog requires sources')
            if p.get('episode_id') and p['episode_id'] not in episode_ids:raise ValueError('Unknown editorial episode')
            for s in p['sources']:
                if urlsplit(s['url']).scheme!='https' or not urlsplit(s['url']).netloc:raise ValueError('Editorial source must be HTTPS')
            posts.append(p)
    paths={p['kind']+'/'+p['slug'] for p in posts}
    if len(paths)!=len(posts):raise ValueError('Duplicate editorial path')
    for p in posts:
        if any(x not in paths for x in p['related']):raise ValueError('Unknown related post')
    posts.sort(key=lambda p: p['published'], reverse=True)
    return posts

def card(p):
    return f'<article class="resource-card editorial-card" data-post data-category="{esc(p["category"])}"><div class="meta">{esc(p["category"])} · {minutes(p)} min read</div><h2><a href="{url(p)}">{esc(p["title"])}</a></h2><p>{esc(p["summary"])}</p><a class="text-link" href="{url(p)}" aria-label="Read {esc(p["title"])}">Read {"the story" if p["kind"]=="stories" else "the post"} →</a></article>'

def generate(root,template,episodes,shell,episode_path):
    posts=load(root,episodes);pages={};by_id={e['id']:e for e in episodes};by_path={p['kind']+'/'+p['slug']:p for p in posts}
    for kind,label in LABELS.items():
        items=[p for p in posts if p['kind']==kind]
        categories=sorted({p['category'] for p in items})
        title='Stories by T.R. Pomeroy' if kind=='stories' else 'Viking History & Norse Mythology Blog'
        heading='Pull closer to the fire.' if kind=='stories' else 'A little history. A deeper connection.'
        intro='Story excerpts from the manuscripts of T.R. Pomeroy. Original tales, imagined historical scenes and creative retellings of Norse myth and saga—each with a brief note about its roots.' if kind=='stories' else 'Short reads from the manuscripts of T.R. Pomeroy: Viking life, Norse mythology and reflections on what the old stories still ask of us. Read a little, then follow the sources or listen further.'
        filters=f'<form class="editorial-filters archive-filters" role="search" hidden><div><label for="post-search">Search {label.lower()}</label><input id="post-search" type="search" placeholder="Try silver, Odin, or winter"></div><div><label for="post-category">{"Story type" if kind=="stories" else "Topic"}</label><select id="post-category"><option value="">All {"story types" if kind=="stories" else "topics"}</option>'+''.join(f'<option>{esc(c)}</option>' for c in categories)+'</select></div><button class="button button-secondary" type="reset">Clear filters</button></form>'
        body=f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / {label}</nav><section class="support-heading"><div class="eyebrow">{label} · T.R. Pomeroy</div><h1 class="page-title">{heading}</h1><p class="section-intro">{intro}</p></section>{filters}<p id="post-count" role="status" aria-live="polite">{len(items)} {"stories" if kind=="stories" else "posts"}</p><p id="post-empty" hidden>No matches. Try another word or clear the filters.</p><div class="resource-grid">'+''.join(card(p) for p in items)+'</div>'
        body+='<div class="support-actions buttons"><a class="button button-secondary" href="/'+('blog/' if kind=='stories' else 'stories/')+'">'+('Explore the Blog' if kind=='stories' else 'Step into Stories')+'</a><a class="button button-secondary" href="/articles/">Read the sourced guides</a></div>'
        schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':SITE+'/'+kind+'/','mainEntity':{'@type':'ItemList','numberOfItems':len(items),'itemListElement':[{'@type':'ListItem','position':n,'name':p['title'],'url':SITE+url(p)} for n,p in enumerate(items,1)]}}
        page=shell(template,title,intro[:160],'/'+kind+'/',body,schema=schema)
        # Archives have their own controls; the episode archive handler must not bind these.
        page=page.replace('editorial-filters archive-filters','editorial-filters').replace('</body>','<script src="/editorial.js" defer></script></body>')
        pages[kind+'/index.html']=page
    for p in posts:
        kind=p['kind'];label=LABELS[kind]
        stamp=date.fromisoformat(p['published']).strftime('%B %d, %Y').replace(' 0',' ')
        body=f'<article class="reading-article manuscript-post"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/{kind}/">{label}</a></nav><header><div class="eyebrow">{esc(p["category"])}</div><h1 class="page-title">{esc(p["title"])}</h1><p class="post-byline">By {esc(p["author"])} · {minutes(p)} min read · <time datetime="{p["published"]}">{stamp}</time></p><p class="section-intro">{esc(p["summary"])}</p></header>'
        if kind=='stories':body+=f'<aside class="story-context" aria-label="About this story"><p>{esc(p["context"])}</p></aside>'
        body+='<div class="manuscript-prose">'+''.join('<p>'+esc(t)+'</p>' for t in p['paragraphs'])+'</div>'
        if kind=='blog':body+='<section class="source-note"><h2>Historical context &amp; sources</h2><p>'+esc(p['context'])+' '+''.join(f'<a href="#post-source-{i}" aria-label="Source {i}">[{i}]</a> ' for i,_ in enumerate(p['sources'],1))+'</p><ol class="source-list">'+''.join(f'<li id="post-source-{i}"><a href="{esc(s["url"])}">{esc(s["title"])}</a><p>{esc(s["note"])}</p></li>' for i,s in enumerate(p['sources'],1))+'</ol></section>'
        body+=f'<details class="excerpt-credit"><summary>About this excerpt</summary><p>From the manuscript <cite>{esc(p["source_title"])}</cite>, by {esc(p["author"])}.</p><p>{esc(p["editorial_note"])}</p></details>'
        if p.get('episode_id'):
            e=by_id[p['episode_id']]
            body+=f'<section class="post-listen"><div class="eyebrow">Continue listening</div><h2>The episode behind the excerpt</h2><p><a href="{episode_path(e)}">{esc(e["title"])}</a></p><p class="note">Read the episode notes and choose an audio or video player.</p></section>'
        if p['related']:
            body+='<section><h2>Keep reading</h2><ul>'+''.join(f'<li><a href="/{key}/">{esc(by_path[key]["title"])}</a></li>' for key in p['related'])+'</ul></section>'
        body+=f'<p class="post-return"><a class="text-link" href="/{kind}/">← All {label.lower()}</a></p></article>'
        schema={'@context':'https://schema.org','@type':'ShortStory' if kind=='stories' else 'BlogPosting','headline':p['title'],'name':p['title'],'description':p['summary'],'url':SITE+url(p),'mainEntityOfPage':SITE+url(p),'author':{'@type':'Person','name':p['author'],'url':SITE+'/about/'},'publisher':{'@type':'Organization','name':'Viking Legacy & Lore','url':SITE},'datePublished':p['published'],'inLanguage':'en','genre':p['category'],'wordCount':len(' '.join(p['paragraphs']).split()),'isAccessibleForFree':True,'image':SITE+'/cover.jpg'}
        if p['sources']:schema['citation']=[s['url'] for s in p['sources']]
        page=shell(template,p['title'],p['summary'],url(p),body,schema=schema)
        page=page.replace('<meta property="og:type" content="website">','<meta property="og:type" content="article">')
        pages[url(p).lstrip('/')+'index.html']=page
    return pages,posts

def episode_links(episode_id,posts):
    selected=[p for p in posts if p.get('episode_id')==episode_id]
    if not selected:return ''
    return '<section class="source-note"><h2>Read from this episode</h2><ul>'+''.join(f'<li><a href="{url(p)}">{esc(p["title"])}</a> — {LABELS[p["kind"]]}</li>' for p in selected)+'</ul></section>'
