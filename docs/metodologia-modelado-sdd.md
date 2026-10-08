# Specification-Driven Product and Development Modeling Methodology

**Status:** agreed methodological approach. The project will be public and MIT-licensed, and will use GitHub as its platform. Tool installation/configuration and an interoperability pilot were initially pending; the development environment is now installed, while the pilot and product artifacts remain pending.

**Project:** `ha-tank-os`.

## Purpose

Define how to turn the ha-tank-os vision and requirements into a reviewable product and technical model before developing each capability. BMAD, Spec Kit, OpenSpec, and Git practices will be combined without maintaining parallel pipelines or multiple canonical representations of the same artifact.

The approach is **Spec-Driven Development (SDD)**: behavioral specifications and their acceptance criteria guide design, work breakdown, testing, and implementation. Code must not silently replace the specification.

Before the first product change, a sufficient global baseline must exist: a capability map, PRD, and initial architecture with its relevant technical decisions. It is not necessary to specify, design, and break down every future capability in detail before implementing the first one. Each change must pass its own readiness gate before work begins.

This methodology does not claim that the product is designed or implemented. The repository tooling is installed, but product artifacts have not yet been generated.

## Principles

- The product owner decides scope, priorities, and acceptance. Tools may propose options and identify gaps, but their proposals do not become approved decisions automatically.
- Each artifact has one canonical representation and an identifiable authority. Derived artifacts are marked as such and link to their source.
- Confirmed facts, assumptions, recommendations, and pending decisions remain distinct.
- Requirements describe observable outcomes and constraints. A specification does not prescribe internal details unless an architectural decision requires them.
- Every relevant functional requirement must be testable through scenarios or acceptance criteria.
- Every change must link to the requirements it affects and the scenarios it must satisfy. Tests must link to the requirements or scenarios they verify. Avoid maintaining a redundant manual chain from every task to every artifact when the change can provide that traceability.
- Global modeling precedes the first change, but does not attempt to close every detail of future capabilities in advance. Uncertainties requiring technical evidence are recorded as bounded spikes, not closed facts.
- Later updates preserve history and rationale; approved intent is not changed retrospectively without traceability.
- An agent must not resolve contradictions between documents by silently choosing a source. It stops, identifies the conflicting authorities, and requests correction of the owning artifact.
- Verification asks whether the implementation satisfies the specification. Validation asks whether the specified behavior is what the product owner needs. They are different controls.

## Role of each tool

| Tool | Role in ha-tank-os | Must not become |
| --- | --- | --- |
| BMAD | Discovery, PRD, global architecture, and initial capability-map boundaries | The day-to-day change, behavioral-specification, task, or implementation flow when OpenSpec is adopted for changes |
| Spec Kit | An approved engineering constitution and quality controls shown to be compatible with canonical artifacts | A second `specify → plan → tasks → implement` pipeline running in parallel with OpenSpec |
| OpenSpec | The lifecycle of each bounded change and its canonical behavioral specifications | A copy of the PRD or a place to duplicate global architecture decisions |
| GitHub | Public repository, review, and collaboration; Issues, Projects, milestones, planning features, teams, Wiki, Actions, artifacts, packages, and releases may be used when valuable and available | One GitHub task for every `tasks.md` line, a Wiki that duplicates canonical documentation, or an authority for system behavior |
| Git | Version history, diffs, and review of documents and code | Sufficient evidence of approval or functional correctness by itself |

Integration between these tools is an explicit documentation flow. Native interoperability is not assumed, nor is it assumed that one tool automatically reads another tool's artifacts. Before adopting cross-analysis commands, run a small pilot. If Spec Kit cannot analyze OpenSpec artifacts directly, do not duplicate them merely to satisfy Spec Kit: choose between a manual check, a bounded approved adapter, or omitting that command.

### Agents, models, and portability

VS Code is the primary IDE. Codex is the initial preferred development agent, but IDE, agent, and model are separate layers: specifications, change contracts, and architecture must not depend exclusively on Codex or VS Code. Product and engineering rules remain provider-neutral whenever possible. Each agent's integration is limited to bridges, skills, commands, or adapters that invoke the same flow and respect the same authorities. VS Code usage is documented without preventing other editors.

GPT-6 Luna is preferred for most tasks it can handle adequately, and GPT-6 Astra is reserved for tasks requiring its capabilities. Routing is a revisable operational preference, not an architectural decision or a reason to relax gates. Every agent receives the same change contract, must read its sources, and must stop when it finds contradictions.

Implementation context must live in the repository: PRD, architecture, ADRs, constitution, specification, and active change. A new session must be able to understand a change from these artifacts without depending on conversational memory. Documentation should allow Luna to complete most routine tasks; product decisions, validation, and approval remain the owner's responsibility.

The initial working environment is a Mac mini with an Apple M4, but the repository is open to contributions. Setup, development, testing, and contribution documentation must cover macOS, Linux, and Windows. CI will validate the operating systems and versions declared as supported. macOS-specific details must not become implicit requirements for shared tools or scripts.

