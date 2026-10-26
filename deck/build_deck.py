from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
BG=RGBColor(0x0F,0x17,0x2A); FG=RGBColor(0xF1,0xF5,0xF9); AC=RGBColor(0x22,0xD3,0xEE); MU=RGBColor(0x94,0xA3,0xB8)
p=Presentation(); p.slide_width=Inches(13.333); p.slide_height=Inches(7.5)
def slide(title, kicker=None):
    s=p.slides.add_slide(p.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=BG
    if kicker: tb(s,kicker,0.7,0.45,12,0.5,16,AC,True)
    tb(s,title,0.7,0.85,12,1.1,36,FG,True); return s
def tb(s,text,x,y,w,h,size,color=FG,bold=False,font='Calibri'):
    t=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame; t.word_wrap=True
    for i,line in enumerate(text.split('\n')):
        para=t.paragraphs[0] if i==0 else t.add_paragraph(); r=para.add_run(); r.text=line
        r.font.size=Pt(size); r.font.color.rgb=color; r.font.bold=bold; r.font.name=font; para.space_after=Pt(8)
    return t
def box(s,x,y,w,h,head,body,col=AC,bs=19):
    r=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h)); r.fill.solid(); r.fill.fore_color.rgb=RGBColor(0x1E,0x29,0x3B); r.line.color.rgb=col
    tb(s,head,x+0.2,y+0.15,w-0.4,0.6,20,col,True); tb(s,body,x+0.2,y+0.8,w-0.4,h-0.9,bs,FG)
# 1 title
s=slide('NameScout','Open Agent Hackathon 2026 · Track 02: The Agent That Can Explain Why')
tb(s,'The brand-clearance agent that shows its work',0.7,2.1,12,1,28,AC)
tb(s,'Every verdict cites its evidence: source, endpoint, UTC timestamp.\nBuilt by Tali, an AI agent, for Mykel Nelson · github.com/talibot-agent/namescout',0.7,3.3,12,2,20,MU)
# 2 problem
s=slide('The problem: names die late and expensively','Problem & users')
box(s,0.7,2.2,3.8,3.8,'Who','Founders, product marketers and brand/legal teams naming a product, feature or company.')
box(s,4.75,2.2,3.8,3.8,'Pain','The .com, handles, an App Store app, a live trademark, or one of your own products or customers already has the name. Found out after the logo is paid for.')
box(s,8.8,2.2,3.8,3.8,'Gap','Checkers say "available / taken" with no reasons, and silently treat "no answer" as "free". Nobody can audit why.')
# 3 solution
s=slide('Verdict + cited reasons, never a guess','Solution')
tb(s,'Verdict for "notion": AVOID (risk 100/100).\n+40: Live USPTO mark "NOTION" (serial 97879391) matches exactly [E11].\n+30: 4 App Store apps start with this name [E10].\n+25: notion.com is already registered [E1].\nNot counted either way, the source would not confirm: [E2] [E5] [E7].\nContext: H-MEM recalls a prior check on a similar name [E12].',0.7,2.0,12,3.6,19,FG,False,'Consolas')
tb(s,'LIKELY CLEAR / CAUTION / AVOID · explicit point rules · unconfirmed ≠ available · HTML report with clickable citations',0.7,6.1,12,0.8,16,AC)
# 4 architecture
s=slide('Agent workflow','Architecture')
steps=[('1 Plan','name → TLDs, platforms, registries'),('2 Gather','RDAP/WHOIS · GitHub/Reddit/YouTube · App Store · USPTO · Zetaris internal view · H-MEM recall'),('3 Score','auditable rules, each tied to [E#] ids'),('4 Explain','cited text; optional Nemotron rewrite validated citation-by-citation'),('5 Remember','verdict + reasons stored in H-MEM with provenance')]
for i,(h,b) in enumerate(steps): box(s,0.5+i*2.5,2.2,2.35,4.2,h,b,bs=16)
# 5 sponsors
s=slide('How the sponsor tech is used','Zetaris · Meterless · NVIDIA')
box(s,0.7,2.1,3.8,4.9,'Zetaris','Federates an org\'s own scattered name data (CRM accounts, product catalogue, ERP vendors) into one Lightning view namescout.brand_portfolio. NameScout queries it read-only over the run-query REST route; an exact internal collision adds +35 with its own citation.',bs=16)
box(s,4.75,2.1,3.8,4.9,'Meterless H-MEM','Vendored H-MEM reference engine is the agent\'s memory: MemoryStoreService remembers each verdict with provenance, MemoryRetrievalService recalls prior checks on similar names, TrustLedger audits them. Local, no keys.',bs=16)
box(s,8.8,2.1,3.8,4.9,'NVIDIA Nemotron','Optional plain-English narration via an OpenAI-compatible endpoint (llama-3.3-nemotron-super-49b-v1). Output is rejected unless every [E#] exists and every original citation is kept: no hallucinated reasons.',bs=16)
# 6 unique
s=slide('What is different','Innovation')
box(s,0.7,2.2,5.8,4.0,'Explainability as a contract','Every scored factor carries evidence ids. The LLM can only rephrase; a validator rejects any output that drops or invents a citation. Silent sources are labelled, never counted.')
box(s,6.8,2.2,5.8,4.0,'Internal + external + memory','Public registries tell you if the world uses the name; Zetaris tells you if your own company already does; H-MEM tells you what you concluded last time about a near-identical name.')
# 7 stack
s=slide('Technical stack','Built to run anywhere')
tb(s,'• Python 3 standard library agent (no pip deps) + pytest (8 tests incl. mocked Zetaris + live H-MEM)\n• TypeScript H-MEM bridge (tsx) over the vendored Meterless reference engine (Apache-2.0)\n• Zetaris UI-proxy SQL route, same as zetaris/getting-started scripts; SQL is sanitised and SELECT-only\n• Public sources: IANA RDAP bootstrap, WHOIS :43, iTunes Search API, USPTO tmsearch\n• ThreadPoolExecutor parallel gathering, JSON + HTML report output',0.7,2.1,12,4.5,19)
# 8 future
s=slide('Next','Future enhancements')
tb(s,'• EUIPO / WIPO Global Brand Database and phonetic (sound-alike) trademark matching\n• Zetaris connectors pre-built for Salesforce and HubSpot exports\n• H-MEM feedback loop: legal team marks verdicts helpful/wrong, confidence updates via TrustLedger\n• Batch mode for naming agencies: rank 50 candidates by clearance risk overnight with Meterless Nightshift\n\nAI disclosure: code, tests, docs, deck and demo were produced by Tali, an autonomous AI agent, directed and reviewed by Mykel Nelson.',0.7,2.1,12,4.8,19)
p.save('NameScout_deck.pptx')
