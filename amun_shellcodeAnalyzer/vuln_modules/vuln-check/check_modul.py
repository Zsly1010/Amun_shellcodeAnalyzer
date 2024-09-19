"""
[Amun - low interaction honeypot]
Copyright (C) [2014]  [Jan Goebel]

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>
"""

try:
    import psyco
    psyco.full()
    from psyco.classes import *
except ImportError:
    pass

import struct
import random
import hashlib
import os
import traceback
import StringIO
import sys
import amun_logging
import requests

class vuln:
    def __init__(self):
        try:
            self.vuln_name = "CHECK Vulnerability"
            self.stage = "CHECK_STAGE1"
            self.shellcode = []
            self.randomNumber_dir = random.randint(255, 5100)
            self.randomNumber_net = random.randint(255, 5100)
            self.randomAttackerPort = random.randint(49152, 65535)
            self.computerName = "DESKTOP-%i" % (random.randint(255, 5100))
            self.randomNumber = random.randint(255, 5100)
            self.defaultGW = "192.168.1.1"
            self.ownIP = "192.168.1.%d" % random.randint(2, 254)  # Generate a random IP for the honeypot
            self.log_obj = amun_logging.amun_logging("vuln_check")                
            self.system_type = None
            self.prompt = None
            
            self.welcome_message = 'telnet'

        except KeyboardInterrupt:
            raise

    def write_hexdump(self, shellcode=None, extension=None):
        if not shellcode:
            hash = hashlib.sha("".join(self.shellcode))
        else:
            hash = hashlib.sha("".join(shellcode))
        if extension != None:
            filename = "hexdumps/%s-%s.bin" % (extension, hash.hexdigest())
        else:
            filename = "hexdumps/%s.bin" % (hash.hexdigest())
        if not os.path.exists(filename):
            fp = open(filename, 'a+')
            if not shellcode:
                fp.write("".join(self.shellcode))
            else:
                fp.write("".join(shellcode))
            fp.close()
            print ".::[Amun - CHECK] no match found, writing hexdump ::."
        return

    def print_message(self, data):
        print "\n"
        counter = 1
        for byte in data:
            if counter == 16:
                ausg = hex(struct.unpack('B', byte)[0])
                if len(ausg) == 3:
                    list = str(ausg).split('x')
                    ausg = "%sx0%s" % (list[0], list[1])
                    print ausg
                else:
                    print ausg
                counter = 0
            else:
                ausg = hex(struct.unpack('B', byte)[0])
                if len(ausg) == 3:
                    list = str(ausg).split('x')
                    ausg = "%sx0%s" % (list[0], list[1])
                    print ausg,
                else:
                    print ausg,
            counter += 1
        print "\n>> Incoming Codesize: %s\n\n" % (len(data))

    def getVulnName(self):
        return self.vuln_name

    def getCurrentStage(self):
        return self.stage

    def getWelcomeMessage(self):
        return self.welcome_message

    def incoming(self, message, bytes, ip, vuLogger, random_reply, ownIP, system_type):
        try:
            self.log_obj = amun_logging.amun_logging("vuln_check", vuLogger)
            self.reply = random_reply[:62]
            self.system_type = system_type
            
            resultSet = {}
            resultSet['vulnname'] = self.vuln_name
            resultSet['result'] = False
            resultSet['accept'] = False
            resultSet['shutdown'] = False
            resultSet['reply'] = "None"
            resultSet['stage'] = self.stage
            resultSet['shellcode'] = "None"
            resultSet["isFile"] = False

            if self.stage == "CHECK_STAGE1":
                if message == "":
                    resultSet['result'] = True
                    resultSet['accept'] = True
                    resultSet['reply'] = self.welcome_message
                    self.stage = "SHELL"
                    return resultSet
                elif message.rfind('USER') != -1:
                    resultSet['result'] = True
                    resultSet['accept'] = True
                    resultSet['reply'] = "login without authentication\n\nsolaris#"
                    self.stage = "CHECK_STAGE1"
                    return resultSet
                elif bytes == 3:
                    resultSet['result'] = True
                    resultSet['accept'] = True
                    resultSet['reply'] = "login without authentication\n\nsolaris#"
                    self.stage = "CHECK_STAGE1"
                    return resultSet
                elif message.rfind('quit') != -1 or message.rfind('exit') != -1 or message.rfind('QUIT') != -1 or message.rfind('EXIT') != -1:
                    resultSet['result'] = True
                    resultSet['accept'] = False
                    resultSet['reply'] = "command unknown\n\nsolaris#"
                    self.stage = "CHECK_STAGE1"
                    return resultSet
                else:
                    if bytes > 0:
                        self.log_obj.log("CHECK (%s) Incoming: %s (Bytes: %s)" % (ip, message, bytes), 6, "debug", True, True)
                    resultSet['result'] = True
                    resultSet['accept'] = True
                    resultSet['reply'] = self.handle_command(message)
                    self.stage = "CHECK_STAGE1"
                    return resultSet
            elif self.stage == "SHELLCODE":
                if bytes > 0:
                    print "CHECK Collecting Shellcode"
                    resultSet['result'] = True
                    resultSet['accept'] = True
                    resultSet['reply'] = "None"
                    self.shellcode.append(message)
                    self.stage = "SHELLCODE"
                    return resultSet
                else:
                    print "CHECK finished Shellcode"
                    resultSet['result'] = False
                    resultSet["accept"] = True
                    resultSet['reply'] = "None"
                    self.shellcode.append(message)
                    resultSet['shellcode'] = "".join(self.shellcode)
                    return resultSet
            else:
                resultSet["result"] = False
                resultSet["accept"] = False
                resultSet["reply"] = "None"
                return resultSet
            return resultSet
        except KeyboardInterrupt:
            raise
        except StandardError as e:
            print e
            f = StringIO.StringIO()
            traceback.print_exc(file=f)
            print f.getvalue()
            sys.exit(1)

    def handle_command(self, message):
        data = message.strip()
        response = ""
        
        if self.system_type == 'Windows':
            self.prompt = 'C:\\WINNT\\System32>'
        else:
            self.prompt = '[root@localhost ~]#'
        
        if data == "":
            return self.prompt
        
        if data == "exit":
            return "Exiting..."
        
        url="http://127.0.0.1:12345/execute"
        params = {
            "command": data
        }
        response = requests.get(url, params=params).text

        # if self.system_type == 'Windows':
        #     if data.startswith('cd'):
        #         self.changeDirectory(data)
        #         response = self.prompt
        #     elif data.startswith('netstat'):
        #         response = self.netstat(data)
        #     elif data.startswith('net '):
        #         response = self.net(data)
        #     elif data.startswith('dir'):
        #         response = self.dir(data)
        #     elif data.startswith('ipconfig'):
        #         response = self.ipconfig(data)
        #     else:
        #         response = "{0} is not recognized as an internal or external command,\noperable program or batch file".format(data)
        # else:
        #     if data.startswith('cd'):
        #         self.changeDirectoryLinux(data)
        #         response = self.prompt
        #     elif data.startswith('netstat'):
        #         response = self.netstatLinux(data)
        #     elif data.startswith('ls'):
        #         response = self.ls(data)
        #     elif data.startswith('ifconfig'):
        #         response = self.ifconfig(data)
        #     else:
        #         response = "{0}: command not found".format(data)
        
        return "{0}\n{1}".format(response, self.prompt)

    def dir(self, data):
        reply = ""
        if data == "dir":
            reply = ("\n Volume in drive C has no label.\n"
                    " Volume Serial Number is %04X-%04X\n\n"
                    " Directory of C:\\WINNT\\System32\n\n") % (random.randint(0, 0xFFFF), random.randint(0, 0xFFFF))
            reply += "06/11/2007  05:01p    <DIR>\t\t.\n"
            reply += "06/11/2007  05:01p    <DIR>\t\t..\n"
            reply += "               0 File(s)\t\t0 bytes\n"
            reply += "               2 Dir(s)\t1,627,193,344 bytes free\n\n"
        return reply

    def net(self, data):
        reply = ""
        if data == "net user":
            reply = "\nUser accounts for \\\\%s\n\n" % (self.computerName)
            reply += "--------------------------------------------------------------------------------\n"
            reply += "admin\t\t\tAdministrator\t\t\tGuest\n"
            reply += "HelpAssistant\t\tSUPPORT_%ia0\n" % (self.randomNumber)
            reply += "The command completed successfully\n\n"
        return reply

    def netstat(self, data):
        reply = ""
        if data == "netstat -anp tcp" or data == "netstat -nap tcp":
            reply = "\nActive Connections\n\n  Proto  Local Address          Foreign Address        State\n"
            reply += "  TCP    0.0.0.0:21             0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:25             0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:110            0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:443            0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:%i             0.0.0.0:0              LISTENING\n" % (self.randomAttackerPort)
            reply += "  TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:6667           0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:10000          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:24800          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    0.0.0.0:33890          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:110          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:143          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:389          0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:5000         0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:8080         0.0.0.0:0              LISTENING\n"
            reply += "  TCP    127.0.0.1:8888         0.0.0.0:0              LISTENING\n\n"
        return reply

    def changeDirectory(self, data):
        data = data.split()
        if len(data) > 1:
            directory = data[1]
            if directory == "..":
                if self.prompt.count("\\") > 1:
                    self.prompt = "\\".join(self.prompt.split("\\")[:-2]) + ">"
            elif directory.startswith("\\"):
                self.prompt = "C:" + directory + ">"
            else:
                if self.prompt.endswith("\\"):
                    self.prompt = self.prompt[:-1] + directory + ">"
                else:
                    self.prompt = self.prompt + "\\" + directory + ">"
        else:
            self.prompt = "C:\\>"

    def ipconfig(self, data):
        reply = "Windows IP Configuration\n\n"
        reply += "Ethernet adapter Local Area Connection 3:\n\n"
        reply += "\tConnection-specific DNS Suffix  . :\n"
        reply += "\tIP Address. . . . . . . . . . . . : %s\n" % (self.ownIP)
        reply += "\tSubnet Mask . . . . . . . . . . . : 255.255.255.0\n"
        reply += "\tDefault Gateway . . . . . . . . . : %s\n" % (self.defaultGW)
        return reply

    # Linux Commands
    def changeDirectoryLinux(self, data):
        data = data.split()
        if len(data) > 1:
            directory = data[1]
            if directory == "..":
                if self.prompt.count("/") > 1:
                    self.prompt = "/".join(self.prompt.split("/")[:-2]) + ">"
            elif directory.startswith("/"):
                self.prompt = directory + ">"
            else:
                if self.prompt.endswith("/"):
                    self.prompt = self.prompt[:-1] + directory + ">"
                else:
                    self.prompt = self.prompt + "/" + directory + ">"
        else:
            self.prompt = "/root>"

    def netstatLinux(self, data):
        reply = ""
        if data == "netstat -an":
            reply = "\nActive Internet connections (servers and established)\nProto Recv-Q Send-Q Local Address           Foreign Address         State       \n"
            reply += "tcp        0      0 0.0.0.0:21              0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:25              0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:110             0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 0.0.0.0:%i              0.0.0.0:*               LISTEN      \n" % (self.randomAttackerPort)
            reply += "tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      \n"
            reply += "tcp        0      0 127.0.0.1:6379          0.0.0.0:*               LISTEN      \n\n"
        return reply

    def ls(self, data):
        reply = ""
        if data == "ls":
            reply = ("total 4\n"
                     "drwxr-xr-x 2 root root 4096 Jun 11 05:01 .\n"
                     "drwxr-xr-x 2 root root 4096 Jun 11 05:01 ..\n")
        return reply

    def ifconfig(self, data):
        reply = "eth0      Link encap:Ethernet  HWaddr 00:0c:29:68:8c:64  \n"
        reply += "          inet addr:%s  Bcast:192.168.1.255  Mask:255.255.255.0\n" % (self.ownIP)
        reply += "          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1\n"
        reply += "          RX packets:0 errors:0 dropped:0 overruns:0 frame:0\n"
        reply += "          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0\n"
        reply += "          collisions:0 txqueuelen:1000 \n"
        reply += "          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)\n"
        reply += "          Interrupt:19 Base address:0x2000 \n\n"
        reply += "lo        Link encap:Local Loopback  \n"
        reply += "          inet addr:127.0.0.1  Mask:255.0.0.0\n"
        reply += "          UP LOOPBACK RUNNING  MTU:16436  Metric:1\n"
        reply += "          RX packets:0 errors:0 dropped:0 overruns:0 frame:0\n"
        reply += "          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0\n"
        reply += "          collisions:0 txqueuelen:0 \n"
        reply += "          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)\n"
        return reply

