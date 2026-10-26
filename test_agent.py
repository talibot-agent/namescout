import agent
EV = [dict(id='E1', kind='domain', check='acme.com', result='taken', at='t'),
      dict(id='E2', kind='domain', check='acme.io', result='available', at='t'),
      dict(id='E3', kind='handle', check='github:@acme', result='taken', at='t'),
      dict(id='E4', kind='handle', check='x:@acme', result="couldn't confirm (x)", at='t'),
      dict(id='E5', kind='apps', check='app', matches=[{'app': 'Acme Pro', 'seller': 'A Inc'}], at='t'),
      dict(id='E6', kind='trademark', check='tm', matches=[{'wordmark': 'ACME', 'alive': True, 'id': '1', 'ownerName': 'X'}], at='t')]

def test_assess_and_citations():
    a = agent.assess('acme', EV)
    assert a['verdict'] == 'AVOID' and a['unconfirmed'] == ['E4']
    txt = agent.explain('acme', a, EV)
    assert '[E1]' in txt and '[E6]' in txt and '[E4]' in txt

def test_clear_name():
    ev = [dict(EV[1]), dict(id='E5', kind='apps', matches=[], at='t'), dict(id='E6', kind='trademark', matches=[], at='t')]
    a = agent.assess('zq', ev); assert a['verdict'] == 'LIKELY CLEAR'
    assert 'No conflicts' in agent.explain('zq', a, ev)

def test_llm_rejects_bad_citations(monkeypatch):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    assert agent.llm_narrate('x [E1]', EV) is None


def test_trademarks_parses_uspto_response(monkeypatch=None):
    import checks, json as _j
    fake = {"hits": {"hits": [
        {"id": "1", "source": {"wordmark": "NOTION", "id": "74490398", "alive": False, "statusDescription": "CANCELLED", "ownerName": ["A"]}},
        {"id": "2", "source": {"wordmark": "NOTION", "id": "88000000", "alive": True, "statusDescription": "REGISTERED", "ownerName": ["Notion Labs"]}}]}}
    orig = checks.get
    checks.get = lambda *a, **k: (200, _j.dumps(fake).encode())
    try:
        r = checks.trademarks("notion")
    finally:
        checks.get = orig
    assert r["matches"][0]["alive"] is True and r["matches"][0]["statusDescription"] == "REGISTERED"
    assert len(r["matches"]) == 2
    checks.get = lambda *a, **k: (500, b"err")
    try:
        assert "couldn't confirm" in checks.trademarks("x")["result"]
    finally:
        checks.get = orig


def test_trademarks_live():
    import os, checks
    if os.environ.get("NAMESCOUT_LIVE") != "1":
        return
    r = checks.trademarks("notion")
    assert any(m["wordmark"] == "NOTION" and m["alive"] for m in r["matches"])


# --- sponsor integrations -------------------------------------------------
import io, json as _json, os as _os, agent as _agent, zetaris_source as _z, hmem as _h

def test_zetaris_sql_is_sanitised():
    sql = _z.build_sql("Zen'tro; DROP")
    assert "zentrodrop" in sql and ";" not in sql.split("FROM")[1] and "'" not in sql.split("LIKE '%")[1].rstrip("%'")

def test_zetaris_portfolio_collision_scores(monkeypatch):
    for k in ('ZETARIS_BASE_URL', 'ZETARIS_ORG_ID', 'ZETARIS_API_KEY'): monkeypatch.setenv(k, 'http://z' if 'URL' in k else '1')
    seen = {}
    def opener(req, timeout=30):
        seen['url'] = req.full_url; seen['org'] = req.get_header('X-org-id')
        return io.BytesIO(_json.dumps({'data': {'columns': ['name', 'kind', 'system', 'owner'], 'rows': [['Zentro', 'product', 'catalogue', 'growth']]}}).encode())
    e = dict(id='E9', kind='portfolio', **_z.portfolio('zentro', opener))
    assert seen['url'].endswith('/api/proxy/sql-editor/sqls/run-query') and seen['org'] == '1'
    a = _agent.assess('zentro', [dict(id='E1', kind='apps', check='apps', matches=[]), dict(id='E2', kind='trademark', check='tm', matches=[]), e])
    assert any('Zetaris' in why and ids == ['E9'] for _, why, ids in a['factors'])

def test_hmem_remember_then_recall(tmp_path, monkeypatch):
    monkeypatch.setenv('NAMESCOUT_HMEM_DIR', str(tmp_path))
    mid = _h.remember(dict(name='quillora', verdict='CAUTION', risk=30, factors=[(25, 'quillora.com is already registered', ['E1'])]))
    assert mid and mid.startswith('mem-')
    r = _h.recall('quillorai')
    assert any('quillora' in m['content'] for m in r['matches'])
