"""Update only enriched hub sitemap entries and publish their RSS feed."""
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import unquote, quote, urlsplit
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://xn--ru4bz7e9zf0zk.com'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--modified', required=True)
    args = parser.parse_args()
    modified = datetime.fromisoformat(args.modified)
    assert modified.tzinfo is not None
    records = json.loads((ROOT/'tools/reports/hub-enrichment/generation.json').read_text(encoding='utf-8'))['targets']
    by_url = {}
    for record in records:
        soup = BeautifulSoup((ROOT/record['path']).read_text(encoding='utf-8'),'html.parser')
        url = soup.select_one('[rel=canonical]')['href']
        by_url[unquote(url)] = {'url':DOMAIN+quote(unquote(urlsplit(url).path),safe='/'), 'title':soup.title.get_text(), 'description':soup.select_one('meta[name=description]')['content']}
    sitemap = (ROOT/'sitemap.xml').read_text(encoding='utf-8')
    inventory = [x.text for x in ET.fromstring(sitemap).findall('{*}url/{*}loc')]
    count = 0
    def update_block(match):
        nonlocal count
        block = match.group(0)
        url = html.unescape(re.search(r'<loc>(.*?)</loc>',block).group(1))
        if unquote(url) not in by_url: return block
        count += 1
        lastmod = '<lastmod>'+modified.date().isoformat()+'</lastmod>'
        return re.sub(r'<lastmod>.*?</lastmod>',lastmod,block) if '<lastmod>' in block else block.replace('</loc>','</loc>'+lastmod,1)
    updated = re.sub(r'<url>.*?</url>',update_block,sitemap,flags=re.S)
    assert count == len(by_url)
    assert inventory == [x.text for x in ET.fromstring(updated).findall('{*}url/{*}loc')]
    (ROOT/'sitemap.xml').write_text(updated,encoding='utf-8',newline='\n')
    rss = ET.Element('rss',{'version':'2.0'})
    channel = ET.SubElement(rss,'channel')
    for name,value in [('title','채움학습 학년·과목별 학습 안내'),('link',DOMAIN+'/'),('description','채움학습의 학년·과목별 허브 안내와 지역 학습 정보'),('language','ko'),('lastBuildDate',format_datetime(modified))]:
        ET.SubElement(channel,name).text = value
    for record in by_url.values():
        item = ET.SubElement(channel,'item')
        for name,value in [('title',record['title']),('link',record['url']),('description',record['description']),('pubDate',format_datetime(modified))]:
            ET.SubElement(item,name).text = value
        ET.SubElement(item,'guid',{'isPermaLink':'true'}).text = record['url']
    ET.indent(rss,space='  ')
    output = ET.tostring(rss,encoding='unicode',xml_declaration=True)
    (ROOT/'rss.xml').write_text(output,encoding='utf-8',newline='\n')
    assert len(ET.fromstring(output).findall('./channel/item')) == len(by_url)
    print(json.dumps({'sitemap_total':len(inventory),'updated_hubs':count,'rss_items':len(by_url)}))

if __name__ == '__main__': main()
