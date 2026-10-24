# Contributing

Keep each plugin in its own folder, with complete bundled source and dependencies. Start from `template/`.
Follow VOOL’s plugin-authoring guide and JSON Schema. Declare exact public HTTPS hosts and only your own
service credential slots. Never include keys, runtime downloads or money/signing/approval permissions.

Run `python scripts/check.py --vool-source <VOOL checkout>`. Then exercise a disposable profile: install
disabled, decline, accept access, connect a key, invoke, disable during a call, update and uninstall.
Use real local TLS service processes for provider/scanner tests. Validate failure paths and secret redaction.
For MCP, capture initialization, tools/list and a real tool call over stdio using `.mcp.json` exactly.

Store submission uses the existing VOOL registry’s complete review and signing chain. A local check is not
store review. Keep READMEs precise about capabilities and untested application installs. Include MIT LICENSE
and CHANGELOG in every distribution. No remote publication or repository creation is performed by this layout.
