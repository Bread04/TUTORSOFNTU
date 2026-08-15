#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
First Breath — Deterministic sanctum scaffolding.

This script runs BEFORE the conversational awakening. It creates the sanctum
folder structure, copies template files with config values substituted,
copies all capability files and their supporting references into the sanctum,
and auto-generates CAPABILITIES.md from capability prompt frontmatter.

After this script runs, the sanctum is fully self-contained — the agent does
not depend on the skill bundle location for normal operation.

This initializes the agent's runtime sanctum memory, not build-time config. It
reads the project's BMad config strictly to substitute values into the sanctum
templates, and it never writes or authors any config file. Build-time
customization is owned by customize.toml, a separate surface this script never
touches.

Usage:
    uv run --managed-python init-sanctum.py <project-root> <skill-path>
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# --- Agent-specific configuration (set by builder) ---

SKILL_NAME = "agent-abigail"
SANCTUM_DIR = SKILL_NAME

# Files that stay in the skill bundle (only used during First Breath)
SKILL_ONLY_FILES = {"first-breath.md"}

TEMPLATE_FILES = [
    "INDEX-template.md",
    "PERSONA-template.md",
    "CREED-template.md",
    "BOND-template.md",
    "MEMORY-template.md",
    "LEDGER-template.md",
    "PULSE-template.md",
]

# Whether the owner can teach this agent new capabilities
EVOLVABLE = True

# --- End agent-specific configuration ---

# Config files searched for template values, lowest precedence first. BMad has
# used both .yaml and .toml across versions and splits values between the root
# and per-module files, so every known location is read and merged rather than
# one filename being trusted. Missing files are skipped.
CONFIG_CANDIDATES = [
    "config.yaml",
    "bmb/config.yaml",
    "config.toml",
    "config.user.yaml",
    "config.user.toml",
    "custom/config.toml",
    "custom/config.user.toml",
]

# The only keys substituted into templates. Everything else in the config is
# irrelevant here.
WANTED_KEYS = {"user_name", "communication_language"}

def strip_inline_comment(value: str) -> str:
    """Drop a trailing # comment, unless the # sits inside a quoted value."""
    if value[:1] in "\"'":
        end = value.find(value[0], 1)
        if end != -1:
            return value[: end + 1]
    head, sep, _ = value.partition("#")
    return head if sep else value

def parse_config_file(path: Path) -> dict:
    """Read the wanted scalars from one BMad config file.

    Separator comes from the suffix: TOML is `key = "value"`, YAML is
    `key: value`. Keys under a section other than [core] are skipped so a
    per-agent or per-module block cannot shadow a root value.
    """
    found = {}
    if not path.is_file():
        return found

    sep = "=" if path.suffix == ".toml" else ":"
    section = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if section not in (None, "core"):
            continue

        key, found_sep, value = line.partition(sep)
        if not found_sep or key.strip() not in WANTED_KEYS:
            continue
        value = strip_inline_comment(value.strip()).strip().strip("'\"")
        if value:
            found[key.strip()] = value

    return found

def load_config(bmad_dir: Path) -> tuple[dict, list[str]]:
    """Merge every config file that exists, later candidates winning."""
    config = {}
    read = []
    for name in CONFIG_CANDIDATES:
        values = parse_config_file(bmad_dir / name)
        if values:
            config.update(values)
            read.append(name)
    return config, read

