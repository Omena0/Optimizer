import subprocess as s
import ctypes, os
from contextlib import suppress
from time import sleep
import os

try:
    is_admin = os.getuid() == 0
except AttributeError:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin:
    print('\n####################\nYou need admininstrator permissions to kill most processes.')
    print('Please run this from elevated cmd.\n####################\n')

chars = ' '+'\n'+'\r'+"'"+'"'

optional = [
    'taskhostw','services','registry','trustedinstaller','textinputhost',
    'runtimebroker','regsrvc','fontdrvhost'
]

def get_whitelist():
    global whitelist
    try:
        with open('whitelist.txt') as file: whitelist = file.read().split('\n')
    except Exception:
        with open('whitelist.txt','w') as file: file.write('') 
    return whitelist

sysProc = [
    'winlogon','wininit','cmd','optimize','audiodg','powershell','dwm',
    'smss','csrss','vmmem','lsass','RuntimeBroker','explorer'
]

def get_processes():
    whitelist = get_whitelist()
    out = s.check_output('powershell /c Get-Process | Format-Table ProcessName -HideTableHeaders')

    out = str(out).strip().replace(' ','').split('\\r\\n')

    processes = []
    for i in out:
        i = i.strip(chars)
        if i in ['','b']: continue
        if i.lower() in sysProc: continue
        if 'service' in i.lower(): continue
        if 'host' in i.lower(): continue
        if 'system' in i.lower(): continue
        if i in whitelist: continue
        processes.append(i)
    
    return processes
    
processes = get_processes()
print(f'Processes fetched.\nFound {len(processes)} Processes\n')

commands = ["max", "normal", "norm", "manual", "list", "refresh", "auto", "help"]

def getCommand() -> str:
    command = input('> ').lower()
    if command == '': command = 'normal'
    
    if command not in commands:
        print('Invalid command.')
        return getCommand()
    return command

def main():
    global processes
    cmd = getCommand()
    killed = 0
    failed = 0
    if cmd == 'max':
        for proc in processes:
            try: s.check_output(f'taskkill /t /f /im {proc}.exe')
            except Exception: 
                print(f'Failed to kill {proc}.exe')
                failed += 1
                continue
            print(f'Killed process {proc}.exe')
            killed += 1

    elif cmd in ['normal', 'norm', '']:
        for proc in processes:
            if proc in optional: continue # Dont kill optional processes
            try: s.check_output(f'taskkill /t /f /im {proc}.exe')
            except Exception:
                print(f'Failed to kill {proc}.exe')
                failed += 1
                continue
            print(f'Killed process {proc}.exe')
            killed += 1

    elif cmd == 'manual':
        print('Enter process name to kill, or "exit" to quit: ')
        while True:
            proc = input('> ')
            if proc == 'exit': break
            if proc in sysProc:
                print('Killing this process might crash windows.\nAre you sure you want to continue? [y/N]')
                if input('> ').lower() != 'y': continue
            try: s.check_output(f'taskkill /t /f /im {proc}.exe')
            except Exception:
                print(f'Failed to kill {proc}.exe')
                continue
            print(f'Killed process {proc}.exe')

    elif cmd == 'list':
        for i in range(0,len(processes),4):
            with suppress(): print(f'{processes[i]:30}',end='')
            with suppress(): print(f'{processes[i+1]:30}',end='')
            with suppress(): print(f'{processes[i+2]:30}',end='')
            with suppress(): print(f'{processes[i+3]:30}')

    elif cmd == 'refresh':
        processes = get_processes()
        print(f'Processes fetched.\nFound {len(processes)} Processes',end='')

    elif cmd == 'auto':
        try:
            while True:
                processes = get_processes()
                for proc in processes:
                    if proc in whitelist: continue
                    if os.path.exists('log.txt'):
                        with open('log.txt','a') as file: file.write('\n'+proc)
                    try: s.check_output(f'taskkill /t /f /im {proc}.exe',stderr=s.PIPE)
                    except Exception: continue
                    print(f'Killed process {proc}.exe')
                sleep(0.5)
                if os.path.exists('log.txt'):
                        with open('log.txt','w') as file: file.write('')
        except KeyboardInterrupt:
            print('Stopped.')
            return

    elif cmd == 'help': helpMsg()
    
    if cmd in ['max','normal','norm']:
        print('\n\n--- Results ---')
        print(f'Killed {killed}')
        print(f'Failed {failed}',end='')


def helpMsg(): # ["max", "normal", "norm", "manual", "list", "refresh", "auto", "help"]
    print('----- Commands -----')
    print('max     - Kill everything possible')
    print('normal  - Kill almost everything')
    print('manual  - Manually kill processes')
    print('list    - List all non-system non-whitelisted processes')
    print('refresh - Refresh processes and whitelist')
    print('auto    - Automatically execute refresh and max')
    print('help    - Send this help message')
    print('')
    print('----- Extra -----')
    print('WHITELIST: You can add processes to the whitelist by adding the processe\'s name to whitelist.txt')
    print('DEBUG LOG: By creating a log.txt file, you can log all process terminations when using max',end='')
            

print(f'Commands: {', '.join(commands).strip(',')} (Default: Normal)')
print('Enter Command:\n')

while True:
    try: main()
    except Exception as e: pass
    print('\n\n')
