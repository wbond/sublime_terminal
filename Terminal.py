import sublime
import sublime_plugin
import os
import sys
import subprocess
import locale

if os.name == 'nt':
    import _winreg


class NotFoundError(Exception):
    pass


class TerminalSelector():
    default = None

    @staticmethod
    def get():
        settings = sublime.load_settings('Terminal.sublime-settings')
        package_dir = os.path.join(sublime.packages_path(), __name__)

        terminal = settings.get('terminal')
        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(package_dir, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0755)
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
            else :
                default = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'

        elif sys.platform == 'darwin':
            default = os.path.join(package_dir, 'Terminal.sh')
            if not os.access(default, os.X_OK):
                os.chmod(default, 0755)

        else:
            ps = 'ps -eo comm | grep -E "gnome-session|ksmserver|' + \
                'xfce4-session" | grep -v grep'
            wm = [x.replace("\n", '') for x in os.popen(ps)]
            if wm:
                if wm[0] == 'gnome-session':
                    default = 'gnome-terminal'
                elif wm[0] == 'xfce4-session':
                    default = 'terminal'
                elif wm[0] == 'ksmserver':
                    default = 'konsole'
            if not default:
                default = 'xterm'

        TerminalSelector.default = default
        return default


class TerminalCommand():
    def get_path(self, paths):
        if paths:
            return paths[0]
        elif self.window.active_view():
            return self.window.active_view().file_name()
        elif self.window.folders():
            return self.window.folders()[0]
        else:
            sublime.error_message(__name__ + ': No place to open terminal to')
            return False

    def run_terminal(self, dir, parameters):
        try:
            if not dir:
                raise NotFoundError('The file open in the selected view has ' +
                    'not yet been saved')
            for k, v in enumerate(parameters):
                parameters[k] = v.replace('%CWD%', dir)
            args = [TerminalSelector.get()]
            args.extend(parameters)
            encoding = locale.getpreferredencoding(do_setlocale=True)
            subprocess.Popen(args, cwd=dir.encode(encoding))

        except (OSError) as (exception):
            print str(exception)
            sublime.error_message(__name__ + ': The terminal ' +
                TerminalSelector.get() + ' was not found')
        except (Exception) as (exception):
            sublime.error_message(__name__ + ': ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        if parameters == None:
            settings = sublime.load_settings('Terminal.sublime-settings')
            parameters = settings.get('parameters')

        if not parameters:
            parameters = []

        if os.path.isfile(path):
            path = os.path.dirname(path)

        self.run_terminal(path, parameters)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand,
        TerminalCommand):
    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        folders = [x for x in self.window.folders() if path.find(x) == 0][0:1]

        command = OpenTerminalCommand(self.window)
        command.run(folders, parameters=parameters)