"""CI check using VOOL’s installed parser, without executing plugin code."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vool-source", type=Path, required=True)
    options = parser.parse_args()
    sys.path.insert(0, str(options.vool_source.resolve()))
    from core.plugin_package import capture_package
    from core.plugin_tools import load_manifest
    root = Path(__file__).resolve().parents[1]
    results = []
    for folder in sorted(root.iterdir()):
        manifest = folder / ".codex-plugin/plugin.json"
        if not manifest.is_file():
            continue
        plugin = load_manifest(manifest)
        assert plugin.vool, "Current access declarations are required"
        identity = capture_package(folder)
        for name in ("README.md", "LICENSE", "CHANGELOG.md"):
            assert (folder / name).read_bytes().strip(), folder.name + ": missing " + name
        other = json.loads((folder / ".claude-plugin/plugin.json").read_text())
        assert other["name"] == plugin.plugin_id and other["version"] == plugin.version
        servers = plugin.vool.get("mcpServers", {})
        if servers:
            compatible = json.loads((folder / ".mcp.json").read_text())["mcpServers"]
            for server in servers.values():
                assert any(all(item.get(k, default) == server.get(k, default)
                               for k, default in (("command", ""), ("args", []), ("env", {})))
                           for item in compatible.values()), "MCP commands differ"
        results.append({"id": plugin.plugin_id, "version": plugin.version, "digest": identity.digest})
    assert len(results) == 3, "The three reference packages must all be present"
    print(json.dumps({"status": "validated", "packages": results}, indent=2))


if __name__ == "__main__":
    main()
