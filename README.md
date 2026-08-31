# Email Newsletter Digest Agent

An automated agent that reads long newsletters in Gmail, follows the credible links inside them (including linked reports), and produces an engaging PDF briefing that takes about 15 to 20 minutes to read. The PDF is emailed automatically to <digest-inbox>.

## Schedule

Runs every Monday, Wednesday, Friday, and Sunday at 7:00 AM (Asia/Shanghai time) via the Claude Code local scheduler. The task definition lives at `~/.claude/scheduled-tasks/newsletter-digest/SKILL.md`, and a copy of the prompt is kept in this repo at [task/scheduled-task-prompt.md](task/scheduled-task-prompt.md).

Note: the scheduler runs while the Claude Code desktop app is open. If the app is closed at fire time, the task runs on next launch.

## How a run works

1. Search Gmail for newsletters received since the last digest (roughly the last 2 to 3 days), skipping receipts, alerts, spam digests, and pure ad blasts.
2. Read each newsletter in full.
3. Extract every link and classify it. Ads, unsubscribe links, tracking pixels, social icons, and scammy-looking links are skipped. Substantive links (articles, event pages, program pages, linked reports and PDFs) are fetched and read, including multi-page PDF reports.
4. Write one long-form report (3,800 to 4,500 words, about 15 to 20 minutes of reading) in engaging plain-English paragraphs, organized by theme, with no em dashes, and a Sources section at the end listing every newsletter and URL that was read.
5. Render the report to PDF using the HTML template in `template/` and headless Google Chrome.
6. Email the PDF as an attachment to <digest-inbox> and save a copy in `output/`.

## Repo layout

- `template/report_template.html` — the styled HTML shell the report body is injected into (controls the PDF's typography and layout)
- `scripts/build_pdf.sh` — merges a report body HTML fragment into the template and renders the PDF with headless Chrome
- `task/scheduled-task-prompt.md` — the full prompt the scheduled agent runs on
- `output/` — generated digest PDFs

## Building a PDF manually

```bash
./scripts/build_pdf.sh path/to/body.html "Your Newsletter Digest" output/digest.pdf
```
