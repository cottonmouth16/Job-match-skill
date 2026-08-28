#!/usr/bin/env python3
"""
Local Job Match Scorer — ZERO tokens, runs fully offline.
Implements Agent 01 (ATS Scorer) deterministically: keyword extraction,
weighted match score, ATS compliance audit.

Usage:
    python3 local_scorer.py <resume.pdf|resume.txt> <jd.txt> [--json out.json]

Only the LLM steps (Match Max rewrites, cover letter) need job_match_agent.py.
"""
import argparse, json, re, sys
from pathlib import Path

# ---------------- keyword dictionary (extend freely) ----------------
# canonical term -> list of regex-safe synonyms/variants (case-insensitive)
HARD = {
    "product vision": ["product vision", "platform vision", "feature vision", "vision and roadmap"],
    "working backwards": ["working backwards", "working-backwards", "pr-faq", "pr faq"],
    "roadmap": ["roadmap"],
    "user stories": ["user stor(?:y|ies)", "use case"],
    "requirements decomposition": ["decompos\\w+", "business requirement"],
    "user research": ["user research", "user stud\\w+", "customer research", "feedback session", "discovery"],
    "metrics": ["metrics", "kpi", "instrument\\w+"],
    "runtime metrics feedback": ["runtime metric", "feedback loop", "usage metric"],
    "competitive analysis": ["competitive analys\\w+", "competitive review", "competitor", "benchmark\\w+"],
    "experimentation": ["test.and.learn", "a/b test\\w*", "experiment\\w+"],
    "prioritization": ["prioriti\\w+", "trade.?off"],
    "backlog management": ["backlog"],
    "launch/GTM": ["go.to.market", "gtm", "launch\\w*"],
    "acceptance criteria": ["acceptance criteria", "demo"],
    "post-launch monitoring": ["post.launch", "post.go.live", "operational health", "adoption"],
    "documentation": ["documentation", "self.service support"],
    "risk escalation": ["risk\\w*", "escalat\\w+"],
    "platform product": ["platform"],
    "technical fluency": ["api", "gen ?ai", "rag", "machine learning", "llm", "sql"],
    "stakeholder alignment": ["stakeholder", "cross.functional", "interdependent team"],
}
TOOLS = {
    "jira": ["jira"], "confluence": ["confluence"], "figma": ["figma"],
    "sql": ["sql"], "tableau": ["tableau"], "power bi": ["power ?bi"],
    "postman": ["postman"], "amplitude": ["amplitude"], "mixpanel": ["mixpanel"],
    "aws": ["aws", "amazon web services"], "azure": ["azure"], "gcp": ["gcp", "google cloud"],
    "mural": ["mural"], "visio": ["visio"], "excel": ["excel"],
}
TITLE = {
    "product manager": ["product manager"], "product owner": ["product owner"],
    "lead": ["lead"], "senior": ["senior", "sr\\.?", "avp", "vp"],
    "technical": ["technical"], "mentoring": ["mentor\\w+", "coach\\w+", "onboard\\w+ .{0,20}candidate", "candidate selection"],
}
SOFT = {
    "communication": ["communicat\\w+", "present\\w+"],
    "voice of customer": ["voice of the (?:business )?customer", "customer.centric", "voice of customer"],
    "collaboration": ["collaborat\\w+", "partner\\w+ with", "coordinat\\w+"],
    "leadership": ["leadership", "led ", "drove ", "owned ", "accountab\\w+"],
    "network building": ["network\\w*", "forum"],
}
BUCKETS = [("Hard skills", HARD, 40), ("Tools", TOOLS, 25), ("Title/seniority", TITLE, 20), ("Soft skills", SOFT, 15)]

# ---------------- helpers ----------------
def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            sys.exit("pip install pypdf  (needed to read PDF resumes), or pass a .txt file")
        return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    return path.read_text(errors="ignore")

def present(variants, text):
    for v in variants:
        pat = r"(?i)\b" + v
        if v[-1].isalnum() or v[-1] in ")+*?":   # block prefix matches ('visio' vs 'visions') but allow plurals
            pat += r"s?(?![a-z])"
        if re.search(pat, text):
            return True
    return False

# ---------------- scoring ----------------
def score(resume: str, jd: str):
    total, details = 0.0, []
    for name, dic, weight in BUCKETS:
        jd_terms = {t: v for t, v in dic.items() if present(v, jd)}
        if not jd_terms:                       # JD silent on bucket -> full credit, flagged
            total += weight
            details.append((name, weight, weight, [], [], True))
            continue
        matched = [t for t, v in jd_terms.items() if present(v, resume)]
        missing = [t for t in jd_terms if t not in matched]
        pts = weight * len(matched) / len(jd_terms)
        total += pts
        details.append((name, round(pts, 1), weight, matched, missing, False))
    return round(total), details

# ---------------- ATS audit ----------------
def ats_audit(resume: str, is_pdf: bool):
    issues = []
    up = resume.upper()
    if not re.search(r"(?m)^\s*(SUMMARY|PROFILE|OBJECTIVE)", up):
        issues.append(("High", "No Summary section — add 2-3 lines with target-title keywords at top"))
    for h in ["EXPERIENCE", "EDUCATION", "SKILL"]:
        if h not in up:
            issues.append(("High", f"Standard section header missing: {h}"))
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", resume):
        issues.append(("High", "No email found"))
    if not re.search(r"\+\d{1,3}[ -]?\d", resume):
        issues.append(("Low", "Phone lacks country code (+XX)"))
    dates = re.findall(r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{4}", resume)
    if len(dates) < 4:
        issues.append(("Med", "Few/no 'MMM YYYY' dates detected — check date formatting consistency"))
    if re.search(r"(?i)\b(i|my|me)\b", resume):
        issues.append(("Low", "First-person pronouns found — remove for ATS convention"))
    words = len(resume.split())
    if words > 1100:
        issues.append(("Med", f"Long resume (~{words} words) — consider trimming to 2 pages"))
    if is_pdf:
        issues.append(("Info", "PDF source: text extracted OK; keep a .docx variant for strict ATS portals"))
    return issues

# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resume"); ap.add_argument("jd")
    ap.add_argument("--json", help="also write results to this JSON file")
    a = ap.parse_args()
    rp, jp = Path(a.resume), Path(a.jd)
    resume, jd = read_text(rp), read_text(jp)

    total, details = score(resume, jd)
    issues = ats_audit(resume, rp.suffix.lower() == ".pdf")

    print(f"\n{'='*58}\n  JOB MATCH SCORE: {total}/100\n{'='*58}")
    for name, pts, weight, matched, missing, silent in details:
        print(f"\n{name}: {pts}/{weight}" + ("  (JD names none — full credit)" if silent else ""))
        if matched: print("  ✓ matched: " + ", ".join(matched))
        if missing: print("  ✗ MISSING: " + ", ".join(missing).upper())
    print(f"\n{'-'*58}\nATS AUDIT ({len(issues)} findings)")
    for sev, msg in issues:
        print(f"  [{sev}] {msg}")
    print()

    if a.json:
        Path(a.json).write_text(json.dumps({
            "total": total,
            "buckets": [{"bucket": n, "points": p, "weight": w, "matched": m, "missing": x} for n, p, w, m, x, _ in details],
            "ats_issues": [{"severity": s, "issue": i} for s, i in issues],
        }, indent=2))
        print(f"JSON written to {a.json}")

if __name__ == "__main__":
    main()
