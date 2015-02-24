#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
VERSION=$(sw_vers -productVersion)
NEWWINDOW=0

while [ "$1" != "" ]; do
	case $1 in
		--openNewWindow )   NEWWINDOW=1
												;;
		--openNewTab )      NEWWINDOW=0
												;;
	esac
	shift
done

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
		tell current terminal
			launch session "Default Session"
			tell the last session
				write text "$CD_CMD"
			end tell
		end tell
	end tell
END
else
	if (( $NEWWINDOW )); then
		osascript &>/dev/null <<EOF
		tell application "iTerm"
			set term to (make new terminal)
			tell term
				launch session "Default Session"
				tell the last session
					write text "$CD_CMD"
				end tell
			end tell
		end tell
EOF
	else
		osascript &>/dev/null <<EOF
		tell application "iTerm"
			tell current terminal
				launch session "Default Session"
				tell the last session
					write text "$CD_CMD"
				end tell
			end tell
		end tell
EOF
	fi
fi
