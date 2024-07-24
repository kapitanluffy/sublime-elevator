import sublime
import sublime_plugin


def cast_to_int(val):
    try:
        return int(val)
    except ValueError:
        return 0


def get_first_sel(sels):
    return sels[0] if len(sels) else None


def get_first_and_last_lines(view):
    sel = get_first_sel(view.sel())
    if sel is None:
        firstlinenum = 0
    else:
        firstlinenum, _ = view.rowcol(sel.a)

    lastlinenum, _ = view.rowcol(view.size())
    return [firstlinenum, lastlinenum]


class ElevatorMoveCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        is_forward = kwargs.get('forward', True)
        character = kwargs.get('character', 0)

        view = self.window.active_view()
        if view is None:
            return

        settings = sublime.load_settings("Preferences.sublime-settings")
        is_relative = settings.get("relative_line_numbers", False)

        if is_relative is False:
            self.move_absolute(character, is_forward)

        if is_relative is True:
            self.move_relative(character, is_forward)

    def move_relative(self, character, is_forward):
        view = self.window.active_view()
        if view is None:
            return

        # "up" and "down" strings will be casted to zero
        lines = cast_to_int(character)

        # Use default_line_jump if lines is zero
        if lines == 0 and (character == "up" or character == "down"):
            settings = sublime.load_settings("Elevator.sublime-settings")
            lines = cast_to_int(settings.get("default_line_jump", 0))

        if lines != 0:
            for _ in range(lines):
                self.window.run_command("move", {"by": "lines", "forward": is_forward})
            view.run_command("show_at_center")
            return

        firstlinenum, lastlinenum = get_first_and_last_lines(view)
        initial_value = ""

        label = "Move To Line [{} - {}]:".format(1, lastlinenum)

        # move down and NOT in the last line
        if is_forward is True and firstlinenum != lastlinenum:
            label = "Move To Line [{} - {}]:".format(1, lastlinenum - firstlinenum)
        # move up and NOT in the first line
        if is_forward is False and firstlinenum != 0:
            label = "Move To Line [{} - {}]:".format(1, firstlinenum)
        # move down and in the last line
        if is_forward is True and firstlinenum == lastlinenum:
            initial_value = lastlinenum + 1
            is_forward = not is_forward
            pass
        # move up and in the first line
        if is_forward is False and firstlinenum == 0:
            initial_value = lastlinenum
            is_forward = not is_forward
            pass

        self.window.show_input_panel(label, str(initial_value), lambda v: self.on_done_move_rel(v, is_forward), None, None)

    def on_done_move_rel(self, text, is_forward):
        view = self.window.active_view()
        if view is None:
            return

        lines = cast_to_int(text)

        # @bug has problems with wrapped lines
        for _ in range(lines):
            self.window.run_command("move", {"by": "lines", "forward": is_forward})
        view.run_command("show_at_center")

    def move_absolute(self, character, is_forward):
        view = self.window.active_view()
        if view is None:
            return

        firstlinenum, lastlinenum = get_first_and_last_lines(view)
        initial_value = cast_to_int(character)
        no_initial_value = False

        if initial_value == 0:
            no_initial_value = True
            settings = sublime.load_settings("Elevator.sublime-settings")
            initial_value = cast_to_int(settings.get("default_line_jump", 0))

        label = "Move To Line [{} - {}]:".format(1, lastlinenum + 1)

        if initial_value != 0 and no_initial_value is True:
            direction = 1 if is_forward is True else -1
            line = firstlinenum + (initial_value * direction)
            view.run_command("goto_line", {"line": line if line > 0 else 1})
            view.run_command("show_at_center")
            return

        # move down and NOT in the last line
        if is_forward is True and firstlinenum != lastlinenum:
            initial_value = (firstlinenum + 1) + initial_value
            label = "Move To Line [{} - {}]:".format(firstlinenum + 1, lastlinenum + 1)
        # move up and NOT in the first line
        if is_forward is False and firstlinenum != 0:
            initial_value = (firstlinenum + 1) - initial_value
            label = "Move To Line [{} - {}]:".format(1, firstlinenum + 1)
        # move down and in the last line
        if is_forward is True and firstlinenum == lastlinenum:
            initial_value = initial_value + 1
        # move up and in the first line
        if is_forward is False and firstlinenum == 0:
            initial_value = (lastlinenum + 1) - initial_value

        # handle out of bounds
        initial_value = initial_value if initial_value > 0 else 1
        initial_value = (lastlinenum + 1) if initial_value > (lastlinenum + 1) else initial_value

        if initial_value == (firstlinenum + 1) and no_initial_value is True:
            self.window.show_input_panel(label, str(initial_value), self.on_done_move_abs, None, None)
            return

        if initial_value != 0:
            view.run_command("goto_line", {"line": initial_value})
            view.run_command("show_at_center")


    def on_done_move_abs(self, text):
        view = self.window.active_view()
        if view is None:
            return

        line = cast_to_int(text)

        view.run_command("goto_line", {"line": line})
        view.run_command("show_at_center")


class ElevatorToggleRelativeLineNumbersCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        is_relative = settings.get("relative_line_numbers", False)
        settings.set("relative_line_numbers", not is_relative)
        sublime.save_settings("Preferences.sublime-settings")
