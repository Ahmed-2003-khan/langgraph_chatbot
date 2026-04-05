---
description: Push changes with learning comments to GitHub
---

# Automated Push Workflow with Learning Comments

This workflow automates the process of:
1. Identifying changed files in the repository
2. Grouping changes into logical commits (up to 3)
3. Adding educational comments per group before each commit
4. Pushing all commits to the remote GitHub repository
5. Removing ALL comments in one final clean-up commit

---

## Steps:

### 1. Check Git Status
```bash
git status
git diff
```
Review all modified, added, or untracked files.

---

### 2. Group Changes into Logical Commits (up to 3)

Analyse the changed files and split them into **up to 3 logical groups** based on what concept or layer they belong to. Use judgement — fewer commits are fine if changes are small.

**Grouping guidelines:**
- **Backend / graph logic** → one commit (e.g. new nodes, edges, state, checkpointer)
- **Frontend / UI** → one commit (e.g. Streamlit pages, new UI patterns)
- **Config / infra / other** → one commit (e.g. requirements.txt, .env, new files that don't fit above)

If all changes are in a single file or tightly coupled, use **1 commit** instead of forcing 3.

---

### 3. For Each Group: Add Comments → Stage → Commit

Repeat this mini-cycle for each group:

#### 3a. Add Learning Comments to the files in this group
- Explain what LangGraph / Python concepts are demonstrated
- Note why this pattern is used
- Call out any bugs that were fixed, with the error and the fix
- Comments should be educational for future reference

#### 3b. Stage only the files in this group
```bash
git add <file1> <file2> ...
```

#### 3c. Commit with a descriptive message
```bash
git commit -m "Learning: [Concept demonstrated in this group]"
```

Example commit messages:
- `"Learning: SqliteSaver persistent checkpointing with sqlite3 connection"`
- `"Learning: Streamlit sidebar with dynamic thread switching via get_state()"`
- `"Learning: Add requirements.txt and fix module import casing"`

---

### 4. Push All Commits at Once
```bash
git push origin main
```

---

### 5. Remove ALL Learning Comments (from every file that was touched)
After a successful push:
- Strip every comment that was added in step 3 from all touched files
- Restore the files to clean, uncluttered working copies

---

### 6. Final Clean-Up Commit
Stage and commit the comment-stripped versions so the local and remote are in sync and no comment lines appear locally:
```bash
git add .
git commit -m "Cleanup: remove learning comments from local files"
git push origin main
```

This ensures:
- The working files are identical to what the user wrote (no injected lines)
- The Git history still contains the fully-commented educational versions in earlier commits
- The final commit is always a clean `Cleanup:` commit, never a `Learning:` commit

---

### 7. Verify Clean State
```bash
git status
```
Should show "working tree clean".

---

## Summary of Commit Pattern

| Commit # | Content | Message prefix |
|---|---|---|
| 1 | Backend / graph changes with comments | `Learning:` |
| 2 | Frontend / UI changes with comments | `Learning:` |
| 3 | Config / infra / other (if needed) | `Learning:` |
| Final | Comment-stripped versions of all files | `Cleanup:` |

## Notes
- Always use fewer commits if the changes don't justify splitting
- The `Cleanup:` commit is **always** the last one — never skip it
- Local workspace should always end up identical to what the user wrote
- Past commits are the learning log; the working directory is always clean
