# Assets

Diagrams, covers, and snippet files referenced by published content.

**Nothing in an article is pasted inline.** Figures live here and are referenced,
so the same figure can serve several outputs and a correction propagates once.

---

## Layout

```text
assets/
├── figures/     Rendered figures used in articles (PNG)
└── source/      Original source files for the figures above
```text
Keep the source file. A PNG exported from an SVG cannot be corrected; the SVG
can.

---

## Sourcing rules

Every figure is one of two kinds, and the kind determines the credit line.

**Third-party figures** come from the project's own repository, usually under its
licence. Credit them with the exact file path and the project's licence, and
check the licence permits reuse before publishing. Do not restyle them — a
modified vendor diagram is neither their figure nor yours.

**Self-drawn figures** are yours. **Label them as such** in the article. Do not
place them next to vendor figures in a way that implies they came from the same
source; a reader will assume every diagram in a technical piece is the project's
own.

Both kinds are in `figures/`:

| File | Kind | Credit |
| --- | --- | --- |
| `openshell-system-architecture.png` | Third-party | NVIDIA OpenShell repository, `docs/images/openshell-system-architecture.svg`, Apache-2.0 |
| `openshell-sandbox-enforcement.png` | Third-party | NVIDIA OpenShell repository, `docs/images/openshell-sandbox-enforcement.svg`, Apache-2.0 |
| `agent-capability-surface.png` | Self-drawn | Author diagram. **Not** a NVIDIA figure. |

---

## Covers

Covers are platform-specific and are not reused across platforms: aspect ratio,
type size, and safe area differ, and a single source stretched to three
platforms looks wrong on at least one of them.

Naming: `cover-<platform>-<aspect>.png`, e.g. `cover-wechat-16x9.png`.

---

## Snippets

Code that a reader might run belongs in a file rather than in a code block, so it
can be copied without transcription errors and so it can be tested.

```text
assets/snippets/<project>/<topic>.<ext>
```text
Keep them runnable. A snippet that does not run is documentation, and at that
point it belongs in the article prose instead.
