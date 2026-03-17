---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.
---

# Systematic Debugging

## Overview
Stop guessing. Fixes without root cause understanding create new bugs.

## The Iron Law
**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

## The Process

### Phase 1: Investigation (Do NOT edit code yet)
1.  **Read Errors**: Use `run_command` to capture exact error output. Read stack traces.
2.  **Locate Code**: Use `grep_search` or `find_by_name` to find relevant files.
3.  **Trace**: Use `view_file` to read code around the error. Trace data flow backwards.
4.  **Reproduce**: Create a minimal reproduction script or test case.

### Phase 2: Hypothesis
-   Formulate a hypothesis: "I think X causes Y because Z".
-   Test hypothesis: Modify code *only* to log/verify, not to fix yet.

### Phase 3: Fix (The Only Time You Edit)
-   Create a failing test case (Red phase of TDD).
-   Apply the fix.
-   Verify test now passes.

## Red Flags
-   "I'll just try this..." -> **STOP**.
-   "Maybe it's a race condition..." -> **PROVE IT**.
-   Trying 3+ fixes without success -> **Revert and Re-investigate**.
