#!/usr/bin/env python3

"""
Script to configure system-wide proxy settings on Linux distributions.

created by:
Nityananda Gohain 
School of Engineering, Tezpur University
27/10/17

Modified by:
Pablo Peitsch
Data Scientist, UNSAM, ARG
"""

# This files takes the location as input and writes the proxy authentication

import getpass
import os
import shutil
import sys

APT_CONF = '/etc/apt/apt.conf'
APT_BACKUP = './.backup_proxy/apt.txt'
BASH_BASHRC = '/etc/bash.bashrc'
BASH_BACKUP = './.backup_proxy/bash.txt'
ENVIRONMENT = '/etc/environment'
ENV_BACKUP = './.backup_proxy/env.txt'


def write_to_apt(proxy, port, username, password, flag):
    """
    Writes the proxy configuration to the apt.conf file.

    :param proxy: Proxy address
    :param port: Proxy port
    :param username: Username for authentication
    :param password: Password for authentication
    :param flag: Flag indicating whether to remove the configuration
    """
    with open(APT_CONF, "w") as filepointer:
        if not flag:
            auth = f"{username}:{password}@" if username and password else ""
            filepointer.write(f'Acquire::http::proxy "http://{auth}{proxy}:{port}/";\n')
            filepointer.write(f'Acquire::https::proxy "https://{auth}{proxy}:{port}/";\n')
            filepointer.write(f'Acquire::ftp::proxy "ftp://{auth}{proxy}:{port}/";\n')
            filepointer.write(f'Acquire::socks::proxy "socks://{auth}{proxy}:{port}/";\n')


