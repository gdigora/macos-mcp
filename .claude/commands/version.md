# Version Release Command

Release version: **$ARGUMENTS**

## Steps

1. **Update VERSION in apple_mcp.py**
   - Find `VERSION = "x.x.x"` constant near the top of apple_mcp.py
   - Change to `VERSION = "$ARGUMENTS"`
   - If VERSION doesn't exist, add it after the imports: `VERSION = "$ARGUMENTS"`

2. **Update CHANGELOG.md**
   - Get previous version tag (latest v* tag)
   - Get all commits since previous version tag
   - Add new section at top of CHANGELOG.md: `## [$ARGUMENTS] - {today's date in YYYY-MM-DD format}`
   - If CHANGELOG.md doesn't exist, create it with header:
     ```
     # Changelog
     All notable changes to this project will be documented in this file.
     ```
   - Organize changes by type:
     - Added: New features or functionality
     - Changed: Changes to existing functionality
     - Fixed: Bug fixes
     - Documentation: Documentation changes
   - Write clear, user-focused descriptions

3. **Commit all changes**
   - Commit ALL changes (including any uncommitted work)
   - Use commit message: `chore: Release version $ARGUMENTS`
   - Create annotated git tag: `v$ARGUMENTS` with message `Release version $ARGUMENTS`

4. **Push to remote**
   - Push commits: `git push origin main`
   - Push the tag: `git push origin v$ARGUMENTS`

## Important Notes

- If no previous version tag exists, include all commits
- Use today's date in YYYY-MM-DD format
- Tag should be annotated (git tag -a) not lightweight
