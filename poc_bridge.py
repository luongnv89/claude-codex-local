#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
ORIG_HOME = Path(os.environ.get("HOME", str(Path.home())))
STATE_DIR = Path(os.environ.get("CLAUDE_CODEX_LOCAL_STATE_DIR", ROOT / ".claude-codex-local"))
STATE_HOME = STATE_DIR / "home"
DEFAULT_MODEL = os.environ.get("CLAUDE_CODEX_LOCAL_MODEL", "qwen2.5-coder:0.5b")

CODING_MODEL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"coder",
        r"codeqwen",
        r"codegemma",
        r"deepseek-coder",
        r"granite-code",
        r"starcoder",
        r"codestral",
        r"codellama",
    )
]

LLMFIT_QUERY_MAP = {
    "qwen2.5-coder:0.5b": "Qwen/Qwen2.5-Coder-0.5B-Instruct",
    "qwen2.5-coder:1.5b": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "qwen2.5-coder:3b": "Qwen/Qwen2.5-Coder-3B-Instruct",
    "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
}


def ensure_path(env: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(os.environ if env is None else env)
    local_bin = ORIG_HOME / ".local/bin"
    path_entries = merged.get("PATH", "").split(os.pathsep) if merged.get("PATH") else []
    if local_bin.exists() and str(local_bin) not in path_entries:
        merged["PATH"] = f"{local_bin}{os.pathsep}{merged.get('PATH', '')}".rstrip(os.pathsep)
    return merged


def run(cmd: list[str], *, env: dict[str, str] | None = None, check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    final_env = ensure_path(env)
    return subprocess.run(cmd, check=check, capture_output=True, text=True, env=final_env, timeout=timeout)


def command_version(name: str, args: list[str] | None = None) -> dict[str, Any]:
    args = args or ["--version"]
    try:
        cp = run([name, *args])
        text = (cp.stdout or cp.stderr).strip().splitlines()
        return {"present": True, "version": text[0] if text else ""}
    except Exception as exc:
        return {"present": False, "error": str(exc)}


def state_env() -> dict[str, str]:
    env = ensure_path()
    env["HOME"] = str(STATE_HOME)
    env["XDG_CONFIG_HOME"] = str(STATE_HOME / ".config")
    env["XDG_DATA_HOME"] = str(STATE_HOME / ".local/share")
    return env


def ensure_state_dirs() -> None:
    (STATE_HOME / ".config").mkdir(parents=True, exist_ok=True)
    (STATE_HOME / ".local/share").mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def require(cmd: str) -> None:
    version = command_version(cmd)
    if not version.get("present"):
        print(f"missing required command: {cmd}", file=sys.stderr)
        sys.exit(1)


def run_shell(command: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return run(["bash", "-lc", command], env=env)


def configure_ollama_integration(target: str, model: str) -> dict[str, Any]:
    ensure_state_dirs()
    require("ollama")
    env = state_env()
    shell_cmd = f"printf 'n\\n' | ollama launch {shlex.quote(target)} --config --model {shlex.quote(model)}"
    cp = run_shell(shell_cmd, env=env)
    return {
        "target": target,
        "model": model,
        "state_dir": str(STATE_DIR),
        "home": str(STATE_HOME),
        "stdout": cp.stdout.strip(),
    }


def parse_ollama_list() -> list[dict[str, Any]]:
    cp = run(["ollama", "list"])
    lines = [line.rstrip() for line in cp.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    models: list[dict[str, Any]] = []
    for line in lines[1:]:
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 4:
            continue
        name, model_id, size, modified = parts[0], parts[1], parts[2], parts[3]
        models.append(
            {
                "name": name,
                "id": model_id,
                "size": size,
                "modified": modified,
                "local": size != "-",
                "coding": any(pattern.search(name) for pattern in CODING_MODEL_PATTERNS),
            }
        )
    return models


def llmfit_system() -> dict[str, Any] | None:
    if not command_version("llmfit").get("present"):
        return None
    cp = run(["llmfit", "system", "--json"])
    return json.loads(cp.stdout)


def llmfit_info_for_ollama_model(model: str) -> dict[str, Any] | None:
    query = LLMFIT_QUERY_MAP.get(model)
    if not query or not command_version("llmfit").get("present"):
        return None
    try:
        cp = run(["llmfit", "info", query, "--json"])
        payload = json.loads(cp.stdout)
        models = payload.get("models") or []
        return models[0] if models else None
    except Exception:
        return None


def smoke_test_ollama_model(model: str) -> dict[str, Any]:
    try:
        cp = run(["ollama", "run", model, "Reply with exactly READY"], timeout=180)
        text = cp.stdout.strip()
        ok = "READY" in text.upper()
        return {"ok": ok, "response": text}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout after 180s"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def smoke_test_codex(model: str) -> dict[str, Any]:
    env = state_env()
    try:
        cp = run(
            [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--oss",
                "--local-provider",
                "ollama",
                "-m",
                model,
                "Reply with exactly READY",
            ],
            env=env,
            timeout=240,
        )
        merged = (cp.stdout + "\n" + cp.stderr).strip()
        normalized = re.sub(r"[^a-z]", "", merged.lower())
        ok = "ready" in normalized
        auth_noise = "failed to refresh available models" in merged.lower() or "401 unauthorized" in merged.lower()
        return {"ok": ok, "output": cp.stdout.strip(), "stderr": cp.stderr.strip(), "auth_noise": auth_noise}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout after 240s"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def machine_profile() -> dict[str, Any]:
    llmfit = llmfit_system()
    profile: dict[str, Any] = {
        "host": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "tools": {
            "ollama": command_version("ollama"),
            "claude": command_version("claude"),
            "codex": command_version("codex"),
            "llmfit": command_version("llmfit"),
        },
        "ollama": {
            "models": parse_ollama_list(),
        },
        "state_dir": str(STATE_DIR),
    }
    if llmfit:
        profile["llmfit_system"] = llmfit.get("system", llmfit)
    return profile


def select_balanced_model(profile: dict[str, Any]) -> dict[str, Any]:
    models = [m for m in profile.get("ollama", {}).get("models", []) if m.get("local")]
    coding_models = [m for m in models if m.get("coding")]
    rationale: list[str] = []
    caveats: list[str] = []
    next_steps: list[str] = []
    status = "ready"
    smoke: dict[str, Any] | None = None
    llmfit_model: dict[str, Any] | None = None

    if coding_models:
        preferred_order = [DEFAULT_MODEL] + [m["name"] for m in coding_models if m["name"] != DEFAULT_MODEL]
        pick_name = next((name for name in preferred_order if any(m["name"] == name for m in coding_models)), coding_models[0]["name"])
        selected = next(m for m in coding_models if m["name"] == pick_name)
        smoke = smoke_test_ollama_model(selected["name"])
        llmfit_model = llmfit_info_for_ollama_model(selected["name"])
        rationale.append(f"{selected['name']} is already installed in Ollama, so the POC avoids extra downloads.")
        if smoke.get("ok"):
            rationale.append("A live `ollama run` smoke test succeeded on this machine, so the bridge should prefer a model that actually starts over a cleaner theoretical score.")
        else:
            caveats.append("Installed coding model exists, but the live Ollama smoke test failed.")
        if llmfit_model:
            rationale.append(
                f"llmfit classifies this as a {llmfit_model.get('category', 'coding')} model and estimates {llmfit_model.get('estimated_tps', 'unknown')} tok/s on this CPU-only host."
            )
            fit_level = llmfit_model.get("fit_level")
            if fit_level and fit_level.lower() != "good":
                caveats.append(f"llmfit marks the fit as `{fit_level}` on this low-memory host, so expect short prompts and weak quality ceilings.")
    else:
        status = "download-required"
        selected = {"name": DEFAULT_MODEL}
        rationale.append("No local coding model is installed in Ollama yet.")
        rationale.append(f"{DEFAULT_MODEL} is the smallest practical coder model for this CPU-only 2 GB-class box.")
        next_steps.append(f"ollama pull {DEFAULT_MODEL}")
        next_steps.append("./bin/codex-local")

    caveats.append("Quality mode is intentionally blocked in the POC on this hardware. Anything larger than the tiny coder model is more theory than reality here.")

    return {
        "runtime": "ollama",
        "mode": "balanced",
        "status": status,
        "selected_model": selected["name"],
        "modes": {
            "balanced": selected["name"],
            "fast": selected["name"],
            "quality": None,
        },
        "rationale": rationale,
        "caveats": list(dict.fromkeys(caveats)),
        "next_steps": next_steps,
        "smoke_test": smoke,
        "llmfit": llmfit_model,
        "state_dir": str(STATE_DIR),
    }


def doctor(run_codex_smoke: bool) -> dict[str, Any]:
    profile = machine_profile()
    recommendation = select_balanced_model(profile)
    issues: list[str] = []
    fixes: list[str] = []

    for tool_name, tool_info in profile["tools"].items():
        if not tool_info.get("present"):
            issues.append(f"Missing required tool: {tool_name}")

    if not profile["ollama"]["models"]:
        issues.append("Ollama is reachable but has no models listed.")
        fixes.append(f"Pull a tiny local coder first: ollama pull {DEFAULT_MODEL}")

    if recommendation["status"] == "download-required":
        issues.append("No installed local coding model was found.")
        fixes.extend(recommendation["next_steps"])

    config_written = {
        "codex": configure_ollama_integration("codex", recommendation["selected_model"]),
        "claude": configure_ollama_integration("claude", recommendation["selected_model"]),
    }

    codex_smoke = smoke_test_codex(recommendation["selected_model"]) if run_codex_smoke else None
    if codex_smoke and not codex_smoke.get("ok"):
        issues.append("Codex local smoke test failed.")
    elif codex_smoke and codex_smoke.get("auth_noise"):
        fixes.append("Codex still emits a harmless 401 model-refresh warning in local-only mode; the response itself is fine, so document rather than paper over it.")

    return {
        "profile": profile,
        "recommendation": recommendation,
        "issues": issues,
        "fixes": fixes,
        "config_written": config_written,
        "codex_smoke": codex_smoke,
    }


def print_payload(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="POC helper for claude-codex-local")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profile")
    sub.add_parser("recommend")

    ensure_cmd = sub.add_parser("ensure-config")
    ensure_cmd.add_argument("target", choices=["codex", "claude"])
    ensure_cmd.add_argument("--model", default=DEFAULT_MODEL)

    doctor_cmd = sub.add_parser("doctor")
    doctor_cmd.add_argument("--run-codex-smoke", action="store_true")

    args = parser.parse_args()

    if args.command == "profile":
        print_payload(machine_profile())
    elif args.command == "recommend":
        print_payload(select_balanced_model(machine_profile()))
    elif args.command == "ensure-config":
        print_payload(configure_ollama_integration(args.target, args.model))
    elif args.command == "doctor":
        print_payload(doctor(args.run_codex_smoke))


if __name__ == "__main__":
    main()
