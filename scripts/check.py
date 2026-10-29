"""Validate plugin folders with VOOL's own manifest validator, without running plugin code.

Usage: python3 scripts/check.py --vool-source /path/to/vool [folder ...]
With no folders, every plugin folder in this repository is checked. Folders may be anywhere.
Each problem is printed as one line: "<folder>: <message>". The exit status is 1 if any folder fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REFERENCE = {"vool-plugin-template", "vool-plugin-usepod", "vool-plugin-eyebrow"}


class Problem(Exception):
    pass


def check(folder: Path) -> dict:
    from core.blackbox.coverage.capability import LOCAL_MUTATION_CLASSES, MutationCapability
    from core.plugin_package import capture_package
    from core.plugin_tools import load_manifest

    manifest = folder / ".codex-plugin/plugin.json"
    if not manifest.is_file():
        raise Problem("no .codex-plugin/plugin.json")
    try:
        raw = json.loads(manifest.read_text())
    except ValueError as exc:
        raise Problem(f".codex-plugin/plugin.json is not valid JSON: {exc}") from None
    try:
        plugin = load_manifest(manifest)
    except ValueError as exc:
        raise Problem(str(exc)) from None
    if not plugin.vool:
        raise Problem('the manifest needs a "vool" block with id, version and access declarations')
    try:
        identity = capture_package(folder)
    except (ValueError, OSError) as exc:
        raise Problem(str(exc)) from None
    for name in ("README.md", "LICENSE", "CHANGELOG.md"):
        path = folder / name
        if not path.is_file() or not path.read_bytes().strip():
            raise Problem(f"{name} is missing or empty")
    meta_path = folder / ".claude-plugin/plugin.json"
    if not meta_path.is_file():
        raise Problem(".claude-plugin/plugin.json is missing")
    meta = json.loads(meta_path.read_text())
    if meta.get("name") != plugin.plugin_id or meta.get("version") != plugin.version:
        raise Problem(".claude-plugin/plugin.json name and version must match the manifest "
                      f"({plugin.plugin_id} {plugin.version})")
    servers = plugin.vool.get("mcpServers", {})
    for tool in plugin.vool.get("tools", []):
        handler = tool["handler"]
        entry = handler.get("entry") if handler["kind"] == "subprocess" else servers.get(handler.get("server"), {}).get("command")
        if entry and not os.access(folder / entry, os.X_OK):
            raise Problem(f"{entry} is not executable; run chmod +x {entry}")
        effect = (tool.get("trust") or {}).get("side_effect_class") or tool.get("side_effect_class")
        if effect in LOCAL_MUTATION_CLASSES:
            declared = tool.get("mutation")
            capability = MutationCapability.from_dict(declared) if isinstance(declared, dict) else None
            if capability is None or capability.tool != tool["intent"]:
                raise Problem(f"{tool['intent']}: a {effect} tool needs a mutation block naming this tool; "
                              "see docs/authoring.md")
            if capability.problems():
                raise Problem(f"{tool['intent']}: mutation block: " + "; ".join(capability.problems()))
    if servers:
        mcp_path = folder / ".mcp.json"
        if not mcp_path.is_file():
            raise Problem(".mcp.json is missing; it must repeat each bundled MCP server")
        compatible = json.loads(mcp_path.read_text()).get("mcpServers", {})
        for server in servers.values():
            if not any(all(item.get(k, default) == server.get(k, default)
                           for k, default in (("command", ""), ("args", []), ("env", {})))
                       for item in compatible.values()):
                raise Problem(".mcp.json command, args and env must match mcpServers in the manifest")
    if raw.get("name") != folder.name and folder.name != "template":
        print(f"{folder}: note: the folder name differs from the plugin id {raw.get('name')!r}", file=sys.stderr)
    return {"id": plugin.plugin_id, "version": plugin.version, "digest": identity.digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vool-source", type=Path, required=True, help="a VOOL source checkout with the plugin system")
    parser.add_argument("folders", nargs="*", type=Path, help="plugin folders to check (default: all in this repository)")
    options = parser.parse_args()
    sys.path.insert(0, str(options.vool_source.resolve()))
    try:
        import core.plugin_tools  # noqa: F401
    except ImportError as exc:
        raise SystemExit(f"Cannot load VOOL from {options.vool_source}: {exc}. Point --vool-source at a VOOL "
                         "source checkout that includes the plugin system, and use VOOL's Python environment.")
    root = Path(__file__).resolve().parents[1]
    folders = [folder.resolve() for folder in options.folders] or sorted(
        folder for folder in root.iterdir() if (folder / ".codex-plugin/plugin.json").is_file())
    results, failed = [], False
    for folder in folders:
        try:
            results.append(check(folder))
        except Problem as exc:
            print(f"{folder}: {exc}", file=sys.stderr)
            failed = True
    if not options.folders:
        missing = REFERENCE - {row["id"] for row in results}
        if missing and not failed:
            print("Reference packages missing: " + ", ".join(sorted(missing)), file=sys.stderr)
            failed = True
    print(json.dumps({"status": "failed" if failed else "validated", "packages": results}, indent=2))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
