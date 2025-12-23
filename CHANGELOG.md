# Changelog

All notable changes to this project will be documented in this file.

## [0.0.2] - 2025-12-23

### Added
- `list_reminder_lists` tool - shows all reminder lists with counts
- `list_reminders` tool - get reminders with optional list/limit filters
- `get_reminder_stats` tool - count completed vs incomplete reminders
- `delete_completed_reminders` tool - batch delete completed reminders

### Fixed
- `search_reminders` now uses `whose` clause for server-side filtering (much faster)
- `create_reminder` parameter name fixed (was passing `title` instead of `name`)
- Reminders module uses JSON output for reliable parsing
- Default to incomplete reminders only for better performance with large lists

## [0.0.1] - 2025-12-23

### Added
- VERSION constant in apple_mcp.py for version tracking
- Version release command (`.claude/commands/version.md`)

### Documentation
- Improved CLAUDE.md with architecture overview, data flow patterns, and development commands
