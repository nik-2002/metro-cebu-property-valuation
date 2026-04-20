---
name: brainstorming
description: Use BEFORE creating any features or complex changes. Explores requirements via Socratic dialogue.
---

# Brainstorming Ideas Into Designs

## Overview
Turn ideas into fully formed designs through collaborative dialogue. Do NOT start coding until a design is approved.

## The Process

1.  **Explore Context**:
    -   Use `list_dir`, `view_file` to understand the current project state.
    -   Check `task.md` or `project-context.md` if available.

2.  **Socratic Dialogue (Loop)**:
    -   Use `notify_user` to ask *one clarifying question at a time*.
    -   Focus on: Purpose, Constraints, Success Criteria.
    -   *Constraint:* Do not propose a solution yet. Just understand the problem.

3.  **Propose Approaches**:
    -   Once you understand the goal, use `notify_user` to propose 2-3 approaches.
    -   List trade-offs for each.
    -   Recommend one.

4.  **Create Design Artifact**:
    -   Once an approach is selected, create or update `implementation_plan.md`.
    -   Use the `writing-plans` skill concepts (Goal, Architecture, Proposed Changes).

## Transition
-   **Terminal State:** You have an approved `implementation_plan.md`.
-   **Next Step:** Invoke the `writing-plans` / `planning` skill to break down the plan into tasks.