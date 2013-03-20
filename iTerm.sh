#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
# This:
# > tell application "System Events" to set iTermIsRunning to exists (processes where bundle identifier is "com.googlecode.iterm2")
# does not currently work properly, since it will always report iTerm as running. Not intended, since
# running first osascript snippet when no iTerm is actually running results in extra tab being opened.
RUNNING=$(ps -eo pid,comm -U $UID  | grep iTerm.app | wc -l)

if (( $RUNNING )); then
	osascript<<END
	tell application "iTerm"
		try
			set term to last terminal
		on error
			set term to (make new terminal)
		end try
		tell term
			set sess to (launch session "Default Session")
			tell sess
				write text "$CD_CMD"
			end tell
		end tell
		activate
	end tell
END
else
	osascript<<END
	tell application "iTerm"
		set sess to the first session of the first terminal
		tell sess
			write text "$CD_CMD"
		end tell
		activate
	end tell
END
fi