# claude-codex-local

Local backend bridge for Claude Code and Codex.

Core idea:
- keep the existing Claude Code / Codex harness
- swap the backend to a best-fit local model/runtime
- keep workflow change as close to zero as possible

## POC status

This repo now has a real POC for the narrowest sensible path:

- runtime: **Ollama**
- real proved harness: **Codex CLI**
- config-prepared harness: **Claude Code**
- model-fit helper: **llmfit**
- isolation rule: **repo-local state only; official configs untouched**

## Quickstart

### Prereqs assumed

Already installed on the machine:

- `ollama`
- `claude`
- `codex`

Installed during this POC and expected on `PATH`:

- `llmfit` (tested with `0.9.3`)

### Minimal setup

Pull the tiny local coder model if it is not already present:

```bash
ollama pull qwen2.5-coder:0.5b
```

Inspect the machine and recommendation:

```bash
./bin/poc-machine-profile
./bin/poc-recommend
```

Run the doctor + smoke test:

```bash
./bin/poc-doctor --run-codex-smoke
./bin/codex-local exec --skip-git-repo-check 'reply with exactly READY'
```

Launch the local Codex path:

```bash
./bin/codex-local
```

Prepare the local Claude config path:

```bash
./bin/claude-local-config
```

## Repo-local state

Everything local to the bridge is written under:

```text
.claude-codex-local/
```

You can override that with `CLAUDE_CODEX_LOCAL_STATE_DIR`.

## Included docs

- `idea.md`
- `validate.md`
- `prd.md`
- `tasks.md`
- `docs/poc-bootstrap.md`
- `docs/poc-architecture.md`
- `docs/poc-proof.md`

## Positioning

This is **not** an offline replacement for Claude Code or Codex.
It is a local backend bridge that preserves the existing workflow while making local model usage practical.
