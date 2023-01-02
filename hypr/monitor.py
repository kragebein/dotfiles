#!/usr/bin/env python3

# Watches Hyprland socket for monitor changes, and if certain treshholds are met
# we'll update the Hyprland config and change the monitor setup.

import socket
import asyncio
import os
import json
import sys

from typing import Dict

class HyprSocket():
    LAST: str = None

    def __init__(self):
        ''' Checks and sets SOCKET.'''
        try:
            instance = os.environ['HYPRLAND_INSTANCE_SIGNATURE']
            self.SOCKET = f'/tmp/hypr/{instance}/.socket2.sock'
            if not os.path.exists(self.SOCKET):
                raise IOError('Path not found')
        except Exception:
            print('Cannot read socket, HYPRLAND_INSTANCE_SIGNATURE not set.')
            exit(1)

    def express(self, n: str) -> Dict:
        '''Expresses the socket-data as list instead of CSV.'''
        # Socket has a bug that that sometimes will spam socket with the same event.
        if n == self.LAST:
            return None
        self.LAST = n    
        expressed = {
            'event': None,
            'data': []
        }
        
        action = n.split('>>')
        expressed['event'] = action[0]
        if expressed['event'] == 'focusedmon':
            del expressed['data']
            expressed['monitor'] = action[1].split(',')[0]
            expressed['workspace'] = action[1].split(',')[1].strip()
        elif expressed['event'] == 'activewindow':
            del expressed['data']
            expressed['class'] = action[1].split(',')[0]
            expressed['windowName'] = action[1].split(',')[1].strip()
        elif expressed['event'] == 'workspace':
            del expressed['data']
            expressed['changedTo'] = action[1].split(',')[0].strip()
        elif expressed['event'] == 'monitoradded':
            expressed['monitor'] = action[1].split(',')[0].strip()
        else:
            for detail in action[1].split(','):
                expressed['data'].append(detail.strip())
        return expressed

    async def handle(self, n: dict) -> bool:
        ''' Will handle upon actions.'''
        if n is None:
            return
        handles = {
            'activewindow': self.updatetaskbar
        }

        # Pass through to handler.
        if n['event'] in handles:
            await handles[n['event']](n)
        return True


    async def updatetaskbar(self,n: dict) -> None:
        ''' MacOS style taskbar that changes names when you change focus.'''
        window_name = n['windowName']
        classs = n['class']

        waybar = {
            'text': window_name.replace('\u2014', '--'),
            'class': classs,
            'tooltip': 'active window',
        }
        waybar_data = json.dumps(waybar)
        #sys.stderr.write(waybar_data+'\n')
        print(waybar_data)

    async def read(self) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(self.SOCKET)

            while True:
                data = client.recv(1024).decode()
                expressed = self.express(data)
                await self.handle(expressed)
if __name__ == "__main__":
    hyprsock = HyprSocket()
    asyncio.run(
        hyprsock.read()
    )