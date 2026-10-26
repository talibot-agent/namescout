# Open Agent Hackathon 2026: Submission draft

**Title:** NameScout: the brand-clearance agent that can explain why

**Track:** Track 02, "The Agent That Can Explain Why"

**Repo:** https://github.com/talibot-agent/namescout
**Demo video:** demo.mp4 (2:07)

**Description:**
Founders pick a product name, then find out weeks later that the .com, the social handles, an App Store app or a live trademark already belong to someone else. NameScout is an agent that checks independent public sources in parallel and returns LIKELY CLEAR, CAUTION or AVOID. Every reason in its verdict cites numbered evidence ([E#]), and each piece of evidence records its source endpoint and the UTC time it was checked. The sources are RDAP/WHOIS, GitHub/Reddit/YouTube handles, the Apple App Store and the USPTO Trademark Search.

The scoring rules are explicit and auditable: an exact live USPTO mark adds 40, a registered .com adds 25, and so on. Sources that refuse to answer are labelled "unconfirmed" and never counted as available, so the agent doesn't overclaim. An optional LLM (NVIDIA Nemotron) can rewrite the explanation in plain English. Its output is rejected unless every citation it uses exists and every original citation is kept, which guards against hallucinated reasons. The output is a JSON file plus an HTML report whose citations link to the evidence table.

**Tech used:** Python 3 (standard library only), RDAP via the IANA bootstrap, WHOIS (port 43), the iTunes Search API, the USPTO tmsearch backend, ThreadPoolExecutor for parallel evidence gathering, an optional OpenAI-compatible LLM endpoint (NVIDIA Nemotron llama-3.3-nemotron-super-49b-v1) with citation validation, and pytest.

**AI disclosure:** Tali, an autonomous AI agent, built NameScout (code, tests, docs and demo) for Mykel Nelson.

Trademark results are a starting point, not legal advice.
