"""Install a plugin into a throwaway VOOL profile and call one of its tools, the way VOOL does.

Usage:
  python3 scripts/try.py --vool-source /path/to/vool <folder> <intent> '<arguments as JSON>' [--key SLOT=VALUE]

The plugin is installed switched off, enabled as if its access sheet were accepted, then called once with
VOOL's own confinement. Everything lives in a temporary folder that is deleted afterwards; your own VOOL
profile is never touched. Use test keys only with --key.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vool-source", type=Path, required=True, help="a VOOL source checkout with the plugin system")
    parser.add_argument("folder", type=Path)
    parser.add_argument("intent", help="the tool to call, such as vool-plugin-template.sha256")
    parser.add_argument("arguments", help="the tool arguments as a JSON object")
    parser.add_argument("--key", action="append", default=[], metavar="SLOT=VALUE", help="a test key for a credential slot")
    options = parser.parse_args()
    folder = options.folder.resolve()
    arguments = json.loads(options.arguments)
    source = options.vool_source.resolve()

    scratch = Path(tempfile.mkdtemp(prefix="vool-plugin-try-"))
    os.environ.update(VOOL_HOME=str(scratch / "profile"), VOOL_PLUGIN_LIFECYCLE_PATH=str(scratch / "lifecycle.json"),
                      VOOL_PLUGINS_DIR=str(scratch / "installed"), VOOL_PLUGIN_SCRATCH_ROOT=str(scratch / "scratch"),
                      VOOL_BUNDLED_PLUGINS_DIR=str(scratch / "no-bundled"), VOOL_CREDENTIAL_STORE="vault",
                      VOOL_KEY_STORAGE_MODE="file", VOOL_KEY_PASSPHRASE=os.urandom(16).hex())
    sys.path.insert(0, str(source))
    os.chdir(source)
    try:
        from core import plugin_manager as manager
        from core import plugin_tools, tool_registry

        review = manager.prepare_local(str(folder))
        info = manager.install(review["review_id"], accepted=True, digest=review["digest"])["plugin"]
        print(f"installed: enabled={info['enabled']} (installs always start switched off)")
        if not info.get("executable_runtime_available", True):
            print("this computer cannot run it: " + str(info.get("executable_runtime_refusal", "")))
        for pair in options.key:
            slot, _, value = pair.partition("=")
            manager.connect(info["id"], slot, value)
            print(f"saved test key for slot {slot!r}")
        manager.enable(info["id"], accepted=True, approval_digest=info["approval_digest"])
        print("enabled after accepting access")
        contract = tool_registry.tool_for_intent(options.intent)
        if not contract or not contract.supported:
            raise SystemExit(f"no usable tool {options.intent!r} in this plugin")
        result = plugin_tools.execute_plugin_contract(contract, arguments)
        print(json.dumps({"ok": result.ok, "status": result.status, "text": result.text, "error": result.error,
                          "confinement": result.confinement}, indent=2))
        raise SystemExit(0 if result.ok else 1)
    except ValueError as exc:
        raise SystemExit(f"refused: {exc}") from None
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
