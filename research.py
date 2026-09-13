"""Curated research pages. External material remains at its credited source."""
import html,json,re
from datetime import date
from urllib.parse import urlsplit,quote
esc=lambda s:html.escape(str(s),quote=True)
SLUG=r'[a-z0-9]+(?:-[a-z0-9]+)*'
def load(root,episodes):
    folder=root/'content/research'
    resources=json.loads((folder/'resources.json').read_text())
    paths=json.loads((folder/'paths.json').read_text())
    discoveries=json.loads((folder/'discoveries.json').read_text())
    known_episodes={json.loads(p.read_text())['id'] for p in (root/'content/episodes').glob('*.json')}
    published_episodes={e['id'] for e in episodes}
    for collection in (resources,paths,discoveries):
        ids=[x['id'] for x in collection]
        if len(ids)!=len(set(ids)) or any(not re.fullmatch(SLUG,i) for i in ids):raise ValueError('Duplicate or unsafe research ID')
        for item in collection:
            if set(item.get('episode_ids',[]))-known_episodes:raise ValueError('Unknown related episode')
            item['episode_ids']=[i for i in item.get('episode_ids',[]) if i in published_episodes]
    resource_ids={r['id'] for r in resources}
    for r in resources:
        for key in ('title','credit','kind','topic','level','access','summary','context','citation','language','rights','reviewed'):
            if not isinstance(r.get(key),str) or not r[key].strip():raise ValueError('Missing resource '+key)
        u=urlsplit(r['url'])
        if u.scheme!='https' or not u.netloc or u.username or u.password:raise ValueError('Resource URL must be public HTTPS')
        if r['status'] not in ('active','unavailable'):raise ValueError('Invalid resource status')
        if date.fromisoformat(r['reviewed'])>date.today():raise ValueError('Future review date')
    for p in paths:
        if len(p['resources'])!=len(p['steps']) or set(p['resources'])-resource_ids:raise ValueError('Invalid learning path')
    for d in discoveries:
        if [s['heading'] for s in d['sections']]!=['Evidence','Interpretation','What remains open']:raise ValueError('Discovery must distinguish evidence and interpretation')
        date.fromisoformat(d['reviewed'])
        for s in d['sections']:
            if not s['sources'] or set(s['sources'])-resource_ids:raise ValueError('Discovery claim lacks a valid citation')
    return resources,paths,discoveries

def resource_card(r,episodes,episode_path):
    report='mailto:vikinglegacyandlore@gmail.com?subject='+quote('Resource correction: '+r['title'])
    by_id={e['id']:e for e in episodes}
    related=''.join(f'<li><a href="{episode_path(by_id[i])}">{esc(by_id[i]["title"])}</a></li>' for i in r['episode_ids'])
    action=f'<a class="text-link" href="{esc(r["url"])}">Visit credited source ↗</a>' if r['status']=='active' else '<p class="note">Source link is under review.</p>'
    attrs=' '.join(f'data-{key}="{esc(r[key])}"' for key in ('kind','topic','level','access'))
    return f'''<article class="resource-card" id="resource-{r['id']}" data-research-item {attrs}><div class="meta">{esc(r['kind'])} · {esc(r['topic'])}</div><h3>{esc(r['title'])}</h3><p class="resource-credit">{esc(r['credit'])}</p><p>{esc(r['summary'])}</p><p class="resource-context"><strong>Read with context:</strong> {esc(r['context'])}</p><div class="resource-tags"><span>{esc(r['level'])}</span><span>{esc(r['access'])}</span></div>{action}<details><summary>Citation, access &amp; related listening</summary><p class="citation">{esc(r['citation'])}</p><p>Language: {esc(r['language'])}. Reviewed <time datetime="{r['reviewed']}">{r['reviewed']}</time>.</p><p>{esc(r['rights'])}</p>{'<p>Related listening — selected for its topic, not presented as a source citation:</p><ul>'+related+'</ul>' if related else ''}<a href="{report}">Report a broken link or suggest a correction</a></details></article>'''

