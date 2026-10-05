# NVIDIA OpenShell Analysis

> **Example #001** — the reference worked example for this pipeline.
>
> This is a pipeline artifact, not an article. An article targets a reader; this
> targets the next person running the process. It shows what the research note
> looked like *before* prose existed, which claims survived into the article, and
> which ones did not.
>
> Produced by: Discovery → Research → Analysis → Draft → Editor → Assets
> Follows: [`research/templates/github-project-analysis.md`](../research/templates/github-project-analysis.md)

---

## Project Overview

| Field | Value |
| --- | --- |
| Project name | NVIDIA OpenShell |
| Official repository | https://github.com/NVIDIA/OpenShell |
| Official documentation | https://docs.nvidia.com/openshell/latest |
| Product page | https://www.nvidia.com/en-us/ai/openshell/ |
| Licence | Apache-2.0 |
| Category | AI Agent Security / Agent Runtime / Sandbox / Policy |
| Analyzed at | v0.1.x, October 2026 |
| Confidence | High for architecture and policy mechanics; medium for roadmap and ecosystem maturity |

### Why it matters

The interesting thing about OpenShell is not any single mechanism. It is that a
GPU vendor shipped a **runtime whose job is to constrain agents**, and positioned
it explicitly *beneath* agent harnesses rather than as another agent framework.

That positioning is the signal. Once a vendor whose business is compute decides
the bottleneck for agent adoption is authorization rather than capability, the
question "how much should this agent be allowed to do" has moved from a
compliance footnote to an infrastructure layer with real engineering behind it.

It is also unusually honest. The project's own documentation states which
checks it cannot perform, and returns `unsupported` rather than a misleading
pass. For a security tool, that is the most credible thing in the repository.

---

## Research Notes

### Problem

Autonomous coding agents read files, modify code, execute commands, call tools,
reach the network, and call APIs. The failure mode is not a wrong answer — it is
a **reasonable-looking sequence of steps with an irreversible consequence**:
a package install that fetches from an unrelated host, a commit that pushes more
than intended, a request body that carries a credential to the wrong destination.

Risk classification as stated in the project's own security documentation:

| Risk | Shape |
| --- | --- |
| Data exfiltration | Agent sends repository contents to a third party |
| Credential theft | Agent reads and forwards tokens |
| Unauthorized API use | Mutating calls from an agent that should only read |
| Privilege escalation | Agent reaches beyond the identity it was given |

The structural problem is a **magnitude mismatch**: the permission required for
a task and the loss possible if the task goes wrong are orders of magnitude
apart. No amount of model capability reduces this. A more capable model produces
more consequential actions from the same flawed permission.

### Background

Agent tooling grew out of a completion paradigm. Sandboxing arrived late because
the threat model was implicit for as long as agents mostly edited text. Once
agents run commands and hold credentials, the implicit model expired.

NVIDIA's response is positioned as a **runtime**, not a model, not a chatbot,
and explicitly not another agent framework. Per its own FAQ it sits below
harnesses such as Claude Code, Codex, OpenCode and OpenClaw. That is a
deliberate choice: the enforcement layer should not compete with the thing it
constrains.

It is also positioned as part of NVIDIA's broader *Open Agent Safety Platform*,
alongside Sentry and BlueField-4 hardware enforcement — indicating a
direction where runtime policy and hardware policy converge.

### Technical architecture

Five components, each with a distinct job. Conflating them is the most common
misreading of this project.

| Component | Role | Trust level | Decides |
| --- | --- | --- | --- |
| **Sandbox** | Where the agent process runs | Untrusted | Nothing — it is the constrained thing |
| **Supervisor** | Intercepts and evaluates requests from inside the boundary | Trusted side | Whether each request is allowed |
| **Gateway** | Control plane: identity, policy distribution, provider credentials, sandbox lifecycle, relay coordination | Trusted | Who exists and what it is configured with |
| **Policy** | Declarative YAML: filesystem, process identity, per-binary egress, request rules, credential bindings | Data | What is permitted |
| **Compute runtime** | Docker / Podman / Kubernetes / MicroVM | Infrastructure | How the boundary is built and proven, never whether to allow |

The load-bearing boundary is the split between **Supervisor and Sandbox**. The
agent runs unprivileged inside the network-isolated sandbox; the Supervisor runs
outside it, on the trusted side. Every outbound connection is forced through a
local proxy back to the Supervisor. Enforcement therefore happens **outside the
process being constrained** — the agent's own output cannot influence the
decision about itself.

