Nestview is a web-based viewer for nested data - folder hierarchies, XML, whatever you can represent as a hierarchy of text nodes. If you need an idea of what it looks like, take a look at [Nested](http://orteil.dashnet.org/nested).

### Architecture

Technically, the viewer is just `nestview.html`. On page load, it looks for an array called `dataTree`. You're supposed to throw Nestview trees into the array, and they'll show up as top-level. Conveniently, the viewer already has `dataTree=/* json */;` in it, so all you need to do is search for `/* json */` and replace it with a JSON array.

A Nestview tree is a simple array that looks like this:

	[name, [subtree, ...], [textnode, ...]]

It gets rendered like this:

	- name
		+ subtree name
		+ ...
		textnode
		...

Basically: trees have a name, can contain other trees and text nodes, and can be expanded or collapsed. Just like files and folders on a filesystem.

The second part of Nestview is a Python library, in `nestview.py`. It defines a Folder class, which maps into a Nested tree through the .toTree() method. The trees produced by .toTree() can be passed through json.dumps() to get something to plug into the dataTree array. You instantiate Folder like this:

	Folder(name, [subfolders...], [items...])

The subfolders should be other Folder instances, and items should be strings. Note that you do need to at least pass it empty arrays, at least until I narrow down that weird recursion bug.

The third part of Nestview is NVCommon, a library for creating small tools like nvtree and nvini. It handles common command line arguments and implements things like the HTTP server. Using it involves subclassing NVCommon and overriding a couple of functions:

	def setupArgumentParser(self)
	def generateData(self)

The first one gives you a chance to declare your own argparse arguments, and the second one is expected to return an array of arrays, ready to plug into the viewer as `dataTree`. Just so you get a mental picture:

	[folder1.toTree(), folder2.toTree(), ...]

You can also override `def generateHTML(self, outfile)` and call `nvWrite` from there or something, but that's so 10 minutes ago.

Also see the "Viewing Python data structures" section - in a pinch, you can just use nvToTree() and nvServer() to write your script, and extend it later if you need to.


### Tools

#### nvtree

nvtree is a Python script that uses Nestview to give you a folder tree - a slow and not particularly useful file browser, essentially. Here's a possibly out of date printout of the self-explanatory help message:

	usage: nvtree [-h] [-v] [-q] [-o FILE] [-O] [-a] [-s [PORT]]
              [-e EXCLUDE [EXCLUDE ...]]
              [DIRECTORY]

	A directory tree viewer for Nestview.

	positional arguments:
	  DIRECTORY             the directory to list

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -q, --quiet           don't print progress messages
	  -o FILE, --outfile FILE
	                        the HTML file to output to (overwrites contents)
	  -O, --open            save file to a temporary location and open it in
	                        browser
	  -a, --autodelete      automatically deletes temporary files after 3 seconds
	  -s [PORT], --server [PORT]
	                        run a web server on a given port (default 8000)
	  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
	                        filename substrings to exclude from the listing

Overkill? Probably. But I can do `nvtree -qs` and browse folders from my phone now. Or `nvtree -Oqa` and have Chrome open up. Or `nvtree -Oqs` and do both, because why not.

Note: just don't do it on really densely nested folders, at least not on Windows. And beware of symlinks. And use -e to exclude things like `.git` folders. (Although Chrome seems to cope well with displaying my massive home folder even on low-end hardware, it takes a bloody long time for nvtree to go through it.)

#### nvini

nvini is really just a toy written as a test for NVCommon. You feed it a ConfigParser-supported INI file as an argument - or pipe it in - and it Nestviews it. (Not that there's a lot of nesting in an INI file.) You can output the HTML viewer to a file, or open it directly, or run a web server, whatever nvtree can do.

#### nvxml

Throw it an XML file (or an HTML file and the `--html` command line option) and it'll turn it into a Nestview tree. You can use `-T` to make things a bit more readable, or pass it a URL and `-u` to automatically download a file.


### Viewing Python data structures

`nvcommon.py` includes a few functions that let you convert simple Python objects like strings, dicts, lists and objects into a Nestview tree and view it, straight from an interactive console. To wit:

	from nvcommon import nvServer, nvToTree
	test = [1, [2, 3], {4: [5, 6]}]
	nvServer(nvToTree(test))

Just don't try to view things where order is important - right now, expandable items are listed first in the viewer (a consequence of how the data structures are defined).


### Build procedure

*Note: I've changed nestview.py so this is no longer needed, for now*

Since in Europe we're too poor to afford Makefiles and node.js, the `nestview.html` file needs to be minified manually for now. Basically, throw it into [this generic but excellent HTML minifier](http://kangax.github.io/html-minifier/) and paste the results into `nestview.min.html`.

Or just `cp nestview.html nestview.min.html` if you have better things to do. Minification isn't a particularly big reduction.


### Things to do

* write more tools! how about a reddit client?
* split `nestview.html` into 3 files and get a build system working
* figure out ways to make getting data into the viewer easier
* set git up and push all of this crap onto GitHub so I can have docs and bug tracking like a normal human being
* interactivity? we do have a web server
* make the viewer embeddable
* change the data structures so ordering is maintained


### Things I already did

* wrote the HTML/JS viewer and Python backend
* gave the viewer nice expand/collapse links
* made the viewer work on mobile
* refactored everything several times so we can have nice abstractions
* wrote a tool for viewing the filesystem
* integrated an HTTP server into said tool
* ripped out the DRY-prone parts out of said tool, including HTTP server, and turned them into a library so I can build other tools with HTTP servers
* used said library to write an INI viewer that worked on the first try
* implemented proper filtering in the viewer - it kicks ass
* wrote a tool for viewing XML (and HTML)
* implemented functions in nvcommon to make Nestview usable from an interactive Python console