GitHub is the agreed platform. During the PRD and architecture phases, the concrete native features to use, their maintainers, and their source of truth will be decided. Versioned repository documentation remains canonical; a Wiki, if used, links to it or serves derived content. Actions, artifacts, packages, and releases are enabled according to available workflows and permissions; no plan is assumed to include every capability.

## Artifact authority

| Artifact | Authority | Content |
| --- | --- | --- |
| Vision and requirements | `vision-y-requisitos.md`, with decisions approved by the product owner | Purpose, scope, needs, confirmed decisions, and open questions |
| PRD | Product document produced/reviewed with BMAD and approved by the product owner | Users, problems, goals, scope, product requirements, exclusions, and success measures |
| Global architecture and ADRs | Approved architecture document and decision records | Boundaries, components, flows, persistence, Home Assistant integration, security, alternatives, and consequences |
| Engineering constitution | `.specify/memory/constitution.md`, if Spec Kit is adopted, approved and versioned | Engineering principles and constraints governing planning, review, and changes; not product requirements and not immutable |
| Current behavior | Canonical OpenSpec specifications | Behavioral contracts, rules, inputs/outputs, errors, and verifiable scenarios |
| Active change | An OpenSpec change folder | Rationale, affected requirements, specification delta, specific design, tasks, and evidence |
| Technical tasks | The active change's `tasks.md` | Technical checklist for completing the change; not replicated as individual Issues |
| Organizational status | One GitHub Issue per change, if GitHub is adopted as the tracker | Change stage, priority, owner, blocker, and milestone; does not replicate `tasks.md` |
| Milestones and plan views | GitHub Milestones/Projects, if adopted | Grouping and visualization of approved changes, not canonical requirements |
| Implementation and tests | Versioned code and tests in Git | What was implemented and the automated evidence available; does not replace the specification |
| History and review | Git and associated reviews | Diffs, versions, changes, and recorded decisions over time |

If a change reveals that the product or architecture is insufficiently defined, correct the relevant higher-level authority—vision/requirements, PRD, or architecture/ADR—and then update derived artifacts. Do not resolve a contradiction by editing only a design, task, or code.

## Modeling sequence before development

### 1. Requirements baseline

Use `vision-y-requisitos.md` as the current input. Review each statement and label it as a confirmed decision, requirement, preference, hypothesis, recommendation, or open question. Identify ambiguous terms, actors, scenarios, and scope boundaries.

The result is a reviewable baseline; everything appearing in notes or external contributions is not automatically approved.

### 2. Product definition and validation with BMAD

Use BMAD to organize discovery and produce a PRD. The PRD must be understandable without prior conversations and must keep assumptions and pending decisions visible. Validate it before deriving technical design and planning.

As appropriate, the PRD covers goals, actors, problems, capabilities, use cases, functional and non-functional requirements, exclusions, risks, success metrics, and proposed phases. The product owner approves scope and priorities.

### 3. Architecture and technical decisions

After PRD approval, create and review the architecture document. It must describe domain, application, Home Assistant integration, interface, and persistence boundaries; data flows; responsibilities and contracts; considered options; and operational and security consequences.

Relevant decisions are recorded as ADRs with an explicit status—proposed, accepted, rejected, or superseded—together with context, alternatives, consequences, and date. Options not yet verified, including API and Home Assistant version decisions, remain pending or are validated through a separate technical experiment.

### 4. Global capability map

Derive a capability map from the PRD with priorities, dependencies, and first-version boundaries. Assign stable identifiers to relevant requirements and scenarios to preserve traceability without requiring a manual matrix across every task, Issue, pull request, and test.

Before the first change, there must be a coherent product view and an initial global architecture. Detailed designs, complete scenarios, and tasks for every future capability are not required yet. Lower-priority capabilities may remain high-level goals and open questions.

### 5. Engineering constitution and Spec Kit controls

If Spec Kit is adopted, create a concise constitution containing engineering principles approved by the owner. It may cover, for example, domain/Home Assistant boundaries, persistence authority, provenance preservation, action safety, non-blocking operations, and acceptance testing.

The constitution governs engineering decisions; it does not define the product. It is versioned and can be changed through explicit review. Do not fill it with generic maxims or unapproved proposals.

Spec Kit must not run its complete `specify → plan → tasks → implement` flow in parallel for a change already managed by OpenSpec. Its checklists or analyses may be adopted only if a pilot shows that they add value without creating canonical copies. Spec Kit's current analysis operates on its own artifacts; direct compatibility with OpenSpec documents is not assumed.

### 6. OpenSpec change preparation and lifecycle

The agent's planning and context unit is a **bounded OpenSpec change**, not an isolated technical task. Each change contains, as appropriate, a proposal, specification deltas, specific design, and `tasks.md`. Tasks decompose the change but do not become separate Issues by default.

The specification describes observable behavior, rules, inputs and outputs, errors, and testable scenarios. It links to the requirements it satisfies and respects applicable global decisions and ADRs. The design explains how to approach that change without duplicating global architecture.

