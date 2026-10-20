# Umbriel Scripts by @tordex

## Sidebar settings

Optional per-strut settings are loaded from
`${XDG_CONFIG_HOME:-~/.config}/umbriel/sidebar.toml`. Each side defaults to
`enabled = true`, `size = 400`, `gap = 4`, and 4 pixels for each window
margin. Omit any setting to use its default.

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

