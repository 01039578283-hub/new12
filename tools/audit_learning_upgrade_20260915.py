"""Independent, read-only production audit for the 2026-09-15 learning upgrade.

Only this script's ignored report directory is written.  Run snapshot before
integration, then audit after generation.  This is not a deployment command.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
LIB = Path('C:/Users/1992k/Desktop/CodexData/tmp/site15-branches-2026-09-09/qa-libs')
sys.path.insert(0, str(LIB))
from bs4 import BeautifulSoup

REPORT = ROOT / 'tools/reports/learning-upgrade/independent-qa'
BASE = REPORT / 'baseline.json'
ZIP = REPORT / 'target-baseline.zip'
DOMAIN = 'https://xn--ru4bz7e9zf0zk.com'
COMMIT = 'f2ae2251f532f938eae05de8160a5910bab77561'
CORE = ['index.html', '학습가이드/index.html', '상담문의/index.html']
NEW = '학습코칭/index.html'
HUBS = list(json.loads((ROOT/'tools/data/hub-guides/subject-copy.json').read_text(encoding='utf-8')))
TARGETS = CORE + HUBS + [NEW]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def soup(value):
    return BeautifulSoup(value, 'html.parser')


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def public_url(rel):
    return DOMAIN + '/' + (rel[:-10] if rel.endswith('index.html') else rel)


def nodes(document):
    out = []
    for script in document.select('script[type="application/ld+json"]'):
        value = json.loads(script.string or script.get_text())
        for item in value if isinstance(value, list) else [value]:
            out.extend(item.get('@graph', [item]))
    return out


def typed(node, name):
    value = node.get('@type', [])
    return name in ([value] if isinstance(value, str) else value)


def xml_urls(value, rss=False):
    root = ET.fromstring(value)
    return [e.text for e in root.findall('./channel/item/link')] if rss else [e.text for e in root.findall('{*}url/{*}loc')]


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.autocrlf=false', *args], cwd=ROOT)


def snapshot():
    if BASE.exists() or ZIP.exists():
        raise SystemExit('Existing baseline is protected; do not overwrite it.')
    head = git('rev-parse', 'HEAD').decode().strip()
    if head != COMMIT:
        raise SystemExit(f'Unexpected starting commit: {head}')
    paths = [p.decode('utf-8') for p in git('ls-files', '-z').split(b'\0') if p]
    selected = [p for p in paths if p.endswith('.html') or p.startswith('assets/') or p in ['sitemap.xml', 'rss.xml', 'robots.txt', 'llms.txt', 'vercel.json', '.vercelignore']]
    hashes = {p: digest((ROOT/p).read_bytes()) for p in selected}
    REPORT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in CORE+HUBS+['sitemap.xml', 'rss.xml']:
            archive.write(ROOT/rel, rel)
    result = {
        'commit': head, 'hashes': hashes, 'targets': TARGETS, 'hubs': HUBS,
        'html_count': sum(p.endswith('.html') for p in hashes),
        'assets_count': sum(p.startswith('assets/') for p in hashes),
        'sitemap_urls': xml_urls((ROOT/'sitemap.xml').read_bytes()),
        'rss_urls': xml_urls((ROOT/'rss.xml').read_bytes(), rss=True),
    }
    BASE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in {'hashes','sitemap_urls','rss_urls'}}, ensure_ascii=False))


def audit():
    base = json.loads(BASE.read_text(encoding='utf-8'))
    errors, checks, warnings, counts = [], [], [], Counter()

    def check(ok, label, detail=None):
        checks.append(label)
        if not ok:
            errors.append({'check': label, 'detail': detail})

    @lru_cache(maxsize=None)
    def load(rel):
        return soup((ROOT/rel).read_text(encoding='utf-8-sig'))

    def local_target(rel, href):
        absolute = urlsplit(urljoin(public_url(rel), href))
        if absolute.scheme not in {'http', 'https'} or absolute.netloc not in {urlsplit(DOMAIN).netloc, '채움학습.com'}:
            return None
        path = unquote(absolute.path).lstrip('/')
        if not path or path.endswith('/'):
            path += 'index.html'
        elif not Path(path).suffix and (ROOT/path).is_dir():
            path += '/index.html'
        return path, unquote(absolute.fragment)

    for rel, before in base['hashes'].items():
        if rel.endswith('.html') and rel not in TARGETS:
            check((ROOT/rel).exists() and digest((ROOT/rel).read_bytes()) == before, 'untouched_html:'+rel)
            counts['untouched_html'] += 1
        if rel.startswith('assets/'):
            check((ROOT/rel).exists() and digest((ROOT/rel).read_bytes()) == before, 'existing_asset:'+rel)
            counts['preserved_assets'] += 1
        if rel in ['robots.txt', 'vercel.json', '.vercelignore']:
            check(digest((ROOT/rel).read_bytes()) == before, 'host_config:'+rel)

    current_html = {p.relative_to(ROOT).as_posix() for p in ROOT.glob('**/*.html')
                    if not any(part in {'tools','.git','.vercel','node_modules'} for part in p.relative_to(ROOT).parts)}
    expected_html = {p for p in base['hashes'] if p.endswith('.html')} | {NEW}
    check(current_html == expected_html, 'public_html_scope_exact', {'extra':sorted(current_html-expected_html),'missing':sorted(expected_html-current_html)})
    counts['total_public_html'] = len(current_html)

    with zipfile.ZipFile(ZIP) as archive:
        for rel in HUBS:
            old = soup(archive.read(rel).decode('utf-8-sig'))
            now = load(rel)
            for name, selector, attr in [('title','title',None),('h1','h1',None),('canonical','link[rel="canonical"]','href'),('og:url','meta[property="og:url"]','content')]:
                a, b = old.select_one(selector), now.select_one(selector)
                a = a.get(attr) if attr else a.get_text()
                b = b.get(attr) if attr and b else b.get_text() if b else None
                check(a == b, f'hub_preserved_{name}:{rel}', [a,b])
            # Existing directory, reviewed center details, paragraphs, FAQ and
            # contact fragments stay intact. Only the newly added brief is removed.
            new_main = soup(str(now.main))
            for addition in new_main.select('#coaching-brief'):
                addition.decompose()
            check(normalize(old.main.get_text(' ', strip=True)) == normalize(new_main.get_text(' ', strip=True)), 'hub_original_main_text:'+rel)
            old_ids = {x['id'] for x in old.main.select('[id]')}
            check(old_ids <= {x['id'] for x in now.main.select('[id]')}, 'hub_original_anchors:'+rel)
            old_links = Counter(x['href'] for x in old.main.select('a[href]'))
            new_links = Counter(x['href'] for x in now.main.select('a[href]'))
            check(not (old_links-new_links), 'hub_original_links:'+rel, list((old_links-new_links).elements())[:10])
            old_scripts = [normalize(x.get_text()) for x in old.select('script:not([type="application/ld+json"]):not([src])')]
            new_scripts = [normalize(x.get_text()) for x in now.select('script:not([type="application/ld+json"]):not([src])')]
            check(old_scripts == new_scripts, 'hub_inline_search_scripts:'+rel)
            old_items = {x.get('@id'): x for x in nodes(old) if typed(x,'ItemList')}
            new_items = {x.get('@id'): x for x in nodes(now) if typed(x,'ItemList')}
            check(all(new_items.get(k) == v for k,v in old_items.items()), 'hub_original_itemlist:'+rel)
            old_images = [(x.get('src'),x.get('alt'),x.get('width'),x.get('height'),x.get('style')) for x in old.main.select('img')]
            new_images = [(x.get('src'),x.get('alt'),x.get('width'),x.get('height'),x.get('style')) for x in now.main.select('img')]
            check(all(x in new_images for x in old_images), 'hub_original_images:'+rel)
            check(len(now.select('#coaching-brief')) == 1, 'hub_brief_one:'+rel)
            counts['hubs'] += 1

    unique_titles, unique_canonicals = [], []
    for rel in TARGETS:
        check((ROOT/rel).is_file(), 'page_exists:'+rel)
        if not (ROOT/rel).is_file():
            continue
        doc = load(rel)
        visible = normalize(doc.main.get_text(' ', strip=True))
        check(len(doc.select('h1')) == 1, 'one_h1:'+rel)
        title = doc.title.get_text(strip=True) if doc.title else ''
        unique_titles.append(title)
        check(bool(title), 'title_present:'+rel)
        canonical = doc.select_one('link[rel="canonical"]')
        canonical = canonical.get('href') if canonical else None
        unique_canonicals.append(canonical)
        check(canonical == public_url(rel), 'canonical_matches_route:'+rel, canonical)
        og = doc.select_one('meta[property="og:url"]')
        check(og and og.get('content') == canonical, 'og_matches_canonical:'+rel)
        og_image = doc.select_one('meta[property="og:image"]')
        check(og_image is not None, 'og_image_present:'+rel)
        if og_image:
            target = local_target(rel, og_image.get('content',''))
            check(target is not None and (ROOT/target[0]).is_file(), 'og_image_local_file:'+rel, og_image.get('content'))
        check(bool(doc.select_one('meta[name="description"][content]')), 'description_present:'+rel)
        all_ids = [x['id'] for x in doc.select('[id]')]
        check(len(all_ids) == len(set(all_ids)), 'unique_dom_ids:'+rel, [k for k,v in Counter(all_ids).items() if v>1])
        contacts = {x['href'] for x in doc.select('a[href]') if x['href'].startswith(('tel:', 'sms:'))}
        check(contacts == {'tel:010-6839-8283','sms:01068398283'}, 'contact_targets:'+rel, list(contacts))
        nav = doc.select_one('header .nav-links')
        check(nav is not None, 'navigation_present:'+rel)
        if nav:
            routes = {local_target(rel,x['href'])[0] for x in nav.select('a[href]') if local_target(rel,x['href'])}
            check(set(CORE+[NEW,'전국학원/index.html','과목별학원/index.html']) <= routes, 'six_core_navigation_routes:'+rel, sorted(routes))
        try:
            graph = nodes(doc)
            counts['jsonld_graph_nodes'] += len(graph)
            faq = [x for x in graph if typed(x, 'FAQPage')]
            check(len(faq) == 1, 'one_faq_schema:'+rel, len(faq))
            schema_pairs = []
            for faq_node in faq:
                for q in faq_node.get('mainEntity', []):
                    schema_pairs.append((normalize(q.get('name','')), normalize(q.get('acceptedAnswer',{}).get('text',''))))
            html_pairs = []
            for detail in doc.main.select('details'):
                summary = detail.find('summary', recursive=False)
                if not summary:
                    continue
                paragraphs = detail.find_all('p', recursive=False)
                if paragraphs:
                    html_pairs.append((normalize(summary.get_text(' ',strip=True)),normalize(' '.join(p.get_text(' ',strip=True) for p in paragraphs))))
            check(Counter(schema_pairs) == Counter(html_pairs), 'faq_visible_schema_match:'+rel, {'schema':schema_pairs,'html':html_pairs} if Counter(schema_pairs)!=Counter(html_pairs) else None)
            counts['faq_pairs'] += len(schema_pairs)
            for node in graph:
                if typed(node, 'VideoObject'):
                    check(bool(node.get('name')) and bool(node.get('description')) and bool(node.get('thumbnailUrl')), 'video_schema_fields:'+rel)
                    embed = node.get('embedUrl', '')
                    check(bool(embed) and ('youtube' in embed or 'youtu.be' in embed), 'video_schema_embed:'+rel, embed)
                if typed(node, 'WebPage') or typed(node,'CollectionPage'):
                    check(node.get('url') == canonical, 'webpage_schema_url:'+rel, node.get('url'))
        except (ValueError,TypeError) as exc:
            check(False, 'jsonld_parse:'+rel, str(exc))

        for tag in doc.select('a[href],link[href],img[src],script[src],iframe[src],source[src]'):
            attr = 'href' if tag.has_attr('href') else 'src'
            value = tag.get(attr,'')
            target = local_target(rel, value)
            if target is None:
                continue
            path, anchor = target
            check((ROOT/path).is_file(), f'local_{tag.name}_target:{rel}:{value}')
            counts['local_references'] += 1
            if (ROOT/path).is_file() and anchor and path.endswith('.html'):
                check(load(path).find(id=anchor) is not None or load(path).find(attrs={'name':anchor}) is not None, 'local_anchor:'+rel+':'+value)
                counts['anchors'] += 1
            check(not path.startswith(('tools/', '.env', '.git', '.vercel/')), 'private_path_not_linked:'+rel+':'+value)
        for image in doc.main.select('img'):
            check(bool(image.get('alt','').strip()), 'image_alt:'+rel+':'+image.get('src',''))
            local_image = local_target(rel, image.get('src',''))
            if local_image and local_image[0] not in base['hashes']:
                check(image.get('width') and image.get('height'), 'new_image_dimensions:'+rel+':'+image.get('src',''))
        for term in ['SEO · AEO · GEO CHECK','FAQ CHECK','PARENT REVIEW','상담 후 아이가 어떤 과목을 먼저 잡아야 하는지 정리가 됐고']:
            check(term not in visible, 'no_work_or_fake_review_copy:'+rel+':'+term)
        counts['target_pages'] += 1

    check(len(unique_titles)==len(set(unique_titles)), 'unique_target_titles')
    check(len(unique_canonicals)==len(set(unique_canonicals)), 'unique_target_canonicals')
    current_site = xml_urls((ROOT/'sitemap.xml').read_bytes())
    before_site = base['sitemap_urls']
    check(len(current_site) == len(before_site)+1 == 7818, 'sitemap_count', len(current_site))
    check(len(current_site)==len(set(current_site)), 'sitemap_unique')
    check(set(before_site) <= set(current_site), 'sitemap_existing_preserved')
    check(public_url(NEW) in current_site, 'coaching_in_sitemap')
    current_rss = xml_urls((ROOT/'rss.xml').read_bytes(), rss=True)
    check(len(current_rss) == len(base['rss_urls'])+1 == 24, 'rss_count', len(current_rss))
    check(set(base['rss_urls']) <= set(current_rss), 'rss_existing_preserved')
    check(public_url(NEW) in current_rss, 'coaching_in_rss')

    report = {'baseline_commit': base['commit'], 'checks':len(checks), 'counts':dict(counts), 'errors':errors, 'warnings':warnings, 'scope':TARGETS}
    (REPORT/'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checks':len(checks), 'counts':dict(counts), 'errors':len(errors), 'first_errors':errors[:12]}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['snapshot','audit'])
    args = parser.parse_args()
    if args.mode == 'snapshot':
        snapshot()
    else:
        raise SystemExit(audit())