Before implementation, check within the change that:

- the rationale and scope are clear and contain no unapproved work;
- every affected requirement has verifiable scenarios and does not contradict the current baseline;
- design and tasks respect architecture, ADRs, and the constitution;
- tasks cover relevant tests and dependencies; and
- no blocking decisions remain unresolved.

The owner approves the prepared change. If contradictions appear between the PRD, ADRs, constitution, and specifications, the agent stops and identifies which authority must be updated; it does not choose a version silently.

### 7. Spikes for technical uncertainty

When an important decision cannot reasonably be resolved from documentation, open a bounded spike before closing the affected design or baseline. Each spike states the question, objective, agreed time limit, method, required evidence, and possible outcomes: `PASS`, `FAIL`, or `INCONCLUSIVE`. It may include a disposable technical prototype, but it is not product implementation.

The result includes the tested environment and version, observed limits, and reproducible artifacts when appropriate. Evidence may feed an ADR or leave the decision open. A spike prototype does not become production code automatically; reuse requires separate review and approval.

### 8. Organizational tracking with GitHub

If GitHub is the chosen tracker, create at most one tracking Issue per OpenSpec change and link it to the change folder. The Issue holds priority, owner, milestone, blockers, and organizational status. `tasks.md` keeps the detailed technical checklist. Do not synchronize two checklists or replicate each OpenSpec task as an Issue.

Milestones and Projects show groupings and roadmap changes. Dates and estimates are revisable forecasts; they do not replace acceptance criteria or scope decisions.

### 9. Readiness gates

The process has three distinct states:

| State | Criterion | Allows |
| --- | --- | --- |
| `Product baseline ready` | Approved PRD, global capability map, initial architecture, and resolved blocking decisions. Non-blocking uncertainty may have bounded spikes | Preparation and approval of concrete changes; not necessarily detailed specification of every future capability |
| `Change ready` | Bounded OpenSpec change with proposal, specification, design where needed, tasks, tests, and resolved blocking decisions | Authorization to implement that change |
| `Change done` | Verified implementation, independent review, owner validation, and archived/synchronized change | Closing the change and updating the current canonical specification |

Product development does not begin until `Product baseline ready` exists and the first change is `Change ready`. Each later change is prepared and approved individually. Exhaustive roadmap design is not required before proceeding with an approved change.

## SDD cycle for each change

1. Explore the problem and bound a small, reviewable OpenSpec change.
2. Prepare and approve the proposal, specification deltas, relevant design, and tasks.
3. Start implementation in a fresh agent context, providing the complete change and global sources instead of relying on a long prior conversation.
4. Implement approved tasks and run tests demonstrating the scenarios.
5. Verify that the implementation satisfies the specification. Automate this verification where possible.
6. Review the change in an independent session that receives the constitution, specification, relevant ADRs, diff, and test results without relying on the implementer's reasoning.
7. Ask the owner to validate whether the delivered behavior is what they wanted. The agent does not accept it on their behalf.
8. Correct discrepancies in the owning source, verify again, and archive/synchronize the OpenSpec change only after acceptance.

Technical verification and product validation are distinct. A test may show that code satisfies a specification without showing that the specification correctly expresses the owner's need.

## Automation and evidence

From the first implemented change onward, configure continuous integration for applicable validations: OpenSpec structural validation, formatting, linting, types, unit and integration tests, and Home Assistant compatibility tests. Extend checks as frontend, migrations, or other components appear.

Automate checkable invariants—validators, tests, migrations, and CI—instead of adding documents without a concrete need. A tool or agent result is not evidence by itself: record commands, versions, results, and relevant limits.

## Exclusions and controls

- Do not generate parallel canonical PRDs, specifications, plans, or task lists from BMAD, OpenSpec, and Spec Kit.
- Do not start a change that has not reached `Change ready`.
- Do not require detailed design of every capability before the first change; do maintain a sufficient global map and initial architecture.
- Do not turn a spike prototype into production code without reviewing its design, quality, and tests.
- Do not accept an agent assertion as a substitute for tests or independent review.
- Do not confuse `Change done` with automatic acceptance: owner validation is a human decision.
- Do not install or initialize tools, create a remote repository, or publish a backlog as an implicit consequence of this methodology; each action requires its own authorization and timing.
- Do not treat models, diagrams, automated analyses, or checklists as evidence that a Home Assistant integration works on a real version.

## Official references

- [BMad Method: Plan inside an organization](https://docs.bmad-method.org/plan/plan-inside-an-organization/)
- [BMad Method: Choose a planning path](https://docs.bmad-method.org/cs/plan/choose-a-planning-path/)
- [BMad Method: Break work into stories and track it](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [GitHub Spec Kit: Agentic SDD](https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md)
- [OpenSpec: spec-driven schema](https://openspec.dev/docs/schemas/spec-driven)
- [OpenSpec: setup and workflows](https://openspec.dev/docs/setup)
- [GitHub Projects: views](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-with-projects)
- [GitHub Issues: milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)
