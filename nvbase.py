from __future__ import print_function
import json, sys, io, os
nvVersion = "0.4"

class Folder:
	def __init__(self, name, *args):
		self.name = name
		self.subitems = []
		for arg in args:
			self.subitems.extend(arg)

	def add(self, obj):
		self.subitems.append(obj)
		return self.subitems[-1]

	def toTree(self):
		# returns a Nestview tree - an array of arrays and strings
		tree = [self.name]
		for subitem in self.subitems:
			# folders get .toTree()d and appended to the tree
			if isinstance(subitem, Folder):
				tree.append(subitem.toTree())
			# strings get appended directly to the tree
			elif isinstance(subitem, str) or isinstance(subitem, unicode):
				tree.append(subitem)
		return tree

	def subfolders(self):
		# returns all immediate subfolders in an array
		subfolders = []
		for subitem in self.subitems:
			if isinstance(subitem, Folder):
				subfolders.append(subitem)
		return subfolders

	def textitems(self):
		# returns all immediate string subitems
		textitems = []
		for subitem in self.subitems:
			if isinstance(subitem, str) or isinstance(subitem, unicode):
				textitems.append(subitem)
		return textitems

def getDefaultSrc():
	# finds the default template, nestview..min.html
	scriptPath = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(scriptPath, "nestview.html")

def nvWrite(tree, file=sys.stdout, src=getDefaultSrc(), pattern="/* json */"):
	# writes a tree into a Nestview HTML template
	with io.open(src, encoding="utf-8") as source:
		print(source.read().replace(pattern, json.dumps(tree)), file=file)