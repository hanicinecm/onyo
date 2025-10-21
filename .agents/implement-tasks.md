# How-To Guide: Implementing Tasks

This document provides guidelines for AI assistants on implementing tasks listed
in a task list markdown file and tracking progress.

## Starting the Feature Implementation

Feature development should happen on a feature branch with a name consistent with
the feature name.
If you are asked to start implementing tasks from an untouched task list, check the
current branch and alert the user if it is inconsistent with the current feature.

## Task Implementation Guidelines

- **One sub-task at a time**: Never start the next sub-task until you receive a green
  light from the developer.
- **Test as you go**: Run relevant tests after implementing each sub-task to catch
  issues early.
- When you finish a **sub-task** (confirmed by the developer), mark it as completed by
  changing `[ ]` to `[x]`.
- **Document changes**: Briefly explain what was implemented and any important decisions
  made during the sub-task.
- Add or modify tasks as they emerge and keep the `Relevant Files` section in the task
  list file up to date and consistent with the tasks.
- Once **all** sub-tasks underneath a parent task are completed, offer to finalize the
  current parent task (see the *Parent Task Finalization* section below).

## Error Handling

If issues arise during implementation:

- **Blockers**: If a sub-task cannot be completed due to missing information or
  dependencies, clearly communicate the blocker to the developer and suggest solutions.
- **Scope changes**: If implementation reveals that the task scope needs adjustment,
  propose specific changes to the task list and get approval before proceeding.
- **Technical challenges**: If alternative approaches are needed, explain the
  trade-offs and get developer input before deviating from the planned approach.

## Parent Task Finalization

The following is the process for finalizing a parent task, if all its sub-tasks are
marked as completed and the developer gives the go-ahead for finalization.

1. Run the full test suite, if applicable.
2. Clean up all the temporary files and code.
3. Mark the parent task as completed.
4. Unless instructed otherwise, stage all the changes and commit them using the
   conventional commit format. The commit message should reference the task number.

## Finalizing the Feature

Once **all** the tasks from the given feature's task list have been completed,
offer to finalize the feature.

Feature finalization consists of squashing all the commits and merging into the
`dev` branch.
Follow the commit format and reference the feature name in the commit message.
Instead of doing this autonomously, present the intent in detail to the developer and
ask for the go-ahead.
