# Contributing

Thank you for building for VOOL. Plugins are planned for VOOL 0.8, not released yet. Submissions are welcome
now, so they can be reviewed against the 0.8 rules.

## Add a plugin

1. Read [docs/authoring.md](docs/authoring.md). Start from a copy of [`template/`](template/), or from the
   word-count walk-through in the guide.
2. Put your plugin in its own top-level folder, named the same as its id, for example
   `vool-plugin-yourservice/`.
3. Include every file it needs:
   - `.codex-plugin/plugin.json`;
   - `.claude-plugin/plugin.json`;
   - `.mcp.json` if you bundle an MCP server;
   - your code, its dependencies and lock files;
   - `README.md`, `LICENSE` (MIT) and `CHANGELOG.md`.
4. Run `python3 scripts/check.py --vool-source /path/to/vool <your-folder>` and fix every message.
5. Run each tool once with `scripts/try.py`, then work through the [test list](docs/authoring.md#test-before-you-submit) in a test VOOL profile.
6. Open a pull request using the template. Say what the plugin reaches and how you tested it.

## What reviewers check

- The manifest asks for no more than the plugin uses: hosts, keys, effect class and permissions.
- No key, token or personal data is in any file, fixture, log or screenshot.
- Nothing is downloaded at run time. All code is in the folder and readable.
- The README says plainly what the plugin does, what it reaches and what it needs installed. It claims nothing
  that was not tested.
- Failure paths return a clear `error`: missing key, wrong key, timeout, service error and no network.
- Your plugin's own service is the only one named in its README. Do not name or compare other services.

## What is never accepted

- Anything that moves money, signs, approves, or reads or changes the wallet, spending limits, budgets or
  receipts.
- Requests for the owner's model keys or another plugin's keys.
- Auto-start, auto-enable, or code that changes itself after install.
- Hidden network use, wildcard hosts, or private or local addresses.
- Obfuscated or minified code without its source.

## Changing a plugin

Raise the version in all four places: both `version` fields in `.codex-plugin/plugin.json`, and the `version`
in `.claude-plugin/plugin.json` and in `CHANGELOG.md`. People who update get the plugin switched off until
they review its access again. Publish updates from the same repository and under the same `publisher`:
an update from anywhere else does not keep people's saved keys.

## Reference plugins

`template/`, `vool-plugin-usepod/` and `vool-plugin-eyebrow/` are maintained by the VOOL team. Changes to them
follow the same steps.
