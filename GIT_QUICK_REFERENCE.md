# Git Quick Reference

## Daily Git Workflow

### Check Status
```bash
git status
```
Shows which files have been modified, added, or deleted.

### Stage and Commit Changes
```bash
# Stage all changes
git add .

# Or stage specific files
git add path/to/file.py

# Commit with a message
git commit -m "Brief description of changes"
```

### Push to GitHub
```bash
git push
```

### Pull Latest Changes
```bash
git pull
```

### Complete Workflow (After Making Changes)
```bash
git add .
git commit -m "Updated compliance report logic"
git push
```

---

## Common Git Commands

### View Commit History
```bash
git log --oneline
```

### View Remote Repository
```bash
git remote -v
```

### Create a New Branch
```bash
git checkout -b feature-name
```

### Switch Branches
```bash
git checkout master
git checkout main
```

### Undo Changes (Before Commit)
```bash
# Discard changes to a file
git checkout -- filename

# Unstage a file
git reset HEAD filename
```

### View Differences
```bash
# See what changed
git diff

# See what's staged
git diff --cached
```

---

## GitHub Repository Management

### Change Repository Visibility
```bash
# Make private
gh repo edit --visibility private

# Make public
gh repo edit --visibility public
```

### View Repository on GitHub
```bash
gh repo view --web
```

### Clone Your Repository
```bash
git clone git@github.com:coreylee1990/Orion_Operator_Lifecycle_Automation.git
```

---

## Tips

1. **Commit often** - Small, frequent commits are better than large ones
2. **Write clear commit messages** - Describe what changed and why
3. **Pull before push** - Always pull latest changes before pushing
4. **Check status** - Use `git status` frequently to see what's changed

---

## Repository URL
**GitHub:** https://github.com/coreylee1990/Orion_Operator_Lifecycle_Automation
