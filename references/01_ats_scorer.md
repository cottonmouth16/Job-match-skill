# Agent 01 — ATS Scorer

**Input:** Resume + JD
**Output:** Score breakdown + prioritized issue list (written to run log)

## Step 1 — Extract JD keywords
Categorize every requirement in the JD:
- Hard skills (e.g., product strategy, A/B testing, SQL, roadmapping)
- Tools/platforms (e.g., Jira, Amplitude, Figma)
- Title/seniority + years of experience
- Certifications/education
- Soft skills (e.g., stakeholder management, communication)
Mark each as REQUIRED or PREFERRED based on JD language.

## Step 2 — Score match (0–100)
| Bucket | Weight | Method |
|---|---|---|
| Hard skills | 40% | % of JD hard skills present in resume (exact or close synonym). REQUIRED items count double vs PREFERRED. |
| Tools/platforms | 25% | Same method |
| Title/seniority | 20% | Title alignment + years of experience vs asked |
| Soft skills | 15% | Present in resume context (not just listed) |

Report per-bucket score, total score, and full keyword table: keyword | category | required/preferred | found in resume (yes/no/partial) | where.

## Step 3 — ATS compliance audit
Check and list issues with severity (High/Med/Low):
- Parseable single-column layout; no tables, text boxes, graphics, headers/footers with key info
- Standard section headers (Experience, Education, Skills, Summary)
- Keywords appear in context (bullets), not only in a skills list
- Consistent date format (MMM YYYY); no gaps unexplained
- Standard fonts; file naming `<username>_resume.docx` (username = candidate's full name, lowercased with underscores)
- Contact info in body text, not header/footer

## Output format
```
TOTAL SCORE: NN/100
Hard skills: NN/40 | Tools: NN/25 | Title/seniority: NN/20 | Soft skills: NN/15
KEYWORD TABLE: ...
ATS ISSUES: [severity] issue → fix
```
