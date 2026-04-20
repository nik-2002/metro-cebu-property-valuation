---
name: writing-plans
description: Create detailed implementation plans and task breakdowns before any coding begins.
---

# Writing Plans

## Overview
Create a detailed, bite-sized implementation plan. Assume the executor has zero context.

## 1. Create Implementation Plan
If you haven't already (from brainstorming), create `implementation_plan.md` with:
-   **Goal**: One sentence summary.
-   **Proposed Changes**: structured list of files to Create/Modify/Delete.
-   **Verification Plan**: How to test.

## 2. Create Task Checklist
Create or update `task.md`. Break work into **bite-sized tasks** (2-10 mins each).

**Granularity Rule:**
-   Atomic Step: "Write failing test for X"
-   Atomic Step: "Implement X to pass test"
-   Atomic Step: "Refactor"

*Bad Task:* "Implement Auth system"
*Good Task:* "Create `auth.py` with login function stub"

## 3. Review
Use `notify_user` to ask the user to review the Plan and Task list.

## Transition
-   **Terminal State:** User approved `implementation_plan.md` and `task.md`.
-   **Next Step:** Invoke the `executing-plans` skill to start building.