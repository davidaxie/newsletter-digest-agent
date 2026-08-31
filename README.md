# Email Newsletter Digest Agent

An automated agent that reads the newsletters in David's personal Gmail (<digest-inbox>), follows the credible links inside them (including linked research reports), and produces an engaging, importance-weighted PDF briefing of up to about 40 minutes of reading. The PDF is emailed automatically to <digest-inbox>.

## Schedule

Runs every Monday, Wednesday, Friday, and Sunday at 7:00 AM (Asia/Shanghai time) via the Claude Code local scheduler. The task definition lives at `~/.claude/scheduled-tasks/newsletter-digest/SKILL.md`, and a synced copy of the prompt is kept in this repo at [task/scheduled-task-prompt.md](task/scheduled-task-prompt.md).

Note: the scheduler runs while the Claude Code desktop app is open. If the app is closed at fire time, the task runs on next launch.

## Sources

Content comes ONLY from the personal Gmail inbox (Morning Brew, The Idea Farm, Bloomberg, Luma DC and SF, the Claude Code weekly, and similar). The Georgetown mailbox (<digest-inbox>) is never read for content. Reading paths, in order of preference:

1. A Gmail connector for <digest-inbox> (not yet connected as of 2026-08-31; connecting it at claude.ai connector settings makes runs fully robust).
2. The Claude in Chrome extension, which is signed into the personal account (requires Chrome running; extraction recipe documented in the task prompt).
3. If neither is available, the run emails a notice instead of a digest.

## How a run works

1. Collect newsletters received since the last digest (roughly the last 2 to 3 days), skipping receipts, alerts, and pure promos.
2. Read each newsletter in full and follow its substantive links. Ads, unsubscribe links, tracking pixels, sponsor blocks, and scammy links are skipped. Curated research reports get found and actually read (public copies, coverage, PDFs); paywalled journalism gets reconstructed from public coverage with attribution.
3. Write one long-form report: importance-weighted, up to 40 minutes of reading (9,500 words max), engaging plain-English paragraphs, no em dashes, organized by theme, deadlines and dates bolded, full Sources section at the end. Unimportant material is dropped entirely, never padded.
4. Render two PDFs: a pretty archive version (headless Chrome via `template/` + `scripts/build_pdf.sh`) and a compact email version (`scripts/build_compact_pdf.py`, reportlab, no font embedding).
5. Commit and push to this repo first, then email the compact PDF as an attachment with a GitHub fallback link in the body.
6. Verify the sent attachment byte-for-byte (SHA-256 round trip through the Gmail API) and resend or fall back to link-only delivery if corrupted.

## Repo layout

- `template/report_template.html` — the styled HTML shell for the archive PDF
- `scripts/build_pdf.sh` — pretty PDF via headless Chrome
- `scripts/build_compact_pdf.py` — compact PDF via reportlab (safe to email inline)
- `task/scheduled-task-prompt.md` — the full prompt the scheduled agent runs on
- `output/` — generated digest PDFs and their HTML bodies

## Building a PDF manually

```bash
./scripts/build_pdf.sh path/to/body.html "Your Newsletter Digest" output/digest.pdf
```

```bash
python3 scripts/build_compact_pdf.py path/to/body.html "Your Newsletter Digest" output/digest-compact.pdf
```
