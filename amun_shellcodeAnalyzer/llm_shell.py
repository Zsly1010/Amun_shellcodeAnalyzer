import json
import os
import socket
import sys
import requests
from openai import OpenAI
from flask import Flask, request

api_base = "https://api.chatanywhere.tech"
api_key = "sk-iALwU7cnvOufvsV9cZray5cac4sXuNDfzveOv93f1Nbv5qWo"
prompt = "You are a shell with system information Linux svr04 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64 GNU/Linux with distribution Debian GNU/Linux 8.11 (jessie), now that you need to simulate a bash shell, your output should look as if you executed this command, and you should not output any other text that is not part of the response of this command"


#用chatgpt模拟shell,获得命令响应
def get_response(message):
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )
    messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": message},
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        #print(response)
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return 0

# 模拟命令的输出
def run_command(command):
    if command == "uname -a":
        return "Linux svr04 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64 GNU/Linux\n"
    elif command == "lsb_release -a":
        return ("No LSB modules are available.\n"
                "Distributor ID: Debian\n"
                "Description:    Debian GNU/Linux 8.11 (jessie)\n"
                "Release:        8.11\n"
                "Codename:       jessie\n")
    elif command == "dpkg --get-selections":
        return ("adduser                                    install\n"
                "apt                                        install\n"
                "base-files                                 install\n"
                "base-passwd                                install\n"
                "bash                                       install\n"
                "bsdutils                                   install\n"
                "coreutils                                  install\n"
                "dash                                       install\n"
                "debconf                                    install\n"
                "debian-archive-keyring                     install\n"
                "dpkg                                       install\n"
                "e2fslibs                                   install\n"
                "e2fsprogs                                  install\n"
                "findutils                                  install\n"
                "gcc-4.9-base                               install\n"
                "gzip                                       install\n"
                "hostname                                   install\n"
                "init                                       install\n"
                "initscripts                                install\n"
                "insserv                                    install\n"
                "libc-bin                                   install\n"
                "libc6                                      install\n"
                "libncurses5                                install\n"
                "libpam-modules                             install\n"
                "libpam-runtime                             install\n"
                "libpam0g                                   install\n"
                "login                                      install\n"
                "lsb-base                                   install\n"
                "makedev                                    install\n"
                "mawk                                       install\n"
                "mount                                      install\n"
                "ncurses-base                               install\n"
                "ncurses-bin                                install\n"
                "perl-base                                  install\n"
                "sed                                        install\n"
                "sensible-utils                             install\n"
                "sysv-rc                                    install\n"
                "sysvinit                                   install\n"
                "sysvinit-utils                             install\n"
                "tar                                        install\n"
                "util-linux                                 install\n"
                "zlib1g                                     install\n")
    elif command == "service --status-all":
        return ("[ + ]  acpid\n"
                "[ + ]  cron\n"
                "[ + ]  dbus\n"
                "[ + ]  exim4\n"
                "[ + ]  kmod\n"
                "[ + ]  networking\n"
                "[ + ]  rsyslog\n"
                "[ + ]  ssh\n"
                "[ + ]  udev\n"
                "[ - ]  procps\n")
    elif command.startswith("cat"):
        filename = command.split(" ")[1]
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return f"cat: {filename}: No such file or directory\n"
    elif command.startswith("ls"):
        command+=" "
        path = command.split(" ")[1]
        if path == "":
            path = "."
        try:
            return " ".join(os.listdir(path)) + "\n"
        except FileNotFoundError:
            return f"ls: cannot access {path}: No such file or directory\n"
    elif command.startswith("cd"):
        path = command.split(" ")[1]
        try:
            os.chdir(path)
            return ""
        except FileNotFoundError:
            return f"bash: cd: {path}: No such file or directory\n"
    elif command == "pwd":
        return f"{os.getcwd()}\n"
    elif command.startswith("echo"):
        return command.split(" ", 1)[1] + "\n"
    elif command == "exit":
        exit()
    elif command == "whoami":
        return "root\n"
    else:
        llm_response = get_response(command)
        if llm_response==0:
            command = command.split(" ")[0]
            return f"bash: {command}: command not found\n"
        return llm_response+'\n'

