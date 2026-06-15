# GitHub Setup Checklist

## Current Local State

- The folder is already initialized as a Git repository on branch `main`.
- No GitHub remote is configured yet.
- The project contains local-only artifacts that should not be pushed directly, including `.venv/`, `.env`, cache folders, generated LaTeX files, model binaries, and scraper page dumps.

## Recommended First Commit Cleanup

1. Keep source code, manuscript source files, project notes, and reproducible configuration in Git.
2. Keep secrets, virtual environments, caches, generated build files, and large local binaries out of Git.
3. Use `git rm --cached` for files that are already tracked but should remain only on your computer.
4. Commit the cleanup before connecting the folder to GitHub.

## Create The GitHub Repository

Recommended default: create a private repository first.

Because this folder already had local commits before the cleanup, older history may still contain `.venv/`, cache files, and generated artifacts. If you push the current `main` history as-is, GitHub may still receive those old files through past commits.

For the first GitHub upload, the cleanest option is usually to create a fresh first commit from the cleaned working tree instead of preserving the old local history. Preserve the existing local history only if you specifically need those old commits.

```bash
git status
git add .gitignore .env.example README.md docs/GITHUB_SETUP.md
git commit -m "Prepare thesis project for GitHub"
```

Then create an empty GitHub repository and add it as `origin`:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

If using HTTPS instead of SSH:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## Public Repo Review

Before switching from private to public, check:

- No `.env` or API keys are committed.
- No confidential property data is committed.
- No files exceed GitHub's file size limits.
- The README explains how to recreate local environments and generated outputs.
