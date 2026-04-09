# Idea: Local Claude/Codex Fallback

## Original Concept

A local backend layer for Claude Code and Codex that lets users keep using the same harness, while swapping the model backend to local runtimes when needed.

Core behavior:
- auto-detect installed local runtimes
- start with **Ollama**, **LM Studio**, and **llama.cpp** support
- use **llmfit** to detect the best-fit model for the current machine
- default to a balanced speed/quality mode, with user-selectable faster or higher-quality modes
- expose product names as **`claude-local`** and **`codex-local`**
- preserve the normal Claude Code / Codex usage style with **no workflow change for the user**
- do **not** overwrite or break the official Anthropic / OpenAI setups
- make it easy to switch back to official cloud models at any time

## Clarified Understanding

This should not be positioned as “offline Claude Code” because that implies parity with Anthropic’s official product and creates bad expectations.

The cleaner framing is:

**A local backend bridge for Claude Code and Codex users**.

Key product rule:
- users should not have to change how they normally use Claude Code or Codex
- the backend becomes local, but the harness mental model and usage style stay the same

Naming direction:
- **`claude-local`** for Claude Code users
- **`codex-local`** for Codex users

When the user runs out of Anthropic/OpenAI quota, or wants to work fully local/offline, the tool should:
1. detect available local inference runtimes
2. inspect the machine profile
3. use `llmfit` to identify the best-fit coding model
4. connect the existing Claude/Codex harness style to a local backend
5. keep official Claude Code/Codex untouched and easy to return to

## Target Audience

- Claude Code power users who hit usage limits
- Codex users who want a local fallback path
- developers who already have local model runtimes installed but do not want to manually tune everything
- privacy-conscious or offline-first developers who want local coding help without replacing their main cloud workflow

## Goals & Objectives

### Primary goal
Provide a **one-command fallback** from official cloud coding agents to a sane local coding setup.

### User promise
- "when official tokens run out, you still have a local coding copilot"
- "one command to go local, one command to come back"

### Success criteria
In 6-12 months, the product should:
- reliably detect local runtimes and usable coding models
- recommend or auto-select the best-fit local coding model for a machine
- support at least Claude-oriented and Codex-oriented fallback workflows
- become a trusted emergency/local mode for developers, not a novelty wrapper

## Technical Context
- Stack: likely CLI-first, with a runtime adapter layer and model-scoring layer
- Timeline: MVP should be possible in 2-4 weeks if tightly scoped
- Budget: bootstrapped / solo-friendly
- Constraints:
  - must not break official Claude Code config
  - should avoid pretending local models are equal to frontier cloud models
  - needs good machine/runtime detection or the UX falls apart

## Product Shape

### Best framing
- not “offline Claude Code installation”
- instead: **local backend for Claude Code / Codex**

### Naming
- **`claude-local`**
- **`codex-local`**

### Best UX shape
Preferred rule:
- keep usage as close as possible to normal Claude Code / Codex behavior
- avoid making users learn a second workflow unless absolutely necessary

Setup/status/doctor commands can still exist behind the scenes, but the user-facing experience should preserve the existing harness style.

### Modes
- balanced (default)
- fast
- quality

### Runtime detection
First support:
- Ollama
- LM Studio
- llama.cpp

Potential later support:
- vLLM

### Model selection
Use `llmfit` to:
- inspect hardware/resources
- inspect local runtimes
- rank already-installed models
- recommend one download if no suitable coding model exists

### Configuration rules
- official Claude Code config remains untouched
- local fallback config is stored separately
- switching between official and local should be explicit and reversible

## Discussion Notes

### Strong positioning insight
This product should win as a **local backend bridge**, not by claiming to replicate or replace Claude Code/Codex.

### Important product decision
Make it a **backend bridge + optimizer + switcher**, not a full agent harness from scratch.

### MVP shape
- runtime detection
- hardware detection
- `llmfit` integration for model choice
- one-command setup
- local backend mode with no major workflow change
- support Claude/Codex users directly
- explicit switch back to official cloud tooling

### Risks already identified
- expectation trap if marketed as “offline Claude Code”
- local model quality gap vs official Claude/Codex
- runtime abstraction complexity across backends
- coding UX depends on tool-use quality, not just raw model benchmark strength
