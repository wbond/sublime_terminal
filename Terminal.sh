#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
VERSION=$(sw_vers -productVersion)
if (( $(expr $VERSION '<' 10.7.0) )); then
	IN_WINDOW="in window 1"
fi
osascript<<END
try
	tell application "System Events"
		if (count(processes whose name is "Terminal")) is 0 then
			tell application "Terminal"
				activate
				do script "$CD_CMD" $IN_WINDOW
			end tell
		else
			tell application "Terminal"
				activate
				do script "$CD_CMD"
			end tell
		end if
	end tell
end try
END