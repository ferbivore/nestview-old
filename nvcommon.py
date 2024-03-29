#!/usr/bin/env python
from __future__ import print_function
from argparse import ArgumentParser
from nvbase import Folder, nvWrite, nvToTree, nvToFolder
import sys, os, io
nvVersion = "0.4"

# this is a common base for all the Nestview utils.
# it handles argument parsing and all that crap.
# look at NVCommon to get started.

# try to open a link/file with cygstart, xdg-open or open
def openLink(link, fatal=False):
	from subprocess import call
	print("Attempting to open: %s" % link, file=sys.stderr)
	# note: keep cygstart first
	# for some reason, xdg-open doesn't register as missing on my setup
	for cmd in ["cygstart", "xdg-open", "open"]:
		try:
			call([cmd, link])
			return
		except OSError:
			pass
	if fatal:
		raise OSError("openLink: unable to find any of the required commands")
	else:
		print("openLink: unable to find any of the required commands", file=sys.stderr)

# base class for utils. subclass and maybe override these methods:
#  setupArgumentParser() - use self.parser.add_argument(...) in it
#  generateData() - return an array of Nestview trees (3-element arrays)
#  setupFinal() - runs after parsing arguments but before HTML generation

# legacy but still overrideable:+
#  generateHTML(outfile)

class NVCommon():
	def __init__(self, name="NVCommon", version=nvVersion, description=None):
		# instance variables
		self.name = name
		self.version = version
		self.description = description
		# set up argument parser
		self.parser = ArgumentParser(description=description)
		versionstring = "%s %s, a utility for Nestview (%s)" % (name, version, nvVersion)
		self.parser.add_argument("-v", "--version",
			action="version", version=versionstring)
		self.parser.add_argument("-q", "--quiet", action="store_true",
			help="don't print progress messages")
		self.parser.add_argument("-o", "--outfile", metavar="FILE",
			help="an HTML file to output to (overwrites contents)")
		self.parser.add_argument("-O", "--open", action="store_true",
			help="save file to a temporary location and open it in browser")
		self.parser.add_argument("-a", "--autodelete", action="store_true",
			help="automatically deletes temporary files after 3 seconds")
		self.parser.add_argument("-s", "--server",
			type=int, const=8000, metavar="PORT", nargs="?",
			help="run a web server on a given port (default 8000)")
		# run a user-defined function to set up other arguments
		self.setupArgumentParser()
		# parse the arguments to construct self.args
		self.args = self.parser.parse_args()
		# things to do after parsing arguments
		self.setupFinal()

	def run(self, server=False, server_port=8000, autoopen=False, autodelete=False, outfile=None):
		# run the program in one of the three modes
		# (HTTP server, temporary file or normal)
		if self.args.server or server:
			from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
			from cStringIO import StringIO

			data = StringIO()
			self.generateHTML(outfile=data)

			class NVHandler(BaseHTTPRequestHandler):
				def do_GET(self):
					self.send_response(200)
					self.send_header("Content-Type", "text/html")
					self.end_headers()
					self.wfile.write(data.getvalue())
					return

			print("Starting HTTP server on port " + str(server_port) + "...", file=sys.stderr)
			try:
				if self.args.server:
					server_port = self.args.server
				httpd = HTTPServer(("", server_port), NVHandler)
				print("Server started. Use Ctrl-C to shut down.", file=sys.stderr)
				if(self.args.open or autoopen):
					openLink("http://127.0.0.1:" + str(server_port))
				httpd.serve_forever()
			except KeyboardInterrupt:
				httpd.socket.close()
				print("Server stopped.", file=sys.stderr)

		elif self.args.open or autoopen:
			import tempfile, subprocess
			from time import sleep

			with tempfile.NamedTemporaryFile(mode="w+", suffix=".html") as f:
				self.generateHTML(outfile=f)
				f.flush() # required because we're not closing the file yet
				openLink(f.name, fatal=True)
				if self.args.autodelete or autodelete:
					sleep(3)
				else:
					raw_input("Press Enter to delete the file after it loads.")

		else:
			if(self.args.outfile):
				outfile = self.args.outfile
			if(outfile == None):
				self.generateHTML()
			else:
				if(isinstance(outfile, file)):
					self.generateHTML(outfile=outfile)
				else:
					with io.open(outfile, "w", encoding="utf-8") as f:
						self.generateHTML(outfile=f)

	def generateHTML(self, outfile=sys.stdout):
		nvWrite(self.generateData(), outfile)

	def setupArgumentParser(self):
		pass
	def generateData(self):
		pass
	def setupFinal(self):
		pass

class NVSimple(NVCommon):
	def __init__(self, *data, **kwargs):
		# kwargs is used mainly for maxdepth
		self.datatree = nvToTree(*data, **kwargs)
		NVCommon.__init__(self, "NVSimple")
	def generateData(self):
		return self.datatree
	def serve(self, port=8000, autoopen=False):
		self.run(server=True, server_port=port, autoopen=autoopen)
	def open(self):
		self.run(autoopen=True)
	def save(self, outfile=sys.stdout):
		self.run(outfile=outfile)