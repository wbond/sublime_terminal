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

RUNNING=$(osascript<<END
  tell application "System Events"
    count(processes whose name is "iTerm2")
  end tell
END
)

echo $RUNNING

if (( $RUNNING )); then
  if (( $OPEN_IN_TAB )); then
    osascript &>/dev/null <<EOF
      tell application "iTerm2"
        tell current window
          create tab with profile "Default"
          write text "$CD_CMD"
        end tell
      end tell
EOF
  else
    osascript &>/dev/null <<EOF
      tell application "iTerm2"
        create window with profile "Default"
        write text "$CD_CMD"
      end tell
EOF
  fi
else
  osascript<<END
    tell application "iTerm2"
      create window with profile "Default"
      write text "$CD_CMD"
    end tell
END
fi
