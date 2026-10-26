#!/usr/bin/env python3
"""Brand name availability checker (prototype). Read-only lookups; never registers anything.
Domains: RDAP (IANA bootstrap). Handles: public profile endpoints; 'couldn't confirm' when a
platform hides availability. App stores: iTunes Search API. Trademarks: USPTO tmsearch (if reachable)."""
import json, sys, urllib.request, urllib.error, datetime, re, ssl
UA = {'User-Agent': 'Mozilla/5.0 (brand-checker prototype; read-only)'}
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def get(url, data=None, headers=None, timeout=20):
    h = dict(UA); h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method='POST' if data else 'GET')
    try:
        r = urllib.request.urlopen(req, timeout=timeout); return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
    except Exception as e: return None, str(e).encode()
_boot = None
def rdap_base(tld):
    global _boot
    if _boot is None:
        s, b = get('https://data.iana.org/rdap/dns.json'); _boot = json.loads(b)['services']
    for tlds, urls in _boot:
        if tld in tlds: return urls[0]
WHOIS = {'io': 'whois.nic.io', 'co': 'whois.registry.co', 'me': 'whois.nic.me'}
def whois_domain(name, tld, t):
    import socket
    srv = WHOIS.get(tld, f'whois.nic.{tld}')
    try:
        s = socket.create_connection((srv, 43), timeout=15); s.sendall(f'{name}.{tld}\r\n'.encode())
        buf = b''
        while True:
            c = s.recv(4096)
            if not c: break
            buf += c
        txt = buf.decode('utf-8', 'replace').lower()
    except Exception as e:
        return {'check': f'{name}.{tld}', 'result': f"couldn't confirm (WHOIS {e})", 'at': t}
    if re.search(r'no match|not found|no data found|no entries found|status:\s*free|is available', txt): res = 'available'
    elif re.search(r'domain name:|registrar:|creation date', txt): res = 'taken'
    else: res = "couldn't confirm (WHOIS unparsed)"
    return {'check': f'{name}.{tld}', 'result': res, 'source': 'WHOIS ' + srv, 'at': t}
def domain(name, tld):
    base = rdap_base(tld); t = now()
    if not base: return whois_domain(name, tld, t)
    s, _ = get(base.rstrip('/') + f'/domain/{name}.{tld}')
    res = 'taken' if s == 200 else 'available' if s == 404 else f"couldn't confirm (RDAP {s})"
    return {'check': f'{name}.{tld}', 'result': res, 'source': 'RDAP ' + base, 'at': t}
def handle(name, plat):
    t = now()
    if plat == 'github':
        s, _ = get(f'https://api.github.com/users/{name}')
        res = 'taken' if s == 200 else 'available' if s == 404 else f"couldn't confirm ({s})"
    elif plat == 'reddit':
        s, b = get(f'https://www.reddit.com/user/{name}/about.json')
        res = 'taken' if s == 200 else 'available' if s == 404 else f"couldn't confirm ({s})"
    elif plat == 'youtube':
        s, _ = get(f'https://www.youtube.com/@{name}')
        res = 'taken' if s == 200 else 'available' if s == 404 else f"couldn't confirm ({s})"
    else:  # instagram, tiktok, x: no public availability endpoint without login
        res = "couldn't confirm (platform hides availability; manual check link given)"
    return {'check': f'{plat}:@{name}', 'result': res, 'at': t}
def apps(name):
    t = now(); s, b = get('https://itunes.apple.com/search?' + urllib.parse.urlencode({'term': name, 'entity': 'software', 'limit': 50}))
    hits = []
    if s == 200:
        for a in json.loads(b).get('results', []):
            if re.sub(r'\W', '', a['trackName'].lower()).startswith(re.sub(r'\W', '', name.lower())):
                hits.append({'app': a['trackName'], 'seller': a.get('sellerName'), 'url': a.get('trackViewUrl')})
    return {'check': 'Apple App Store (iTunes Search API)', 'matches': hits[:10], 'at': t, 'status': s}
TM_URL = 'https://tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch'
def trademarks(name):
    t = now()
    q = {"query": {"bool": {"must": [{"bool": {"should": [{"query_string": {"query": f"{name}", "default_operator": "AND", "fields": ["wordmark"]}}]}}]}},
         "size": 50, "_source": ["wordmark", "registrationId", "id", "alive", "statusDescription", "ownerName"]}
    s, b = get(TM_URL, data=json.dumps(q).encode(), headers={'Content-Type': 'application/json'})
    out = []
    try:
        for h in json.loads(b)['hits']['hits']:
            src = h.get('source') or h.get('_source') or {}
            out.append({k: src.get(k) for k in ('wordmark', 'id', 'registrationId', 'alive', 'statusDescription', 'ownerName')})
    except Exception:
        return {'check': 'USPTO tmsearch', 'result': f"couldn't confirm (HTTP {s})", 'at': t}
    if s != 200: return {'check': 'USPTO tmsearch', 'result': f"couldn't confirm (HTTP {s})", 'at': t}
    out.sort(key=lambda m: not m.get('alive'))
    return {'check': 'USPTO tmsearch', 'matches': out, 'source': TM_URL, 'at': t}
import urllib.parse
if __name__ == '__main__':
    name = sys.argv[1].lower(); tlds = (sys.argv[2] if len(sys.argv) > 2 else 'com,io,ai').split(',')
    rep = {'name': name, 'domains': [domain(name, x) for x in tlds],
           'handles': [handle(name, p) for p in ('github', 'reddit', 'youtube', 'instagram', 'tiktok', 'x')],
           'apps': apps(name), 'trademarks': trademarks(name),
           'disclaimer': 'Trademark results are a starting point, not legal advice.'}
    print(json.dumps(rep, indent=1))
