#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
VERSION=$(sw_vers -productVersion)

if (( $(expr $VERSION '<' 10.7) )); then
	RUNNING=$(osascript<<END
	tell application "System Events"
	    count(processes whose name is "iTerm")
	end tell
END
)
else
	RUNNING=1
fi

if (( ! $RUNNING )); then
	osascript<<END
	tell application "iTerm"
		activate
		set term to current terminal
		tell term
			set sess to current session
			tell sess
				write text "$CD_CMD"
			end tell
		end tell
	end tell
END
else
	osascript<<END
	tell application "iTerm"
		activate
		set term to the first terminal
		tell term
			launch session "Default Session"
			set sess to current session
			tell sess
				write text "$CD_CMD"
			end tell
		end tell
	end tell
END
fi
