# Release Workflow

This document describes the release process for PaperPilot.

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Release Process

1. **Prepare Release Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.2.3
   ```

2. **Update Version**
   - Update version in `package.json`
   - Update version in `pyproject.toml`
   - Update changelog (see below)

3. **Run Full Test Suite**
   ```bash
   make lint
   make typecheck
   make test
   make build
   ```

4. **Merge to Main**
   ```bash
   git checkout main
   git merge release/v1.2.3
   git tag v1.2.3
   git push origin main --tags
   ```

5. **Deploy**
   - CI/CD pipeline automatically deploys to staging
   - Manual approval for production deployment
   - Run migrations: `make migrate`
   - Run smoke tests

6. **Merge Back to Develop**
   ```bash
   git checkout develop
   git merge release/v1.2.3
   git push origin develop
   ```

## Changelog

Maintain `CHANGELOG.md` with sections:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

Use automated changelog generation with `git-cliff` or similar.

## Rollback

If rollback needed:

1. Identify last good commit/tag
2. Deploy previous version
3. Investigate root cause
4. Fix and re-release

## Hotfixes

For critical production issues:

1. Create `hotfix/critical-bug` from `main`
2. Fix and test
3. Merge to `main` and tag
4. Merge to `develop`
