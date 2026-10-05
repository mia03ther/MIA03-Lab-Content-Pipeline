#!/usr/bin/env python3
"""Structure validation for MIA03 Lab Content Pipeline.

This repository is a framework of documents, so its only real build artifact is
its own shape: required directories, required templates, required sections
inside those templates, and required example fields. Those are cheap to check and
expensive to lose, because a renamed or gutted template breaks the workflow for
everyone silently.

It checks no prose and no semantics. It cannot tell you whether an example is
good -- only whether the framework that produces examples is still intact.

Usage:
    python scripts/validate_structure.py [--root .] [--quiet]

Exit codes:
    0  structure valid
    1  one or more problems found
    2  bad invocation
"""

import argparse
import os
import re
import sys

# Directories the framework cannot function without.
REQUIRED_DIRS = (
    "docs",
    os.path.join("research", "templates"),
    os.path.join("writing", "templates"),
    "prompts",
    "assets",
    "examples",
    os.path.join(".github", "workflows"),
    "scripts",
)

# Files referenced by the docs, so a rename cannot break the workflow in silence.
REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "docs/workflow.md",
    "docs/architecture.md",
    os.path.join("research", "templates", "github-project-analysis.md"),
    os.path.join("writing", "templates", "wechat-longform.md"),
    os.path.join("writing", "templates", "x-thread.md"),
    os.path.join("writing", "templates", "devlog.md"),
    "prompts/research-agent.md",
    "prompts/writing-agent.md",
    "prompts/editor-agent.md",
    "examples/openshell-analysis.md",
    os.path.join("assets", "README.md"),
    os.path.join(".github", "workflows", "ci.yml"),
)

# A template is a contract: the stages that fill it in look for these headings.
REQUIRED_SECTIONS = {
    os.path.join("research", "templates", "github-project-analysis.md"): (
        "Project Background",
        "Problem",
        "Architecture",
        "Technical Insights",
        "Prior Art and Competitors",
        "Claim Ledger",
        "References",
    ),
    os.path.join("writing", "templates", "wechat-longform.md"): (
        "References",
    ),
    os.path.join("examples", "openshell-analysis.md"): (
        "Project Overview",
        "Research Notes",
        "Technical Breakdown",
        "Key Insights",
        "Limitations",
        "Article Metadata",
        "Claim Ledger",
        "References",
    ),
}

# Markers that must appear somewhere in the text, not necessarily as a heading.
# Used for checklists, which are deliberately inside HTML comments so they never
# reach a rendered article.
REQUIRED_TEXT_MARKERS = {
    os.path.join("writing", "templates", "x-thread.md"): ("SELF-CHECK",),
    os.path.join("writing", "templates", "wechat-longform.md"): ("SELF-CHECK",),
    os.path.join("writing", "templates", "devlog.md"): ("SELF-CHECK",),
}

# Every agent brief must state its role and its prohibitions. A brief that
# forgets to constrain the model is the single most expensive omission here.
REQUIRED_AGENT_MARKERS = {
    "prompts/research-agent.md": ("Your role", "Prohibitions", "Claim Ledger"),
    "prompts/writing-agent.md": ("Your role", "Voice", "Prohibitions"),
    "prompts/editor-agent.md": ("Your role", "Scope boundary", "Title"),
}

HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.MULTILINE)
# Templates number their sections ("## 1. Problem"). The contract is the name,
# not the position, so a section may be renumbered without breaking the check.
SECTION_NUMBER_RE = re.compile(r"^\d+[.)]\s*")

# Relative markdown links, used to catch links to files that do not exist.
# Fragments and absolute URLs are skipped: those are checked by the link job.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def read(root, rel):
    path = os.path.join(root, rel)
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        return None if exc.__class__.__name__ == "FileNotFoundError" else None


def headings(text):
    """Normalised heading names, with any leading list numbering stripped."""
    return [SECTION_NUMBER_RE.sub("", h.strip().lower()) for h in HEADING_RE.findall(text)]


def check_shape(root, problems):
    for rel in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(root, rel)):
            problems.append(f"missing directory: {rel}")

    for rel in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(root, rel)):
            problems.append(f"missing file: {rel}")


def check_sections(root, problems):
    for rel, wanted in REQUIRED_SECTIONS.items():
        text = read(root, rel)
        if text is None:
            continue
        found = headings(text)
        for section in wanted:
            if section.lower() not in found:
                problems.append(
                    f"{rel}: missing required section '{section}'")

    for rel, markers in REQUIRED_TEXT_MARKERS.items():
        text = read(root, rel)
        if text is None:
            continue
        lowered = text.lower()
        for marker in markers:
            if marker.lower() not in lowered:
                problems.append(f"{rel}: missing required marker '{marker}'")


def check_agents(root, problems):
    for rel, markers in REQUIRED_AGENT_MARKERS.items():
        text = read(root, rel)
        if text is None:
            continue
        lowered = text.lower()
        for marker in markers:
            if marker.lower() not in lowered:
                problems.append(f"{rel}: missing required marker '{marker}'")


def check_examples(root, problems):
    """The example must carry the metadata block the docs promise."""
    rel = os.path.join("examples", "openshell-analysis.md")
    text = read(root, rel)
    if text is None:
        return
    if "```yaml" not in text:
        problems.append(f"{rel}: no yaml metadata block")

    # A framework whose only worked example contains a bare URL is a framework
    # that quietly allows unsourced claims.
    if text.count("http://") or text.count("https://") < 5:
        problems.append(f"{rel}: fewer than 5 references -- is it sourced?")


def check_links(root, problems):
    """Verify relative markdown links resolve. Skips URLs and fragments."""
    checked = 0
    for rel in REQUIRED_FILES:
        if not rel.endswith(".md"):
            continue
        text = read(root, rel)
        if text is None:
            continue
        base = os.path.dirname(os.path.join(root, rel))
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#", 1)[0].strip()
            if not clean:
                continue
            checked += 1
            if not os.path.exists(os.path.normpath(os.path.join(base, clean))):
                problems.append(f"{rel}: broken relative link -> {target}")
    return checked


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate pipeline framework structure")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--quiet", action="store_true", help="only print problems")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    problems = []

    check_shape(root, problems)
    check_sections(root, problems)
    check_agents(root, problems)
    check_examples(root, problems)
    links = check_links(root, problems)

    if not args.quiet:
        print(f"Structure validation: {root}")
        print(f"  required dirs   : {len(REQUIRED_DIRS)}")
        print(f"  required files  : {len(REQUIRED_FILES)}")
        print(f"  section contracts: {len(REQUIRED_SECTIONS)}")
        print(f"  text contracts   : {len(REQUIRED_TEXT_MARKERS)}")
        print(f"  relative links checked: {links}")

    if problems:
        print(f"\nERROR x{len(problems)}:")
        for item in problems:
            print(f"  - {item}")
        return 1

    if not args.quiet:
        print("\nOK: framework structure intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())