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

### Always Use Virtual Environment for Testing
**IMPORTANT**: This project uses a Python virtual environment. You MUST activate it before running any tests or testing code manually.

**Required workflow:**
1. **Before testing**: Activate the virtual environment with `source venv/bin/activate` (or `source .venv/bin/activate` depending on the venv location)
2. **Run tests**: Execute `pytest` or test the CLI manually
3. **After testing**: Deactivate with `deactivate`

**Why this matters:**
- Running tests without the venv will fail due to missing dependencies
- Attempting to install packages globally wastes time and may cause permission errors
- Always check for the venv before running Python commands

**Never**: Try to install the Python environment from scratch or install packages globally. The virtual environment already exists and contains all required dependencies.

## Patterns and Conventions

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### Code Comments

**Write self-documenting code.** Use clear names, structure, and type hints. Only add comments when they explain WHY, not WHAT.

**Rules:**
1. **Type hints eliminate documentation**: If a parameter has a type hint, don't document its type in a docstring
2. **Method names should be obvious**: `get_command()`, `register()`, `validate_symbol()` need no docstring
3. **No restating**: `def __init__()` → "Initialize X" adds zero value
4. **Comments explain reasoning**: Use them for business logic, heuristics, or non-obvious constraints

**Examples:**
```python
# ✗ BAD - Just restates code
def __init__(self, provider: StockPriceProvider) -> None:
    """Initialize with provider.

    Args:
        provider: The stock price provider
    """
    self._provider = provider

# ✓ GOOD - Type hint is enough
def __init__(self, provider: StockPriceProvider) -> None:
    self._provider = provider

# ✗ BAD - Restates method name
def get_metadata(self) -> CommandMetadata:
    """Return metadata describing this command."""
    pass

# ✓ GOOD - Signature is the contract
@abstractmethod
def get_metadata(self) -> CommandMetadata:
    pass

# ✓ GOOD - Explains WHY (business logic)
if len(info) <= 3:  # Yahoo Finance returns ≤3 fields for invalid symbols
    return None
```

**Keep these docstrings:**
- **Module/class docstrings** explaining purpose and responsibility
- **Method docstrings** that document contracts beyond what the signature shows (raises, side effects, special return semantics)

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
