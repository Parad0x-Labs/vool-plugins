# Writing a VOOL plugin

> Plugins are planned for VOOL 0.8, not released yet. This guide describes the plugin system that 0.8 is built
> to. Details may still change before the release.

This guide takes you from an empty folder to a plugin that VOOL installs, reviews and runs. It is written for
people and for AI coding agents. Every rule here is checked by VOOL itself. When this guide and VOOL disagree,
VOOL wins; please open an issue.

- [Before you start](#before-you-start)
- [Build your first plugin](#build-your-first-plugin)
- [How VOOL runs a tool](#how-vool-runs-a-tool)
- [Bundling an MCP server](#bundling-an-mcp-server)
- [Model providers and scanners](#model-providers-and-scanners)
- [Manifest reference](#manifest-reference)
- [Keys](#keys)
- [Network](#network)
- [Files and processes](#files-and-processes)
- [Limits and why](#limits-and-why)
- [Test before you submit](#test-before-you-submit)
- [Errors and fixes](#errors-and-fixes)

## Before you start

You need:

- Python 3 for the check script and the examples.
- A VOOL source checkout that includes the plugin system, for `scripts/check.py` and for installing your plugin
  in a real VOOL. The plugin system first ships in VOOL 0.8 (planned, not released yet).
- Any language for your own tool code, as long as it runs as a program bundled in your folder.

Pick the kind you need:

| You want to | Kind | Your plugin contains |
| --- | --- | --- |
| Give VOOL a new action, such as converting a file or querying a public API | `tools` | A manifest and a program |
| Connect a model service that speaks the OpenAI chat format | `model_provider` | A manifest only |
| Add a remote security scan for add-ons before they are installed | `scanner` | A manifest only |

## Build your first plugin

This walk-through builds `vool-plugin-word-count`, a tool that counts words in text. It needs no key and no
network. For a version that uses MCP instead of a plain program, see [`template/`](../template/).

### 1. Make the folder

```
vool-plugin-word-count/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  bin/count
  README.md
  LICENSE
  CHANGELOG.md
```

The folder name, the package `name` and `vool.id` should all be the same. The id uses lower-case letters,
digits, `-` and `_`, starts with a letter, and is at most 80 characters.

### 2. Write the manifest

`.codex-plugin/plugin.json`:

```json
{
  "name": "vool-plugin-word-count",
  "version": "1.0.0",
  "description": "Count the words and characters in supplied text.",
  "vool": {
    "id": "vool-plugin-word-count",
    "version": "1.0.0",
    "name": "Word count",
    "publisher": "Your name",
    "description": "Count the words and characters in supplied text.",
    "homepage": "https://github.com/your-account/vool-plugin-word-count",
    "license": "MIT",
    "kind": ["tools"],
    "network": [],
    "credentials": {},
    "tools": [
      {
        "intent": "vool-plugin-word-count.count",
        "description": "Count the words and characters in the supplied text and return both numbers.",
        "input_schema": {
          "type": "object",
          "required": ["text"],
          "additionalProperties": false,
          "properties": {"text": {"type": "string", "maxLength": 20000}}
        },
        "handler": {"kind": "subprocess", "entry": "bin/count", "timeout_seconds": 10},
        "side_effect_class": "read_only",
        "permission_actions": [],
        "approval_requirement": "none"
      }
    ]
  }
}
```

Points that matter:

- `name` and `vool.id` must be equal. `version` and `vool.version` must be equal.
- Each tool `intent` starts with your plugin id and a dot.
- The model reads `description` to decide when to call the tool. Write a real sentence of at least 12
  characters.
- `homepage` must be a public `https://` address.
- `network` and `credentials` are required even when they are empty.

`.claude-plugin/plugin.json` holds the same three package fields and nothing else:

```json
{"name": "vool-plugin-word-count", "version": "1.0.0", "description": "Count the words and characters in supplied text."}
```

### 3. Write the program

`bin/count` (make it executable with `chmod +x bin/count`):

```python
#!/usr/bin/env python3
import json
import sys

request = json.load(sys.stdin)
text = request["arguments"]["text"]
result = {"words": len(text.split()), "characters": len(text)}
print(json.dumps({"text": json.dumps(result)}))
```

VOOL sends one JSON object on standard input and reads one JSON object from standard output.
[How VOOL runs a tool](#how-vool-runs-a-tool) describes both.

### 4. Try the program on its own

Run it from your plugin folder with the same input VOOL would send:

```
echo '{"intent":"vool-plugin-word-count.count","arguments":{"text":"one two three"},"context":{"scratch_dir":null,"secrets":[],"credentials":{}}}' | bin/count
```

Expected output:

```
{"text": "{\"words\": 3, \"characters\": 13}"}
```

### 5. Add README, LICENSE and CHANGELOG

- `README.md`: what the plugin does, what it reaches (files, hosts, keys), and what it needs installed, such as
  Python 3.
- `LICENSE`: the full MIT licence text, with your name on the copyright line. MIT is required for plugins in
  this repository.
- `CHANGELOG.md`: one section per version, newest first.

### 6. Check it

From this repository:

```
python3 scripts/check.py --vool-source /path/to/vool /path/to/vool-plugin-word-count
```

The folder can be anywhere. The check runs VOOL's own validator and prints the package digest. It never runs your
code. Each problem is printed as one line, `<folder>: <message>`, and the exit status is 1. Look the message up in
[Errors and fixes](#errors-and-fixes).

### 7. Run it in a throwaway VOOL

```
python3 scripts/try.py --vool-source /path/to/vool /path/to/vool-plugin-word-count \
  vool-plugin-word-count.count '{"text": "one two three"}'
```

This installs the plugin into a temporary VOOL profile, enables it as if you accepted its access sheet, and calls
the tool once with VOOL's real confinement. Then it deletes the profile. Your own VOOL is never touched. Add
`--key SLOT=VALUE` to supply a test key. Run it with VOOL's Python environment if plain `python3` cannot load
VOOL. Expected result:

```
installed: enabled=False (installs always start switched off)
enabled after accepting access
{
  "ok": true,
  "status": "executed",
  "text": "{\"words\": 3, \"characters\": 13}",
  "error": "",
  "confinement": "kernel:bwrap"
}
```

`confinement` names the sandbox: `kernel:bwrap` on Linux, `kernel:sandbox-exec` on macOS.

### 8. Install it in VOOL

1. Open **Add-ons → My add-ons → Plugins**.
2. Under **Install from a folder**, enter the folder path and choose **Review folder**.
3. Read the file list, then choose **Install and keep disabled**.
4. Choose **Review access and enable**, read the access sheet, then **Accept and enable**.
5. In a chat, ask: "Use the vool-plugin-word-count.count tool on: the quick brown fox".

If you change any file after installing, VOOL switches the plugin off. Review and enable it again.

## How VOOL runs a tool

Each call starts your program fresh. Its working directory is a read-only copy of your plugin folder, so open
your own files with paths relative to it. VOOL writes one JSON object to its standard input:

```json
{
  "intent": "vool-plugin-word-count.count",
  "arguments": {"text": "..."},
  "context": {
    "scratch_dir": "/path/VOOL/gives/you",
    "secrets": ["SAMPLE_ACCESS"],
    "credentials": {"SAMPLE_ACCESS": "the key value"}
  }
}
```

- `arguments` has already been checked against your `input_schema`. Defaults in the schema are filled in.
- `context.credentials` holds only the keys named in this tool's `handler.env_allowlist`. See [Keys](#keys).
- `context.scratch_dir` is the only place you may write. For `read_only` tools it is still a path, but nothing
  can be written there and it may not exist. Do not test it to decide whether you may write; your effect class
  decides that.

Your program prints one JSON object to standard output:

| Field | Meaning |
| --- | --- |
| `text` | The result the model sees. Use a string; JSON inside a string is fine. |
| `ok` | `false` marks the call as failed. Default `true`. |
| `error` | A short reason, shown when `ok` is `false`. |
| `status` | Optional short status word. |
| `observation` | Optional object with structured details. |
| `resolved_target` | Optional: the file or address the call acted on. |

A non-zero exit with no output counts as a failure, and the first 500 characters of standard error are kept.
Output after 4 MB is cut off. Calls stop after `timeout_seconds` (30 seconds if you leave it out, 300 at most).
VOOL treats everything your program prints as untrusted data and removes any key values from it before
anyone sees it.

## Bundling an MCP server

A plugin can bundle a stdio MCP server instead of a plain program. [`template/`](../template/) is a complete
example.

```json
"mcpServers": {
  "text-digest": {"command": "bin/server", "args": [], "env": {}}
},
"tools": [
  {
    "intent": "vool-plugin-template.sha256",
    "description": "Compute the SHA-256 fingerprint of the supplied text.",
    "input_schema": {"type": "object", "required": ["text"], "properties": {"text": {"type": "string"}}},
    "handler": {"kind": "mcp", "server": "text-digest", "tool": "sha256_text", "timeout_seconds": 10},
    "trust": {"side_effect_class": "read_only", "permission_actions": ["read_files"]}
  }
]
```

- `command` is a path inside your folder. Runtime fetchers such as `npx` and `uvx` are refused, because they
  download code that nobody reviewed.
- `args` cannot expand environment variables.
- `env` may only pass your own declared keys, written as `"NAME": "${NAME}"`.
- Each MCP tool must name its server and tool, and should pin its effect class and permissions under `trust`.
  An unpinned tool asks for explicit approval every time it runs.
- Add a `.mcp.json` file with the same `command`, `args` and `env`, so other apps that read `.mcp.json` start it
  the same way. `scripts/check.py` checks that the two match.

Before submitting, prove that the server answers `initialize`, `tools/list` and a real `tools/call` when started
exactly as `.mcp.json` says.

## Model providers and scanners

These kinds hold no code. VOOL makes the network requests itself, to the hosts you declare, using its own
transport.

**Model provider** (`model_provider` block): an OpenAI-compatible service. After enabling, the person chooses
**Refresh model list**, and the models appear in VOOL's model picker. Published prices are what the service
reports. They are not charge receipts, and VOOL's normal spending checks still apply.

| Field | Required | Meaning |
| --- | --- | --- |
| `base_url` | yes | `https://` address on a declared `network` host, with no query string |
| `auth_placement` | yes | `header` (key sent as a bearer token) or `path` (key placed in the URL path) |
| `auth_path` | for `path` | A path containing `{credential}`, such as `/proxy/{credential}`. The key is never saved in a model URL. |
| `credential_slot` | yes | A slot name from your `credentials` |
| `model_list_path` | yes | Path that lists models, such as `/v1/models` |
| `pricing_source` | yes | Where prices come from |
| `api_path` | no | Chat path, such as `/v1/chat/completions` |
| `x402` | no | Declares that the service may ask for x402 payment. It never grants payment. |

**Scanner** (`scanner` block): a remote scan of public add-on content. VOOL's own check on the device always
runs as well, and an add-on installs only if both pass. A scanner report must name the exact content it
checked, by SHA-256. A scanner can never approve an installation on its own.

| Field | Meaning |
| --- | --- |
| `base_url`, `credential_slot` | As for providers |
| `test_path` | Called by **Test** to check the connection |
| `scan_path` | Called for each requested scan |
| `input_template` | Request body; `{name}` and `{content}` are filled in |
| `response_schema` | JSON Schema the response must match |
| `response_map` | Maps VOOL report fields (`kind`, `engine`, `service`, `verdict`, `lockfile`, `artifacts`, `findings`, `policy`) to paths in the response |

All `*_path` values start with `/`, and cannot contain `?`, `#`, `\` or `..`. VOOL does not follow redirects.

## Manifest reference

The manifest is `.codex-plugin/plugin.json`. VOOL's full JSON Schema is
`docs/reference/plugin-manifest.schema.json` in the VOOL source.

### Package fields

| Field | Rule |
| --- | --- |
| `name` | Same as `vool.id` |
| `version` | Semantic version, same as `vool.version` |
| `description` | One sentence |

### The `vool` block

| Field | Required | Rule |
| --- | --- | --- |
| `id` | yes | `^[a-z][a-z0-9_-]{0,79}$` |
| `version`, `name`, `publisher`, `description`, `license` | yes | Text |
| `homepage` | yes | Public `https://` address |
| `kind` | yes | One or more of `tools`, `model_provider`, `scanner`, with no repeats |
| `network` | yes | Exact lower-case public host names, or `[]` |
| `credentials` | yes | Key slots, or `{}` |
| `tools` | with `tools` | List of tools |
| `mcpServers` | no | Bundled MCP servers; needs the `tools` kind |
| `model_provider` | with that kind | See above |
| `scanner` | with that kind | See above |

### A tool

| Field | Rule |
| --- | --- |
| `intent` | `<plugin id>.<name>`, unique in the plugin |
| `description` | A real sentence, 12 characters or more |
| `input_schema` | JSON Schema object for the arguments |
| `handler` | `subprocess` or `mcp`, see below |
| `side_effect_class` | What the tool can change, see below (plain programs) |
| `permission_actions` | VOOL permissions the tool uses, see below (plain programs) |
| `approval_requirement` | `none`, `runtime_policy` or `explicit_user_opt_in` (plain programs). Only `read_only` tools may use `none`. |
| `trust` | `{side_effect_class, permission_actions}` (MCP tools) |
| `mutation` | Required for tools that change workspace files, see below |

Handler fields:

| Field | For | Rule |
| --- | --- | --- |
| `kind` | both | `subprocess` or `mcp` |
| `entry` | subprocess | Program path inside your folder |
| `args` | subprocess | Fixed arguments |
| `timeout_seconds` | both | Up to 300 |
| `network` | subprocess | `true` to use your declared hosts; see [Network](#network) |
| `env_allowlist` | subprocess | Key names from `credentials` that this tool receives |
| `server`, `tool` | mcp | The bundled server and its tool name |

Effect classes and the permission actions each may use:

| `side_effect_class` | Permission actions |
| --- | --- |
| `read_only` | `read_files`, `list_directories`, `run_safe_commands`, `public_read_only_retrieval` |
| `workspace_write` | `create_files`, `modify_files`, `overwrite_existing_files`, `delete_files` |
| `network_send` | `use_network_access`, `external_messages`, `access_external_providers` |
| `network_publish` | `use_network_access`, `deployment`, `access_external_providers` |
| `media_generation` | `access_external_providers`, `use_network_access` |
| `sandbox_command`, `validation_command` | `run_side_effecting_commands`, `run_safe_commands` |
| `task_orchestration` | `run_side_effecting_commands` |
| `builder_state`, `creative_state` | `create_files`, `modify_files` |

Read actions are allowed with every class. A `read_only` tool may list none (`[]`). Every other class must name
at least one action from its own row. A tool with `handler.network: true` needs a network class or `use_network_access`. Money classes
(`credit_spend`, `wallet_spend`) and money permissions are always refused for plugins, even though VOOL's
"is not one of" message lists them.

A tool that changes workspace files also declares how VOOL records and undoes the change:

```json
"side_effect_class": "workspace_write",
"permission_actions": ["create_files"],
"approval_requirement": "runtime_policy",
"mutation": {"tool": "<your intent>", "scope": "workspace", "effect_class": "reversible",
             "snapshot_strategy": "workspace_scan", "receipt_lifecycle": "intent_then_terminal",
             "rollback_support": "exact", "recorder": "blackbox.coverage_scan"}
```

### Credentials

```json
"credentials": {
  "access": {"label": "Your service key", "help_url": "https://example.org/keys", "env": "PLUGIN_EXAMPLE_ACCESS"}
}
```

- The slot name (`access`) is what providers and scanners name in `credential_slot`.
- `label` is shown beside the key box. `help_url` is a public `https://` page where people get a key.
- `env` matches `^[A-Z][A-Z0-9_]{0,95}$`, is unique in the plugin, and is not a reserved name. Names starting
  with `VOOL_`, `PYTHON`, `LD_`, `DYLD_`, `NODE_` or `RUBY`, and names of well-known model services such as
  `OPENAI_` or `ANTHROPIC_`, are refused. Start yours with `PLUGIN_`.
- Never put a key value in any file.

## Keys

- People paste keys into the plugin's card. VOOL stores them in its key vault under the plugin's own name. They
  never appear in the manifest, in logs or in chat.
- A plain program gets a key only when that tool lists its `env` name in `handler.env_allowlist`. The key arrives
  in `context.credentials` on standard input. Read it from there, because that works on every platform.
- On Linux the key is also set as an environment variable of that name. On macOS it never is: any program
  of the same user can read another program's starting environment there, and the macOS sandbox cannot
  stop that.
- An MCP server gets its keys only as environment variables, through `env`. On macOS such a server runs only in
  VOOL's optional isolated container. Without it, VOOL keeps the plugin off and says why. An MCP server that
  needs no key runs normally.
- VOOL removes key values from everything your program returns.
- Keys that VOOL kept from an older built-in service setting are used only by VOOL's own requests and are never
  handed to plugin code.

## Network

- Declare every host in `network`, exactly: lower-case, no scheme, no port, no path, no wildcard. IP addresses
  and local or private names are refused. VOOL checks every address it connects to and refuses private ranges,
  including IPv6 forms that carry an IPv4 address.
- A plain program gets network only when its tool sets `handler.network: true`.
- On macOS, VOOL starts a private proxy for that one call and points `HTTPS_PROXY` at it. The sandbox allows that
  proxy and nothing else, and the proxy connects only to your declared hosts. Use an HTTP client that honours
  `HTTPS_PROXY`. Direct sockets are refused.
- On Linux and in the isolated container the program cannot reach that proxy, so it runs with no network. The
  access sheet tells the person so. Design your tool to fail with a clear `error` when it is offline.
- Model provider and scanner requests are made by VOOL itself, to declared hosts only, on every platform.

## Files and processes

- Your program runs from a read-only copy of your folder. Write only inside `context.scratch_dir`, and only from
  tools that are not `read_only`. A `read_only` tool cannot write anywhere.
- Bundle everything your code needs: source, dependencies and lock files. Nothing is downloaded at run time.
- Each call checks that the plugin is enabled and that its files still match the reviewed digest. Changed bytes
  switch it off.
- Disable stops running calls, and late results are dropped.
- Packages are limited to 4096 files, 64 MB per file and 128 MB in total. Symbolic links and nested git
  repositories are refused.
- Python programs in the isolated container use its interpreter. Other bundled programs must run on Linux on the
  same processor architecture.

## Limits and why

| Limit | Why |
| --- | --- |
| No money, wallet, signing, approval, spending limit, budget or receipt power | People's money moves only through VOOL's own wallet, with their caps, their approval and a receipt, every time. |
| No owner model keys and no other plugin's keys | A plugin should spend only what its own service key allows, with a key the person gave it on purpose. |
| A key for a service paid from a balance funded through VOOL's wallet is never given to a plugin | That balance is spent only through the wallet's approvals and caps. |
| Installs and updates start switched off | Nothing runs until the person has read the access sheet. |
| No auto-enable or autostart | Same reason. |
| Exact network hosts only | The person sees every place the plugin can reach. |
| No runtime downloads | The code that runs is the code that was reviewed. |
| Changed files switch the plugin off | Same reason. |
| No plugins in remote or phone turns | Those turns never use the owner's keys or tools that can act. |
| Output is untrusted data | Plugin output cannot give VOOL orders. |
| A scanner cannot approve on its own | VOOL's own check always counts. |
| An `x402` declaration grants nothing | Payment always needs the owner's wallet approval. |

## Test before you submit

1. `python3 scripts/check.py --vool-source /path/to/vool <your-folder>` passes.
2. Your program, run by hand with sample input, prints one JSON object.
3. `python3 scripts/try.py ...` returns `"ok": true` for each tool, and a clear `error` for bad input.
4. In VOOL itself, with a separate test profile, run every step by hand:
   - install, which leaves the plugin switched off;
   - decline the access sheet, then accept it;
   - save a key, if the plugin has one;
   - call each tool from a chat;
   - disable it during a call;
   - change a file and confirm the plugin switches off;
   - update it;
   - uninstall it.
5. Test the failure paths: missing key, wrong key, timeout, service error, bad response and no network.
6. Check that no key value appears in output, logs or screenshots. Use test keys only.
7. For MCP, prove `initialize`, `tools/list` and a real call with the exact `.mcp.json` command.
8. For providers and scanners, test against a real local HTTPS test service with a throwaway certificate
   authority.

## Errors and fixes

VOOL refuses a plugin with a plain message. Messages about one tool start with its intent, and some start with
`manifest.vool:`. Match on the words after that.

| Message contains | Fix |
| --- | --- |
| must match exactly one supported schema | A required field is missing or has the wrong type, there is an unknown field, or a `description` is shorter than 12 characters. Compare with the [reference](#manifest-reference); `network` and `credentials` are required even when empty. |
| The plugin id and version must match the package name and version. | Make `name` equal `vool.id`, and `version` equal `vool.version`. |
| a plugin's intents must be prefixed with its own name | Rename each intent to `<plugin id>.<tool>`. |
| side_effect_class ... is not one of | Use a class from the table above. |
| approval_requirement ... is not one of | Use `none`, `runtime_policy` or `explicit_user_opt_in`. |
| can change something, so it cannot declare approval_requirement 'none' | Use `runtime_policy` for tools that are not `read_only`. |
| handler.network is true, so the tool must declare a network side_effect_class | Use `network_send`, or add `use_network_access`. |
| A network handler must declare network hosts. | List the hosts in `vool.network`. |
| Network hosts must be exact lower-case HTTPS host names. | Write the host in lower case. |
| Network hosts cannot contain wildcards, ports or paths. | Write only the name, such as `api.example.org`: no `https://`, `*`, `:443`, `/path`, and not a single word like `localhost`. |
| IP addresses cannot be plugin network hosts. | Use a public DNS name. |
| Local and private network hosts are not allowed. | Names ending in `.local`, `.localhost`, `.internal`, `.lan` or `.home` are refused. Use a public name. |
| This HTTPS destination is not in the plugin network declaration. | `homepage`, `help_url` and service URLs must start with `https://`. A service `base_url` must also be on a host in `network`. |
| Handlers may receive only this plugin's declared credential environment names. | Add the name to `credentials`, or remove it from `env_allowlist`. |
| Plugin key slots cannot request owner model keys or change the process environment policy. | Rename `env`, for example to `PLUGIN_<SERVICE>_ACCESS`. |
| Each credential needs a separate environment name. | Give each slot its own `env`. |
| MCP env may name only this plugin's declared credential slots, never values. | Write `"NAME": "${NAME}"` for a declared `NAME`. |
| MCP arguments cannot expand environment variables. | Remove `${...}` from `args`. |
| An MCP tool must name a bundled server and tool. | Set `handler.server` to a key of `mcpServers`, and set `handler.tool`. |
| MCP servers require the tools kind. / Tool declarations require the tools kind. | Add `tools` to `kind`. |
| The model_provider declaration must match the plugin kind. | Add the block and the kind together, or neither. Same for `scanner`. |
| A service may read only its own declared credential slot. | Set `credential_slot` to a slot in `credentials`. |
| Service paths must be bounded relative paths. | Start paths with `/`, with no `?`, `#`, `\` or `..`. |
| Service base URLs cannot contain query parameters. | Remove `?...` from `base_url`. |
| Plugins cannot request wallet, payment, signing, approval, cap, budget or receipt authority. | Remove money permissions. |
| Plugins cannot declare wallet, paid or approval tools. | Remove money words such as `wallet`, `payment`, `approve` or `budget` from intents and MCP tool names. |
| needs a mutation block / must declare its Blackbox coverage | Add the `mutation` block shown above to tools of class `workspace_write`, `sandbox_command` or `validation_command`. |
| is not executable / Permission denied | Run `chmod +x` on your program and commit the mode. |
| .claude-plugin/plugin.json name and version must match | Copy `name` and `version` from the manifest. |
| README.md / LICENSE / CHANGELOG.md is missing or empty | Add the file. |
| .mcp.json command, args and env must match | Make `.mcp.json` repeat each server exactly. |
| handler did not emit one JSON object on stdout | Print exactly one JSON object and nothing else to standard output. Send logs to standard error. |
| exit N: ... | Your program exited with an error. The text after the colon is the start of its standard error. |
| handler exceeded ...s | Make the call faster or raise `timeout_seconds`, up to 300. |
| This service is paid from a balance VOOL spends only with your wallet approvals | Such a service cannot be used from a plugin. |
| cannot keep private (macOS) | An MCP server that takes keys from its environment needs VOOL's isolated container on a Mac. Use a plain program, which reads keys from standard input. |

## Using a plugin in other apps

`.claude-plugin/plugin.json` and `.mcp.json` let apps that read those files list your plugin and start its MCP
server. Model providers and scanners are VOOL features, so other apps do not get them from these files. Test
any other app yourself before you say it is supported.
