# VOOL plugins

Reference integrations maintained with VOOL. These examples are not endorsements by the named services.
Installation keeps a plugin disabled until its access sheet is accepted. Keys stay in the owner’s vault.

| Folder | Purpose |
| --- | --- |
| `vool-plugin-usepod/` | Declarative OpenAI-compatible provider with path authentication and reported prices. |
| `vool-plugin-eyebrow/` | Optional declarative scanner for requested public add-on checks. |
| `template/` | Bundled local MCP server computing a text digest. |

Each folder carries the native manifest, minimal compatibility metadata, README, MIT LICENSE and CHANGELOG.
The template also carries `.mcp.json`. Metadata alone does not add native providers or scanners to other hosts.
No service is featured or pinned. An x402 declaration never grants money authority.

Run `python scripts/check.py --vool-source <VOOL checkout>` with VOOL’s environment. It imports the actual
manifest validator and complete package capture; this repository keeps no second parser. See CONTRIBUTING.md.

This repository is a local layout prepared for publication by its owner. It has no configured remote.
