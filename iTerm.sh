#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"
if echo "$SHELL" | grep -E "/fish$" &> /dev/null; then
  CD_CMD="cd "\\\"$(pwd)\\\""; and clear"
fi
VERSION=$(sw_vers -productVersion)
OPEN_IN_TAB=0

while [ "$1" != "" ]; do
	PARAM="$1"
	VALUE="$2"
	case "$PARAM" in
		--open-in-tab)
			OPEN_IN_TAB=1
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
	if (( $OPEN_IN_TAB )); then
		osascript &>/dev/null <<EOF
		tell application "iTerm"
			if (count of terminals) = 0 then
				set term to (make new terminal)
			else
				set term to current terminal
			end if
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
			set term to (make new terminal)
			tell term
				launch session "Default Session"
				tell the last session
					write text "$CD_CMD"
				end tell
			end tell
		end tell
EOF
	fi
fi
