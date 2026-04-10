# claude-codex-local

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/luongnv89/claude-codex-local/actions/workflows/ci.yml/badge.svg)](https://github.com/luongnv89/claude-codex-local/actions/workflows/ci.yml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Local backend bridge for Claude Code and Codex.**

Keep your entire Claude Code / Codex workflow — skills, statusline, agents, MCP servers, all config — and swap the backend to a best-fit local model. One alias (`cc` or `cx`) is all it takes.

---

## Why?

Claude Code and Codex are powerful harnesses, but they require a remote API call for every interaction. `claude-codex-local` lets you:

- **Run fully offline** using Ollama, LM Studio, or llama.cpp
- **Keep every config file** (`~/.claude`, `~/.codex`) untouched
- **Pick the best local model** for your hardware automatically via `llmfit`
- **Stay safe** — the wizard never writes outside `.claude-codex-local/`

---

## Features

- **Interactive setup wizard** — discovers your installed harnesses and engines, guides model selection, and wires everything up
- **Ollama first-class support** — uses `ollama launch` for clean process management
- **LM Studio / llama.cpp** — records the inline env vars needed to point the harness at your local server
- **`llmfit` integration** — analyses your hardware and recommends the best model quantization that fits in VRAM/RAM
- **Idempotent shell aliases** — re-running the wizard replaces the existing alias block in `~/.zshrc` / `~/.bashrc` rather than appending
- **Personalized guide** — generates `guide.md` with your exact daily-use commands after setup
- **One-command remote install** — no clone required

---

## Prerequisites

- macOS or Linux with a modern shell (zsh or bash)
- Python 3.10+
- At least one **harness**: [Claude Code](https://claude.ai/code) or [Codex CLI](https://github.com/openai/codex)
- At least one **engine**: [Ollama](https://ollama.com) (recommended), [LM Studio](https://lmstudio.ai), or llama.cpp
- [`llmfit`](https://github.com/luongnv89/llmfit) on `PATH` (optional but recommended for model selection)

---

## Quickstart

### One-command install (no clone required)

```bash
bash <(curl -sSL https://raw.githubusercontent.com/luongnv89/claude-codex-local/main/install.sh)
```

Or with wget:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/luongnv89/claude-codex-local/main/install.sh)
```

> **Important:** Use `bash <(...)`, not `curl … | bash`. The wizard is interactive and needs a real TTY on stdin — piping steals stdin.

Override defaults with env vars:

```bash
CCL_REF=v0.2.0 \
CCL_INSTALL_DIR=~/tools/claude-codex-local \
bash <(curl -sSL https://raw.githubusercontent.com/luongnv89/claude-codex-local/main/install.sh)
```

### Install from a clone

```bash
git clone https://github.com/luongnv89/claude-codex-local.git
cd claude-codex-local

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

./bin/claude-codex-local
```

### After setup

Reload your shell so the alias is picked up:

```bash
source ~/.zshrc   # or source ~/.bashrc
```

Then just run `cc` (Claude) or `cx` (Codex). That's it.

---

## What the wizard does

1. Discovers what you already have (harnesses, engines, `llmfit`, free disk)
2. Reports what's missing and how to install it
3. Asks which harness + engine combination you want
4. Asks which model (or uses `llmfit` to pick automatically)
5. Smoke-tests the engine with that model
6. Wires up the harness — captures `ollama launch claude|codex --model <tag>` or records the inline env for LM Studio / llama.cpp
7. Writes helper scripts to `.claude-codex-local/bin/{cc,cx}` and installs shell aliases
8. Verifies the full launch pipeline end-to-end
9. Writes a personalized `guide.md` with your exact commands

See [`guide.example.md`](guide.example.md) for a sanitized example of the generated output.

---

## Usage

### Wizard flags

```bash
./bin/claude-codex-local setup --harness claude --engine ollama   # skip prefs picker
./bin/claude-codex-local setup --non-interactive                  # CI-friendly
./bin/claude-codex-local setup --resume                           # resume after a failed step
./bin/claude-codex-local find-model                               # standalone llmfit recommendation
```

### Diagnostic helpers

```bash
./bin/poc-machine-profile   # dump the full machine profile as JSON
./bin/poc-doctor            # print wizard state + recommendation
./bin/poc-recommend         # llmfit-only model recommendation
```

---

## Project structure

```
.
├── bin/                        # Entry-point scripts
│   ├── claude-codex-local      # Main wizard entrypoint
│   ├── poc-doctor              # Diagnostic: wizard state
│   ├── poc-machine-profile     # Diagnostic: hardware profile
│   └── poc-recommend           # Diagnostic: model recommendation
├── scripts/
│   └── e2e_smoke.sh            # End-to-end smoke test
├── docs/
│   ├── poc-wizard.md           # 8-step wizard architecture
│   ├── poc-architecture.md     # System design overview
│   ├── poc-bootstrap.md        # Bootstrap / install flow
│   └── poc-proof.md            # Design rationale
├── tests/                      # pytest test suite
├── wizard.py                   # Interactive setup wizard (core logic)
├── poc_bridge.py               # Backend bridge / harness wiring
├── install.sh                  # One-command remote installer
├── pyproject.toml              # Project metadata and tool config
└── .claude-codex-local/        # Runtime state dir (gitignored)
```

---

## Local state

Everything written by the bridge goes under:

```
.claude-codex-local/
```

Override with the `CLAUDE_CODEX_LOCAL_STATE_DIR` environment variable.

---

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| UI / prompts | [questionary](https://github.com/tmbo/questionary), [rich](https://github.com/Textualize/rich) |
| Linting | [ruff](https://github.com/astral-sh/ruff) |
| Type checking | [mypy](https://mypy-lang.org) |
| Testing | [pytest](https://pytest.org) + pytest-cov |
| Security | [bandit](https://github.com/PyCQA/bandit), [detect-secrets](https://github.com/Yelp/detect-secrets) |
| Pre-commit | [pre-commit](https://pre-commit.com) |

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

For security issues, see [SECURITY.md](SECURITY.md).

---

## License

[MIT](LICENSE) — © 2024 Luong NGUYEN
