"""Offline publishing checks: run python3 -m unittest -v test_site.py."""
import unittest,json,tempfile,shutil,re
import xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import build
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.h1=0
    def handle_starttag(self,t,a):
        a=dict(a)
        if 'id' in a:self.ids.add(a['id'])
        if t=='h1':self.h1+=1
        for k in ('href','src'):
            if k in a:self.links.append(a[k])
class SiteTests(unittest.TestCase):
    def test_generated_links_and_headings(self):
        for f in build.PUBLIC.rglob('*.html'):
            p=Links();p.feed(f.read_text());self.assertEqual(p.h1,1,str(f))
            for link in p.links:
                u=urlsplit(link)
                if u.scheme or u.netloc:continue
                target=build.PUBLIC/unquote(u.path).lstrip('/') if u.path else f
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),f'{f}: {link}')
                if u.fragment:
                    other=Links();other.feed(target.read_text());self.assertIn(u.fragment,other.ids)
    def test_build_is_reproducible(self):
        before={p:p.read_bytes() for p in build.PUBLIC.rglob('*') if p.is_file()};build.build()
        self.assertEqual(before,{p:p.read_bytes() for p in build.PUBLIC.rglob('*') if p.is_file()})
    def test_invalid_content_fails(self):
        original=build.ROOT
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'content/episodes').mkdir(parents=True)
            source=next((original/'content/episodes').glob('*.json'));e=json.loads(source.read_text());e['slug']='../escape'
            (root/'content/episodes/bad.json').write_text(json.dumps(e));build.ROOT=root
            try:
                with self.assertRaises(ValueError):build.load_episodes()
            finally:build.ROOT=original
    def test_unpublish_removes_generated_page_and_sitemap_entry(self):
        original,public=build.ROOT,build.PUBLIC
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ('content','public'):shutil.copytree(original/name,root/name)
            for name in ('homepage.json','homepage.template.html','.generated-pages.json'):shutil.copy(original/name,root/name)
            p=root/'content/episodes/17269686.json';e=json.loads(p.read_text());e['draft']=True;p.write_text(json.dumps(e));build.ROOT=root;build.PUBLIC=root/'public'
            try:
                build.build();self.assertFalse((build.PUBLIC/build.path(e).lstrip('/')/'index.html').exists())
                self.assertNotIn(build.path(e),(build.PUBLIC/'sitemap.xml').read_text())
            finally:build.ROOT=original;build.PUBLIC=public
    def test_research_rejects_missing_citations_and_unsafe_links(self):
        import research
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);shutil.copytree(build.ROOT/'content',root/'content')
            path=root/'content/research/discoveries.json';original=path.read_text()
            data=json.loads(original);data[0]['sections'][0]['sources']=['missing-source'];path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'citation'):research.load(root,build.load_episodes())
            path.write_text(original)
            path=root/'content/research/resources.json';data=json.loads(path.read_text());data[0]['url']='javascript:alert(1)';path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'HTTPS'):research.load(root,build.load_episodes())
    def test_articles_have_citations_and_article_metadata(self):
        for file in (build.PUBLIC/'articles').glob('*/index.html'):
            content=file.read_text()
            schema=next(json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',content,re.S) if json.loads(x).get('@type')=='Article')
            self.assertIn('datePublished',schema);self.assertIn('author',schema)
            self.assertIn('Sources &amp; further reading',content)
            self.assertIn('href="#source-',content)
            self.assertIn('href="/start/"',content)
    def test_editorial_collections_have_context_credit_and_links(self):
        import editorial
        posts=editorial.load(build.ROOT,build.load_episodes())
        for kind in ('blog','stories'):
            self.assertGreaterEqual(len([p for p in posts if p['kind']==kind]),10)
        for p in posts:
            text=(build.PUBLIC/editorial.url(p).lstrip('/')/'index.html').read_text()
            self.assertIn('About this excerpt',text)
            self.assertNotIn('docs.google.com',text)
            self.assertIn('By T.R. Pomeroy',text)
            if p['kind']=='blog':self.assertIn('Historical context &amp; sources',text)
            else:self.assertIn('aria-label="About this story"',text)
            if p.get('episode_id'):
                e=next(e for e in build.load_episodes() if e['id']==p['episode_id'])
                self.assertIn(build.path(e),text)
                self.assertIn(editorial.url(p),(build.PUBLIC/build.path(e).lstrip('/')/'index.html').read_text())

    def test_editorial_rejects_broken_references(self):
        import editorial
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);shutil.copytree(build.ROOT/'content',root/'content')
            p=next((root/'content/blog').glob('*.json'));data=json.loads(p.read_text())
            data['sources'][0]['url']='javascript:alert(1)';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'HTTPS'):editorial.load(root,build.load_episodes())

    def test_plain_text_is_escaped(self):
        e=build.load_episodes()[0].copy();e['title']='<script>alert(1)</script>'
        self.assertNotIn('<script>',build.card(e));self.assertIn('&lt;script&gt;',build.card(e))
    def test_metadata_and_sitemap_cover_every_public_page(self):
        canonicals=set();titles=set()
        for file in build.PUBLIC.rglob('*.html'):
            content=file.read_text()
            if file.name=='404.html':
                self.assertIn('name="robots" content="noindex"',content);continue
            canonical=re.search(r'<link rel="canonical" href="([^"]+)"',content).group(1)
            self.assertNotIn(canonical,canonicals);canonicals.add(canonical)
            title=re.search(r'<title>(.*?)</title>',content).group(1)
            self.assertNotIn(title,titles);titles.add(title)
            schemas=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',content,re.S)]
            self.assertTrue(schemas,str(file))
            self.assertTrue(any('@graph' in s for s in schemas),str(file))
            if '/episodes/' in canonical and '/episodes/topics/' not in canonical and not canonical.endswith('/episodes/'):
                episode=next(s for s in schemas if s.get('@type')=='PodcastEpisode')
                self.assertEqual(episode['url'],canonical)
                self.assertRegex(episode['duration'],r'^PT\d+S$')
        xml=ET.parse(build.PUBLIC/'sitemap.xml')
        urls={e.text for e in xml.findall('.//{*}loc')}
        self.assertEqual(canonicals,urls)
    def test_topic_collections_are_linked_and_match_their_episodes(self):
        import topics
        episodes=build.load_episodes()
        archive=(build.PUBLIC/'episodes/index.html').read_text()
        for category in topics.TOPICS:
            url=topics.path(category)
            self.assertIn('href="'+url+'"',archive)
            content=(build.PUBLIC/url.lstrip('/')/'index.html').read_text()
            schema=next(json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',content,re.S) if json.loads(s).get('@type')=='CollectionPage')
            expected={build.SITE+build.path(e) for e in episodes if e['category']==category}
            self.assertEqual({x['url'] for x in schema['mainEntity']['itemListElement']},expected)
            self.assertEqual(schema['mainEntity']['numberOfItems'],len(expected))
            for e in episodes:
                if e['category']==category:
                    page=(build.PUBLIC/build.path(e).lstrip('/')/'index.html').read_text()
                    self.assertIn('href="'+url+'"',page)

    def test_media_does_not_connect_until_requested(self):
        for file in build.PUBLIC.rglob('*.html'):
            content=file.read_text()
            self.assertNotIn('<iframe',content,str(file))
            self.assertEqual(content.count('src="/episodes.js"'),1,str(file))
            if '<audio' in content:
                self.assertIn('preload="none"',content)
                self.assertIn('Listen on the podcast host',content)
if __name__=='__main__':unittest.main()