# 创建模拟的文件和目录结构
def create_files():
    os.makedirs(os.path.join('.', 'etc'), exist_ok=True)
    os.makedirs(os.path.join('.', 'var', 'log'), exist_ok=True)

    with open(os.path.join('.', 'etc', 'issue'), 'w') as f:
        f.write(f"Debian GNU/Linux 8 {os.path.sep}n {os.path.sep}l\n")

    with open(os.path.join('.', 'etc', 'motd'), 'w') as f:
        f.write("The programs included with the Debian GNU/Linux system are free software;\n"
                "the exact distribution terms for each program are described in the\n"
                "individual files in /usr/share/doc/*/copyright.\n"
                "\n"
                "Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent\n"
                "permitted by applicable law.\n")

    with open(os.path.join('.', 'etc', 'passwd'), 'w') as f:
        f.write("root:x:0:0:root:/root:/bin/bash\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                "bin:x:2:2:bin:/bin:/usr/sbin/nologin\n"
                "sys:x:3:3:sys:/dev:/usr/sbin/nologin\n"
                "sync:x:4:65534:sync:/bin:/bin/sync\n"
                "games:x:5:60:games:/usr/games:/usr/sbin/nologin\n"
                "man:x:6:12:man:/var/cache/man:/usr/sbin/nologin\n"
                "lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\n"
                "mail:x:8:8:mail:/var/mail:/usr/sbin/nologin\n"
                "news:x:9:9:news:/var/spool/news:/usr/sbin/nologin\n"
                "uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\n"
                "proxy:x:13:13:proxy:/bin:/usr/sbin/nologin\n"
                "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
                "backup:x:34:34:backup:/var/backups:/usr/sbin/nologin\n"
                "list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\n"
                "irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin\n"
                "gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin\n"
                "nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n")

    with open(os.path.join('.', 'etc', 'shadow'), 'w') as f:
        f.write("root:*:17837:0:99999:7:::\n"
                "daemon:*:17837:0:99999:7:::\n"
                "bin:*:17837:0:99999:7:::\n"
                "sys:*:17837:0:99999:7:::\n"
                "sync:*:17837:0:99999:7:::\n"
                "games:*:17837:0:99999:7:::\n"
                "man:*:17837:0:99999:7:::\n"
                "lp:*:17837:0:99999:7:::\n"
                "mail:*:17837:0:99999:7:::\n"
                "news:*:17837:0:99999:7:::\n"
                "uucp:*:17837:0:99999:7:::\n"
                "proxy:*:17837:0:99999:7:::\n"
                "www-data:*:17837:0:99999:7:::\n"
                "backup:*:17837:0:99999:7:::\n"
                "list:*:17837:0:99999:7:::\n"
                "irc:*:17837:0:99999:7:::\n"
                "gnats:*:17837:0:99999:7:::\n"
                "nobody:*:17837:0:99999:7:::\n")

    with open(os.path.join('.', 'etc', 'network', 'interfaces'), 'w') as f:
        f.write("# This file describes the network interfaces available on your system\n"
                "# and how to activate them. For more information, see interfaces(5).\n"
                "\n"
                "# The loopback network interface\n"
                "auto lo\n"
                "iface lo inet loopback\n"
                "\n"
                "# The primary network interface\n"
                "allow-hotplug eth0\n"
                "iface eth0 inet dhcp\n")

    with open(os.path.join('.', 'etc', 'resolv.conf'), 'w') as f:
        f.write("nameserver 8.8.8.8\n"
                "nameserver 8.8.4.4\n")

# 模拟shell交互
def simulated_shell():
    #create_files()
    while True:
        try:
            command = input("$ ")
            output = run_command(command)
            print(output, end="")
        except KeyboardInterrupt:
            print("\nexit")
            break

app = Flask(__name__)

@app.route('/execute', methods=['GET'])
def execute_command_get():
    command = request.args.get('command')
    output = run_command(command)
    return output

def test(command):
    url="http://127.0.0.1:12345/execute"
    params = {
        "command": command
    }
    response = requests.get(url, params=params)
    print(response.text)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)

# if __name__ == "__main__":
#     simulated_shell()
