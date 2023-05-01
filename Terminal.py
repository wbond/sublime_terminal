import sublime
import sublime_plugin
import os
import sys
import subprocess

if os.name == 'nt':
    try:
        import _winreg
    except (ImportError):
        import winreg as _winreg
    from ctypes import windll, create_unicode_buffer


class NotFoundError(Exception):
    pass


INSTALLED_DIR = __name__.split('.')[0]


def get_setting(key, default=None):
    settings = sublime.load_settings('Terminal.sublime-settings')
    os_specific_settings = {}
    if os.name == 'nt':
        os_specific_settings = sublime.load_settings('Terminal (Windows).sublime-settings')
    elif sys.platform == 'darwin':
        os_specific_settings = sublime.load_settings('Terminal (OSX).sublime-settings')
    else:
        os_specific_settings = sublime.load_settings('Terminal (Linux).sublime-settings')
    return os_specific_settings.get(key, settings.get(key, default))


def powershell(package_dir):
    # This mimics the default powershell colors since calling
    # subprocess.POpen() ends up acting like launching powershell
    # from cmd.exe. Normally the size and color are inherited
    # from cmd.exe, but this creates a custom mapping, and then
    # the LaunchPowerShell.bat file adjusts some other settings.
    key_string = 'Console\\%SystemRoot%_system32_WindowsPowerShell_v1.0_powershell.exe'
    try:
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, key_string)
    except (WindowsError):
        key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, key_string)
        _winreg.SetValueEx(key, 'ColorTable05', 0, _winreg.REG_DWORD, 5645313)
        _winreg.SetValueEx(key, 'ColorTable06', 0, _winreg.REG_DWORD, 15789550)
    default = os.path.join(package_dir, 'PS.bat')
    sublime_terminal_path = os.path.join(
        sublime.packages_path(), INSTALLED_DIR)
    # This should turn the path into an 8.3-style path,
    # getting around unicode issues and spaces
    buf = create_unicode_buffer(512)
    if windll.kernel32.GetShortPathNameW(sublime_terminal_path, buf, len(buf)):
        sublime_terminal_path = buf.value
    os.environ['sublime_terminal_path'] = sublime_terminal_path.replace(' ', '` ')

    return default


def linux_terminal():
    ps = 'ps -eo comm,args | grep -E "^(gnome-session|ksmserver|xfce4-session|lxsession|mate-panel|cinnamon-sessio)" | grep -v grep'  # noqa: E501
    wm = [x.replace("\n", '') for x in os.popen(ps)]
    if wm:
        # elementary OS: `/usr/lib/gnome-session/gnome-session-binary --session=pantheon`
        # Gnome: `gnome-session` or `gnome-session-binary`
        # Linux Mint Cinnamon: `cinnamon-session --session cinnamon`
        if wm[0].startswith('gnome-session') or wm[0].startswith('cinnamon-session'):
            if 'pantheon' in wm[0]:
                return 'pantheon-terminal'
            return 'gnome-terminal'
        if wm[0].startswith('xfce4-session'):
            return 'xfce4-terminal'
        if wm[0].startswith('ksmserver'):
            return 'konsole'
        if wm[0].startswith('lxsession'):
            return 'lxterminal'
        if wm[0].startswith('mate-panel'):
            return 'mate-terminal'

    # nothing specific found, return a default
    return 'xterm'


class TerminalSelector():
    default = None

    @staticmethod
    def get(terminal_key):
        package_dir = os.path.join(sublime.packages_path(), INSTALLED_DIR)
        terminal = get_setting(terminal_key)
        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(package_dir, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0o755)
            return terminal

        if TerminalSelector.default:
            return TerminalSelector.default

        default = None

        if os.name == 'nt':
            if os.path.exists(os.environ['SYSTEMROOT'] + '\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'):
                default = powershell(package_dir)
            else:
                default = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'

        elif sys.platform == 'darwin':
            default = os.path.join(package_dir, 'Terminal.sh')
            if not os.access(default, os.X_OK):
                os.chmod(default, 0o755)

        else:
            default = linux_terminal()

        TerminalSelector.default = default
        return default


class TerminalCommand():
    def get_path(self, paths):
        view = self.window.active_view()

        if paths:
            # a path has been passed to the command (ie. a context)
            return paths[0]

        if view and view.file_name():
            # check that the file actually exists on disk
            return view.file_name()

        if self.window.folders():
            # default to the first project directory, if it exists
            return self.window.folders()[0]

        # finally fall back to the user home directory
        sublime.status_message('Terminal: opening at home directory')
        return os.path.expanduser('~')

    def open_terminal(self, dir, terminal, parameters):
        try:
            for k, v in enumerate(parameters):
                parameters[k] = v.replace('%CWD%', dir)
            args = [TerminalSelector.get(terminal)]
            args.extend(parameters)

            # Copy over environment settings onto parent environment
            env_setting = get_setting('env', {})
            env = os.environ.copy()
            for k in env_setting:
                if env_setting[k] is None:
                    env.pop(k, None)
                else:
                    env[k] = env_setting[k]

            # Run our process
            subprocess.Popen(args, cwd=dir, env=env)

        except (OSError) as exception:
            print(str(exception))
            sublime.error_message('Terminal: The terminal ' + TerminalSelector.get() + ' was not found')
        except (Exception) as exception:
            sublime.error_message('Terminal: ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def is_visible(self, paths=[]):
        # remove the command if the view doesn't have a path to open at
        # taking is_visible over is_enabled to remove it from the context menu,
        # instead of simply disabling the entry
        view = self.window.active_view()
        return bool(view and view.file_name() or paths)

    def run(self, paths=[], parameters=None, terminal=None):
        path = self.get_path(paths)

        if terminal is None:
            terminal = 'terminal'

        if parameters is None:
            parameters = get_setting('parameters', [])

        if os.path.isfile(path):
            path = os.path.dirname(path)

        self.open_terminal(path, terminal, parameters)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def is_visible(self):
        # remove the command if the current window doesn't have directories
        # i.e. it's a single file (use the other command)
        # is_visible and is_enabled effectively do the same thing here
        return bool(self.window.folders())

    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        # We require separator to be appended since /hello and /hello-world
        # would both match a file in `/hello` without it
        # See https://github.com/wbond/sublime_terminal/issues/86
        folders = [x for x in self.window.folders() if path.find(x + os.sep) == 0][0:1]

        command = OpenTerminalCommand(self.window)
        command.run(folders, parameters=parameters)
