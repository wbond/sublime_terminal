#!/bin/bash

###
# See Notice.md for attribution
###

CD_PATH="$(pwd)"

osascript<<END
set myPath to quoted form of POSIX path of "$CD_PATH"

tell application "iTerm"
  activate
  if the (count of terminal) is 0 then
    set myTerm to make new terminal
  else
    set myTerm to the current terminal
  end if
  tell myTerm
    launch session "Default Session"
    tell the last session to write text "cd " & myPath
  end tell
end tell
END
