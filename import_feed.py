"""Import a downloaded RSS feed. Existing editorial fields and slugs are preserved."""
import argparse, html, json, re, unicodedata
from pathlib import Path
from html.parser import HTMLParser
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
IT = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'
class Notes(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.current=''
    def flush(self):
        text = re.sub(r'\s+', ' ', html.unescape(self.current)).strip()
        if text: self.parts.append(text)
        self.current=''
    def handle_starttag(self,tag,attrs):
        if tag in ('p','br','li','h2','h3','div'):self.flush()
    def handle_endtag(self,tag):
        if tag in ('p','li','h2','h3','div'):self.flush()
    def handle_data(self,data): self.current+=data

def ingest(path):
    folder=ROOT/'content/episodes';folder.mkdir(parents=True,exist_ok=True)
    for item in ET.parse(path).findall('./channel/item'):
        ident=item.findtext('guid'); number=ident.removeprefix('Buzzsprout-')
        target=folder/(number+'.json')
        if target.exists(): continue # Never overwrite curated content on re-import.
        title=item.findtext('title');audio=item.find('enclosure').get('url')
        slug=audio.rsplit('/',1)[-1].removesuffix('.mp3')
        parser=Notes();parser.feed(item.findtext('description',''));parser.flush()
        notes=[]
        for p in parser.parts:
            if p.startswith('Support the show'):break
            if p not in ('Send us Fan Mail','Send us a text'):notes.append(p)
        if not notes:notes=[title]
        episode={'id':ident,'slug':slug,'title':title,'published':parsedate_to_datetime(item.findtext('pubDate')).isoformat(),
          'duration':int(item.findtext(IT+'duration','0')),'type':item.findtext(IT+'episodeType','full'),
          'category':'Viking history','summary':notes[0],'notes':notes,'image':'/cover.jpg',
          'audio_url':audio,'spotify_id':None,'youtube_id':None,'sources':[],
          'publication_url':audio.removesuffix('.mp3'),'feed_url':'https://feeds.buzzsprout.com/2459523.rss','draft':False}
        target.write_text(json.dumps(episode,indent=2,ensure_ascii=False)+'\n')
    print('Imported new entries; existing content preserved.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('feed',type=Path);ingest(p.parse_args().feed)
