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
		count(processes whose name is "iTerm2")
	end tell
END
)
else
	RUNNING=1
fi

if (( ! $RUNNING )); then
	osascript<<END
	tell application "iTerm"
		tell current window
			create tab with default profile

			tell current session
				write text "$CD_CMD"
			end tell
		end tell

		activate
	end tell
END
else
	if (( $OPEN_IN_TAB )); then
		osascript &>/dev/null <<EOF
		tell application "iTerm"
			if (count of windows) = 0 then
				set theWindow to (create window with default profile)
				set theSession to current session of theWindow
			else
				set theWindow to current window
				tell current window
					set theTab to create tab with default profile
					set theSession to current session of theTab
				end tell
			end if
			tell theSession
				write text "$CD_CMD"
			end tell

			activate
		end tell
EOF
	else
		osascript &>/dev/null <<EOF
		tell application "iTerm"
			tell (create window with default profile)
				tell the current session
					write text "$CD_CMD"
				end tell
			end tell

			activate
		end tell
EOF
	fi
fi
