# VOOL plugins

Plugins add tools and services to VOOL from the Add-ons page. A skill teaches VOOL a task in writing. A plugin
brings code or a service connection that VOOL can call.

> Plugins are planned for VOOL 0.8, not released yet. This repository holds the reference plugins and the
> rules 0.8 is built to. Details may still change before the release.

## What a plugin can be

| Kind | What it adds | Example in this repository |
| --- | --- | --- |
| `tools` | Tools VOOL can call in a chat, run from code bundled in the plugin. | [`template/`](template/) |
| `model_provider` | A model service that speaks the OpenAI chat format. VOOL makes the requests itself; the plugin is data only. | [`vool-plugin-usepod/`](vool-plugin-usepod/) |
| `scanner` | An extra security scan of public add-on content before it is installed. VOOL makes the requests itself. | [`vool-plugin-eyebrow/`](vool-plugin-eyebrow/) |

The service examples are written by VOOL. They are not endorsed by, or made with, the named services.

## How a person uses a plugin

1. In VOOL, open **Add-ons → My add-ons → Plugins** and choose **Install from a folder**.
2. VOOL shows every file in the package. **Install and keep disabled** installs it switched off.
3. If the plugin needs a service key, paste it into the plugin's card and choose **Save key**. Saving makes no
   request.
4. **Review access and enable** shows what the plugin may reach: tools, network hosts, keys and files.
   **Accept and enable** switches it on. **Keep disabled** leaves it off.
5. **Disable** stops it at once. **Uninstall** removes it and, by default, its saved keys.

Any change to a plugin's files after review switches it off until it is reviewed again. Updates also install
switched off.

## What a plugin can never do

- Spend money, sign, approve, or touch the wallet, spending limits, budgets or receipts.
- Use the owner's own model keys or another plugin's keys.
- Start or enable itself.
- Reach a network host it did not declare, or any private or local address.
- Run in remote or phone turns.

[Limits and why](docs/authoring.md#limits-and-why) explains each one.

## Write a plugin

- [docs/authoring.md](docs/authoring.md): build a plugin step by step, the manifest reference, keys, network,
  testing, and what each error means.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to submit a plugin to this repository.
- [AGENTS.md](AGENTS.md): short rules for AI coding agents working here.
- [`template/`](template/): a complete working plugin to copy.

## Repository layout

```
<plugin-folder>/
  .codex-plugin/plugin.json   the manifest VOOL reads: package fields plus the "vool" block
  .claude-plugin/plugin.json  minimal package metadata: name, version, description
  .mcp.json                   only when the plugin bundles an MCP server
  bin/                        bundled code, if any
  README.md  LICENSE  CHANGELOG.md
scripts/check.py              validates plugin folders with VOOL's own validator
scripts/try.py                runs one tool in a throwaway VOOL profile
docs/authoring.md             the authoring guide
```

## Check every plugin

```
python3 scripts/check.py --vool-source /path/to/vool
```

To run a tool once in a throwaway VOOL profile, use `scripts/try.py`; see
[the guide](docs/authoring.md#7-run-it-in-a-throwaway-vool).

The check uses the manifest validator and package capture from a VOOL source checkout, so this repository
keeps no second copy of those rules. It reads files only and runs no plugin code. The plugin system first
ships in VOOL 0.8 (planned, not released yet), so the checkout must include it.

## Licence

MIT. See [LICENSE](LICENSE). Each plugin folder carries its own LICENSE.