Default state is denial. All egress is denied except the mediated channel to the
Supervisor, so an unconfigured agent has no outbound path at all.

### Core mechanisms

**Sandbox isolation.** On the Linux backend the agent runs as a non-root
identity with **no capabilities granted**. Filesystem access is constrained
path-by-path by the kernel's **Landlock LSM**. Dangerous syscalls are filtered
by **seccomp**, including paths that would bypass the proxy and open a raw
socket. A **network namespace** forces ordinary outbound traffic back through
the local CONNECT proxy.

**Process identity, not self-reporting.** The Supervisor identifies a process by
its real executable path as reported by the kernel, and records a hash the first
time a binary participates in a connection. If the file at that path later
changes, subsequent connections are denied.

**Per-binary policy.** Authorization attaches to real executable paths, not to
commands. `pip` is a Python script, so the process that actually reaches the
package index is the interpreter; a rule written against the wrapper does not
apply. This closes a straightforward evasion path.

**Layer lock-in.** Filesystem, process identity and Landlock rules are locked at
sandbox startup; network rules and middleware are hot-reloadable. The least
spoofable properties sit on the hardest layer.

### Network control

Two-stage evaluation.

1. **Connection check** — is this binary allowed to reach this host and port?
2. **Request inspection** — if the endpoint declares a protocol, each request is
   parsed and checked.

Inspectable protocols: `rest`, `websocket`, `graphql`, `mcp`, `json-rpc`, `tcp`.

The capability this buys is **method-level and path-level control on a single
API**. The documented GitHub example enables a `read-only` preset: `GET`, `HEAD`
and `OPTIONS` pass, `POST` and `DELETE` return a `policy_denied` response. Same
API, read allowed, write blocked — a granularity traditional firewalls cannot
express, because they see connections rather than requests.

Rule composition is **union with deny-wins**, not an ordered list. Several rules
can match one connection and their access adds up; any matching deny beats any
allow. So narrowing permissions requires reviewing every rule that could permit
the request, including those contributed automatically by credential providers.

Private network addresses are blocked by default as an SSRF control. The cloud
metadata address `169.254.169.254` is never authorized as a destination.
Sandbox-local loopback is unaffected.

### Credential protection

This is the most unusual design decision in the project, and the strongest.

**The agent process never holds a real credential.** At sandbox startup,
provider credentials in the environment are replaced with opaque placeholders.
The agent reads a string, places it in a header, and completes its whole flow
without an error. The proxy resolves the placeholder into the real value at the
instant of forwarding.

Resolution requires **two independent authorizations to both pass**:

1. Network policy permits this binary and this destination.
2. Credential binding covers this request's host, port and path.

Failing the second returns HTTP 403 with the reason `credential_endpoint_mismatch`
— even if network policy explicitly allowed the destination. The documented
case: a `GITHUB_TOKEN` provider resolves only at `api.github.com:443` and
`github.com:443`.

Injection points include headers, basic auth, query parameters, URL path
segments, request bodies and WebSocket text frames, with proxy-side AWS SigV4
signing — so long-lived cloud keys need not exist inside the sandbox at all.

Key handling is bound to instance identity: the **Gateway is the sole issuer**,
each credential corresponds to one sandbox generation, and the agent side holds
only a public key. The agent can verify that the peer is a genuine Supervisor
and cannot forge one.

### Policy Prover

The layer above runtime enforcement, and the part with the least precedent.

Policy Prover uses an SMT solver for **formal verification** of policy rather
than pattern matching. Two check types:

