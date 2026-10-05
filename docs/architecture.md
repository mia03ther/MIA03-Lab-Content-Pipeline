# Architecture

This document explains why the pipeline is split the way it is. The stage list
lives in [`workflow.md`](workflow.md); this is about the structural decisions
behind it.

---

## The core problem

An AI assistant is very good at two things: reading a lot of text quickly, and
producing prose that matches a described shape. It is correspondingly bad at one
thing: knowing which of its sentences are load-bearing.

So the failure mode of "give the model the repo and ask for an article" is not
usually invention. It is **structurally sound prose resting on unverified
premises**, where each sentence is individually plausible and the cumulative
weight of them is not supported by anything.

Tightening prose does not fix this. Neither does a longer prompt, and neither
does asking the model to "be careful". The premises have to be checked at the
point of reading, by a process, which is what this framework supplies.

---

## Three principles

### 1. Separate verification from generation

Research and writing are different cognitive jobs with different failure modes.
Verification rewards scepticism and produces nothing publishable. Generation
rewards fluency and produces prose that fills the shape you gave it. Asking one
pass to do both means the fluency mode wins, because it is the one that feels
like progress.

Hence a research stage that ends in a claim ledger, and a writing stage that
takes that ledger as its only factual input.

### 2. Make state explicit and file-based

Every stage boundary is a file on disk. Nothing important lives only in a
conversation.

This gives three things for free:

- **Recoverability.** A long run can be resumed from any stage without
  re-reading the repository.
- **Reviewability.** A claim can be checked without reading the article around
  it.
- **Portability.** The note outlives the tool, the assistant, and the provider.
  A framework that cannot outlive its model is a script with extra steps.

### 3. Fail closed at the ledger

The claim ledger is a hard gate. A claim without a source is not "probably
fine" — it is marked `unverified` and is not available to the writing stage.

The alternative is a soft convention, where writers are *encouraged* to cite.
Encouragement is not a mechanism, and a convention that is cheap to ignore gets
ignored under deadline.

---

## Why these stages and not others

**Discovery is separate from research.** They optimise opposite quantities.
Discovery wants breadth and fast rejection; research wants depth and slow
acceptance. Merging them produces long notes about projects that should have
been dropped in ten minutes.

**Analysis sits between research and writing.** Research produces facts; writing
produces sentences; the argument that connects them is a distinct piece of work
that tends to get skipped. Putting it in its own stage makes it visible, and
makes it reviewable before it is buried under 3000 words.

**The editor pass runs last and touches only packaging.** Title, summary, and
social copy are selection problems. Optimizing them in the same pass as the body
reliably produces headlines that outrun the article, because the two goals pull
in opposite directions at exactly the moment of writing.

**Assets are a separate stage.** Diagrams and covers are derived from the
analysis, not the prose. Deriving them from finished prose means redrawing them
whenever a paragraph moves.

---

## Why templates instead of an orchestrator

The obvious alternative is a Python package that takes a repository URL and
emits drafts. This project deliberately does not do that, for four reasons.

**The selection step cannot be automated.** Deciding a project is worth
researching requires knowing what the reader already knows. That is a
judgement, and automating a judgement produces confident bad output.

**Tooling hides its decisions.** A CLI that produces an article gives no signal
about which sentence came from a README and which came from reading the source.
Templates make the seam visible because you filled it in.

**It would expire.** An orchestrator depends on a model API, and API behaviour
changes. Markdown templates outlive it.

**The audience is a person who wants to get better at this.** That person needs
to see the method, not submit to it.

The consequence is honest: this project does not make you faster on the first
project. It makes the second one defensible.

---

## Layering

```text
┌──────────────────────────────────────────────┐
│  Stage 5  Editor         packaging only      │
├──────────────────────────────────────────────┤
│  Stage 3–4  Writing      platform adaptation │
├──────────────────────────────────────────────┤
│  Stage 2    Analysis     mechanism + tradeoff│
├──────────────────────────────────────────────┤
│  Stage 1    Research     claims + sources    │  ← ledger lives here
│              ↕ gated                              │
│  Stage 0    Discovery    selection            │
└──────────────────────────────────────────────┘
```text
Each layer depends only on the layer below, and each layer's output is the next
layer's input. There are no side channels, which means a stage can be re-run in
isolation once its inputs are unchanged.

---

## Adding a stage

A stage earns its place by doing something the existing stages cannot.

1. Write down its input artifact and its output artifact.
2. State the exit criterion as a property of the output file, not a feeling.
3. Update `workflow.md`.
4. Update `scripts/validate_structure.py` if it added a required file.
5. Extend `examples/` if the new stage needs a worked demonstration.

Stages that only reformat text, or that exist because a particular platform
demands it, do not need a stage — they need a template. Keep the count small.
A pipeline with fifteen stages is a workflow nobody finishes.
