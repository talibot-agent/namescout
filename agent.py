#!/usr/bin/env python3
"""NameScout: a brand-name clearance agent that explains WHY (Open Agent Hackathon, Track 02).
Built by Tali, an AI agent, for Mykel Nelson.

Pipeline: plan -> gather evidence from independent public sources (RDAP/WHOIS, GitHub/Reddit/YouTube,
Apple App Store, USPTO) -> score each risk factor with an explicit rule -> verdict -> explanation where
every sentence cites evidence ids [E#] with source + UTC timestamp. Optional LLM narration via any
OpenAI-compatible endpoint (e.g. NVIDIA Nemotron on build.nvidia.com: set LLM_BASE_URL, LLM_API_KEY,
LLM_MODEL); the LLM may only rephrase cited facts, and every [E#] it emits is validated."""
import json, os, re, sys, html, urllib.request
from concurrent.futures import ThreadPoolExecutor
import checks, hmem, zetaris_source

PLAT = ('github', 'reddit', 'youtube', 'instagram', 'tiktok', 'x')

def gather(name, tlds):
    jobs = [('domain', lambda t=t: checks.domain(name, t)) for t in tlds]
    jobs += [('handle', lambda p=p: checks.handle(name, p)) for p in PLAT]
    jobs += [('apps', lambda: checks.apps(name)), ('trademark', lambda: checks.trademarks(name))]
    if zetaris_source.configured():
        jobs.append(('portfolio', lambda: zetaris_source.portfolio(name)))
    jobs.append(('memory', lambda: hmem.recall(name)))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda j: (j[0], j[1]()), jobs))
    return [dict(id=f'E{i+1}', kind=k, **r) for i, (k, r) in enumerate(res)]

def norm(s): return re.sub(r'\W', '', (s or '').lower())

def assess(name, ev):
    """Rule-based factors. Each factor: points (0-100 risk), rule text, evidence ids."""
    f = []
    dom = [e for e in ev if e['kind'] == 'domain']
    taken = [e for e in dom if e['result'] == 'taken']
    com = next((e for e in dom if e['check'].endswith('.com')), None)
    if com and com['result'] == 'taken':
        f.append((25, f"{com['check']} is already registered, so the most valuable domain is unavailable", [com['id']]))
    if len(taken) > 1:
        f.append((5 * len(taken), f"{len(taken)} of {len(dom)} checked domains are registered", [e['id'] for e in taken]))
    hs = [e for e in ev if e['kind'] == 'handle' and e['result'] == 'taken']
    if hs:
        f.append((5 * len(hs), 'Handle already in use on ' + ', '.join(e['check'].split(':')[0] for e in hs), [e['id'] for e in hs]))
    ap = next(e for e in ev if e['kind'] == 'apps')
    exact = [m for m in ap.get('matches', []) if norm(m['app']).startswith(norm(name))]
    if exact:
        f.append((min(30, 10 * len(exact)), f"{len(exact)} App Store app(s) start with this name, e.g. \"{exact[0]['app']}\" by {exact[0]['seller']}", [ap['id']]))
    tm = next(e for e in ev if e['kind'] == 'trademark')
    live = [m for m in tm.get('matches', []) if m.get('alive') and norm(m.get('wordmark')) == norm(name)]
    if live:
        f.append((40, f"Live USPTO mark \"{live[0]['wordmark']}\" (serial {live[0].get('id')}, owner {live[0].get('ownerName')}) matches exactly", [tm['id']]))
    pf = next((e for e in ev if e['kind'] == 'portfolio'), None)
    if pf:
        hit = [m for m in pf.get('matches', []) if norm(m.get('name')) == norm(name)]
        near = [m for m in pf.get('matches', []) if m not in hit]
        if hit:
            f.append((35, f"Collides with an internal {hit[0].get('kind')} \"{hit[0].get('name')}\" in {hit[0].get('system')} (federated by Zetaris)", [pf['id']]))
        elif near:
            f.append((10, f"{len(near)} internal record(s) contain the name, e.g. \"{near[0].get('name')}\" in {near[0].get('system')}", [pf['id']]))
    unk = [e for e in ev if "couldn't confirm" in str(e.get('result', ''))]
    risk = min(100, sum(p for p, _, _ in f))
    verdict = 'AVOID' if risk >= 60 else 'CAUTION' if risk >= 25 else 'LIKELY CLEAR'
    return dict(risk=risk, verdict=verdict, factors=f, unconfirmed=[e['id'] for e in unk])

