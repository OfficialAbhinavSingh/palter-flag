// Download every study response from the private Blob store into ../outputs/study_responses/.
// Run from study/ with BLOB_READ_WRITE_TOKEN set (vercel env pull, or `set -a; . ./.env.local`).
import { get, list } from "@vercel/blob";
import { mkdir, writeFile, access } from "node:fs/promises";

const out = new URL("../outputs/study_responses/", import.meta.url);
await mkdir(out, { recursive: true });

let cursor, added = 0, total = 0;
do {
  const page = await list({ prefix: "responses/", cursor });
  for (const b of page.blobs) {
    total += 1;
    const dest = new URL(b.pathname.split("/").pop(), out);
    try { await access(dest); continue; } catch {}
    const r = await get(b.pathname, { access: "private", useCache: false });
    await writeFile(dest, await new Response(r.stream).text());
    added += 1;
  }
  cursor = page.hasMore ? page.cursor : undefined;
} while (cursor);
console.log(`${total} responses in store, ${added} new downloaded`);
