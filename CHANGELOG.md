# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Development environment automation scripts (`scripts/dev-setup.sh`, `activate_dev.sh`, `run_tests.sh`)
- Comprehensive development documentation (`DEVELOPMENT.md`)
- Automated testing for development scripts
- Documentation standardization (CONTRIBUTING.md, CHANGELOG.md, DESIGN.md, ROADMAP.md)

### Fixed
- dev-setup.sh --help infinite execution causing test timeouts
- Network test byte handling errors  
- GUI test compatibility issues (temporarily skipped with Issue #85)
- CI workflow permissions for security compliance

---

## [0.3.0] - 2025-07-14

### Added
- Board size preservation in save/load operations
- Backward compatible save file format (3-line and 4-line support)
- Comprehensive board size validation (4-26, even numbers only)
- Development workflow automation scripts
- Gemini AI code review integration
- Issue workflow automation tools

### Fixed
- Memory leak in game history system
- AI board size compatibility issues
- Path traversal security vulnerabilities
- Input validation security improvements

### Security
- Enhanced path traversal protection
- Improved input validation for network operations
- Secure file handling with proper validation

## [0.2.0] - 2025-07-12

### Added
- Comprehensive test coverage improvements (84% → 86%)
- AI difficulty level testing and validation
- Memory management and leak detection tests
- Security testing for input validation and path traversal

### Fixed
- Test coverage gaps in critical components
- AI algorithm edge cases
- Memory management issues

## [0.1.0] - Initial Release

### Added
- Bitboard-based Othello game implementation
- CLI and GUI interfaces
- AI opponents with multiple difficulty levels (easy, hard, expert)
- Network play functionality
- Save/load game state
- Opening book for AI improvements
- Comprehensive test suite
