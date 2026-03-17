---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code.
---

# Test-Driven Development (TDD)

## Overview
Write the test first. Watch it fail. Write minimal code to pass.

## The Iron Law
**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

## The Cycle

### 1. RED (Failing Test)
-   Create a new test file or add a case to existing test.
-   Use `write_to_file`.
-   Run the test using `run_command` (e.g., `npm test`, `pytest`, `python -m unittest`).
-   **VERIFY:** It must fail with the *expected* error (e.g., "function not found", "assertion failed").

### 2. GREEN (Minimal Code)
-   Write the *simplest possible code* to make the test pass.
-   Use `write_to_file` or `replace_file_content`.
-   Run the test again.
-   **VERIFY:** It must pass.

### 3. REFACTOR (Clean Up)
-   Optimize code, remove duplication, improve naming.
-   Run tests again.
-   **VERIFY:** They still pass.

## Anti-Patterns to Avoid
-   Writing code, then testing it. (That's just testing, not TDD).
-   "I'll add tests later." (You won't).
-   Commented out tests.
