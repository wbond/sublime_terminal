#!/bin/sh

CD_CMD="cd "\\\"$(pwd)\\\""; clear"
osascript<<END
try
	tell application "System Events"
		tell application "Terminal" to activate
		tell process "Terminal" to keystroke "t" using command down
		tell application "Terminal" to do script "$CD_CMD" in front window
	end tell
end try
END
