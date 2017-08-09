# changelog
## 1.18.0

 - Added support for Elementary OS. Fixes #159

## 1.17.0

 - Fixed OS X settings via @drbarrett in #162

## 1.16.3

 - Added unicode to str normalization for environment. Fixes #154

## 1.16.2

 - Added fallback for env setting. Fixes #154

## 1.16.1

 - Fixed Windows Powershell support. Fixes #151

## 1.16.0

 - Added support for environment customization via @peterfyj in #150

## 1.15.1

 - Updated examples in Terminal.sublime-settings to be less confusing via @rogeriopradoj in #139

## 1.15.0

 - Fixed iTerm2-v3 script opening multiple tabs if never opened before via @ctf0 in #131

## 1.14.0

 - Fixed iTerm2-v3 script navigation and window activation via @garyking in #133

## 1.13.1

 - Added `release.sh` for release automation

## 1.13.0

 - Added iTerm2-v3 support via @pzgz in #98

## 1.12.1

 - Added missing changelog notes

## 1.12.0

 - Fixed gnome-terminal support via @beledouxdenis in #115

## 1.11.0

 - Fixed custom parameters functionality via @jfcherng in #112

## 1.10.1

 - Replaced `readme.creole` with `readme.md` based off of website
 - Added/updated `changelog.md`
 - Relocated license to `LICENSE`
 - Added common examples to `readme.md`

## 1.10.0

 - Repaired handling of temporary views in Sublime Text 3

## 1.9.0

 - Added commands to open the terminal from the command palette

## 1.8.2

 - Fixed "--open-in-tab" behavior when no terminal is open

## 1.8.1

 - Repaired FiSH compatibility more elegantly

## 1.8.0

 - Added support for opening a new tab in iTerm

## 1.7.2

 - Repaired handling multiple project folders with same base path and starting name

## 1.7.1

 - Corrected hyphen/dash typo in settings

## 1.7.0

 - Added support for OS specific settings

## 1.6.0

 - Added compatibility for FiSH

## 1.5.0

 - Added support for LXTerminal, Mate Terminal, xfce4, and Linux Mint/Cinnamon

## 1.4.0

 - Added support for Sublime Text 3

## 1.3.1

 - Added support for non-ASCII directory paths
 - Fixed an error popup with some Linux distributions, when unable to determine the default terminal application

## 1.3.0

 - Added %CWD% placeholder for parameters to receive the current working directory the terminal was opened to
 - Tweaked menu entries

## 1.2.0

 - Fixed a bug with Open Terminal at Project Folder when no files are open
 - Added an iTerm.sh script for OS X users

## 1.1.1

 - Fixed a bug in spawning the terminal that would cause cmd.exe to hang

## 1.1.0

 - Added parameters setting
 - Added the parameters arg to the open_terminal and open_terminal_project_folder commands

## 1.0.2

 - Fixed the executable name for the XFCE terminal

## 1.0.1

 - Fixed Terminal.sh to not launch a second window on OS X Lion

## 1.0.0

 - Initial release
