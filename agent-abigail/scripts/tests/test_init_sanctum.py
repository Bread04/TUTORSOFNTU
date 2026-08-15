#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for init-sanctum.py. Run: uv run scripts/tests/test_init_sanctum.py

The substitution tests are the point of this file: a placeholder that survives
into the sanctum is permanent, because init refuses to run twice.
"""

import importlib.util
import re
import shutil
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = SKILL_ROOT / "scripts" / "init-sanctum.py"
spec = importlib.util.spec_from_file_location("init_sanctum", MODULE_PATH)
init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init)

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


TOML_ROOT = """# installer-managed
[core]
user_name = "Bread"
communication_language = "English"
output_folder = "{project-root}/_bmad-output"

[modules.bmb]
bmad_builder_output_folder = "{project-root}/skills"

[agents.someone-else]
name = "Mary"
user_name = "WrongPerson"
"""

YAML_MODULE = """# module config
user_name: Yaml Person
communication_language: English
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


print("parse_config_file — the format that broke it")
with tempfile.TemporaryDirectory() as tmp:
    bmad = Path(tmp) / "_bmad"
    write(bmad / "config.user.toml", TOML_ROOT)

    values = init.parse_config_file(bmad / "config.user.toml")
    check("reads user_name from TOML [core]", values.get("user_name") == "Bread",
          f"got {values.get('user_name')!r}")
    check("reads communication_language from TOML",
          values.get("communication_language") == "English")
    check("ignores keys under a non-core section",
          values.get("user_name") != "WrongPerson")
    check("keeps only the wanted keys",
          set(values) <= {"user_name", "communication_language"}, f"got {set(values)}")

print("parse_config_file — YAML form still works")
with tempfile.TemporaryDirectory() as tmp:
    bmad = Path(tmp) / "_bmad"
    write(bmad / "bmb" / "config.yaml", YAML_MODULE)
    values = init.parse_config_file(bmad / "bmb" / "config.yaml")
    check("reads user_name from YAML", values.get("user_name") == "Yaml Person")

print("parse_config_file — absent file is not an error")
with tempfile.TemporaryDirectory() as tmp:
    check("missing file yields {}", init.parse_config_file(Path(tmp) / "nope.toml") == {})

print("load_config — precedence and reporting")
with tempfile.TemporaryDirectory() as tmp:
    bmad = Path(tmp) / "_bmad"
    write(bmad / "bmb" / "config.yaml", YAML_MODULE)
    write(bmad / "config.user.toml", TOML_ROOT)

    config, read = init.load_config(bmad)
    check("later candidate wins", config.get("user_name") == "Bread",
          f"got {config.get('user_name')!r}")
    check("reports which files it read",
          read == ["bmb/config.yaml", "config.user.toml"], f"got {read}")

print("load_config — nothing to read")
with tempfile.TemporaryDirectory() as tmp:
    config, read = init.load_config(Path(tmp) / "_bmad")
    check("no config yields no values", config == {} and read == [])

print("strip_inline_comment")
check("strips a trailing comment", init.strip_inline_comment('"autonomous"   # a | b') == '"autonomous"')
check("keeps a # inside quotes", init.strip_inline_comment('"C#"') == '"C#"')
check("leaves a bare value alone", init.strip_inline_comment("Bread") == "Bread")

print("end to end — the sanctum a real First Breath would get")
with tempfile.TemporaryDirectory() as tmp:
    project_root = Path(tmp)
    write(project_root / "_bmad" / "config.user.toml", TOML_ROOT)

    sys.argv = ["init-sanctum.py", str(project_root), str(SKILL_ROOT),
                "-o", str(project_root / "summary.json")]
    code = init.main()
    sanctum = project_root / "_bmad" / "memory" / init.SANCTUM_DIR

    check("exits 0", code == 0, f"got {code}")
    check("sanctum created", sanctum.is_dir())

    for name in ["INDEX.md", "PERSONA.md", "CREED.md", "BOND.md",
                 "MEMORY.md", "LEDGER.md", "PULSE.md", "CAPABILITIES.md"]:
        check(f"wrote {name}", (sanctum / name).is_file())

    bond = (sanctum / "BOND.md").read_text(encoding="utf-8")
    check("BOND names the owner, not \"friend\"", "Bread" in bond and "friend" not in bond,
          bond.splitlines()[3] if len(bond.splitlines()) > 3 else "")

    persona = (sanctum / "PERSONA.md").read_text(encoding="utf-8")
    check("PERSONA evolution log names the owner", "Bread" in persona)
    check("PERSONA ships her build-time name", "Abigail" in persona)

    pulse = (sanctum / "PULSE.md").read_text(encoding="utf-8")
    check("PULSE quiet hours name the owner", "Bread" in pulse)

    caps = (sanctum / "CAPABILITIES.md").read_text(encoding="utf-8")
    for code_ in ["EX", "WK", "RV"]:
        check(f"CAPABILITIES lists [{code_}]", f"[{code_}]" in caps)

    # The regression guard: no template variable may survive into a living file.
    known = re.compile(r"\{(user_name|communication_language|birth_date|project_root|sanctum_path)\}")
    leaked = [p.name for p in sorted(sanctum.glob("*.md"))
              if known.search(p.read_text(encoding="utf-8"))]
    check("no substitution variable survives", not leaked, f"leaked in {leaked}")

    check("first-breath.md stays in the skill bundle",
          not (sanctum / "references" / "first-breath.md").exists())
    check("capability prompts reached the sanctum",
          (sanctum / "references" / "explain.md").is_file())

print("end to end — idempotence")
with tempfile.TemporaryDirectory() as tmp:
    project_root = Path(tmp)
    write(project_root / "_bmad" / "config.user.toml", TOML_ROOT)
    sys.argv = ["init-sanctum.py", str(project_root), str(SKILL_ROOT),
                "-o", str(project_root / "summary.json")]
    init.main()

    sanctum = project_root / "_bmad" / "memory" / init.SANCTUM_DIR
    (sanctum / "BOND.md").write_text("hand-edited by the agent", encoding="utf-8")

    code = init.main()
    check("second run exits 0", code == 0, f"got {code}")
    check("second run does not overwrite a living sanctum",
          (sanctum / "BOND.md").read_text(encoding="utf-8") == "hand-edited by the agent")

print("end to end — no config anywhere")
with tempfile.TemporaryDirectory() as tmp:
    project_root = Path(tmp)
    (project_root / "_bmad").mkdir()
    sys.argv = ["init-sanctum.py", str(project_root), str(SKILL_ROOT),
                "-o", str(project_root / "summary.json")]
    init.main()
    sanctum = project_root / "_bmad" / "memory" / init.SANCTUM_DIR
    bond = (sanctum / "BOND.md").read_text(encoding="utf-8")
    check("falls back to \"friend\" rather than leaving {user_name}",
          "friend" in bond and "{user_name}" not in bond)

print()
if FAILURES:
    print(f"{len(FAILURES)} test(s) failed: {', '.join(FAILURES)}")
    raise SystemExit(1)
print("All tests passed.")
