# Feature Spec Template

Use this template to describe the intent, scope, and delivery path for a single
feature or milestone.
It should connect the project PRD to specific implementation work while keeping enough
context for future contributors to understand the why, what, and how.
Apply only the sections that fit the nature of the feature or milestone you are
documenting.

## 1. Feature Overview

Summarize the feature in one or two paragraphs so new readers catch up quickly.

Include

- Feature name and succinct elevator pitch
- Problem or opportunity this solves (tie back to the project PRD)
- Expected user impact or value statement

Avoid

- Solution details that belong in later sections
- Vague language that hides the primary value proposition

## 2. Goals & Non-Goals

Define the outcomes you want and guardrails you will respect.

Include

- Clear, measurable goals or exit criteria
- Explicit non-goals or deferred concerns to prevent scope creep

Avoid

- Task or ticket lists
- Long-term aspirations that are unrelated to this feature

## 3. User Impact & Flows

Describe how users interact with the feature and how their experience changes.

Include

- Personas or user segments affected (reference or add brief summaries)
- Primary user journeys, scenarios, or CLI workflows
- Acceptance criteria written in bullet or Given/When/Then form

Avoid

- Pixel-perfect UI specs unless critical to explain intent
- Mixing implementation notes into user narratives

## 4. Requirements

Spell out what the feature must deliver before it can ship.

### Functional

- Key capabilities, commands, endpoints, or interactions
- Data inputs/outputs and validation rules

### Non-Functional

- Performance targets (latency, throughput, resource bounds)
- Reliability, security, accessibility, or compliance expectations

### Data & Schema Changes

- New or modified models, tables, files, or configuration formats
- Migration steps or backward compatibility considerations

Avoid

- Exhaustive class or function inventories
- Requirements without success validation

## 5. Experience Notes

Capture UI or UX guidance needed to implement confidently.

Include

- Wireframes, sketches, or CLI prototypes (link or embed)
- Content guidelines, messaging, or error handling tone
- Interaction nuances, edge cases, and accessibility cues

Avoid

- Final assets that belong in a design repo
- Treating this section as a full design specification

## 6. Technical Design

Explain how you intend to build the feature.

Include

- Architecture overview (modules, services, data flow diagrams)
- Key algorithms, state machines, or interfaces
- External dependencies, libraries, or integration points
- Feature flag or configuration strategy if applicable

Avoid

- Copying entire code snippets
- Tying the design to specific branch plans or sprint tasks

## 7. Testing Strategy

Lay out how you will prove the feature works.

Include

- Unit, integration, and end-to-end test coverage expectations
- Test data or fixtures required
- Manual test scenarios or exploratory charters if necessary

Avoid

- Listing individual test cases without summarizing the intent
- Duplicating automation details from CI configs
