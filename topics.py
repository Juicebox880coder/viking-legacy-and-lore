"""Crawlable subject collections using existing episodes and credited reading paths."""
from html import escape as esc

TOPICS = {
    'Mythology & belief': ('norse-mythology', 'Norse Mythology', 'Explore podcast episodes about Norse gods, beliefs and mythological stories. Pair the retellings with our reading path into the surviving sources.', 'gods-and-myths', 'Read the gods through their sources'),
    'Sagas & storytelling': ('norse-sagas', 'Norse Sagas & Stories', 'Listen to saga storytelling, from legendary weapons to the people who carry them. Follow the reading path to compare stories with credited editions and manuscripts.', 'sagas-and-language', 'Explore sagas, manuscripts and language'),
    'Life & society': ('viking-daily-life', 'Viking Daily Life & Society', 'Explore episodes about Viking food, households, wealth and social life. Continue into museum collections and reading about households and power.', 'society-and-power', 'Read about households, wealth and power'),
    'Warfare & power': ('viking-warfare', 'Viking Warfare & Power', 'Browse episodes about raids, strategy, rulers and the pursuit of power. Use the linked reading path to explore the wider social setting alongside the stories.', 'society-and-power', 'Explore the evidence for wealth and power'),
    'Voyages & exploration': ('viking-voyages', 'Viking Voyages & Exploration', 'Follow episodes about ships, journeys and distant shores. Connect the listening with credited museum resources and archaeological research in our maritime reading path.', 'ships-and-horizons', 'Follow ships, routes and distant shores'),
}

def path(category):
    return '/episodes/topics/'+TOPICS[category][0]+'/' if category in TOPICS else None

def navigation():
    return '<nav class="topic-navigation" aria-label="Episode subjects"><h2>Browse episodes by subject</h2><ul>'+''.join(f'<li><a href="{path(c)}">{esc(t[1])}</a></li>' for c,t in TOPICS.items())+'</ul></nav>'

def generate(template,episodes,shell,card,episode_path,site):
    pages={}
    for category,(_,title,intro,reading,label) in TOPICS.items():
        selected=[e for e in episodes if e['category']==category]
        if not selected:continue
        url=path(category)
        body=f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/episodes/">Episodes</a> / {esc(title)}</nav><section><div class="eyebrow">Explore by subject</div><h1 class="page-title">{esc(title)} Podcast Episodes</h1><p class="section-intro">{esc(intro)}</p><p>{len(selected)} episodes · newest first · listen directly on each episode page</p><div class="grid archive-grid">'+''.join(card(e).replace('<h3>','<h2>').replace('</h3>','</h2>') for e in selected)+'</div></section>'
        body+=f'<section class="source-note"><h2>Go from listening to reading</h2><p>Podcast episodes include narrative interpretation and storytelling. The library identifies editions, sources and access information so you can investigate the subject further.</p><p><a class="text-link" href="/library/paths/{reading}/">{esc(label)} →</a></p><p><a href="/library/editorial/">How we source and credit resources</a> · <a href="/episodes/">Browse every episode</a></p></section>'+navigation()
        schema={'@context':'https://schema.org','@type':'CollectionPage','name':title+' Podcast Episodes','url':site+url,'description':intro,'mainEntity':{'@type':'ItemList','numberOfItems':len(selected),'itemListElement':[{'@type':'ListItem','position':i,'url':site+episode_path(e),'name':e['title']} for i,e in enumerate(selected,1)]}}
        pages[url.lstrip('/')+'index.html']=shell(template,title+' Podcast Episodes',intro,url,body,schema=schema)
    return pages
