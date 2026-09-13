"""Offline publishing checks: run python3 -m unittest -v test_site.py."""
import unittest,json,tempfile,shutil
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
            p=root/'content/episodes/16833140.json';e=json.loads(p.read_text());e['draft']=True;p.write_text(json.dumps(e));build.ROOT=root;build.PUBLIC=root/'public'
            try:
                build.build();self.assertFalse((build.PUBLIC/build.path(e).lstrip('/')/'index.html').exists())
                self.assertNotIn(build.path(e),(build.PUBLIC/'sitemap.xml').read_text())
            finally:build.ROOT=original;build.PUBLIC=public
    def test_plain_text_is_escaped(self):
        e=build.load_episodes()[0].copy();e['title']='<script>alert(1)</script>'
        self.assertNotIn('<script>',build.card(e));self.assertIn('&lt;script&gt;',build.card(e))
if __name__=='__main__':unittest.main()
