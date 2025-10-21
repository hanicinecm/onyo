# How-To Guide: Generating a Task List from a PRD

This guide helps AI assistants create detailed, step-by-step task lists in Markdown
format based on existing Product Requirements Documents (PRDs).

The task list should be suitable to guide a junior developer through
implementation of the feature described in the PRD, step by step.

## Inputs

The following inputs are provided to the AI assistant:

- **Initial Prompt** provided by the developer.
- **Project PRD** located in the `PRD.md` file in the project root folder.
- **Feature PRD** which describes in great detail the feature that is supposed to be
  implemented by following the task list.
- **Existing Codebase** for better context and judgment.

## Output

The AI assistant creates the task list as follows:

- **Format**: Markdown (`.md`)
- **Location**: `tasks/`
- **Filename**: `tasklist-[feature-name].md` (e.g., `tasks/tasklist-data-model.md`)

### Output Structure

The generated task list will follow this structure:

```markdown
# Task List for Feature <feature-name>

## Relevant Files

- `path/to/potential/file1.py` - Brief description of why this file is relevant for
  this feature.
- `path/to/test_file1.py` - Unit tests for `file1.py`.
- etc.

### Notes (Optional)

Section reserved for any additional notes relevant to the impacted files, which are not
part of any PRD or other instructions for AI agents.

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 [Sub-task description 1.1]
  - [ ] 1.2 [Sub-task description 1.2]
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 [Sub-task description 2.1]
- [ ] 3.0 Parent Task Title (may not require sub-tasks if simple enough)

```

## Process

1. **Analyze PRD(s)**: Receive the *Feature PRD* reference and analyze it (together
   with the *Project PRD*) to understand the functional requirements, user stories, etc.
2. **Assess Current State**: Review the existing codebase to understand existing
   infrastructure, architectural patterns, and conventions.
   Also, identify any existing components or features that already exist and could be
   relevant to the current PRD requirements.
   Then, identify existing related files, components, and utilities that can be
   leveraged or need modification.
3. **Generate Parent Tasks**: Based on the PRD analysis and current state assessment,
   create the task list file and generate the main, high-level tasks required to
   implement the feature.
   Use your judgment on how many high-level tasks to use.
   Present these tasks to the developer in the specified format (so far without the
   sub-tasks).
   Pause and wait for the green light from the developer to generate the sub-tasks.
4. **Generate Sub-Tasks**: Once the user confirms, break down each parent task into
   smaller, actionable sub-tasks necessary to complete the parent task.
   Ensure sub-tasks logically follow from the parent task, cover the implementation
   details implied by the PRD, and consider existing codebase patterns where relevant
   without being constrained by them.
5. **Identify Relevant Files**: Based on the tasks and PRD, identify potential files
   that are relevant for this task list, and list these under the `Relevant Files`
   section.
6. **Save Task List**: Save the generated document according to the *Output* section
   above.

## Guidelines

### Target Audience

Assume the primary reader of the task list is a **junior developer** who will be
implementing the feature with awareness of the existing codebase context.

### Tasks Structure

- **Parent tasks** should represent major implementation phases or components.
- **Sub-tasks** should be atomic, well defined, actionable and specific.
- **Minimize task count** - Use the minimal number of tasks/sub-tasks possible. If a
  straightforward implementation can be described by a single sub-task, do not
  artificially break it down into multiple sub-tasks.
- Include both implementation and testing tasks.
- Consider dependencies between tasks and order them logically.

## Quality Validation

Before finalizing the task list, the assistant should:

1. **Check completeness** - Ensure all PRD requirements are covered by the task list.
2. **Verify clarity** - Ask yourself: "Would a junior developer understand this task?".
3. **Validate logical flow** - Ensure tasks are ordered properly.
