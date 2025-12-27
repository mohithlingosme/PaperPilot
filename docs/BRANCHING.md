# Branching Model

This project follows the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model with some simplifications.

## Branches

- `main`: Production-ready code. Only updated via PR merges from `develop` or hotfixes.
- `develop`: Integration branch for features. All feature branches merge here.
- `feature/*`: Feature branches. Created from `develop`, merged back to `develop` via PR.
- `hotfix/*`: Hotfix branches for critical production bugs. Created from `main`, merged to both `main` and `develop`.

## Workflow

1. Create feature branch from `develop`: `git checkout -b feature/my-feature develop`
2. Develop and commit changes.
3. Push and create PR to `develop`.
4. After review and CI pass, merge to `develop`.
5. When ready for release, create PR from `develop` to `main`.
6. Tag releases on `main`.

## Naming Conventions

- Branches: `feature/description-with-hyphens`
- Commits: Follow [Conventional Commits](https://www.conventionalcommits.org/)
- Tags: `v1.2.3` (semantic versioning)

## Protection Rules

- `main`: Require PR, require status checks, require up-to-date branches, restrict pushes.
- `develop`: Require PR, require status checks.
