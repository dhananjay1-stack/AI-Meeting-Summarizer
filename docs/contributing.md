# Contributing Guide

Thank you for your interest in contributing to the AI Meeting Summarizer!

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/meeting-summarizer.git
   ```
3. **Set up** the development environment (see [Developer Guide](developer_guide.md))
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. Make your changes
2. Write or update tests
3. Run the test suite:
   ```bash
   python -m pytest backend/tests/ -v
   ```
4. Run linting:
   ```bash
   ruff check backend/
   ```
5. Commit with a descriptive message:
   ```bash
   git commit -m "feat: add speaker identification to transcript viewer"
   ```
6. Push and open a Pull Request

## Commit Message Convention

We follow [Conventional Commits](https://conventionalcommits.org):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `style:` — Formatting (no code change)
- `refactor:` — Code restructuring
- `test:` — Adding or fixing tests
- `chore:` — Build process, tooling, dependencies

## Code Quality

- All Python code must pass **ruff** linting
- All functions must have **type hints**
- New features must have **tests**
- Keep existing comments and documentation intact unless updating them

## Reporting Issues

When filing an issue, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, browser)

---

# Future Roadmap

## Near-term

- [ ] Real-time transcription via WebSocket streaming
- [ ] Speaker diarization integration (pyannote.audio)
- [ ] Team/shared meetings with workspace support
- [ ] Email notifications when processing completes
- [ ] Meeting calendar integration

## Mid-term

- [ ] Mobile-responsive PWA
- [ ] Batch processing for multiple files
- [ ] Customizable summary templates
- [ ] Webhook notifications for integrations
- [ ] Admin dashboard with user management

## Long-term

- [ ] Real-time meeting capture (system audio)
- [ ] Multi-language UI support (i18n)
- [ ] Meeting analytics and trends dashboard
- [ ] Plugin system for custom AI workflows
- [ ] Enterprise SSO (SAML/OIDC) integration
