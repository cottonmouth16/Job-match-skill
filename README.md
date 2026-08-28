# Job Match Skill

A Claude Skill that turns a resume + job description into a scored, ATS-optimized application package — through a five-stage pipeline with a hard truthfulness gate before any resume edit ships.

Built for [Claude](https://claude.ai) (Claude Code, Claude Desktop, Cowork). Drop this folder into your skills directory and Claude runs the whole pipeline end to end: score, gap-analyze, optimize, get your sign-off, write the cover letter, and package the final files.

## What it does

Give Claude a resume and a job posting, and it runs five agents in sequence:

1. **ATS Scorer** — weighted 0–100 match score across hard skills, tools, title/seniority, and soft skills, plus an ATS-compliance audit (missing sections, formatting issues, keyword gaps).
2. **Skill Up** (runs in parallel with the scorer) — sorts real gaps into three buckets: learnable fast (with a named course/cert and time estimate), reframable from adjacent experience, or genuine dealbreakers — with an honest apply-or-not verdict.
3. **Match Max** — rewrites resume bullets to truthfully surface missing keywords in context. Never invents employers, dates, titles, metrics, tools, or certifications. Net-new bullets are suggested separately and require individual approval.
4. **Checkpoint** — Claude shows you the before/after score, every changed bullet with edits bolded, and a separate accept/skip list for new bullets. **Nothing is finalized without your explicit approval.**
5. **Cover Letter + Packaging** — a one-page cover letter that leads with your strongest match and pre-empts the biggest gap, followed by a packaged `Applications/<Company>_<Role>/` folder with an ATS-safe `.docx` resume, cover letter, and a full score report.

Every run is logged to `runs/<date>_<Company>_<Role>/run_log.md` and appended to a running `Applications/applications_log.csv` so you can track every application you've sent.

### The one rule that never bends

The **Summary/Professional Summary section of your resume is locked** — no stage of the pipeline may rephrase, reorder, or touch it, even if it contains keywords the JD is looking for. Nothing is ever fabricated. If a keyword can't be truthfully claimed, it goes into the gap report instead of the resume.

## How the scoring works (and what it isn't)

This is not a reverse-engineered Workday/Taleo/iCIMS algorithm — no external tool can replicate a specific vendor's internal, proprietary scoring, because that logic isn't public and varies by company and configuration.

What it does instead: approximate the same *categories* of things ATS platforms parse and recruiters filter on — keyword/skill match, standard section headers, date formatting, contact-field detection, structural red flags. That's a directional, ATS-friendliness estimate, not a readout of any specific system's score.

The tradeoff is transparency. The keyword dictionaries in `scripts/local_scorer.py` are plain, editable Python — you can see exactly why a score landed where it did and tune it, unlike black-box paid scorers. Treat the score as a proxy for "would a keyword/structure-based filter flag this," not a guarantee of what any one employer's system will output.

## Repo contents

```
job-match-skill/
├── SKILL.md                     # Entry point Claude reads to run the pipeline
├── references/
│   ├── 01_ats_scorer.md         # Agent 1: scoring + ATS audit instructions
│   ├── 02_match_max.md          # Agent 2: truthful resume optimization rules
│   ├── 03_skill_up.md           # Agent 3: gap analysis instructions
│   ├── 04_cover_letter.md       # Agent 4: cover letter structure/rules
│   └── 05_artifact.md           # Agent 5: packaging + logging instructions
└── scripts/
    └── local_scorer.py          # Standalone, zero-token scorer (see below)
```

## Installation

**Claude Desktop / Claude Code (recommended):**

1. Download this repo as a `.zip`, or clone it.
2. Zip the folder as a single skill (or place the folder as-is) into your Claude skills directory — e.g. `~/.claude/skills/job-match/` for Claude Code, or upload it as a Skill file if your Claude client supports importing `.skill` packages.
3. Restart/refresh your Claude session so it picks up the new skill.

**Manual / any Claude client:**

You can also just paste the contents of `SKILL.md` (and reference it pulls in `references/*.md` as needed) directly into a conversation if your client doesn't support skill folders — Claude will follow the same pipeline.

## Usage

Once installed, just talk to Claude naturally:

- "Run job match on this JD" *(paste the job description)*
- "Am I a good fit for this role?"
- "Score my resume against this posting"
- "Write me a cover letter for this job"

Claude will look for your most recent resume (in a connected folder or an upload), ask for the job description if you haven't pasted one, and walk you through the five stages — pausing at the checkpoint for your approval before finalizing anything.

### Free local re-scoring (zero API cost)

`scripts/local_scorer.py` reproduces the Agent 1 scoring + ATS audit deterministically, offline, with no LLM calls — useful for rapid iteration between edits:

```bash
pip install pypdf   # only needed if scoring a PDF resume
python3 scripts/local_scorer.py resume.pdf jd.txt
python3 scripts/local_scorer.py resume.pdf jd.txt --json results.json
```

The keyword dictionaries (`HARD`, `TOOLS`, `TITLE`, `SOFT`) live at the top of the script and are meant to be edited — extend them for your industry, role level, or the specific JDs you're targeting.

## Design principles

- **Truthfulness over score-maxing.** The pipeline will not inflate a score or fabricate experience to hit a higher match percentage. Structural gaps (years of experience, missing track record) are named honestly, not papered over.
- **Human approval is a checkpoint, not a formality.** Every rephrased bullet is shown with changes highlighted; every suggested new bullet is opt-in, one at a time.
- **Everything is logged.** Each run produces an auditable trail — what was scored, what changed, what was approved — so you can see exactly what went into every application you sent.

## License

MIT — see [LICENSE](LICENSE).
