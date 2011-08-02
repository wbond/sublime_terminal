import sublime
import sublime_plugin
import os
import sys
import subprocess
import stat

if os.name == 'nt':
    import _winreg


class NotFoundError(Exception):
    pass


class TerminalSelector():
    default = None

    @staticmethod
    def get():
        settings = sublime.load_settings('Terminal.sublime-settings')

        if settings.get('terminal'):
            return settings.get('terminal')

        if TerminalSelector.default:
            return TerminalSelector.default

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
                package_dir = os.path.join(sublime.packages_path(), __name__)
                default = os.path.join(package_dir, 'PS.bat')
            else :
                default = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'

        elif sys.platform == 'darwin':
            default = os.path.join(sublime.packages_path(), __name__,
                'Terminal.sh')
            os.chmod(default, 0755)

        else:
            ps = 'ps -eo comm | grep -E "gnome-session|ksmserver|' + \
                'xfce4-session" | grep -v grep'
            wm = [x.replace("\n", '') for x in os.popen(ps)]
            if wm:
                if wm[0] == 'gnome-session':
                    default = 'gnome-terminal'
                elif wm[0] == 'xfce4-session':
                    default = 'xfce4-terminal'
                elif wm[0] == 'ksmserver':
                    default = 'konsole'
            if not default:
                default = 'xterm'

        TerminalSelector.default = default
        return default


class TerminalCommand():
    def run_terminal(self, dir):
        try:
            if not dir:
                raise NotFoundError('The file open in the selected view has ' +
                    'not yet been saved')
            ForkGui(TerminalSelector.get(), dir)
        except (OSError) as (exception):
            print str(exception)
            sublime.error_message('Terminal: The terminal ' +
                TerminalSelector.get() + ' was not found')
        except (Exception) as (exception):
            sublime.error_message('Terminal: ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[]):
        if paths:
            path = paths[0]
        elif self.window.active_view():
            path = self.window.active_view().file_name()
        else:
            path = self.window.folders()[0]

        if os.path.isfile(path):
            path = os.path.dirname(path)
        self.run_terminal(path)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand,
        TerminalCommand):
    def run(self, paths=[]):
        path = paths[0] if paths else self.window.active_view().file_name()
        if path:
            folders = [x for x in self.window.folders() if path.find(x) == 0]
            if folders:
                path = folders[0]

        command = OpenTerminalCommand(self.window)
        command.run([path])


class ForkGui():
    def __init__(self, *args):
        self.args = args
        self.run()

    def run(self):
        proc = subprocess.Popen(self.args[0], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.args[1])