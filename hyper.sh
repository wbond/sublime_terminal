#!/bin/bash

CD_CMD="cd "\\\"$(pwd)\\\"" && clear"

osascript &>/dev/null <<EOF
    tell application "Hyper"
        activate
        tell application "System Events"
            key code 17 using command down   # Open new tab
            delay 0.5                        # Wait a bit for the tab to open
            keystroke "$CD_CMD"              # Input command
            key code 36                      # Press enter
        end tell
    end tell
EOF