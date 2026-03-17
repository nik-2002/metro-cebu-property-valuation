---
name: executing-plans
description: Execute implementation plans with independent tasks step-by-step.
---

# Executing Plans

## Overview
Execute the `implementation_plan.md` task-by-task. Maintain strict discipline.

## Process

1.  **Load Plan**: Read `implementation_plan.md` and `task.md`.
2.  **Execute Batch**: Pick the next unchecked task from `task.md`.
    -   Update `task_boundary` with the current task status.
    -   Follow **TDD** (Red -> Green -> Refactor) for coding tasks.
    -   Follow **Systematic Debugging** for failures.
    -   Mark task as `[/]` (in progress) then `[x]` (complete) in `task.md`.

3.  **Checkpoints**:
    -   After completing a measurable chunk (e.g., 3 sub-tasks), STOP.
    -   Run all verification steps.
    -   Report to user via `notify_user` or `task_boundary` summary.

## Rules
-   **Never skip tests.** See the `test-driven-development` skill.
-   **Never guess fixes.** See the `systematic-debugging` skill.
-   **Always update `task.md`** concurrently with `task_boundary`.

## Transition
-   **Terminal State:** All tasks in `task.md` are checked `[x]`.
-   **Next Step:** Run verification suite and ask for final user review.