def filters(items,fields,label):
    html=f'<form class="research-filters" role="search" aria-label="{label}" hidden><div class="research-search"><label for="research-q">Search {label.lower()}</label><input id="research-q" name="q" type="search" placeholder="Try mythology, ships, runes…"></div>'
    for key,title in fields:
        html+=f'<div><label for="research-{key}">{title}</label><select id="research-{key}" name="{key}"><option value="">All</option>'+''.join(f'<option>{esc(v)}</option>' for v in sorted({r[key] for r in items}))+'</select></div>'
    return html+'<button class="button button-secondary" type="reset">Clear filters</button></form><p class="research-count" role="status" aria-live="polite">'+str(len(items))+' entries</p><p class="research-empty" hidden>No entries match. Try fewer filters or clear your search.</p>'

def local_header(title,intro,eyebrow='Norse Library'):
    parent,label=('/archaeology/','Archaeology') if eyebrow.startswith('Archaeology') else ('/library/','Library')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="{parent}">{label}</a></nav><section class="research-heading"><div class="eyebrow">{eyebrow}</div><h1 class="page-title">{esc(title)}</h1><p class="section-intro">{esc(intro)}</p></section>'

def related(eid,resources):
    matches=[r for r in resources if eid in r['episode_ids']]
    if not matches:return ''
    return '<section class="source-note"><h2>Explore the related research</h2><p>Selected for a shared subject. These links are not a claim that the episode used or cited these works.</p><ul>'+''.join(f'<li><a href="/library/#resource-{r["id"]}">{esc(r["title"])}</a> — {esc(r["credit"])}</li>' for r in matches)+'</ul></section>'

