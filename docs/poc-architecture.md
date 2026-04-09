# POC architecture note

Date: 2026-04-09

## Narrow scope

This POC is deliberately tiny:

- runtime: **Ollama**
- harnesses in scope: **Codex first**, **Claude config path second**
- model-fit engine: **llmfit**
- config rule: **official Claude/Codex configs stay untouched**

That is enough to prove the idea without pretending we solved every backend.

## The bridge shape

### Shared pieces

Both `claude-local` and `codex-local` use the same four shared building blocks:

1. **Machine profile**
   - source of truth: `llmfit system --json`
   - extra local facts: installed Ollama models, tool versions, local-vs-cloud model inventory

2. **Model recommendation**
   - source of truth: `llmfit info <candidate>`
   - POC rule: prefer an **installed** coding model that actually starts on this machine over a more theoretical recommendation

3. **Isolated local state**
   - stored under repo-local `.claude-codex-local/`
   - local HOME/XDG env is set only for the launched subprocesses
   - Ollama integration config lands in `.claude-codex-local/home/.ollama/config/config.json`

4. **Ollama integration config**
   - written via `ollama launch <integration> --config --model <model>`
   - this avoids mutating official `~/.codex`, `~/.claude`, or other user-level config

### Codex bridge model

Codex already exposes a real local path on this machine:

- `codex --oss`
- `codex --local-provider ollama`

So the POC bridge for Codex is thin by design:

1. recommend a model
2. write isolated Ollama integration config for `codex`
3. launch Codex with:
   - `--oss`
   - `--local-provider ollama`
   - `-m <selected model>`

That gives a real end-to-end local run without touching the official Codex config.

### Claude bridge model

Claude Code does **not** expose an equally obvious local-provider flag in the installed CLI help on this machine.

What is real today:

- `ollama launch claude --config --model <model>` writes isolated Ollama integration config for Claude
- the config lives under the repo-local state dir, not the user's real home

What remains intentionally unproven in this POC:

- a fully validated Claude end-to-end smoke test in this repo

That means the Claude path is **config-real but runtime-unproven** here. Honest beats fake.

## Shared vs tool-specific

### Shared

- machine profile collection
- local model inventory
- llmfit lookups
- isolated HOME/XDG strategy
- Ollama config generation
- model-selection rationale and caveats

### Codex-specific

- native `--oss --local-provider ollama` execution path
- end-to-end smoke test using `codex exec`
- known harmless 401 model-refresh noise from Codex in local-only mode

### Claude-specific

- configuration is delegated to `ollama launch claude`
- runtime proof is deferred until we have a stable local launch recipe worth automating

## What is real vs fake in the POC

### Real

- `ollama`, `claude`, `codex` presence verified locally
- `llmfit` installed locally and used for profiling/model metadata
- local coding model pulled into Ollama: `qwen2.5-coder:0.5b`
- isolated config path under `.claude-codex-local/`
- real Codex -> Ollama end-to-end response on this machine

### Fake / manual / deferred

- automatic multi-runtime abstraction beyond Ollama
- perfect llmfit-only ranking; on this tiny host, live runtime proof matters more than pure score
- polished Claude runtime bridge
- quality-mode promise on 2 GB RAM hardware; that's fantasy land

## Config isolation rule

The POC never needs to edit official Claude/Codex config files.

Instead it uses:

- `CLAUDE_CODEX_LOCAL_STATE_DIR` or default `.claude-codex-local/`
- subprocess-local `HOME`
- subprocess-local `XDG_CONFIG_HOME`
- subprocess-local `XDG_DATA_HOME`

That keeps rollback trivial:

```bash
rm -rf .claude-codex-local
```

## POC implementation decision

The first real proof is **Codex + Ollama + qwen2.5-coder:0.5b**.

Why this path first:

- Codex already has a native local-provider flag
- Ollama already has native `launch codex` / `launch claude` integration config support
- this machine is weak, so the smallest coder model wins by survival, not glory

## Known limitations

- llmfit marks the tiny coder model as a tight fit on this host; that warning is fair
- the model is good enough for plumbing proof, not for claiming premium coding quality
- Codex emits a harmless 401 model-refresh warning in local-only mode before still answering successfully
