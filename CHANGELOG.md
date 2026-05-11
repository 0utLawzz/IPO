# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [1.0.0] - 2026-05-11

### Added

- Manual login mode (default) with cookie persistence.
- Graceful stop via `CTRL + C`.
- `--all` mode to run all configured TM forms and exit.
- TM form configuration extended with duplicate-check enable/disable.

### Changed

- TM form configuration updated (fees and duplicate-check columns).
- Menu UI updated to show run-enabled status and duplicate-check column in `COL <letter>` format.

### Fixed

- EOF handling in terminal menus.
