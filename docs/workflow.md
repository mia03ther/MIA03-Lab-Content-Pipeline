# Workflow

Six stages, each with a defined input, output, and exit criterion. The exit
criterion is the part that matters: a stage is done when its output artifact is
complete, not when you feel you have understood the project.

The governing rule is that **every stage writes a file.** If a stage's only
output is a conversation, the next stage starts from memory, and memory is
where unverified claims enter.

---

## Stage 0 — Project Discovery

**Goal:** decide whether this project is worth researching at all.

**Input:** a candidate repository, a changelog entry, a release note, a
recommendation.

**Output:** a shortlist entry stating the project, the hook, and the reason it
is worth a reader's attention.

Ask three questions before committing:

1. **What changed, and when?** A new major version, a licence change, a
   rewritten architecture. Projects mid-rewrite are more interesting than
   finished ones.
2. **Who currently pays the problem it solves?** If you cannot name a user, the
   technical novelty may be the entire story.
3. **Can the source actually be read?** A 400k-line proprietary monorepo is not
   research material. A small focused repository is.

**Exit criterion:** you can state the problem in one sentence without naming any
solution.

**Anti-pattern:** picking a project because it is trending. Trending is a
selection bias, and it rewards the projects with the best announcement
engineering rather than the best engineering.

---

## Stage 1 — Research Notes

**Goal:** build a factual base with traceable sources.

**Input:** the repository, its documentation, its issue tracker, its release
history, and any primary technical material the authors published.

**Output:** a completed
[`research/templates/github-project-analysis.md`](../research/templates/github-project-analysis.md)
instance.

What to extract:

- What the project claims to be, in the authors' own framing
- The problem it names, and who they name it for
- The actual architecture: components, boundaries, and who decides what
- The mechanism that makes the central claim work
- What is genuinely new versus inherited from prior art
- Comparable projects, and the axis on which they actually differ
- **The project's own stated limits** — security tooling especially tends to
  document what it does not cover, and that is usually the most useful sentence
  in the repository

**Exit criterion:** every row in the claim ledger has either a source URL or an
explicit `unverified` marker.

**Anti-pattern:** concluding from the README. The README describes intent. The
code describes behaviour. When they disagree, the code is what ships.

---

## Stage 2 — Technical Analysis

**Goal:** turn facts into mechanism, and mechanism into trade-offs.

**Input:** the research note.

**Output:** the analysis section of the same note, filled in.

This is where most write-ups quietly fail, because they stop at description.
"X uses sandboxing" is a description. "X enforces the sandbox boundary from
outside the agent process, so the agent's own output cannot influence the
decision" is an analysis.

For each major component, answer:

- What problem does this component exist to solve?
- Why this mechanism rather than the obvious alternative?
- What does it make easy, and what does it make hard?
- What breaks if this component is removed?

**Exit criterion:** you can explain at least one design choice as a trade-off
rather than as a best practice.

**Anti-pattern:** restating documentation with different words. If a reader
could get your paragraph from the project's own docs by running it through a
thesaurus, the paragraph is not earning its place.

---

## Stage 3 — Article Draft

**Goal:** produce the long-form body for a developer audience.

**Input:** the research note.

**Output:** a draft following
[`writing/templates/wechat-longform.md`](../writing/templates/wechat-longform.md).

**Exit criterion:** every technical claim traces to a ledger row, and the
reader can act on at least one specific thing from the piece.

**Anti-pattern:** writing before the ledger is complete. Drafting early feels
productive and produces prose that must later be fact-checked line by line,
which is slower than checking a claim once while reading the source.

---

## Stage 4 — Platform Drafts

**Goal:** adapt, do not re-research.

**Input:** the same research note, plus the long-form draft.

**Output:** drafts from
[`x-thread.md`](../writing/templates/x-thread.md) and
[`devlog.md`](../writing/templates/devlog.md).

All platform outputs derive from the same note. This is deliberate: three
artifacts written from three separate investigations will eventually contradict
each other, and the contradiction is always discovered by a reader.

**Exit criterion:** no claim appears in a platform draft that is absent from the
ledger.

---

## Stage 5 — Editor Pass

**Goal:** optimize packaging. Not content.

**Input:** the finished draft and the research note.

**Output:** final title, summary, social copy, and metadata.

**Scope boundary:** the editor may cut, reorder, and retitle. The editor may not
add a claim that is not in the ledger, and may not soften a stated limit.

**Exit criterion:** the title promises something the body delivers, checked by
reading them against each other rather than by reading the title alone.

**Anti-pattern:** raising engagement metrics with specificity the piece does not
contain. A title that overstates costs you the reader who checks.

---

## Stage 6 — Publishing Assets

**Goal:** collect the non-prose deliverables.

**Input:** the finished draft.

**Output:** files in `assets/`.

- Diagrams for relationships that are genuinely structural
- Cover images sized for the target platform
- Runnable snippet files rather than inline code blocks
- A reference list, deduplicated, with titles and access dates

**Exit criterion:** every asset is referenced from the article, and every
inline code block that exceeds a few lines has moved into a file.

---

## Cross-cutting rules

These apply at every stage.

1. **One claim, one source.** If a fact appears twice, both occurrences point at
   the same ledger row.
2. **Absence of evidence is a finding.** A project not covering a case is worth
   as much as a case it covers, and much more than a hedge.
3. **Quote the maintainers, not the coverage.** A project README quoting a
   third party is not a source.
4. **Version every claim.** Record the version or commit a claim was true at.
   Software claims expire quietly.
5. **Cut on the reader.** If a section does not change what the reader would do
   or believe, it goes — regardless of how much work it was.

---

## Time expectations

Rough, based on one project, and worth treating as an upper bound:

| Stage | First-timer | Note |
| --- | --- | --- |
| Discovery | 15 min | Mostly reading release notes |
| Research notes | 2–4 h | Dominated by reading source, not writing |
| Technical analysis | 1–2 h | The thinking, not the typing |
| Article draft | 2–3 h | Longer if the ledger was skipped |
| Platform drafts | 30–60 min | Cheap, because the note already exists |
| Editor pass | 20 min | Fastest stage per unit of improvement |
| Assets | 30–60 min | Depends on diagram count |

The research note is the expensive stage and the only one that cannot be
skipped. Everything downstream is cheap if it is done, and expensive if it is
skipped.
