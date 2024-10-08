try:
	import psyco ; psyco.full()
	from psyco.classes import *
except ImportError:
	pass

import traceback
import StringIO
import sys
import struct
import amun_logging
import random
import time
import php_shellcodes

class vuln():

	def __init__(self):
		try:
			self.vuln_name = "PHP Vulnerability"
			self.stage = "PHP_STAGE1"
			self.welcome_message = ""
			self.shellcode = []
		except KeyboardInterrupt:
			raise

	def getVulnName(self):
		return self.vuln_name

	def getCurrentStage(self):
		return self.stage

	def getWelcomeMessage(self):
		return self.welcome_message

	def incoming(self, message, bytes, ip, vuLogger, random_reply, ownIP):
		try:
			### logging object
			self.log_obj = amun_logging.amun_logging("vuln_php", vuLogger)
			
			self.reply = php_shellcodes.defaultReply

			resultSet = {}
			resultSet["vulnname"] = self.vuln_name
			resultSet["accept"] = False
			resultSet["result"] = False
			resultSet["shutdown"] = False
			resultSet["reply"] = "None"
			resultSet["stage"] = self.stage
			resultSet["shellcode"] = "None"
			resultSet["isFile"] = False

			if self.stage == "PHP_STAGE1" and message.startswith('GET /cmd.php'):
				resultSet["result"] = True
				resultSet["accept"] = True
				header = 'HTTP/1.1 200 OK\r\nServer: Apache/1.3.29 (Unix) PHP/4.3.4\r\nContent-Length: %s\r\nContent-Language: de\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' % (len(php_shellcodes.defaultReply))
				resultSet["reply"] = header+self.reply
				self.shellcode.append(message)
				resultSet["shellcode"] = "".join(self.shellcode)
				self.stage = "SHELLCODE"
				return resultSet
			elif self.stage == "PHP_STAGE1" and bytes==1024:
				resultSet["result"] = True
				resultSet["accept"] = True
				header = 'HTTP/1.1 200 OK\r\nServer: Apache/1.3.29 (Unix) PHP/4.3.4\r\nContent-Length: %s\r\nContent-Language: de\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' % (len(php_shellcodes.defaultReply))
				resultSet["reply"] = header+self.reply
				self.shellcode.append(message)
				self.stage = "SHELLCODE"
				return resultSet
			elif self.stage == "SHELLCODE":
				if bytes>0:
					#print "Shellcode Stage (Bytes: %s)" % (bytes)
					resultSet["result"] = True
					resultSet["accept"] = True
					resultSet['reply'] = "None"
					self.shellcode.append(message)
					self.stage = "SHELLCODE"
					return resultSet
				else:
					resultSet["result"] = False
					resultSet["accept"] = True
					resultSet["reply"] = "None"
					self.shellcode.append(message)
					resultSet["shellcode"] = "".join(self.shellcode)
					return resultSet
            		else:
			    	resultSet["result"] = True
				resultSet["accept"] = True
				header = 'HTTP/1.1 404 Not Found\r\nServer: Apache/1.3.29 (Unix) PHP/4.3.4\r\nContent-Length: %s\r\nContent-Language: de\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' % (len(php_shellcodes.badRequest))
				resultSet["reply"] = header+php_shellcodes.badRequest
            		return resultSet
		except KeyboardInterrupt:
			raise
		except StandardError, e:
			print e
		except:
			print "PHP fatal error" 
