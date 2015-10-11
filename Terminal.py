import sublime
import sublime_plugin
import os
import sys
import subprocess
import locale

if os.name == 'nt':
    try:
        import _winreg
    except (ImportError):
        import winreg as _winreg
    from ctypes import windll, create_unicode_buffer

class NotFoundError(Exception):
    pass


if sys.version_info >= (3,):
    installed_dir, _ = __name__.split('.')
else:
    installed_dir = os.path.basename(os.getcwd())

def get_setting(key, default=None):
    settings = sublime.load_settings('Terminal.sublime-settings')
    os_specific_settings = {}
    if os.name == 'nt':
        os_specific_settings = sublime.load_settings('Terminal (Windows).sublime-settings')
    elif os.name == 'darwin':
        os_specific_settings = sublime.load_settings('Terminal (OSX).sublime-settings')
    else:
        os_specific_settings = sublime.load_settings('Terminal (Linux).sublime-settings')
    return os_specific_settings.get(key, settings.get(key, default))


class TerminalSelector():
    default = None

    @staticmethod
    def get():
        package_dir = os.path.join(sublime.packages_path(), installed_dir)
        terminal = get_setting('terminal')
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
            if os.path.exists(os.environ['SYSTEMROOT'] +
                    '\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'):
                # This mimics the default powershell colors since calling
                # subprocess.POpen() ends up acting like launching powershell
                # from cmd.exe. Normally the size and color are inherited
                # from cmd.exe, but this creates a custom mapping, and then
                # the LaunchPowerShell.bat file adjusts some other settings.
                key_string = 'Console\\%SystemRoot%_system32_' + \
                    'WindowsPowerShell_v1.0_powershell.exe'
                try:
                    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                        key_string)
                except (WindowsError):
                    key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER,
                        key_string)
                    _winreg.SetValueEx(key, 'ColorTable05', 0,
                        _winreg.REG_DWORD, 5645313)
                    _winreg.SetValueEx(key, 'ColorTable06', 0,
                        _winreg.REG_DWORD, 15789550)
                default = os.path.join(package_dir, 'PS.bat')
                sublime_terminal_path = os.path.join(sublime.packages_path(), installed_dir)
                # This should turn the path into an 8.3-style path, getting around unicode
                # issues and spaces
                buf = create_unicode_buffer(512)
                if windll.kernel32.GetShortPathNameW(sublime_terminal_path, buf, len(buf)):
                    sublime_terminal_path = buf.value
                os.putenv('sublime_terminal_path', sublime_terminal_path.replace(' ', '` '))
            else :
                default = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'

        elif sys.platform == 'darwin':
            default = os.path.join(package_dir, 'Terminal.sh')
            if not os.access(default, os.X_OK):
                os.chmod(default, 0o755)

        else:
            ps = 'ps -eo comm | grep -E "gnome-session|ksmserver|' + \
                'xfce4-session|lxsession|mate-panel|cinnamon-sessio" | grep -v grep'
            wm = [x.replace("\n", '') for x in os.popen(ps)]
            if wm:
                if wm[0] == 'gnome-session' or wm[0] == 'cinnamon-sessio':
                    default = 'gnome-terminal'
                elif wm[0] == 'xfce4-session':
                    default = 'xfce4-terminal'
                elif wm[0] == 'ksmserver':
                    default = 'konsole'
                elif wm[0] == 'lxsession':
                    default = 'lxterminal'
                elif wm[0] == 'mate-panel':
                    default = 'mate-terminal'
            if not default:
                default = 'xterm'

        TerminalSelector.default = default
        return default


class TerminalCommand():
    def get_path(self, paths):
        if paths:
            return paths[0]
        # DEV: On ST3, there is always an active view.
        #   Be sure to check that it's a file with a path (not temporary view)
        elif self.window.active_view() and self.window.active_view().file_name():
            return self.window.active_view().file_name()
        elif self.window.folders():
            return self.window.folders()[0]
        else:
            sublime.error_message('Terminal: No place to open terminal to')
            return False

    def run_terminal(self, dir_, parameters):
        try:
            if not dir_:
                raise NotFoundError('The file open in the selected view has ' +
                    'not yet been saved')
            for k, v in enumerate(parameters):
                parameters[k] = v.replace('%CWD%', dir_)
            args = [TerminalSelector.get()]
            args.extend(parameters)
            encoding = locale.getpreferredencoding(do_setlocale=True)
            if sys.version_info >= (3,):
                cwd = dir_
            else:
                cwd = dir_.encode(encoding)
            subprocess.Popen(args, cwd=cwd)

        except (OSError) as exception:
            print(str(exception))
            sublime.error_message('Terminal: The terminal ' +
                TerminalSelector.get() + ' was not found')
        except (Exception) as exception:
            sublime.error_message('Terminal: ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        parameters = get_setting('parameters', [])

        if os.path.isfile(path):
            path = os.path.dirname(path)

        self.run_terminal(path, parameters)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand,
        TerminalCommand):
    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        # DEV: We require separator to be appended since `/hello` and `/hello-world`
        #   would both match a file in `/hello` without it
        #   For more info, see https://github.com/wbond/sublime_terminal/issues/86
        folders = [x for x in self.window.folders() if path.find(x + os.sep) == 0][0:1]

        command = OpenTerminalCommand(self.window)
        command.run(folders, parameters=parameters)
