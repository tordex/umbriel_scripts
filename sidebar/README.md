# Umbriel Sidebar

Umbriel Sidebar is a small Python daemon for docking the focused window to an
edge of its workspace. It listens for Umbriel window events, arranges docked
windows into left, right, top, or bottom struts, and writes the strut layout to
Umbriel's runtime configuration.

## Requirements

- Python 3.11 or later
- The `jq` Python package
- A running Umbriel service with `UMBRIEL_SOCKET` set to its Unix socket path
- `XDG_RUNTIME_DIR` set to a writable runtime directory

## Umbriel configuration

Add these lines to your Umbriel configuration (`~/.config/umbriel/config.toml`):

```toml
[include.optional]
files = [
    "$XDG_RUNTIME_DIR/umbriel-sidebar.toml",
]
```

## Run

From the repository root, start the daemon in the environment where Umbriel is
available:

```sh
python3 sidebar/sidebar
```

The daemon listens for control commands on `/tmp/umbriel_sidebar.sock`. Stop it
with Ctrl+C. On exit, it removes the control socket. While running, it writes
strut layout data to `$XDG_RUNTIME_DIR/umbriel-sidebar.toml`.

## Commands

Send a command to the Unix socket with a tool such as `nc`:

```sh
echo 'dock-left' | nc -U /tmp/umbriel_sidebar.sock
```

Available commands are `dock-left`, `dock-right`, `dock-top`, and `dock-bottom`.
Each docks the currently focused window on the corresponding edge of its
workspace. The daemon accepts one command per socket connection.

## Settings

Optional per-side settings are loaded from
`${XDG_CONFIG_HOME:-~/.config}/umbriel-sidebar/config.toml`. Missing settings
use the defaults: `enabled = true`, `size = 400`, `gap = 4`, and 4 pixels for
each margin. Sizes, gaps, and margins are measured in logical pixels. A side with
`enabled = false` will not accept dock commands.

```toml
[struts.left]
enabled = true
size = 500
gap = 4
[struts.left.margins]
left = 4
top = 4
right = 4
bottom = 4

[struts.right]
enabled = true
size = 400
gap = 4
[struts.right.margins]
left = 4
top = 4
right = 4
bottom = 4

[struts.top]
enabled = true
size = 400
gap = 4
[struts.top.margins]
left = 4
top = 4
right = 4
bottom = 4

[struts.bottom]
enabled = true
size = 400
gap = 4
[struts.bottom.margins]
left = 4
top = 4
right = 4
bottom = 4
```

All four sides are optional. Within a side's `margins` table, each margin is
also optional and defaults to 4. `gap` must be a non-negative integer, `size`
must be a positive integer, and margins must be non-negative integers.

