# MIA03 Lab Content Pipeline

An AI-powered workflow for researching open source projects and generating
developer-focused technical content.

Most technical writing about open source falls into one of two failure modes: it
is a README restatement dressed up as analysis, or it is opinion with the facts
swept under the rug. This project exists to make the first one hard to produce
and the second one easy to avoid.

MIA03 Lab Content Pipeline is a **workflow framework**, not a code generator.
It defines the stages between *I found an interesting repository* and *I
published something a developer can trust*, the templates that carry state
between those stages, and the agent briefs that tell an AI assistant what good
looks like at each step.

---

## Why this project exists

Researching an unfamiliar project well is slow. Writing it up well is slower,
because the writing is where the shortcuts are invisible.

The failure is rarely a hallucination. It is subtler than that:

- Architecture described from the README instead of the code.
- Innovation credited to the project that was actually inherited.
- Competitors compared from blog posts rather than changelogs.
- An article that reads fluently and contains nothing a reviewer can check.
- Security claims repeated with no threat model behind them.

Every one of those is a process failure, not a writing failure. So this project
attacks the process. Each stage has an explicit input, an explicit output, and a
rule about what you are not allowed to claim yet.

The working assumption is narrow and stated up front: **an AI assistant is
excellent at accelerating a process a human already knows how to run, and
actively harmful when asked to run one you have not specified.** The templates
here are that specification. They are the deliverable.

---

## Features

- **Six-stage pipeline** from project discovery to shipping assets, with a
  defined hand-off artifact between every stage.
- **Three agent briefs** — research, writing, editor — that separate the jobs
  most assistants blur together.
- **Fact ledger discipline.** Research notes carry a claim ledger with a source
  and a confidence level per claim, so unverified assertions are visible before
  they reach an article.
- **Platform templates** for WeChat longform, X threads, and devlogs, all
  derived from the same research note so the three outputs cannot contradict
  each other.
- **A worked example** (`examples/openshell-analysis.md`) produced by running
  the pipeline against NVIDIA OpenShell, with every source traceable.
- **CI** that lints Markdown, checks links, and validates repository structure,
  so a broken template fails the build instead of the article.

What this project deliberately does **not** do: it does not fetch repositories
for you, does not call a model API, and does not publish anything. Those are
integration points, not the hard part.

---

## Workflow

```text
GitHub Project Discovery
        │
        ▼
   Research Notes  ──────────►  research/templates/github-project-analysis.md
   (fact ledger, sources, confidence levels)
        │
        ▼
 Technical Analysis
   (architecture, mechanism, trade-offs, what is genuinely new)
        │
        ├──────────────────────────────┐
        ▼                              ▼
 Article Draft                     Platform Drafts
 writing/templates/                writing/templates/x-thread.md
 wechat-longform.md                writing/templates/devlog.md
        │                              │
        ▼                              │
 Editor Pass  ◄────────────────────────┘
 prompts/editor-agent.md
 (title, summary, social copy, SEO)
        │
        ▼
 Publishing Assets  ──────────►  assets/
 (cover, diagrams, code snippets, reference list)
```text
Each arrow is a file on disk, not a conversation. If a stage cannot be
summarized into its output template, that stage did not actually finish.

### Why the editor pass is separate

Title, summary, and social copy are selection problems, not writing problems.
Doing them in the same pass as the body reliably produces an article whose
headline promises something the body does not deliver. The editor brief takes
the finished draft as input and only optimizes the packaging.

Full stage-by-stage detail, including exit criteria:
[`docs/workflow.md`](docs/workflow.md).

---

## Quick Start

Requirements: a clone of this repository, an AI assistant that can read a
Markdown brief, and a text editor. There is no install step.

```bash
git clone https://github.com/mia03ther/MIA03-Lab-Content-Pipeline.git
cd MIA03-Lab-Content-Pipeline
```text
**1. Pick a project.** Start from something you can actually read the source of.

**2. Copy the research template and fill it in.**

```bash
mkdir -p research/active
cp research/templates/github-project-analysis.md \
   research/active/<project-name>.md
```text
Work top to bottom. The claim ledger at the bottom is the part that matters —
if you cannot fill in a source for a claim, it does not go in the article.

**3. Hand the note to the writing agent.** Read `prompts/writing-agent.md` and
use it as the system brief for your assistant. Paste the completed research
note as input.

**4. Format for the target platform.** Start from the matching template in
`writing/templates/`. All three consume the same research note, so the outputs
stay consistent by construction.

**5. Run the editor pass.** `prompts/editor-agent.md` handles title,
summary, social copy, and metadata.

**6. Collect assets.** Diagrams, cover images, and snippet files go in
`assets/`, referenced from the article rather than pasted in.

### Validating your work

The same checks CI runs:

```bash
python scripts/validate_structure.py
```text
It verifies the required directories and templates exist and that each template
declares its required sections. If it passes locally, CI will pass.

---

## Example

[`examples/openshell-analysis.md`](examples/openshell-analysis.md) is a
completed research note for **NVIDIA OpenShell**, an agent security runtime.

It is included because it exercises the parts of the framework that are hardest
to get right:

- separating *what the project does* from *why that is a response to a specific
  risk*
- reading a security tool's own stated limits instead of paraphrasing its
  marketing
- noting where a capability is **not** covered, which is the part most write-ups
  leave out

It follows the template in `research/templates/github-project-analysis.md`, so
you can diff a real note against the blank form.

---

## Repository Layout

```text
.
├── docs/
│   ├── workflow.md              Stage-by-stage input/output/exit criteria
│   └── architecture.md          Why the pipeline is split this way
├── research/
│   └── templates/
│       └── github-project-analysis.md
├── writing/
│   └── templates/
│       ├── wechat-longform.md
│       ├── x-thread.md
│       └── devlog.md
├── prompts/
│   ├── research-agent.md
│   ├── writing-agent.md
│   └── editor-agent.md
├── examples/
│   └── openshell-analysis.md
├── assets/                      Diagrams, covers, snippet files
├── scripts/
│   └── validate_structure.py
└── .github/workflows/ci.yml
```text
Further reading: [`docs/workflow.md`](docs/workflow.md),
[`docs/architecture.md`](docs/architecture.md).

---

## Contributing

This is a framework, and frameworks rot through undocumented drift. If you add a
stage, a template, or an agent brief:

1. Update `docs/workflow.md` in the same change.
2. Update `scripts/validate_structure.py` if you added or renamed a required
   file.
3. Keep templates honest — a template that permits unsupported claims is worse
   than no template.
4. Run `python scripts/validate_structure.py` and let CI do the rest.

Content contributions under `examples/` are welcome. Claims in an example are
held to the same standard as claims in the framework: source or cut.

---

## Roadmap

Ordered by what unblocks the most work, not by what is most fun to build.

- [x] Core framework: workflow, templates, agent briefs
- [x] Worked example (NVIDIA OpenShell)
- [x] Structure and link CI
- [ ] Project shortlist file with explicit selection criteria and a refresh
      cadence
- [ ] Reader-mode notes: how to adapt the same note for a reader who has not
      used the tool, versus one who has
- [ ] Diagram guidance covering which relationships deserve a figure and which
      deserve a table
- [ ] Revision pass template for updating a published article when upstream
      ships a breaking change
- [ ] Optional local tooling for archiving research notes with source snapshots
- [ ] Evaluation set: one research note scored against a fixed rubric, to make
      the framework's claims about quality falsifiable

Non-goals: a hosted service, a model-agnostic orchestration framework, and
automated publishing. Each would add moving parts without improving the part
that is actually hard.

---

## License

MIT — see [`LICENSE`](LICENSE).
