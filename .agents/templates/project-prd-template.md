# Project PRD Template

Use this template to capture the high-level intent, boundaries, and guiding decisions
for a Python project.
It is meant to orient contributors and frame future *Feature PRD* without locking in
implementation detail too early.

## 1. Project Overview

Set the stage in one or two sentences and make the value obvious.

Include

- Project name and core purpose
- The primary problem you solve and why it matters now
- Who benefits at a high level

Avoid

- Long anecdotes or historical play-by-plays
- Feature-level detail or implementation hints

## 2. Context, Constraints & Assumptions

Ground the reader in the broader situation and surface known limits.

Include

- Key background, links to prior work, or motivating data points
- Explicit assumptions, constraints, and dependencies (technical or organizational)
- External systems, APIs, or resources the project relies on

Avoid

- Exhaustive research papers—link out instead
- Hiding critical blockers or uncertain areas

## 3. Objectives & Scope

Clarify the outcomes you are targeting and the boundaries you will respect.

Include

- Top-level objectives stated as outcomes or capabilities
- Core epics or capabilities in scope for the initial delivery
- Clear out-of-scope statements to prevent scope creep

Avoid

- Task-level backlogs or milestone timelines
- Detailed feature specs better suited for Feature PRDs

## 4. User Personas & Scenarios

Keep the focus on real users and representative flows.

### Personas

- 2–3 concise profiles with name, role, primary goals, and pain points

### Key Scenarios

- Brief scenario names that capture what the user is trying to accomplish
- Short summaries of triggers, desired outcome, and success signals

Avoid

- Hi-fi UI mockups for CLI-first experiences
- Implementation detail or Given/When/Then acceptance criteria (save for Feature PRDs)

## 5. Experience & Capabilities

Outline the experience you intend to deliver and the capabilities that enable it.

Include

- High-level interface concepts (CLI commands, workflows, integrations)
- Major data flows, inputs/outputs, or storage expectations
- Essential non-functional expectations (reliability, observability, accessibility)

Avoid

- Detailed class structures, modules, or package layouts
- Designing extensibility layers before the core experience exists

## 6. Technical Strategy

Document the guiding technical choices that future features should align with.

Include

- Target Python version and major libraries or frameworks
- Preferred architecture patterns or diagrams (even rough sketches)
- Data storage choices, tooling standards, and deployment approach
- Performance and resource targets that shape technical decisions

Avoid

- Full configuration files or environment setup scripts
- Branch-specific or sprint-specific instructions

## 7. Risks, Open Questions & Next Steps

Capture the uncertainties you need to resolve to ship confidently.

Include

- Key risks with likelihood, impact, and mitigation strategies
- Open questions or assumptions to validate, with owners and due dates if known
- Immediate next steps to keep the project moving

Avoid

- Generic “TBD” statements without context or follow-up
- Deferring all risk tracking to feature-level documents
