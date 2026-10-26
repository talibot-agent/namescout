"""Meterless H-MEM memory for NameScout: recall prior verdicts on similar names, remember each new one.
Runs memory/bridge.ts (vendored H-MEM reference, Apache-2.0) via `npx tsx`. Never fatal: if Node is
missing the agent still works and the report says memory was unavailable."""
import json, os, subprocess, datetime, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
def _call(cmd, timeout=60):
    if os.environ.get('NAMESCOUT_NO_MEMORY'): return None
    try:
        p = subprocess.run(['npx', '--no-install', 'tsx', 'bridge.ts'], cwd=os.path.join(HERE, 'memory'),
                           input=json.dumps(cmd, default=str), capture_output=True, text=True, timeout=timeout)
        return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None
    except Exception:
        return None
def recall(name):
    t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    r = _call({'op': 'recall', 'name': name})
    if r is None:
        return {'check': 'prior verdicts (H-MEM)', 'result': "couldn't confirm (memory unavailable)", 'source': 'Meterless H-MEM', 'at': t}
    # H-MEM ranks by content; keep only prior names that are actually close to this one (spelling-level).
    ms = [m for m in r.get('memories', []) if difflib.SequenceMatcher(None, name, m['source'].split(':', 1)[1]).ratio() >= 0.7]
    return {'check': 'prior verdicts (H-MEM)', 'matches': ms, 'source': f"Meterless H-MEM MemoryRetrievalService ({r.get('engine')})", 'at': t}
def remember(rep):
    r = _call({'op': 'remember', 'report': {k: rep[k] for k in ('name', 'verdict', 'risk', 'factors')}})
    return r.get('id') if r else None
