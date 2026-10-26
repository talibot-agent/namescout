// NameScout <-> Meterless H-MEM bridge. Python calls this with one JSON command on stdin
// and reads one JSON reply on stdout. State persists in ../.hmem/ between runs.
//   {"op":"recall","name":"zentro"}          -> MemoryRetrievalService.query (prior verdicts on similar names)
//   {"op":"remember","report":{...}}         -> MemoryStoreService.add (verdict + cited reasons, with provenance)
//   {"op":"feedback","id":"mem-3","signal":"helpful"} -> TrustLedger feedback delta
//   {"op":"audit","id":"mem-3"}              -> TrustLedgerService.history
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadHMEM } from "./engine.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const chunks: Buffer[] = [];
for await (const c of process.stdin) chunks.push(c as Buffer);
const cmd = JSON.parse(Buffer.concat(chunks).toString() || "{}");
const { HMEM, source } = await loadHMEM();
const hmem = new HMEM({ persistDir: process.env.NAMESCOUT_HMEM_DIR || path.join(here, "..", ".hmem") });
let out: any = { engine: source };
if (cmd.op === "recall") {
  const r = hmem.query(`brand name ${cmd.name} verdict`, { threshold: 0.05, topN: 5 });
  out.memories = r.memories
    .map((m: any) => ({ id: m.memory.id, relevance: Number(m.relevance.toFixed(3)), content: m.memory.content, source: m.memory.source }))
    .filter((m: any) => m.source.startsWith("namescout:") && !m.source.endsWith(":" + cmd.name));
  out.strategy = r.trace?.strategy;
} else if (cmd.op === "remember") {
  const rep = cmd.report;
  const reasons = (rep.factors || []).map((f: any) => `${f[1]} [${f[2].join(",")}]`).join("; ");
  const rec = hmem.add({
    content: `brand name ${rep.name} verdict ${rep.verdict} risk ${rep.risk}/100. ${reasons || "no conflicts found"}`,
    type: "general", source: `namescout:${rep.name}`, tags: ["namescout", rep.verdict.toLowerCase().replace(" ", "-")],
  });
  out.id = rec.id; out.layer = rec.layer;
} else if (cmd.op === "feedback") {
  out.result = hmem.feedback(cmd.id, cmd.signal);
} else if (cmd.op === "audit") {
  out.history = hmem.ledger.history(cmd.id);
} else out.error = "unknown op";
process.stdout.write(JSON.stringify(out));