def write_to_env(proxy, port, username, password, flag):
    """
    Writes the proxy configuration to the environment file.

    :param proxy: Proxy address
    :param port: Proxy port
    :param username: Username for authentication
    :param password: Password for authentication
    :param flag: Flag indicating whether to remove the configuration
    """
    with open(ENVIRONMENT, "r+") as opened_file:
        lines = opened_file.readlines()
        opened_file.seek(0)
        for line in lines:
            if all(protocol not in line for protocol in ["http://", "https://", "ftp://", "socks://"]):
                opened_file.write(line)
        opened_file.truncate()

    if not flag:
        with open(ENVIRONMENT, "a") as filepointer:
            auth = f"{username}:{password}@" if username and password else ""
            filepointer.write(f'http_proxy="http://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'https_proxy="https://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'ftp_proxy="ftp://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'socks_proxy="socks://{auth}{proxy}:{port}/"\n')


def write_to_bashrc(proxy, port, username, password, flag):
    """
    Writes the proxy configuration to the bash.bashrc file.

    :param proxy: Proxy address
    :param port: Proxy port
    :param username: Username for authentication
    :param password: Password for authentication
    :param flag: Flag indicating whether to remove the configuration
    """
    with open(BASH_BASHRC, "r+") as opened_file:
        lines = opened_file.readlines()
        opened_file.seek(0)
        for line in lines:
            if all(protocol not in line for protocol in ["http://", "https://", "ftp://", "socks://"]):
                opened_file.write(line)
        opened_file.truncate()

    if not flag:
        with open(BASH_BASHRC, "a") as filepointer:
            auth = f"{username}:{password}@" if username and password else ""
            filepointer.write(f'export http_proxy="http://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'export https_proxy="https://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'export ftp_proxy="ftp://{auth}{proxy}:{port}/"\n')
            filepointer.write(f'export socks_proxy="socks://{auth}{proxy}:{port}/"\n')


def write_to_snap(proxy, port, username, password, flag):
    """
    Writes the proxy configuration to Snap.

    :param proxy: Proxy address
    :param port: Proxy port
    :param username: Username for authentication
    :param password: Password for authentication
    :param flag: Flag indicating whether to remove the configuration
    """
    if flag:
        os.system("snap set system proxy.http=''")
        os.system("snap set system proxy.https=''")
    else:
        auth = f"{username}:{password}@" if username and password else ""
        os.system(f"snap set system proxy.http=http://{auth}{proxy}:{port}")
        os.system(f"snap set system proxy.https=http://{auth}{proxy}:{port}")


def write_to_git(proxy, port, username, password, flag):
    """
    Writes the proxy configuration to Git.

    :param proxy: Proxy address
    :param port: Proxy port
    :param username: Username for authentication
    :param password: Password for authentication
    :param flag: Flag indicating whether to remove the configuration
    """
    if flag:
        os.system("git config --global --unset http.proxy")
        os.system("git config --global --unset https.proxy")
    else:
        auth = f"{username}:{password}@" if username and password else ""
        os.system(f"git config --global http.proxy http://{auth}{proxy}:{port}")
        os.system(f"git config --global https.proxy https://{auth}{proxy}:{port}")


def select_proxies():
    """
    Allows the user to select which proxies to configure.
    """
    options = {
        'apt': True,
        'env': True,
        'bashrc': True,
        'snap': True,
        'git': True
    }

    while True:
        print("\nSelect which proxies to configure (toggle selection with numbers):")
        for i, (key, value) in enumerate(options.items(), 1):
            print(f"{i}. {'[x]' if value else '[ ]'} {key.capitalize()} Proxy")
        print(f"{len(options) + 1}. Confirm selection")

        try:
            choice = int(input("\nToggle selection (1-5) or confirm (6): "))
            if 1 <= choice <= len(options):
                key = list(options.keys())[choice - 1]
                options[key] = not options[key]
            elif choice == len(options) + 1:
                return options
            else:
                print("\nInvalid choice. Please choose a valid option.")
        except ValueError:
            print("\nInvalid input. Please enter a number between 1 and 6.")


def set_proxy(flag):
    """
    Sets or removes the proxy configuration.

    :param flag: Flag indicating whether to remove the configuration
    """
    proxy, port, username, password = "", "", "", ""
    if not flag:
        proxy = input("Enter proxy: ")
        port = input("Enter port: ")
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

    write_to_apt(proxy, port, username, password, flag)
    write_to_env(proxy, port, username, password, flag)
    write_to_bashrc(proxy, port, username, password, flag)
    write_to_snap(proxy, port, username, password, flag)
    write_to_git(proxy, port, username, password, flag)


def view_proxy():
    """
    Displays the current proxy configuration.
    """
    if os.path.getsize(APT_CONF):
        with open(APT_CONF, "r") as filepointer:
            line = filepointer.readline()
            if "@" in line:
                print('\nHTTP Proxy:', line[line.rfind('@') + 1:line.rfind(':')])
                print('Port:', line[line.rfind(':') + 1:line.rfind('/')])
                print('Username:', line.split('://')[1].split(':')[0])
                print('Password:', '*' * len(line[line.rfind(':', 0, line.rfind('@')) + 1:line.rfind('@')]))
            else:
                print('HTTP Proxy:', line[line.rfind('http'):line.rfind(':')])
                print('Port:', line[line.rfind(':') + 1:line.rfind('/')])
    else:
        print("\nNo proxy is set")


def restore_default():
    """
    Restores the proxy configuration to the default state.
    """
    shutil.copy(APT_BACKUP, APT_CONF)
    shutil.copy(ENV_BACKUP, ENVIRONMENT)
    shutil.copy(BASH_BACKUP, BASH_BASHRC)


def main():
    """
    Main function that handles the program flow.
    """
    if not os.path.isdir("./.backup_proxy"):
        os.makedirs("./.backup_proxy")
        if os.path.isfile(APT_CONF):
            shutil.copyfile(APT_CONF, APT_BACKUP)
        shutil.copyfile(ENVIRONMENT, ENV_BACKUP)
        shutil.copyfile(BASH_BASHRC, BASH_BACKUP)

    menu_options = {
        1: 'Set Proxy',
        2: 'Remove Proxy',
        3: 'View Current Proxy',
        4: 'Restore Default',
        5: 'Select Proxies to Configure',
        6: 'Exit'
    }

    actions = {
        1: lambda: set_proxy(flag=0),
        2: lambda: set_proxy(flag=1),
        3: view_proxy,
        4: restore_default,
        6: sys.exit
    }

    selected_proxies = {
        'apt': True,
        'env': True,
        'bashrc': True,
        'snap': True,
        'git': True
    }

    while True:
        print("\nPlease run this program as Super user (sudo)\n")
        for key in sorted(menu_options):
            print(f"{key}. {menu_options[key]}")

        try:
            choice = int(input("\nChoose an option (1, 2, 3, 4, 5, or 6) and then press ENTER: "))
            if choice == 5:
                selected_proxies = select_proxies()
            elif choice in actions:
                actions[choice]()
                if choice == 6:
                    break
            else:
                print("\nInvalid choice. Please choose a valid option.")
        except ValueError:
            print("\nInvalid input. Please enter a number between 1 and 6.")

        print("\nDONE!\n")


if __name__ == "__main__":
    main()
