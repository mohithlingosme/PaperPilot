# Contributing to PaperPilot

Thank you for your interest in contributing to PaperPilot! This document provides guidelines and information for contributors.

## Development Setup

1. Fork the repository.
2. Clone your fork: `git clone https://github.com/your-username/paperpilot.git`
3. Run setup: `make setup`
4. Run locally: `make dev`
5. Check health: `make doctor`

## Branch Naming Rules

Follow the [branching model](docs/BRANCHING.md):

- `main`: Production branch
- `develop`: Integration branch
- `feature/*`: New features (e.g., `feature/add-user-authentication`)
- `hotfix/*`: Critical fixes (e.g., `hotfix/security-patch`)

Branch names should be lowercase, use hyphens, and be descriptive.

## Pull Request Checklist

Before submitting a PR:

- [ ] Branch is up-to-date with target branch
- [ ] All tests pass: `make test`
- [ ] Code linted: `make lint`
- [ ] Type checked: `make typecheck`
- [ ] Documentation updated if needed
- [ ] Migrations added for schema changes
- [ ] Security review completed for sensitive changes
- [ ] UI changes include screenshots/videos
- [ ] Breaking changes clearly documented

## Review Requirements

- At least 1 maintainer approval required
- CI must pass all checks
- No unresolved conversations
- Follow [Definition of Done](docs/DEFINITION_OF_DONE.md)

## Commit Convention Rules

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
- `feat: add user authentication`
- `fix: resolve login timeout issue`
- `docs: update API documentation`

## Testing

- Write unit tests for all new code
- Add integration tests for DB/API changes
- Ensure coverage meets thresholds
- Run full test suite: `make test`

## Code Style

- Frontend: ESLint + Prettier
- Backend: Ruff + Black + MyPy
- Run `make lint` and `make format` before committing
