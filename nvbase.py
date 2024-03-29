from __future__ import print_function
import json, sys, io, os
from inspect import isfunction, isbuiltin, ismodule
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

def saneRepr(obj):
	return repr(obj).replace("<", "(").replace(">", ")")

def nvToFolder(obj, name=None, maxdepth=30, cdepth=0, maxodepth=3, codepth=0, maxmoduledepth=2):
	# turns a simple Python datatype into a Folder

	# check maximum nesting depth
	# maxdepth is used for everything, maxodepth for objects
	if cdepth > maxdepth:
		return saneRepr(obj)

	# set maxdepth to maxmoduledepth for modules
	if ismodule(obj):
		maxdepth = maxmoduledepth
	
	# get a valid type name to use if we don't have a variable name
	if name == None:
		# yeah, ugly, but Python doesn't give me usable type names
		name = "(" + repr(type(obj)).partition("'")[2].rpartition("'")[0] + ")"
	
	# wrap everything in a try/except block because Python is weird sometimes
	try:
		# test for numbers
		if(hasattr(obj, "__float__")):
			return str(obj)
		# test for strings (TODO: find a more general test)
		# also TODO: figure out if unicode strings work at all
		if(isinstance(obj, str) or isinstance(obj, unicode)):
			return obj
		# test for dicts and other dict-like thing
		if(hasattr(obj, "iteritems")):
			folder = Folder(name, [])
			for key, val in obj.iteritems():
				valToFolder = nvToFolder(val, key, maxdepth, cdepth+1, maxodepth, codepth)
				# if(isinstance(val, str) or isinstance(val, unicode)):
				# 	folder.add(key + " = " + val)
				# elif(hasattr(val, "__float__")):
				# 	folder.add(key + " = " + str(val))
				# else:
				# 	folder.add(nvToFolder(val, key))
				if(isinstance(valToFolder, str) or isinstance(valToFolder, unicode)):
					folder.add(str(key) + " = " + valToFolder)
				elif(isinstance(valToFolder, Folder)):
					folder.add(valToFolder)
				else:
					folder.add(Folder(key, [valToFolder]))
			return folder
		# test for lists et al.
		if(hasattr(obj, "__iter__")):
			folder = Folder(name, [])
			for thing in obj:
				folder.add(nvToFolder(thing, None, maxdepth, cdepth+1, maxodepth, codepth))
			return folder
		# objects
		if(hasattr(obj, "__dict__") and (not isfunction(obj)) and (not isbuiltin(obj))):
			# see if we've reached maximum object nesting depth
			if codepth > maxodepth:
				return saneRepr(obj)
			# if we haven't reached maxdepth...
			oname = repr(obj).replace("<", "(").replace(">", ")")
			return nvToFolder(obj.__dict__, oname, maxdepth, cdepth+1, maxodepth, codepth+1)
	except TypeError:
		pass
	except IOError:
		pass
	return saneRepr(obj)

def nvToTree(*args, **kwargs):
	# turns a simple Python datatype (or a few) into a Nestview data tree
	# ready to plug into nvcommon.nvStartServer
	datatree = []
	for obj in args:
		# arguments (ie. maxdepth) are passed to nvToFolder
		fo = nvToFolder(obj, **kwargs)
		if isinstance(fo, Folder):
			datatree.append(fo.toTree())
		else:
			datatree.append(fo)
	return datatree