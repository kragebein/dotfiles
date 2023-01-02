#!/bin/bash

# Enables eDP1 if lid is open, and disables other monitors.
# Else if lid is closed, disable eDP1 and lets kanshi to its thing.

if grep "closed" /proc/acpi/button/lid/LID/state 1>/dev/null 2>/dev/null; then
	echo "Closed"
	hyprctl keyword monitor eDP-1,disable
else
	echo "Open"
	hyprctl keyword monitor eDP-1,preferred,0x0,1
fi
