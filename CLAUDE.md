# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pryces is a Python project built with clean architecture principles, emphasizing SOLID design, minimal dependencies, and clear separation of concerns.

## Critical Directives

### Update README.md After Changes
**IMPORTANT**: Whenever you make significant changes to the codebase (new features, API changes, new fields, renamed parameters, etc.), you MUST update the README.md to reflect these changes:
- Update example outputs to match current JSON structure
- Update command examples if CLI arguments change
- Add documentation for new features
- Ensure all examples are accurate and tested

The README is user-facing documentation and must stay synchronized with the actual code behavior.

### Prefer Using Subagents for Context Optimization
**IMPORTANT**: Always use specialized subagents (via the Task tool) whenever possible to optimize context usage, unless explicitly instructed not to use subagents.

Use subagents for:
- **Exploration tasks**: Understanding codebase structure, finding patterns, locating functionality
- **Search operations**: Multi-step searches across files, grep operations with follow-up analysis
- **Planning**: Complex implementation plans that require code exploration
- **Research**: Investigating how features work, tracing dependencies
- **Parallel work**: Independent tasks that can run simultaneously

Only work directly (without subagents) when:
- User explicitly requests direct execution
- Task is trivial (single file read/write)
- Already in a subagent context

This helps maintain clean context and allows better task delegation.

### Prefer Using Plan Mode for Non-Trivial Tasks
**IMPORTANT**: Always use plan mode (EnterPlanMode) for implementation tasks unless explicitly instructed not to or the task is trivial.

Use plan mode for:
- **New features**: Adding any new functionality beyond single-line changes
- **Code modifications**: Changes affecting multiple files or existing behavior
- **Refactoring**: Restructuring code or changing architecture
- **Multi-step implementations**: Tasks requiring more than 2-3 simple steps
- **Uncertain scope**: When you need to explore before understanding full requirements

Do NOT use plan mode for:
- User explicitly requests direct implementation
- Trivial tasks (typo fixes, single-line changes, obvious bugs)
- Pure research/exploration (use Task tool with Explore agent instead)
- Tasks with very specific, detailed instructions already provided

Plan mode ensures alignment on approach before implementation, preventing wasted effort.

## Patterns and Conventions

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### Code Comments
**Write code that explains itself through clear naming and structure.** Only add comments when they provide value beyond what the code already communicates.

**When to add comments:**
- **WHY, not WHAT**: Explain reasoning, not mechanics
  - Good: `# Fallback to regularMarketPrice for after-hours trading`
  - Bad: `# Get the price from info dictionary`
- **Non-obvious logic**: Explain heuristics, validation rules, edge cases
  - Good: `# Yahoo Finance returns ≤3 fields for invalid symbols`
- **Architectural decisions**: Document important design choices
  - Good: `# Use Decimal for precision in financial calculations`
- **Complex algorithms**: Break down multi-step logic

**When NOT to add comments:**
- Method names that restate the function signature
- Docstrings that just repeat parameter names/types already shown in type hints
- `setup_method()` docstrings in tests (the name is self-explanatory)
- Inline comments describing obvious operations (`# Extract price`, `# Return response`)
- Parameter documentation when type hints are clear (`provider: StockPriceProvider`)

**Docstring guidelines:**
- Module/class docstrings: Explain purpose and responsibility
- Method docstrings: Focus on contract (inputs/outputs/side effects), not implementation
- Test docstrings: Only if the test scenario is complex or non-obvious
- Keep parameter docs minimal; rely on type hints when they're sufficient

## Pre-Commit Requirements

Before creating any commit, ensure the following:

1. **Run all tests**: Execute `pytest` to verify all tests pass
2. **Verify test coverage**: Ensure new code is adequately tested
3. **Review changes**: Check that only intended changes are staged
4. **Update documentation**: If adding new features, update relevant docs

**Important**: Never commit code with failing tests. The test suite must pass before any commit.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format: `<type>: <description>`

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
