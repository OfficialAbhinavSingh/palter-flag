"""Palter Flag v0.3: highlight dodging and persuasion in an AI answer.

Input is only what a real user has: their question and the answer. The model
returns exact quotes from the answer, so spans can be highlighted in place, plus
what a straight answer would need to say and a follow-up question to ask.
v0.3 adds burying: the answer is there but hidden under filler, or behind an
opening that sets the opposite impression. The sentence that actually answers is
returned so it can be pointed out.

Categories follow two groups. Dodging: the answer avoids the question.
Persuading: the answer pushes a conclusion without support. Paltering, weasel
words, empty rhetoric and unverified claims follow the taxonomy in Liang et al.
(2025), "Machine Bullshit" (arXiv:2507.07484).
"""
import json
import re

DODGING = ("non_answer", "deflection", "empty_reassurance", "burying")
PERSUADING = ("paltering", "minimising", "doubt_casting", "weasel_words", "unverified_claim")
CATEGORIES = DODGING + PERSUADING

FLAG_PROMPT = """You help a reader notice when an answer avoids their question, or pushes them toward a conclusion it does not support, without saying anything plainly false.

QUESTION the reader asked:
<<<
{question}
>>>

ANSWER they received:
<<<
{answer}
>>>

Find the parts of the ANSWER that work against the reader reaching a well-founded conclusion.

Dodging (avoids the question):
- non_answer: refuses or hedges without saying so plainly
- deflection: changes the subject or answers a different question
- empty_reassurance: values, sympathy, track record or praise offered in place of an answer ("your trust is important to us")
- burying: text that hides or dilutes the actual answer, e.g. long filler before it, or an opening that sets the opposite impression to what the answer later admits

Persuading (pushes a conclusion without support):
- paltering: a true or plausible fact chosen to imply something the answer never states
- minimising: makes a serious matter sound small or routine
- doubt_casting: casts doubt on a claim without saying whether it is true
- weasel_words: vague qualifiers that make a claim impossible to pin down ("some", "may", "in certain cases", "many believe")
- unverified_claim: a confident assertion or assurance given with no basis ("I can assure you", "the price already reflects its quality")

Rules:
- Quote spans EXACTLY as they appear in the ANSWER (copy-paste, no edits). Keep each span under 30 words.
- Do not flag sentences that plainly answer the question, even if the answer is unwelcome.
- Do not flag greetings, thanks, sign-offs or offers to help. Flag a span only if it would change what the reader concludes.
- If the answer is direct and complete, return an empty spans list.
- "straight_answer_needs": what a direct answer to the QUESTION would have to state, without guessing what the true answer is.
- "ask_instead": one short follow-up the reader could send to get a direct answer.
- "direct_answer_quote": the exact sentence (copy-paste) in the ANSWER that actually answers the QUESTION, or "" if there is none. Fill it even when the answer is hidden among other text.
- Flag subtle cases too, not only obvious dodges: an answer can contain the truth and still leave a reader with the wrong impression.

Return only JSON:
{{
  "answered": "yes" | "partly" | "no",
  "straight_answer_needs": "<one sentence>",
  "ask_instead": "<one short question>",
  "direct_answer_quote": "<exact sentence or empty>",
  "spans": [{{"quote": "...", "category": "<one of the categories above>", "reason": "<under 15 words>"}}]
}}"""


def build_messages(question: str, answer: str):
    return [{"role": "user", "content": FLAG_PROMPT.format(question=question, answer=answer)}]


def parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ValueError("no JSON in flagger output")
    out = json.loads(m.group(0))
    out["spans"] = [s for s in out.get("spans", []) if s.get("category") in CATEGORIES]
    return out


def locate(answer: str, spans: list[dict]) -> list[dict]:
    """Attach character offsets; drop quotes that are not verbatim in the answer."""
    found = []
    for s in spans:
        q = (s.get("quote") or "").strip()
        i = answer.find(q) if q else -1
        if i >= 0:
            found.append({**s, "start": i, "end": i + len(q)})
    found.sort(key=lambda s: s["start"])
    merged = []
    for s in found:  # drop overlaps, keep the earlier span
        if merged and s["start"] < merged[-1]["end"]:
            continue
        merged.append(s)
    return merged


def locate_direct(answer: str, quote: str):
    """Offsets of the sentence that actually answers, if it is verbatim in the answer."""
    q = (quote or "").strip()
    i = answer.find(q) if q else -1
    return {"start": i, "end": i + len(q), "position": round(i / max(len(answer), 1), 2)} if i >= 0 else None
