"""Entry points and original, cited editorial articles."""
import json,re
from datetime import date
from research import esc,SLUG,local_header

def generate(root,template,episodes,shell,card,episode_path,resources):
    eps={e['id']:e for e in episodes};refs={r['id']:r for r in resources};pages={}
    def wrap(title,description,url,body,schema_type='CollectionPage',extra=None):
        schema={'@context':'https://schema.org','@type':schema_type,'name':title,'url':'https://vikinglegacyandlore.com'+url}
        schema.update(extra or {})
        return shell(template,title,description,url,body,schema=schema)
    picks=[('17503297','History','Start with the episode about the beginning of the Viking Age.'),('17269686','Mythology','Meet the mythological world before following individual gods and stories.'),('17149679','Ships & travel','Explore the longship episode, then follow our maritime reading path.'),('17850122','Voyages','Listen to the Vinland story, then compare it with the archaeological evidence.'),('17054359','Saga','Enter the world of Grettir. Read this as saga storytelling, with its own relationship to history.')]
    body=local_header('Your first journey into the Viking world.','New to Viking Legacy & Lore? Choose a subject you love, or work through these five starting points. You can listen directly on each episode page.','Start listening')+'<div class="learning-grid">'
    for number,(id,label,note) in enumerate(picks,1):
        e=eps.get('Buzzsprout-'+id)
        if e:body+=f'<article class="learning-card"><div class="eyebrow">{number:02} · {esc(label)}</div><h2><a href="{episode_path(e)}">{esc(e["title"])}</a></h2><p>{esc(note)}</p><a class="text-link" href="{episode_path(e)}#listen">Listen to this episode →</a></article>'
    body+='</div><section class="source-note"><h2>Find your next path</h2><p>For historical context, start with First Steps. For the gods and their surviving sources, choose the mythology path. For saga reading, explore the texts and language route. Each links to credited sources.</p><div class="buttons"><a class="button button-secondary" href="/library/paths/first-steps/">Viking history</a><a class="button button-secondary" href="/library/paths/gods-and-myths/">Norse mythology</a><a class="button button-secondary" href="/library/paths/sagas-and-language/">Sagas &amp; language</a></div></section><section><h2>Keep the stories close</h2><p>Follow the show in your preferred app to find future releases. Know someone who loves these subjects? Share this guide and let them choose their first journey.</p><div class="buttons"><a class="button button-primary" href="https://podcasts.apple.com/podcast/id1803707614">Apple Podcasts</a><a class="button button-secondary" href="https://open.spotify.com/show/7ocooMGKkr9oTVeggU237S">Spotify</a><a class="button button-secondary" href="https://www.youtube.com/playlist?list=PLlScZ6Itayse--imjcPAr8coOn-QSjbQm">YouTube podcast</a></div></section>'
    body=body.replace('<a href="/library/">Library</a></nav>', 'Start Here</nav>',1)
    pages['start/index.html']=wrap('Start Here: Viking History & Norse Mythology Podcast','Five starting episodes for Viking Legacy & Lore, with guided routes into history, Norse mythology, voyages and sagas.','/start/',body)
    articles=[]
    for file in sorted((root/'content/articles').glob('*.json')):
        a=json.loads(file.read_text())
        if not re.fullmatch(SLUG,a['slug']):raise ValueError('Unsafe article slug')
        if date.fromisoformat(a['published'])>date.today():raise ValueError('Future article publication date')
        if a.get('draft'):continue
        articles.append(a);url='/articles/'+a['slug']+'/'
        body=f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/articles/">Articles</a></nav><article class="reading-article"><header><div class="eyebrow">A reader’s guide</div><h1 class="page-title">{esc(a["title"])}</h1><p class="meta">By {esc(a["author"])} · <time datetime="{a["published"]}">{a["published"]}</time></p><p class="section-intro">{esc(a["intro"])}</p></header>'
        used=[]
        for section in a['sections']:
            cites=[]
            for id in section['sources']:
                if id not in refs:raise ValueError('Article citation missing')
                if id not in used:used.append(id)
                cites.append(f'<a href="#source-{id}" aria-label="Source {used.index(id)+1}">[{used.index(id)+1}]</a>')
            body+='<section><h2>'+esc(section['heading'])+'</h2><p>'+esc(section['text'])+' <span class="claim-citations">'+' '.join(cites)+'</span></p></section>'
        body+='<section class="source-note"><h2>Sources &amp; further reading</h2><p>Original editorial guide by Viking Legacy &amp; Lore. Linked works remain credited to their creators; no affiliation or endorsement is implied. Sources consulted '+a['published']+'.</p><ol class="source-list">'
        for id in used:
            r=refs[id];body+=f'<li id="source-{id}"><a href="{esc(r["url"])}">{esc(r["citation"])}</a><p><a href="/library/#resource-{id}">Edition, access and rights notes →</a></p></li>'
        body+='</ol><a class="text-link" href="/library/editorial/">How we source and credit →</a></section></article><section><h2>Listen further</h2><p>Related by subject; the episodes are not presented as sources for this article.</p><div class="grid">'+''.join(card(eps[id]) for id in a['episode_ids'] if id in eps)+'</div><div class="support-actions buttons"><a class="button button-secondary" href="/library/paths/'+a['path']+'/">Follow the reading path</a><a class="button button-secondary" href="/start/">New to the podcast? Start here</a></div></section>'
        pages['articles/'+a['slug']+'/index.html']=wrap(a['title'],a['description'],url,body,'Article',{'headline':a['title'],'datePublished':a['published'],'author':{'@type':'Organization','name':a['author']},'mainEntityOfPage':'https://vikinglegacyandlore.com'+url})
    body='<div class="eyebrow">Articles</div><h1 class="page-title">Follow the story. Find the source.</h1><p class="section-intro">Original reading guides to Viking history and Norse mythology, with visible citations and a route into the podcast.</p><div class="resource-grid">'
    for a in articles:body+=f'<article class="resource-card"><h2><a href="/articles/{a["slug"]}/">{esc(a["title"])}</a></h2><p>{esc(a["intro"])}</p><a class="text-link" href="/articles/{a["slug"]}/">Read the guide →</a></article>'
    body+='</div><div class="support-actions buttons"><a class="button button-secondary" href="/start/">Start listening</a><a class="button button-secondary" href="/library/">Explore the Norse Library</a></div>'
    pages['articles/index.html']=wrap('Articles','Original, cited guides to Viking history and Norse mythology with related podcast episodes and reading paths.','/articles/',body)
    return pages
