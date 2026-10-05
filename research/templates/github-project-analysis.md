# Research Note — <project-name>

> Fill every section. If a section cannot be filled, that is a finding: write
> `not found` and say what you looked at. Do not delete the heading.
>
> The Claim Ledger is the hard gate. A claim without a source is `unverified`
> and is not available to the writing stage.

**Repository:** <url>
**Analyzed at version / commit:** <tag, release date, or SHA>
**Analyst:** <name>
**Date:** <YYYY-MM-DD>

---

## 1. Project Background

<!--
One paragraph. What the project is, in the authors' own framing first, then
yours. Who ships it and who maintains it.
-->

**In the project's own words:**

**In plain language:**

**Maintainer / organization:**

**First release / current version:**

---

## 2. Problem

<!--
The problem, not the solution. Who has this problem, how often, and what it
costs them today.

If you cannot name a specific user with this problem, the project may be
solution-shaped. Say so here.
-->

**Who has this problem:**

**How it shows up today:**

**Why existing approaches fall short:**

**Is this a new problem or a newly-recognized one?**

---

## 3. Architecture

<!--
Components, their boundaries, and — most important — who decides what.
Do not paraphrase the README's component list; determine what each part
actually does.
-->

### Component map

| Component | Responsibility | Trust level | Decides |
| --- | --- | --- | --- |
| | | | |

### Boundaries

**Where is the boundary drawn, and what enforces it?**

**What can reach across a boundary, and under what condition?**

**Which boundary is the load-bearing one?**

### Request / data flow

<!-- Numbered. The actual path, end to end. -->

1.
2.
3.

### Key mechanisms

<!--
For each significant mechanism: the problem it solves, why this mechanism
instead of the obvious alternative, and what it makes hard.
-->

**Mechanism 1:**

- Problem it solves:
- Why this and not the obvious alternative:
- What it makes easy:
- What it makes hard:
- If removed:

---

## 4. Technical Insights

<!--
What is genuinely new here, versus inherited. Naming prior art is the single
highest-value part of this section.
-->

### What is genuinely new

**What is inherited or conventional:**

**What the README implies that the implementation does not do:**

---

## 5. Prior Art and Competitors

<!--
Compare on a real axis. "Project A is better than B" is not an axis.
Fill in the axis, then place each project on it.
-->

**Comparison axis:**

| Project | On this axis | Different in |
| --- | --- | --- |
| | | |

**Where this project is genuinely weaker:**

**Where a competitor is genuinely stronger:**

---

## 6. Stated Limits and Gaps

<!--
The project's own documented limitations, and the coverage gaps you found.
This section is routinely skipped and it is the reason readers trust the rest.
-->

**Documented by the project:**

**Gaps found in review:**

**Who should not use this, and why:**

---

## 7. Adoption Reality

<!--
Not the pitch. What it would actually cost a team to start using.
-->

**Prerequisites:**

**Migration / integration cost:**

**Operational burden:**

**Who has a reason to adopt it today:**

---

## Claim Ledger

<!--
The gate. Every technical claim the article might make gets a row.
`confidence` is one of: confirmed (read the implementation or primary doc),
documented (authors state it, implementation not checked), unverified (not
checked — not usable in an article).

Do not add a claim here to justify a sentence you already wrote.
-->

| # | Claim | Source | Confidence | Checked at |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

## Reader Takeaways

<!--
What a developer who reads the note should be able to do or decide afterwards.
If this list is empty, the note is not finished regardless of how complete it
looks.
-->

**Can now do:**

**Can now evaluate:**

**Should still be careful about:**

---

## References

<!--
Deduplicated, with titles and access dates. Prefer primary sources: the
repository, official documentation, the authors' own technical writing.

A project README quoting a third party is not a source.
-->

1. <title> — <url> (accessed <YYYY-MM-DD>)
2.

---

## Open Questions

<!--
What you could not resolve, and what would resolve it. These become follow-up
work, and they are also the honest edge of the final article.
-->

-
