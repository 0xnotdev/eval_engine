# Validator Usage

## validate-loop.py

A stdlib-only Python script that validates `LOOP.md` files against the repository's quality standards.

### Requirements

- Python 3.8+
- No external dependencies (stdlib only)

### Usage

```bash
# Validate a single loop
python tools/validate-loop.py loops/evaluating-rag-faithfulness/LOOP.md

# Validate all loops
python tools/validate-loop.py --all

# JSON output (for CI/CD)
python tools/validate-loop.py --all --json

# Strict mode (warnings = errors)
python tools/validate-loop.py --all --strict
```

### What It Checks

| Check | Level | Description |
|-------|-------|-------------|
| YAML frontmatter exists | ERROR | File must start with `---` |
| Required fields present | ERROR | `name`, `description`, `domain`, `subdomain`, `tags`, `version`, `author`, `license` |
| Name format | ERROR | Must be kebab-case, max 64 characters |
| Name consistency | ERROR | Directory name must match frontmatter `name` |
| Description length | ERROR | Minimum 50 characters |
| Domain value | ERROR | Must be `ai-testing` |
| Subdomain value | ERROR | Must be from allowed list |
| Tag count | ERROR | At least 2 tags |
| Required sections | ERROR | Must have: When to Use, Prerequisites, Workflow |
| Recommended sections | WARNING | Should have: Overview, Objectives, Validation Criteria |
| Code blocks in Workflow | WARNING | Workflow should contain executable code |
| Directory structure | WARNING | Should have `references/` and `scripts/` subdirectories |
| LICENSE file | WARNING | Each loop should include an Apache-2.0 LICENSE copy |
