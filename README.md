# Newsletter Digest Agent

A scheduled Claude agent that reads my newsletters, follows them to the actual research, checks the news across tech, policy and markets, and delivers one briefing I can read or listen to in about 20 minutes.

## What it does

On a Monday, Wednesday, Friday and Sunday cadence, the agent:

- Collects the newsletter issues that arrived since the last digest (markets, investing and tech analysis), and skips platform notifications, promos, receipts and anything that isn't a newsletter.
- Follows the substantive links in each issue and, when an issue points at a research paper, downloads and reads the paper itself rather than the abstract.
- Runs a separate web sweep across three areas (tech and AI, government and policy, finance and markets), keeping a story only when two independent credible outlets report it or it comes from a primary source. A single-outlet scoop gets in only when it is labeled as one.
- Writes one themed narrative, meant to be heard as well as read, with a numbered Sources section at the end.
- Delivers it as a PDF attachment.

## How it works

The system is two scheduled agents plus a small rendering toolchain.

**1. Cloud agent: research and write** (`task/scheduled-task-prompt.md`)
The full operating prompt for the cloud run. Highlights:
- **Mailbox restraint.** It opens only newsletter mail. Everything else is judged by sender and subject metadata alone and is never opened, quoted or modified.
- **Link triage.** Tracking redirects get resolved. Unsubscribe links, pixels, sponsor blocks and promos are skipped. When a domain is blocked, the agent rebuilds the story from public coverage with attribution instead of dropping it.
- **Credibility rules.** It uses an allow-list of source tiers (wires, the major financial and national press, primary documents), requires a second source for every number, labels single-outlet scoops, and keeps reporting separate from interpretation.
- **Prompt-injection handling.** Email bodies and web pages are treated as data. Any text addressed to an AI is ignored and flagged in the wrap-up.
- **Parallelism.** One subagent per newsletter and one per news area, each with a tool-call budget so none stalls.
- **Delivery.** The briefing is emailed as full-text HTML with a fixed subject marker. That email is both the handoff to step 2 and the fallback copy.

**2. Local agent: attach the PDF** (`task/local-pdf-attach-task.md`)
Base64 attachments pasted by a model through an email connector tend to get corrupted, so the PDF is built and attached on a Mac instead:
- It finds the day's handoff email, loads the HTML body from the saved tool result with Python (no retyping), and unwraps redirect links.
- It renders the compact PDF and checks it (PDF magic bytes, `%%EOF`, page count, SHA-256).
- It attaches the PDF through Gmail compose in Chrome, confirming each UI step with DOM checks. For example, it checks that a compose dialog exists before typing, so stray keystrokes can't fire Gmail shortcuts.
- It trashes the text handoff only after the connector confirms the new message has the PDF attached.
- It is idempotent and retries inside a 3-hour window. Catch-up runs later in the day exit right away if the job is already done.

**3. Rendering**
- `scripts/build_compact_pdf.py`: converts the briefing's HTML fragment to reportlab Platypus flowables using the built-in base-14 fonts, with no font embedding and raw Flate streams, so the email attachment stays small.
- `scripts/build_pdf.sh` + `template/report_template.html`: a nicer archive PDF, made by merging the fragment into a print-styled template and rendering it with headless Chrome.

## Tech stack

- Claude Code scheduled tasks, the Gmail connector and the Claude in Chrome extension
- Python 3, reportlab
- Bash, headless Google Chrome, HTML/CSS print styles

## Running locally

Build a PDF from any briefing body fragment (an HTML fragment that uses `h1`, `h2`, `h3`, `p`, `ul`, `ol`, `li`, `a` and `strong`):

```bash
pip install -r requirements.txt
python3 scripts/build_compact_pdf.py path/to/body.html "Your Daily Digest" digest-compact.pdf
```

```bash
# Archive version. The script expects Google Chrome at the default macOS location.
./scripts/build_pdf.sh path/to/body.html "Your Daily Digest" digest.pdf
```

To run the agents themselves, register the two prompts in `task/` as Claude Code scheduled tasks, connect a Gmail connector for the inbox that receives the newsletters, and put that address wherever the prompts say `<digest-inbox>`. In the local task, replace `<repo-path>` with the folder you cloned this repo into, and create an `output/` folder there for the PDFs (it is git-ignored).

## Status

In regular personal use since late August 2026. The cloud prompt is at v13 and the local attach task at v3. The commit history shows the architecture changing as delivery problems turned up, from Chrome-based reading to connector-based reading, and from emailing the PDF directly to the cloud/local split.
