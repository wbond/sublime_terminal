#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
VERSION=$(sw_vers -productVersion)
if (( $(expr $VERSION '<' 10.7) || $(expr $VERSION '>=' 10.8) )); then
	RUNNING=$(ps -eo pid,comm -U $UID  | grep iTerm.app | grep -v grep | wc -l)
else
    RUNNING=1
fi

if (( $RUNNING )); then
	osascript<<END
	tell application "iTerm"
		activate
		set term to (make new terminal)
		tell term
			set sess to (launch session "Default Session")
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
		set sess to the first session of the first terminal
		tell sess
			write text "$CD_CMD"
		end tell
	end tell
END
fi