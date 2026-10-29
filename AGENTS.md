# Notes for AI coding agents

This repository holds VOOL plugins. Each top-level folder with a `.codex-plugin/plugin.json` is one plugin.
Plugins are planned for VOOL 0.8, not released yet.

## Do

- Read [docs/authoring.md](docs/authoring.md) before writing a manifest. It covers every field and every
  error message.
- Copy [`template/`](template/), or the word-count walk-through in the guide, as your starting point.
- Keep `name` = `vool.id` = folder name, and `version` = `vool.version` = the version in
  `.claude-plugin/plugin.json`.
- Prefix every tool `intent` with `<plugin id>.`.
- In plain programs, read input from standard input and print exactly one JSON object to standard output. Read
  keys from `context.credentials`, not from the environment.
- Declare the smallest effect class, permission actions, hosts and keys that work.
- Run `python3 scripts/check.py --vool-source <VOOL checkout> <folder>` and fix every message before you
  finish.
- Run your program by hand with a sample input, then run
  `python3 scripts/try.py --vool-source <VOOL checkout> <folder> <intent> '<JSON arguments>'` and show both
  outputs. `try.py` uses a throwaway VOOL profile, so it is safe to run.
- Replace the copyright line in LICENSE with the real author.

## Never

- Write a key, token or password into any file, fixture or log. Use clearly fake test values.
- Add money, wallet, signing, approval, cap, budget or receipt permissions, or tool names containing those
  words. VOOL refuses them.
- Use `npx`, `uvx`, `pip install` or any other download at run time.
- Declare wildcard hosts, IP addresses, or local or private names.
- Claim in a README that something works when you have not run it.
- Change `scripts/check.py` to make a failing plugin pass.
