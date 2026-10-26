"""Zetaris evidence source: checks the candidate name against an organisation's OWN fragmented data
(CRM accounts, product catalogue, vendor list, domain inventory...) federated by Zetaris Lightning into
one view, so a name that collides with an internal product or a customer is caught before launch.
Uses the Zetaris UI-proxy SQL route (/api/proxy/sql-editor/sqls/run-query), same as the official
zetaris/getting-started scripts. Enabled only when ZETARIS_BASE_URL, ZETARIS_ORG_ID and ZETARIS_API_KEY
are set; see zetaris/portfolio_view.sql for the federated view. Read-only SELECT only."""
import json, os, re, uuid, datetime, urllib.request
VIEW = os.environ.get('ZETARIS_PORTFOLIO_VIEW', 'namescout.brand_portfolio')
def configured():
    return all(os.environ.get(k) for k in ('ZETARIS_BASE_URL', 'ZETARIS_ORG_ID', 'ZETARIS_API_KEY'))
def build_sql(name):
    n = re.sub(r'[^a-z0-9]', '', name.lower())  # sanitised: alnum only, no injection surface
    return (f"SELECT name, kind, system, owner FROM {VIEW} "
            f"WHERE lower(regexp_replace(name, '[^A-Za-z0-9]', '')) LIKE '%{n}%'")
def _post(sql, opener=urllib.request.urlopen):
    base = os.environ['ZETARIS_BASE_URL'].rstrip('/')
    body = {'sql': sql, 'limit': 50}
    if os.environ.get('ZETARIS_ENGINE_ID'): body['engineId'] = os.environ['ZETARIS_ENGINE_ID']
    req = urllib.request.Request(base + '/api/proxy/sql-editor/sqls/run-query', json.dumps(body).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['ZETARIS_API_KEY'], 'X-Org-ID': os.environ['ZETARIS_ORG_ID'],
                 'X-Request-ID': str(uuid.uuid4()), 'Content-Type': 'application/json'})
    return json.load(opener(req, timeout=30))
def rows(result):
    """Normalise the run-query payload to a list of dicts (handles {columns,rows} and list-of-dicts shapes)."""
    d = result.get('data', result) if isinstance(result, dict) else result
    if isinstance(d, dict) and 'rows' in d:
        cols = [c.get('name', c) if isinstance(c, dict) else c for c in d.get('columns', [])]
        return [r if isinstance(r, dict) else dict(zip(cols, r)) for r in d['rows']]
    return d if isinstance(d, list) else []
def portfolio(name, opener=urllib.request.urlopen):
    t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    src = f'Zetaris Lightning view {VIEW}'
    try:
        return {'check': 'internal portfolio (Zetaris)', 'matches': rows(_post(build_sql(name), opener)), 'source': src, 'at': t}
    except Exception as e:
        return {'check': 'internal portfolio (Zetaris)', 'result': f"couldn't confirm (Zetaris {type(e).__name__})", 'source': src, 'at': t}
