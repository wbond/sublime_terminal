#!/bin/bash

# open in new window or in a tab?
# if tab mode and no window exists, open in new window
OPEN_TYPE="tab" # tab|window


if [[ $OPEN_TYPE == "window" ]]; then 

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

elif [[ $OPEN_TYPE == "tab" ]]; then

	# set the name of the tab
	function tabname {
	  printf "\e]1;$1\a"
	}

	CD_CMD="cd "\\\"$(pwd)\\\"" && _name="\\\"$(pwd)\\\""; tabname \${_name##*/}; unset _name; clear;"
	osascript<<END
	try
		activate application "Terminal"
		tell application "System Events"
		    keystroke "t" using {command down}
		end tell

		tell application "Terminal"
		    repeat with win in windows
		        try
		            if get frontmost of win is true then
		                do script "$CD_CMD" in (selected tab of win)
		            end if
		        end try
		    end repeat
		end tell
	end try
END

fi