def generate(root,template,episodes,shell,episode_card,episode_path,data):
    resources,paths,discoveries=data;by_id={r['id']:r for r in resources};eps={e['id']:e for e in episodes};pages={}
    def wrap(title,description,url,body,kind='CollectionPage'):
        schema={'@context':'https://schema.org','@type':kind,'name':title,'url':'https://vikinglegacyandlore.com'+url}
        return shell(template,title,description,url,body,schema=schema).replace('</body>','<script src="/research.js" defer></script></body>')
    body=local_header('A world of knowledge. A place to begin.','Explore Viking history and Norse mythology through carefully chosen texts, books, museums and research. Follow a guided path or find the source for your next question.')
    body+='<nav class="research-nav" aria-label="Research sections"><a href="#learning-paths">Choose a learning path</a><a href="#catalogue">Browse all resources</a><a href="/archaeology/">Archaeology case studies</a><a href="/library/editorial/">How we curate &amp; credit</a></nav>'
    body+='<section id="learning-paths"><div class="eyebrow">Build your understanding</div><h2>Six ways into the Norse world</h2><p class="section-intro">Start broadly, compare sources, then follow the questions that interest you. Each route gives you a reading order and a question to carry forward.</p><div class="learning-grid">'
    for i,p in enumerate(paths,1):body+=f'<article class="learning-card"><span class="number" aria-hidden="true">0{i}</span><h3><a href="/library/paths/{p["id"]}/">{esc(p["title"])}</a></h3><p>{esc(p["intro"])}</p><span class="meta">{len(p["resources"])} selected resources</span></article>'
    body+='</div></section><section id="catalogue" data-research-index><div class="eyebrow">The curated shelves</div><h2>Find your next source</h2><p class="section-intro">Every entry names its creator or institution. Free online describes reading access, not permission to reuse a work. The collection is selective and grows as sources are reviewed.</p>'+filters(resources,[('topic','Topic'),('kind','Source type'),('level','Reading level'),('access','Access')],'Resources')+'<div class="resource-grid">'
    body+=''.join(resource_card(r,episodes,episode_path) for r in resources)+'</div></section>'
    body+='<section class="source-note"><h2>Follow the evidence further</h2><p>A strong understanding grows through comparison, not a promise of complete certainty. Explore the discovery case studies, or read how this collection distinguishes source material from our annotations.</p><a class="text-link" href="/archaeology/">Explore archaeology →</a> · <a class="text-link" href="/library/editorial/">Our source and credit standards →</a></section>'
    pages['library/index.html']=wrap('Norse Library','A curated Viking and Norse mythology library: primary texts, credited translations, books, museums and research, with guided reading paths.','/library/',body)
    for p in paths:
        body=local_header(p['title'],p['intro'],'A guided learning path')+'<ol class="reading-path">'
        for id,instruction in zip(p['resources'],p['steps']):
            r=by_id[id]
            action=f'<a class="text-link" href="{esc(r["url"])}">Read at the credited source ↗</a>' if r['status']=='active' else '<p class="note">Source link is under review.</p>'
            body+=f'<li><h2><a href="/library/#resource-{id}">{esc(r["title"])}</a></h2><p class="resource-credit">{esc(r["credit"])} · {esc(r["access"])}</p><p>{esc(instruction)}</p>{action}</li>'
        body+='</ol><section class="reading-question"><h2>A question to carry forward</h2><p>'+esc(p['question'])+'</p></section><section><h2>Related listening</h2><p>Selected by subject; these episodes are not substitutes for the linked works.</p><div class="grid">'+''.join(episode_card(eps[e]) for e in p['episode_ids'])+'</div></section><a class="text-link" href="/library/#learning-paths">Choose another path →</a>'
        pages['library/paths/'+p['id']+'/index.html']=wrap(p['title'],p['intro'],'/library/paths/'+p['id']+'/',body)
    body=local_header('What the ground can tell us.','Read discoveries through their evidence, methods and open questions. These are selected research case studies, not a breaking-news feed.','Archaeology')+'<nav class="research-nav" aria-label="Research sections"><a href="/library/">Norse Library</a><a href="/library/paths/reading-archaeology/">Learn to read a discovery</a><a href="/library/editorial/">Source standards</a></nav><section data-research-index><h2>Evidence &amp; interpretation</h2>'+filters(discoveries,[('method','Method')],'Discoveries')+'<div class="resource-grid">'
    for d in discoveries:body+=f'<article class="resource-card" data-research-item data-method="{esc(d["method"])}"><div class="meta">{esc(d["place"])} · {esc(d["method"])}</div><h3><a href="/archaeology/{d["id"]}/">{esc(d["title"])}</a></h3><p>{esc(d["intro"])}</p><p class="note">{esc(d["milestone"])}</p><a class="text-link" href="/archaeology/{d["id"]}/">Read the evidence →</a></article>'
    body+='</div></section>'
    pages['archaeology/index.html']=wrap('Archaeology','Sourced Viking archaeology case studies separating observations, interpretation and remaining questions.','/archaeology/',body)
    for d in discoveries:
        body=local_header(d['title'],d['intro'],'Archaeology case study')+f'<p class="meta">{esc(d["place"])} · {esc(d["period"])}</p><p class="note">{esc(d["milestone"])} · Sources reviewed {d["reviewed"]}</p><div class="evidence-sections">'
        ids=[]
        for section in d['sections']:
            refs=[]
            for id in section['sources']:
                if id not in ids:ids.append(id)
                refs.append(f'<a href="#source-{id}" aria-label="Source {ids.index(id)+1}: {esc(by_id[id]["title"])}">[{ids.index(id)+1}]</a>')
            body+=f'<section><h2>{esc(section["heading"])}</h2><p>{esc(section["text"])} <span class="claim-citations">'+ ' '.join(refs)+'</span></p></section>'
        body+='</div><section class="source-note"><h2>Sources &amp; credits</h2><p>Original summary by Viking Legacy &amp; Lore. Research and discoveries credited below; no institutional affiliation or endorsement is implied.</p><ol class="source-list">'
        for id in ids:
            r=by_id[id];body+=f'<li id="source-{id}"><a href="{esc(r["url"])}">{esc(r["citation"])}</a><p>{esc(r["access"])} · {esc(r["credit"])}</p><a class="text-link" href="/library/#resource-{id}">View reading context and rights note →</a></li>'
        body+='</ol></section><section><h2>Related listening</h2><p>Connected by topic, not presented as independent verification of the findings.</p><div class="grid">'+''.join(episode_card(eps[e]) for e in d['episode_ids'])+'</div></section><a class="text-link" href="/archaeology/">More archaeology case studies →</a>'
        pages['archaeology/'+d['id']+'/index.html']=wrap(d['title'],d['intro'],'/archaeology/'+d['id']+'/',body,'WebPage')
    body=local_header('Know where the knowledge comes from.','A useful library makes its sources visible. Here is how we select, describe and credit the works linked from Viking Legacy & Lore.','Our editorial standards')
    body+='<div class="editorial-sections"><section><h2>Selection, not a claim to completeness</h2><div><p>We prioritize museums, universities, heritage bodies, scholarly publishers and identifiable researchers. The collection offers routes into a broad subject; it does not claim to settle every question or contain every worthwhile work.</p><p>We look for a clear creator, relevant subject matter, a traceable publication and a stable, legitimate destination. A link is a reading recommendation, not institutional endorsement of this website.</p></div></section><section><h2>Keep different kinds of evidence distinct</h2><div><p>Primary text / translation identifies a historical text presented in a modern edition. Museum guide identifies a modern explanation. Research paper identifies the linked publication, not a claim that our own summary has been peer reviewed.</p><p>For archaeology, we separate the reported observations from interpretation and unresolved questions. A discovery date, the date of an ancient object and a paper’s publication date are recorded as different things.</p></div></section><section><h2>Credit is not a reuse licence</h2><div><p>Our descriptions are original editorial annotations. Full texts, photographs, scans and databases remain at their credited sources. We do not mirror them or embed them as if they belonged to Viking Legacy &amp; Lore.</p><p>Free reading access does not necessarily permit copying. A medieval work and its modern translation, introduction or photograph can have different rights. Before reproducing material, check the specific licence or obtain permission; attribution alone is not permission. <a href="https://www.copyright.gov/circs/m10.pdf">U.S. Copyright Office: obtaining permission</a>.</p></div></section><section><h2>Cite the work you actually used</h2><div><p>Record the author or institution, work title, editor or translator, edition and publication date, page or passage, and URL or DOI. For a changing online record, add the date you consulted it. An inscription identifier or museum accession number helps readers find the same evidence.</p><p>Use each resource’s citation as a starting point. If quoting a translated passage, credit its individual translator and your edition’s page number. If using our archaeology summary, cite that page as a summary and consult its linked research before making the underlying claim yourself.</p></div></section><section><h2>Access, independence and corrections</h2><div><p>Free online refers to the linked reading material, not museum admission. Book / library access directs you to a publisher record: look for a lawful library copy or purchase option. These resource links contain no affiliate codes.</p><p>Related episodes are selected by subject, not represented as having cited those works. Our original reading guides connect selected research with related listening; explore them in the <a href="/articles/">article collection</a>.</p><p>Review dates describe our source check, not continuous monitoring. We check links separately from reviewing their meaning, and reconsider entries when sources change. To report a broken link, miscredit or substantive concern, <a href="/contact/">contact the show</a> with the resource title and correction.</p></div></section></div>'
    pages['library/editorial/index.html']=wrap('Source and credit standards','How Viking Legacy & Lore selects sources, credits creators, distinguishes evidence and interpretation, and handles rights and corrections.','/library/editorial/',body,'WebPage')
    return pages
