# How-To Guide: Generating a Product Requirements Document (PRD)

This guide helps AI assistants create detailed Product Requirements Documents
(PRDs) in Markdown format, based on initial prompts from developers and
subsequent brainstorming sessions.
The PRD should be clear, actionable, and most importantly, suitable for a junior
developer to understand and implement the feature.

In the context of this project, we distinguish between two types of PRDs:

- **Project PRD**: Captures the high-level intent of the project and its boundaries,
  without locking in the implementation details and specifics.
  This document will remain relatively stable across the lifetime of the project.
  The project-level PRD provides the general overview of the project and does not have
  to be actionable (it will not be used drive the development directly).
- **Feature PRD**: Captures in great detail all the specifics of a single feature or
  milestone.
  The *Feature PRD* exists only during the implementation of the specific feature
  it was created for.

As an example, the *Project PRD* might describe the overall context, objectives,
scope, and some high-level user stories for a self-hosted expense management
dashboard app, while one of the *Feature PRDs* might describe in great technical detail
how the data storage, data model, and database are structured.

Two *PRD Templates* are available: `project-prd-template.md` and
`feature-prd-template.md`, which serve as guides for creating
concrete PRD documents.

## Process

1. **Receive Initial Prompt**: The developer provides a brief description or request
   for a new feature or functionality (or for the entire project in the case of a Project
   PRD).
2. **Ask Clarifying Questions**: Before writing the PRD, the assistant *must* ask
   clarifying questions to gather sufficient detail appropriate for the type of PRD
   being created.
3. **Generate the PRD**: Based on the initial prompt and the developer's answers to the
   clarifying questions, the assistant generates a PRD using the structure outlined in
   the relevant template.
4. **Save the PRD**: The project-level PRD is saved as `PRD.md` in the project root,
   while a feature-level PRD is saved as `prd-[feature-name].md` inside the `tasks/`
   directory (e.g., `tasks/prd-data-model.md`).
   Create the `tasks/` directory in the root folder, if it does not exist.
5. **Ensure Consistency**: If the newly-created *Feature PRD* conflicts with
   the *Project PRD*, consistency must be restored by updating the project-level
   document to comply with the new feature-level document.

Unless asked otherwise, do *not* start implementing the PRD.

## Clarifying Questions

The assistant should adapt its questions based on the prompt, the nature of the
feature, and the specific template being used.
The clarifying dialogue between the assistant and the developer must go into
sufficient detail.
Assume the primary reader of the PRD is a **junior developer**.
Therefore, requirements should be explicit, unambiguous, and avoid jargon.
Provide enough detail for them to understand the feature's purpose and core logic.

### Question Guidelines

- Number questions so the developer can address multiple questions at once.
- Ask **open-ended questions** first to understand scope and context.
- Follow up with **specific questions** to clarify technical details.
- **Iterate** - it's better to ask multiple rounds of questions than to create an
  incomplete PRD.
- **Don't make assumptions** - ask for clarification.
- **Provide examples** of what you need to know.
- **Confirm understanding** by summarizing what you've learned.

## PRD Structure

The structure of the PRD output needs to follow the template:

- **Project PRD**: `project-prd-template.md`
- **Feature PRD**: `feature-prd-template.md`

### Template Usage Notes

- The template structure does not need to be followed exactly - adapt the content to
  the specific feature.
- If a template section doesn't apply, simply omit it.
- If a section is missing that is critical for understanding the feature, then
  add it.
- Maintain consistent terminology throughout the document.

## Quality Validation

Before finalizing the PRD, the assistant should:

1. **Check completeness** - Ensure all relevant template sections are addressed.
2. **Verify clarity** - Ask yourself: "Would a junior developer understand this?"
3. **Validate consistency** - Ensure the PRD doesn't contradict itself.
4. **Confirm actionability** - Each requirement should be implementable.
5. **Review scope** - Ensure the PRD matches the intended scope.