def parse_frontmatter(file_path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    meta = {}
    content = file_path.read_text(encoding="utf-8")

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta

    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta

def copy_references(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copy all reference files (except skill-only files) into the sanctum."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for source_file in sorted(source_dir.iterdir()):
        if source_file.name in SKILL_ONLY_FILES:
            continue
        if source_file.is_file():
            shutil.copy2(source_file, dest_dir / source_file.name)
            copied.append(source_file.name)

    return copied

def copy_scripts(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copy any scripts the capabilities might use into the sanctum."""
    if not source_dir.exists():
        return []
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for source_file in sorted(source_dir.iterdir()):
        if source_file.is_file() and source_file.name != "init-sanctum.py":
            shutil.copy2(source_file, dest_dir / source_file.name)
            copied.append(source_file.name)

    return copied

def discover_capabilities(references_dir: Path, sanctum_refs_path: str) -> list[dict]:
    """Scan references/ for capability prompt files with frontmatter."""
    capabilities = []

    for md_file in sorted(references_dir.glob("*.md")):
        if md_file.name in SKILL_ONLY_FILES:
            continue
        meta = parse_frontmatter(md_file)
        if meta.get("name") and meta.get("code"):
            capabilities.append({
                "name": meta["name"],
                "description": meta.get("description", ""),
                "code": meta["code"],
                "source": f"{sanctum_refs_path}/{md_file.name}",
            })
    return capabilities

def generate_capabilities_md(capabilities: list[dict], evolvable: bool) -> str:
    """Generate CAPABILITIES.md content from discovered capabilities."""
    lines = [
        "# Capabilities",
        "",
        "## Built-in",
        "",
        "| Code | Name | Description | Source |",
        "|------|------|-------------|--------|",
    ]
    for cap in capabilities:
        lines.append(
            f"| [{cap['code']}] | {cap['name']} | {cap['description']} | `{cap['source']}` |"
        )

    if evolvable:
        lines.extend([
            "",
            "## Learned",
            "",
            "_Capabilities added by the owner over time. Prompts live in `capabilities/`._",
            "",
            "| Code | Name | Description | Source | Added |",
            "|------|------|-------------|--------|-------|",
            "",
            "## How to Add a Capability",
            "",
            'Tell me "I want you to be able to do X" and we\'ll create it together.',
            "I'll write the prompt, save it to `capabilities/`, and register it here.",
            "Next session, I'll know how.",
            "Load `references/capability-authoring.md` for the full creation framework.",
        ])

    lines.extend([
        "",
        "## Tools",
        "",
        "Prefer crafting your own tools over depending on external ones. A script you wrote "
        "and saved is more reliable than an external API. Use the file system creatively.",
        "",
        "### User-Provided Tools",
        "",
        "_MCP servers, APIs, or services the owner has made available. Document them here._",
    ])

    return "\n".join(lines) + "\n"

def substitute_vars(content: str, variables: dict) -> str:
    """Replace {var_name} placeholders with values from the variables dict."""
    for key, value in variables.items():
        content = content.replace(f"{{{key}}}", value)
    return content

def log(message: str = "") -> None:
    """Progress goes to stderr so stdout stays a clean JSON summary."""
    print(message, file=sys.stderr)

def emit(payload: dict, output: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold the agent's sanctum for First Breath. Idempotent: "
                    "exits without touching anything if a sanctum already exists.",
    )
    parser.add_argument("project_root", help="Project root (where _bmad/ lives)")
    parser.add_argument("skill_path", help="Skill directory (where SKILL.md, references/, assets/ live)")
    parser.add_argument("-o", "--output", help="Write the JSON summary here instead of stdout")
    parser.add_argument("--verbose", action="store_true", help="List every file written")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    skill_path = Path(args.skill_path).resolve()

    # Paths
    bmad_dir = project_root / "_bmad"
    memory_dir = bmad_dir / "memory"
    sanctum_path = memory_dir / SANCTUM_DIR
    assets_dir = skill_path / "assets"
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"

    # Sanctum subdirectories
    sanctum_refs = sanctum_path / "references"
    sanctum_scripts = sanctum_path / "scripts"

    # Relative path for CAPABILITIES.md references (agent loads from within sanctum)
    sanctum_refs_path = "references"

    # Check if sanctum already exists
    if sanctum_path.exists():
        log(f"Sanctum already exists at {sanctum_path}")
        log("This agent has already been born. Skipping First Breath scaffolding.")
        emit({"status": "already_born", "sanctum": str(sanctum_path)}, args.output)
        return 0

    # Load config
    config, config_files_read = load_config(bmad_dir)
    if "user_name" not in config:
        log(f"  Warning: no user_name found in any of {CONFIG_CANDIDATES} under {bmad_dir}.")
        log("  BOND.md and PERSONA.md will say \"friend\". Fix the config and delete the")
        log("  sanctum to redo First Breath, or correct those files by hand afterwards.")

    # Build variable substitution map
    today = date.today().isoformat()
    variables = {
        "user_name": config.get("user_name", "friend"),
        "communication_language": config.get("communication_language", "English"),
        "birth_date": today,
        "project_root": str(project_root),
        "sanctum_path": str(sanctum_path),
    }

    # Create sanctum structure
    sanctum_path.mkdir(parents=True, exist_ok=True)
    (sanctum_path / "capabilities").mkdir(exist_ok=True)
    (sanctum_path / "sessions").mkdir(exist_ok=True)
    (sanctum_path / "review").mkdir(exist_ok=True)
    log(f"Created sanctum at {sanctum_path}")

    # Copy reference files (capabilities + techniques + guidance) into sanctum
    copied_refs = copy_references(references_dir, sanctum_refs)
    log(f"  Copied {len(copied_refs)} reference files to sanctum/references/")
    if args.verbose:
        for name in copied_refs:
            log(f"    - {name}")

    # Copy any supporting scripts into sanctum
    copied_scripts = copy_scripts(scripts_dir, sanctum_scripts)
    if copied_scripts:
        log(f"  Copied {len(copied_scripts)} scripts to sanctum/scripts/")
        if args.verbose:
            for name in copied_scripts:
                log(f"    - {name}")

    # Copy and substitute template files
    missing_templates = []
    written = []
    for template_name in TEMPLATE_FILES:
        template_path = assets_dir / template_name
        if not template_path.exists():
            log(f"  Warning: template {template_name} not found, skipping")
            missing_templates.append(template_name)
            continue

        # Remove "-template" from the output filename and uppercase it
        output_name = template_name.replace("-template", "").upper()
        # Fix extension casing: .MD -> .md
        output_name = output_name[:-3] + ".md"

        content = template_path.read_text(encoding="utf-8")
        content = substitute_vars(content, variables)

        output_path = sanctum_path / output_name
        output_path.write_text(content, encoding="utf-8")
        written.append(output_name)
        log(f"  Created {output_name}")

    # Auto-generate CAPABILITIES.md from references/ frontmatter
    capabilities = discover_capabilities(references_dir, sanctum_refs_path)
    capabilities_content = generate_capabilities_md(capabilities, evolvable=EVOLVABLE)
    (sanctum_path / "CAPABILITIES.md").write_text(capabilities_content, encoding="utf-8")
    written.append("CAPABILITIES.md")
    log(f"  Created CAPABILITIES.md ({len(capabilities)} built-in capabilities discovered)")

    log()
    log("First Breath scaffolding complete.")
    log("The conversational awakening can now begin.")
    log(f"Sanctum: {sanctum_path}")

    emit({
        "status": "created",
        "sanctum": str(sanctum_path),
        "user_name": variables["user_name"],
        "config_files_read": config_files_read,
        "files_written": written,
        "references_copied": len(copied_refs),
        "scripts_copied": len(copied_scripts),
        "capabilities_discovered": [c["code"] for c in capabilities],
        "missing_templates": missing_templates,
    }, args.output)

    return 1 if missing_templates else 0

if __name__ == "__main__":
    raise SystemExit(main())
