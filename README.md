# 🔺 Elevator

Go up and down quickly


## Commands:

These commands should be self explanatory

- Toggle Relative Line Numbers
- Move Up
- Move Down

## Usage

Assuming suggested keybindings are enabled, here's how the plugin works


### `alt+up, [1-9]` / `alt+down, [1-9]`

   Moves you from your current line relative to a line based on the number pressed. 

### `alt+up, up` / `alt+down, down`

   Moves you from your current line relative to a line based on the `default_line_jump` value.

   If `default_line_jump` is disabled (`False` or `0`), an input panel will show up.
   An initial value set to the current line will be provided if `relative_line_numbers` is disabled
