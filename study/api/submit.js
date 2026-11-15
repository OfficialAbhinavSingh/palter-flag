import { put } from "@vercel/blob";

const ITEM_IDS = new Set(Array.from({ length: 12 }, (_, i) => `S${String(i + 1).padStart(2, "0")}`));
const PID = /^[A-Za-z0-9-]{8,64}$/;
const CHOICE = { use: ["daily", "weekly", "rarely"], src: ["hub", "friend", "other"] };

function clean(body) {
  if (!body || typeof body !== "object" || !PID.test(body.pid || "")) return null;
  const results = Array.isArray(body.results) ? body.results : [];
  if (results.length !== ITEM_IDS.size) return null;
  const seen = new Set();
  const rows = [];
  for (const r of results) {
    const value = Number(r?.value);
    const trust = Number(r?.trust);
    if (!ITEM_IDS.has(r?.item) || seen.has(r.item) || !Number.isFinite(value) || value < 0 || value > 100) return null;
    if (!Number.isInteger(trust) || trust < 1 || trust > 5) return null;
    seen.add(r.item);
    rows.push({
      item: r.item,
      highlight: r.highlight === true,
      value: Math.round(value),
      trust,
      ms: Math.max(0, Math.min(3_600_000, Math.round(Number(r.ms) || 0))),
      order: Math.max(0, Math.min(11, Math.round(Number(r.order) || 0))),
    });
  }
  return {
    pid: body.pid,
    version: 2,
    prior_submission: body.prior_submission === true,
    use: CHOICE.use.includes(body.use) ? body.use : null,
    src: CHOICE.src.includes(body.src) ? body.src : null,
    results: rows,
    received_at: new Date().toISOString(),
  };
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "method not allowed" });
  }
  const record = clean(req.body);
  if (!record) return res.status(400).json({ error: "invalid submission" });
  try {
    await put(`responses/${record.received_at.slice(0, 19).replace(/[:T]/g, "-")}_${record.pid}.json`,
      JSON.stringify(record), { access: "private", contentType: "application/json", addRandomSuffix: true });
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("blob put failed", err);
    return res.status(500).json({ error: "could not save" });
  }
}
