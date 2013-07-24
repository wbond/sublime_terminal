#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"""
IN_WINDOW="in window 1"

osascript<<END
try
	tell application "System Events"
		if (count(processes whose name is "Terminal")) is 0 then
			tell application "Terminal"
				activate
				do script "$CD_CMD" $IN_WINDOW
				tell application "System Events" to set frontmost of process "Terminal" to true
			end tell
		else
			tell application "Terminal"
				activate
				do script "$CD_CMD" $IN_WINDOW
			end tell
		end if
	end tell
end try
END
