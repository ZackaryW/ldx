# Documentation Workflow Instructions

## Pattern: Scenario-Based Documentation

When creating documentation for ldx, follow this workflow.

## Core Principles

1. **One scenario = One file**
2. **Keep files under 100 lines**
3. **Focus on "I want to..." questions**
4. **No junk - only essentials**

## File Structure

```
docs/
  scenarios/
    launch-one.md
    launch-many.md
    use-cli.md
    automate.md
    schedule.md
    custom-plugin.md
  reference/
    installation.md
    configuration.md
    api-basics.md
```

## Scenario File Template

```markdown
# [Action in Title Case]

**Goal:** [One sentence describing what user achieves]

## Basic Setup

[Minimal imports/setup code]

## [Main Feature 1]

[Code example]

## [Main Feature 2]

[Code example]

## Complete Example

[Working end-to-end example]
```

## README Pattern

Keep README minimal with links only:

```markdown
## What Can You Do?

### [category name]
[Scenario 1: Description](docs/scenarios/file.md)

[Scenario 2: Description](docs/scenarios/file.md)
```

**NO code examples in README** - link to scenarios instead.

## Workflow

### 1. Create Scenario File First

- Write focused scenario (under 100 lines)
- Use clear headings
- Include working examples
- No tips/next steps sections

### 2. Update README After

- Add link under appropriate category
- Keep it simple: `[Scenario X: Description](path)`
- No code snippets in README

### 3. Test Pattern

Before adding:
- Check existing README structure
- Match the pattern exactly
- Don't add extra sections

## Anti-Patterns

❌ Don't create 500+ line scenario files
❌ Don't add code examples to README
❌ Don't add "Tips" or "Next Steps" sections
❌ Don't assume - check existing patterns first

## Example: Adding New Scenario

```bash
# 1. Create scenario file
docs/scenarios/new-feature.md

# 2. Keep it focused (< 100 lines)
Goal + Setup + Examples + Complete Example

# 3. Update README
Add link under appropriate category
```

That's it.
