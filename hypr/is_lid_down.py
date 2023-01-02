
# Checks if lid is closed. If lid is closed, use dual monitor setup
# if lid is open, enable eDP-1
import subprocess
# Read LID state:
if open('/proc/acpi/button/lid/LID/state').read().split(':')[1].strip() == 'closed':
    

    print('closed')
else:
    # Set internal display profile
    print('open')

