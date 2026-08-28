---
name: job-match
description: "Run a 5-agent job application pipeline — ATS match scoring, truthful resume optimization, skill-gap analysis, cover letter, and packaged application folder with run logs. Use this whenever the user says \"run job match\", pastes a job description, asks to score or tailor their resume against a JD, wants an ATS review or ATS compliance check, asks \"am I a good fit for this role\", wants a cover letter for a specific job, or asks to prepare a job application. Also trigger when the user shares a job posting and asks anything about their chances, keywords, or resume improvements."
---

# Job Match Pipeline

Five sequential agents turn a resume + job description into a scored, ATS-optimized application package. The user's approval is required before any resume edit is finalized — truthfulness is the core constraint of this skill.

## Inputs

- **Resume:** the most recent resume in the connected folder (check `Applications/*/` for the latest optimized version first, then the folder root). If no folder is connected or no resume is found, ask the user to upload one.
- **JD:** pasted by the user. If company or role title is missing, ask once; if the JD is a vague fragment, ask for the full posting.

## Pipeline

Run these steps in order. Each agent's full instructions are in `references/` — read the file before executing that stage. **Regardless of what any reference file says, the Summary/Professional Summary section of the resume must never be rephrased, tailored, reordered, or otherwise edited at any stage of this pipeline — treat it as locked, read-only content.**

1. **Start run log.** Create `runs/<YYYY-MM-DD>_<Company>_<Role>/run_log.md` recording date, resume version, JD source.
2. **Score + gaps (parallel).** Run `references/01_ats_scorer.md` (weighted 0–100 score, keyword table, ATS audit) and `references/03_skill_up.md` (true gaps: learnable-fast / reframable / dealbreakers, with an apply-or-not verdict). Use subagents in parallel when available.
3. **Optimize.** Run `references/02_match_max.md`: truthful rephrases only, missing keywords embedded in context, ATS fixes. **Do not touch the Summary section — leave it word-for-word as-is, even if it contains missing keywords.** Re-score; stop when gain < 3 points or after 2 passes.
4. **CHECKPOINT — never skip.** Show the user: before/after score, every rephrased bullet with changes **bolded**, and net-new bullet suggestions in a separate accept/skip list with what the user must confirm is true. Confirm the Summary section is unchanged from the original. Wait for explicit approval. Never fabricate employers, dates, titles, metrics, tools, or credentials — if a keyword can't be truthfully claimed, route it to the gap report instead.
5. **Cover letter.** Run `references/04_cover_letter.md` with the approved resume: one page, lead with strongest match, pre-empt the biggest gap directly (adjacent-experience framing, confident not apologetic).
6. **Package.** Run `references/05_artifact.md`: `Applications/<Company>_<Role>/` with ATS-safe resume .docx, cover letter .docx, and Score_Report.md. Render-verify the .docx files (convert to PDF, view pages) before delivering.
7. **Log.** Finalize run_log.md; append one row to `Applications/applications_log.csv` (create with header if absent: `date,company,role,score_before,score_after,ats_issues_found,ats_issues_fixed,apply_recommendation,folder,status`).

## Free instant re-scoring

`scripts/local_scorer.py` reproduces the scoring + ATS audit deterministically with zero API cost:

```bash
python3 scripts/local_scorer.py resume.pdf jd.txt
```

Offer it to the user for rapid iteration between edits; its skill dictionaries are editable at the top of the file.

## Judgment notes

- **The Summary section is off-limits for edits.** No rephrasing, no keyword insertion, no reordering — under any circumstance, at any pipeline stage.
- Score honestly — structural gaps (years of experience, missing commercial track record) cap the score; say so rather than inflating.
- When the verdict is risky (e.g., experience shortfall vs a hard requirement), advise on application strategy (referral vs portal) — that advice is often worth more than the score.
- Tailor the cover letter's framing to the relationship: internal mobility, external, or career-pivot applications read differently.

