# Contributing

## Branching

1. Create a feature branch from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/<short-description>
   ```
2. Implement changes (tests, helpers, docs).
3. Run the full suite and fix failures:
   ```bash
   pytest
   ```

## Commit messages

- Prefer imperative, concise messages focused on **why**.
- Examples: `Add Users negative coverage for missing ids`, `Document marker usage for agents`.

## Pull requests

1. Push the branch and open a PR against `main`.
2. PR description should include:
   - **Summary** — what changed and why
   - **Test plan** — commands run and results (e.g. `pytest` green)
3. Keep PRs focused: one resource/feature area when practical.

## Adding a new scenario

1. Confirm the endpoint is in scope (Users/Posts) or update README scope first.
2. Add the test to the matching module under `tests/`.
3. Apply the correct marker (`positive` / `negative` / `edge`).
4. Use fixtures; do not invent a second HTTP session unless required.
5. Run `pytest` locally until green.

## Code review checklist

- [ ] No hardcoded hostnames or secrets
- [ ] Markers and Arrange/Act/Assert present
- [ ] Assertions check status and meaningful fields
- [ ] README / AGENTS.md updated if needed
- [ ] `pytest` passes
