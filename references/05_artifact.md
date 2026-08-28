# Agent 05 — Artifact Agent

**Input:** All upstream outputs (approved resume, cover letter, scores, gap report)
**Output:** Packaged deliverables + logs

## Package per job
Create `Applications/<Company>_<Role>/`:
- `<username>_resume.docx` — approved edited resume (use docx skill; ATS-safe single-column format). Derive `<username>` from the candidate's full name on their resume, lowercased with underscores (e.g., "Jane Doe" → `jane_doe_resume.docx`); if no name is found, fall back to `candidate_resume.docx`.
- `Cover_Letter.docx`
- `Score_Report.md` — before/after total + bucket scores, keyword table (matched/missing), ATS fixes applied, accepted/skipped suggestions, gap report summary

## Logging (every run, no exceptions)
1. Finalize `runs/<timestamp>_<Company>_<Role>/run_log.md` — full agent outputs, decisions, user approvals
2. Append row to `Applications/applications_log.csv`:
   `date,company,role,score_before,score_after,ats_issues_found,ats_issues_fixed,apply_recommendation,folder,status`
   (status starts as `prepared`; user updates later to applied/interview/offer/rejected)

## Final step
Present the three deliverable files to the user and report: before → after score, one-line gap summary.