def explain(name, a, ev):
    lines = [f"Verdict for \"{name}\": {a['verdict']} (risk {a['risk']}/100)."]
    if not a['factors']:
        ok = [e['id'] for e in ev if e['id'] not in a['unconfirmed']]
        lines.append('No conflicts were found in the sources that answered: ' + ' '.join(f'[{i}]' for i in ok) + '.')
    for p, why, ids in sorted(a['factors'], reverse=True):
        lines.append(f"+{p}: {why} " + ' '.join(f'[{i}]' for i in ids) + '.')
    if a['unconfirmed']:
        lines.append('Not counted either way, because the source would not confirm: ' + ' '.join(f'[{i}]' for i in a['unconfirmed']) + '.')
    mem = next((e for e in ev if e['kind'] == 'memory' and e.get('matches')), None)
    if mem:
        m = mem['matches'][0]
        lines.append(f"Context, not scored: H-MEM recalls a prior check on a similar name: {m['content'][:140]} [{mem['id']}].")
    lines.append('Trademark results are a starting point, not legal advice.')
    return '\n'.join(lines)

def llm_narrate(text, ev):
    base, key = os.environ.get('LLM_BASE_URL'), os.environ.get('LLM_API_KEY')
    if not (base and key): return None
    body = {'model': os.environ.get('LLM_MODEL', 'nvidia/llama-3.3-nemotron-super-49b-v1'), 'temperature': 0.2,
            'messages': [{'role': 'system', 'content': 'Rewrite the findings as a short plain-English brief for a founder. Use ONLY facts given. Keep every [E#] citation next to the fact it supports. Add no new facts.'},
                         {'role': 'user', 'content': text}]}
    req = urllib.request.Request(base.rstrip('/') + '/chat/completions', json.dumps(body).encode(),
                                 {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        out = json.load(urllib.request.urlopen(req, timeout=60))['choices'][0]['message']['content']
    except Exception as e:
        return None
    valid = {e['id'] for e in ev}
    cited = set(re.findall(r'\[(E\d+)\]', out))
    return out if cited and cited <= valid and cited >= set(re.findall(r'\[(E\d+)\]', text)) else None

def report_html(name, a, ev, text):
    rows = ''.join(f"<tr id='{e['id']}'><td>{e['id']}</td><td>{html.escape(e['check'])}</td><td>{html.escape(str(e.get('result', '') or (str(len(e.get('matches', []))) + ' match(es)')))}</td><td>{html.escape(e.get('source', ''))}</td><td>{e['at']}</td></tr>" for e in ev)
    body = html.escape(text).replace('\n', '<br>')
    body = re.sub(r'\[(E\d+)\]', r"<a href='#\1'>[\1]</a>", body)
    return f"<!doctype html><meta charset=utf-8><title>NameScout: {html.escape(name)}</title><style>body{{font:15px system-ui;max-width:900px;margin:2em auto}}td,th{{border-bottom:1px solid #ddd;padding:4px 8px}}.v{{font-size:1.6em;font-weight:700}}</style><h1>NameScout</h1><div class=v>{html.escape(name)}: {a['verdict']} ({a['risk']}/100)</div><p>{body}</p><h2>Evidence</h2><table><tr><th>id</th><th>check</th><th>result</th><th>source</th><th>checked (UTC)</th></tr>{rows}</table><p><small>Built by Tali, an AI agent. Read-only lookups; nothing is registered.</small></p>"

def run(name, tlds=('com', 'io', 'ai'), out_dir='.'):
    name = name.lower()
    ev = gather(name, list(tlds)); a = assess(name, ev); text = explain(name, a, ev)
    narr = llm_narrate(text, ev)
    rep = dict(name=name, **a, explanation=text, narration=narr, evidence=ev)
    rep['memory_id'] = hmem.remember(rep)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, f'{name}.json'), 'w').write(json.dumps(rep, indent=1, default=str))
    open(os.path.join(out_dir, f'{name}.html'), 'w').write(report_html(name, a, ev, narr or text))
    return rep

if __name__ == '__main__':
    for n in sys.argv[1:] or ['notion']:
        r = run(n, out_dir='reports'); print(r['explanation']); print()