- **Boundary check** — given a declared ceiling ("this environment may not exceed
  X"), does the policy under test exceed it? Violations print a **counterexample**,
  e.g. `counterexample: filesystem write /tmp`.
- **Proposal risk check** — when an agent requests a new network rule, does it
  introduce risk access relative to the current state: a new destination, a new
  HTTP method, or credentials reaching a new place?

Any finding **blocks automatic approval**.

Paired with it, Policy Advisor lets a blocked agent propose a narrower rule
through a local endpoint in its own sandbox. The Gateway remains the sole
arbiter, and the default approval mode is `manual`. The agent does not open its
own door.

---

## Technical Breakdown

Five mechanisms, each with the problem it solves. No marketing.

### 1. Sandbox

**Problem it solves.** An agent process that can reach the host filesystem,
spawn unrestricted syscalls, and open raw sockets has no boundary at all — and a
compromise, or merely a bad instruction, becomes a host incident.

**Why this rather than the alternative.** Container isolation alone is
advisory: it restricts namespaces and capabilities, but an agent that can run
`mount`, load a kernel module path, or open a raw socket degrades it. OpenShell
stacks independent mechanisms — non-root with zero capabilities, Landlock for
file paths, seccomp for syscalls, a network namespace for egress — and relies on
their overlap. Additionally, the Supervisor sits *outside* the boundary, so
enforcement cannot be tampered with from inside.

**What it makes hard.** Rule authoring. The agent is identified by real
executable path, so a policy that looks right and silently does not apply is a
routine failure mode; the project mitigates it by rejecting connections and
logging the identified path.

### 2. Policy engine

**Problem it solves.** Per-agent and per-task permission needs. Blocking
everything makes the agent useless; allowing everything makes it unsafe.

**Why this rather than the alternative.** Unix-style host-level permission is
the wrong granularity — it is per-user, not per-task, and the agent runs under
the invoking user. A per-sandbox declarative policy expressed per binary and per
endpoint is the correct unit, and it is reviewable as a file.

**What it makes hard.** The startup-locked versus hot-reloadable split means
changing filesystem or identity rules costs a sandbox restart, while network
rules are cheap to adjust but carry the full burden of correctness. The design
accepts that trade deliberately.

### 3. Network control

**Problem it solves.** Egress is the exfiltration path. A sandbox with
filesystem isolation but unrestricted network is a sandbox with a pipe out of
it.

**Why this rather than the alternative.** Host firewalls cannot see inside TLS,
and cannot express method-level rules. Terminating and inspecting requests at a
proxy the agent cannot bypass gives request-level granularity, and means one
place to enforce one policy.

**What it makes hard.** Every endpoint that needs credentials has to keep the
credential binding and the network rule consistent; and because `enforcement:
audit` is the default on inspected endpoints, a misjudged rule can log
violations without blocking. The project documents the audit-then-enforce
sequence for exactly this reason.

### 4. Credential protection

**Problem it solves.** API keys in an agent's environment are single points of
failure. Any prompt injection, any unintended tool call, any log line, and the
key is exfiltrated — with no further exploitation required.

**Why this rather than the alternative.** Scoped, short-lived credentials help
but still hand the secret to the process. Placeholder substitution means the
agent never possesses anything worth stealing. A leak becomes useless because
the stolen string resolves nowhere.

**What it makes hard.** Anything requiring the secret in the computation itself
cannot use this model — most notably signing operations, which have no
placeholder form.

### 5. Policy Prover

**Problem it solves.** Runtime controls stop what happens; they do not tell you
whether the configuration is correct in the first place. A policy that is wrong
at review time stays wrong until an incident proves it.

**Why this rather than the alternative.** Reading a policy and judging it is
exactly the task humans do unreliably at scale, and exactly the task where a
solver can be exhaustive. A declared ceiling plus an SMT solver turns "is this
policy excessive?" into a check with a counterexample.

**What it makes hard.** Coverage. A checker that cannot inspect a rule type must
not appear to pass it, and the project's answer — return `unsupported`, treat
anything but `within_boundary` as failure — makes the tool usable precisely
because of the limitation.

---

## Key Insights

1. **Agent security is a permission problem, not a model problem.** Once an
   agent acts on the world, the binding constraint is authorization. Improving
   the model does not improve the permission model, and can make outcomes worse
   by making the agent more effective inside a flawed one.

2. **Runtime control matters more than model capability for production
   adoption.** The scarce resource in deploying agents is not intelligence; it
   is the confidence to let the system press enter unattended. Enforcement
   outside the agent process is what converts an impressive demo into something
   a team can operate.

3. **MCP raises the need for a policy layer rather than lowering it.** Every
   connected server is a capability and an attack surface simultaneously.
   Because tool lists grow by configuration while permission review does not
   scale the same way, the tool inventory must become a reviewable artifact.
   `protocol: mcp` is that artifact.

4. **Credentials should be absent from the agent, not merely restricted.** The
   strongest move in this design is not a finer ACL on a secret — it is removing
   the secret from the process, converting credential theft from a breach into a
   no-op. This is a more useful general principle than the implementation.

5. **A security tool's stated limits are a quality signal.** Returning
   `unsupported` instead of a green tick, and documenting that MCP permission is
   "enforced at runtime but unproven", are stronger credibility signals than any
   benchmark. Reviewers should treat coverage gaps as a reason to trust the rest
   of the documentation, and never as an afterthought to smooth over.

---

## Limitations

Reported, not smoothed over. Several items below are the project's own stated
limits.

### Tool-call parameters are not matched

For `protocol: mcp`, authorization applies at the method and tool-name level.
**Tool argument matching is not supported**, so an allowed tool can receive any
argument the server accepts. A policy granting `tools/call` for a read tool
relies on that tool's own server-side checks for its arguments. This is the
single most important caveat for anyone extending this model.

### The prover does not cover several protocol rule types

Boundary verification covers filesystem, process identity, Landlock, network
connection, and REST requests. **GraphQL, MCP, WebSocket and JSON-RPC rules
return `unsupported`** rather than a result. Very large policies (over 1024
rules, or over 4096 endpoints) return `inconclusive`.

The practical consequence: MCP permissions are currently *enforced at runtime
but unproven* — a distinction the project's own documentation makes. An
organization whose compliance requirement is provable bounds needs something the
current prover does not provide.

### Signing operations have no placeholder form

This is an analysis of the design's boundary rather than a vendor statement, and
it is the most consequential gap for adjacent use cases.

The credential model assumes the agent never needs the secret in order to
compute a result — it needs it only so that a proxy can substitute it on the way
out. A transaction signature is the opposite: **the signature is the
computation.** The private key cannot be replaced with a placeholder that
something else later turns into a valid signature, because producing that
signature is precisely the authority being restricted.

So an agent that can sign is an agent that can sign, and the constraint has to
move to a different layer: key custody, transaction-level allowlists, amount
limits, and an approval step. Within this architecture there is no answer that
is both automatic and scoped. An `unsupported` result here is the correct
outcome; a claimed solution would be the thing to worry about.

### Additional caveats

- **Hash-based tool-call keys are guessable.** It is documented that keys
  derived from hashing tool names collide under brute force. Treat them as
  identifiers, not as authorization boundaries.
- **Granularity follows what the declared protocol exposes.** Method-level
  control is only as good as the protocol's own surface. Opaque binary
  protocols are `tcp`: connected or not, nothing more.
- **The unattended path is not proven.** The prover has a `trusted` mode for
  certain deterministic cases, but it is described as experimental and it skips
  the human review step entirely.
- **Ecosystem maturity.** The version line is young, and the officially
  documented host platforms are Linux plus macOS on Apple Silicon, with WSL2
  marked experimental. Hardware-enforcement integration implies specific
  infrastructure.

---

## Article Metadata

```yaml
project: NVIDIA OpenShell
category:
  - AI Agent Security
  - Agent Runtime
  - Open Source
platform:
  - WeChat
  - X
status: published
source:
  - https://github.com/NVIDIA/OpenShell
  - https://docs.nvidia.com/openshell/latest
  - https://www.nvidia.com/en-us/ai/openshell/

licence: Apache-2.0
version_analyzed: v0.1.x
analyzed_at: 2026-10

article:
  primary:
    title: "AI Agent开始失控了？NVIDIA给AI装一层安全操作系统"
    language: zh-CN
    platform: WeChat
    length_chars: 4957
    sections: 12
  derivative:
    - platform: X
      format: thread
      status: planned
  body_band: long
  writing_score: 96        # 0-100, pipeline writing check
  theme: moyu-green

deliverables:
  research_note: examples/openshell-analysis.md
  figures:
    - source: project
      file: assets/figures/openshell-system-architecture.png
      credit: NVIDIA OpenShell repository (docs/images), Apache-2.0
    - source: project
      file: assets/figures/openshell-sandbox-enforcement.png
      credit: NVIDIA OpenShell repository (docs/images), Apache-2.0
    - source: self
      file: assets/figures/agent-capability-surface.png
      credit: author diagram, not a NVIDIA figure
  cover:
    backend: offline_render
    ratio: "16:9"

claims:
  total: 12
  confirmed: 9
  documented: 3
  unverified: 0
```text
---

## Claim Ledger

Every technical claim made in the article, and its basis.

| # | Claim | Source | Confidence | Checked at |
| --- | --- | --- | --- | --- |
| 1 | Positioned as an agent security runtime, Apache-2.0, not an agent framework | Product page; docs Overview | confirmed | v0.1.x |
| 2 | Five components with distinct roles: Sandbox, Supervisor, Gateway, Policy, compute runtime | docs Architecture | confirmed | v0.1.x |
| 3 | Sandbox: non-root, no capabilities, Landlock, seccomp, network namespace | docs Architecture, Sandbox Policies | confirmed | v0.1.x |
| 4 | Default state is denial of all egress except the mediated Supervisor channel | docs Architecture | confirmed | v0.1.x |
| 5 | Identity from real executable path; file hash recorded; later change denied | docs Network Rules | confirmed | v0.1.x |
| 6 | Two-stage network check; rest/websocket/graphql/mcp/json-rpc/tcp inspection | docs Network Rules | confirmed | v0.1.x |
| 7 | `read-only` preset allows GET/HEAD/OPTIONS; POST returns `policy_denied` | docs Network Rules | confirmed | v0.1.x |
| 8 | Private addresses blocked by default; `169.254.169.254` never authorized | docs Network Rules | confirmed | v0.1.x |
| 9 | Credentials replaced by placeholders; resolved at forward time | docs Providers | confirmed | v0.1.x |
| 10 | Two independent authorizations required; `credential_endpoint_mismatch` on failure | docs Providers | confirmed | v0.1.x |
| 11 | Gateway is sole issuer; per-sandbox-per-generation credentials; agent holds public key only | docs Sandbox Authentication | confirmed | v0.1.x |
| 12 | Prover uses SMT solver; boundary and proposal-risk checks; findings block auto-approval | docs Policy Prover | confirmed | v0.1.x |
| 13 | Prover returns `unsupported` for GraphQL/MCP rules; `inconclusive` on large policies | docs Policy Prover | documented | v0.1.x |
| 14 | MCP tool argument matching unsupported | docs Network Rules | documented | v0.1.x |
| 15 | Policy Advisor: Gateway sole arbiter, default `manual` | docs Policy Advisor | confirmed | v0.1.x |
| 16 | Docker/K8s/Podman/MicroVM are the substrate; OpenShell adds agent-specific control | Product page FAQ | documented | v0.1.x |
| 17 | Names Claude Code, Codex, OpenCode, GitHub Copilot CLI; part of Open Agent Safety Platform | docs Overview; product page | documented | v0.1.x |
| 18 | Signing cannot use the placeholder model (author analysis of the design's boundary) | derived from claims 9–11 | documented | 2026-10 |

---

## References

Primary sources only. No third-party coverage is cited as evidence of
capability.

1. NVIDIA OpenShell — Developer Guide (Overview, Architecture, Sandbox Policies,
   Network Rules, Providers, Policy Prover, Policy Advisor, Sandbox Runtimes,
   Support Matrix) — https://docs.nvidia.com/openshell/latest (accessed
   2026-10)
2. NVIDIA OpenShell — product page, architecture components and official FAQ —
   https://www.nvidia.com/en-us/ai/openshell/ (accessed 2026-10)
3. NVIDIA OpenShell — GitHub repository, README and `architecture/` documents —
   https://github.com/NVIDIA/OpenShell (accessed 2026-10)
4. NVIDIA OpenShell — `docs/images/openshell-system-architecture.svg` and
   `docs/images/openshell-sandbox-enforcement.svg`, Apache-2.0 (accessed
   2026-10)
5. NVIDIA Developer Blog — *Add Runtime Controls to AI Agents With NVIDIA
   OpenShell* (accessed 2026-10)
6. NVIDIA Build — OpenShell product page and architecture overview —
   https://build.nvidia.com/openshell (accessed 2026-10)

---

## What This Example Demonstrates

Recorded so the example teaches something, rather than just existing.

- **A claim ledger that survives contact with prose.** Nine of eighteen claims
  were confirmed against implementation or primary documentation; three are
  documented-only and were written as the project's claims rather than adopted
  as the author's.
- **Stated limits carried into the article.** The MCP parameter limitation and
  the prover's `unsupported` cases appear in the published piece. They were not
  dropped because they complicate the narrative, which is the specific failure
  this pipeline exists to prevent.
- **Analysis separated from description.** "The agent runs unprivileged and the
  Supervisor sits outside the boundary" is documentation. "Enforcement therefore
  happens outside the process being constrained, so the agent's own output
  cannot influence the decision about itself" is analysis.
- **One boundary reached and reported honestly.** The signing limitation in
  particular was included as a limit rather than resolved with a confident
  suggestion, which is the harder and more useful outcome.
- **One note, three platforms.** The WeChat article and the planned thread
  derive from this single note, so they cannot contradict each other.
