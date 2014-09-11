from __future__ import print_function
import json, sys, io, os

class Folder:
	# giving [] as default initializers seems to cause problems
	# (they sometimes inherit values instead, for some reason)
	def __init__(self, name, subfolders, items):
		self.name = name
		self.subfolders = subfolders # Folder instances
		self.items = items # strings

	def add(self, obj):
		if isinstance(obj, Folder):
			self.subfolders.append(obj)
			return self.subfolders[-1]
		elif isinstance(obj, str) or isinstance(obj, unicode):
			self.items.append(obj)

	def toTree(self):
		tree = [self.name]
		for subfolder in self.subfolders:
			tree.append(subfolder.toTree())
		tree.extend(self.items)
		return tree

	def subfolderByName(self, name):
		for subfolder in self.subfolders:
			if(name == subfolder.name):
				return subfolder
		return None

def getDefaultSrc():
	# finds the default template, nestview..min.html
	scriptPath = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(scriptPath, "nestview.min.html")

def nvWrite(tree, file=sys.stdout, src=getDefaultSrc(), pattern="/* json */"):
	# writes a tree into a Nestview HTML template
	with io.open(src, encoding="utf-8") as source:
		print(source.read().replace(pattern, json.dumps(tree)), file=file)