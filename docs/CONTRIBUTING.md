# Contributing to Invoice Buddy

*Up to date as of v0.2.9*

## TL;DR

Invoice Buddy is currently a solo project. If you're interested in contributing, reach out first so we can coordinate.

- Commits go directly to `main` (for now)
- Use descriptive commit messages
- Run the app locally before pushing to verify it actually starts
- Keep changes focused — one feature or fix per commit

## Commit Conventions

Use the following prefixes:

- `added:` for a new feature or enhancement
- `fixed:` for a bug fix
- `security:` for a security patch
- `docs:` for documentation changes
- `changed:` for code restructuring, dependencies updated, or changes which don't fit into any other category

Write a short description after the prefix. Keep it to one line if possible. Look at the changelog for more guidance.

Examples:
- `fixed: updated setuptools dependency`
- `added: toast notification when auto-name completes`
- `docs: updated build instructions for Nuitka build`

## Development Environment Setup

See [build.md](docs/build.md) for detailed setup instructions including Python version, virtual environment creation, and system dependencies.

## Release Process

Releases are handled by an internal deployment script not publised on GitHub. The script:

1. Verifies build artifacts exist (AppImage, .deb, .exe)
2. Generates SHA256 checksums
3. Uploads backups to Proton Drive via rclone
4. Pushes source to Forgejo (internal, not public), GitHub, and Codeberg
5. Creates releases with assets on all three platforms
6. Posts release announcement to Mastodon (stable releases only)

Versions labeled -alpha are skipped entirely. Beta versions are marked as pre-releases.

## Project Structure

See [architecture.md](docs/architecture.md) for a detailed breakdown of the codebase, folder structure, and key design decisions.

## AI Usage Policy

Using AI tools to assist with contributions is fine, but:

- You are responsible for every line of code you submit
- Do not submit AI-generated code you don't understand
- Test your changes before committing
