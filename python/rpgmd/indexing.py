# Macros to handle a directory index

import logging, os

from .core import *
from .linking import NamespaceMacro

class IndexMacro(FileMacro):
	'''Macro to create an index macro

	Attributes:
		- items (list<NamespaceMacro>): The import macros to the files under the
			index
		- index (Path): The absolute path to this document's index
	'''

	TAG = 'index'

	@staticmethod
	def makeMacro(title, items, index, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title to display for this document
			- items (list<str>): The relative paths to the modules to include
				under this index, in the order they are specified. Items should
				be separated by commas (',')
			- index (Path|str|None): The path to this item's index, or None if
				no index should be used
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Only specify an items_string if we have items
		items_string = None
		if not items is None and len(items) > 0:
			items_string = ''
		# Populate the items string with items and delimeters
		for item in items:
			items_string += item + ','
		# Cut off the last comma delimeter
		if not items is None:
			items_strimg = items_strimg[:-1]

		# Get the index string
		indexstr = None
		if not index is None:
			indexstr = str(index)

		# Make the macro
		attrs = [title, items, indexstr]
		macro_text = Macro.makeMacroText(IndexMacro.TAG, attrs)
		return IndexMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			title | items | [index]
		Where
			- title (str): The title to display for this document
			- items (str): The relative paths to the modules to include under
				this index, in the order they are specified. Items should be
				separated by commas (',')
			- index (str): The index containing this document

		Args:
			- text (str): The text (including the containing characters) for the
				macro
			- startline (int): The line the macro starts on
			- startcolumn (int): The character index the macro starts on
			- endline (int): The line the macro ends on
			- endcolumn (int): The character index the macro ends on
			- doc (Document): The document object defining the macro

		Raise:
			- ValueError:
				- The macro spec string contains a badly-formatted attribute
				- Not enough attributes were provided to the macro
			- FileNotFoundError:
				- One of the specified files in the index was not found
				- The provided index was not found
		'''

		# The Macro superclass will parse all of the attributes
		super(IndexMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 2:
			raise MacroError(ValueError, 'Index macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Get the items from the items list string
		self.items = []
		for i,item in enumerate(self.attrs[1].split(',')):
			# Make the import macro
			new_macro = NamespaceMacro.makeMacro('_item{0:d}'.format(i), item, startline, startcolumn, endline, endcolumn, doc, compiled=True)
			# Add it to the document and our import lists 
			doc.addMacro(new_macro)
			self.items.append(new_macro)

		# Make the navbar macro for this item
		self.index = None
		if len(self.attrs) >= 3:
			self.index = Path(self.attrs[2])
			if not self.index.is_absolute():
				self.index = Path(doc.filepath).parent.joinpath(self.index)
			if not self.index.exists():
				raise MacroError(FileNotFoundError, 'Could not find index file "{0:s}"'.format(str(self.index)))

	def compile(self, profile='web', depth=0, path_prefix=Path('.')):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation
			- depth=0 (int): The recursive depth down we have gone in indexing
			- path_prefix=Path('.') (Path): The prefix to prepend to all paths
				output from this function (used for recursive linking)

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		if profile == 'web':
			output = ''

			# Output the navbar if we have an index specified
			if not self.index is None and depth == 0:
				navbar = NavBarMacro.makeMacro(self.title, self.index, self._line, self._column, self._endline, self._endcolumn, self._doc)
				output += navbar.compile(profile)

			# Only output the title if we are at max depth
			if depth == 0:
				output += '<div class="index"><h1>Index</h1>'

			# Create the unordered list for the indexed items
			output += '<ol>'
			for item in self.items:
				# Get the path to the linked item
				link_path = item.getRelPath(profile='web')
				output += '<li>'
				try:
					# Make and parse the document to get the file info for it
					doc = Document(item.path, self._doc.aliases)
					doc.parse()
					# Need to get the file info for the item
					finfo = doc.file_macro
					# Add in the title
					output += '<a href="{0:s}">{1:s}</a>'.format(str(path_prefix.joinpath(link_path)), finfo.title)
					if isinstance(finfo, IndexMacro) and depth < 4:
						output += finfo.compile(profile='web', depth=depth+1, path_prefix=path_prefix.joinpath(link_path).parent)
				except Exception as e:
					# Rethrow (Document-based) exceptions with the information for this macro
					raise MacroError(type(e), str(e))
				output += '</li>'
			output += '</ol>'

			# Close the containing div if we are a root index
			if depth == 0:
				output += "</div>"
			return output
		else:
			raise MacroError(NotImplementedError, 'Anchor macro does not support "{0:s}" profile'.format(profile))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the anchor macro class to the list
addMacroClass(IndexMacro)

class NavBarMacro(FileMacro):
	'''Macro to navigate forwards and backwards in an index

	Attributes:
		- index (tupe<str,NamespaceMacro>): The NamespaceMacro referencing the
			index. The string part of the tuple is the index title
		- nextf (tuple<str,NamespaceMacro>|None): The NamespaceMacro referencing
			the next file in the index (or None if there is no next file). The
			string part of the tuple is the file title
		- prevf (tuple<str,NamespaceMacro>|None): The NamespaceMacro referencing
			the previous file in the index (or None if there is no previous
			file). The string part of the tupe is the file title
	'''

	TAG = 'navbar'

	@staticmethod
	def makeMacro(title, index, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title to display for this document
			- index (Path|str): The relative path to the index to use for
				navigation
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Make the macro
		attrs = [title, str(index)]
		macro_text = Macro.makeMacroText(NavBarMacro.TAG, attrs)
		return NavBarMacro(macro_text, *init_args, **init_kwargs)

	def getFileTitleAndNSM(self, lpath, mname):
		'''Method to create a title, NamespaceMacro tuple for a given document
		file

		Args:
			- lpath (str|Path): The path to the document
			- mname (str): The name of the namespace macro to make

		Return:
			- tuple<str, NamespaceMacro>: The tuple of the title string and the
				created NamespaceMacro
		'''
		# Get the document
		doc = Document(lpath, self._doc.aliases)
		doc.parse()

		# Make the namespace macro to reference the document and return the title, NSM pair
		return (doc.file_macro.title, NamespaceMacro.makeMacro(
			mname, lpath, self._line, self._column, self._endline, self._endcolumn, self._doc, compiled=True))

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			title | index
		Where
			- title (str): The title to display for this document
			- index (str): The relative path to the index to use for navigation

		Args:
			- text (str): The text (including the containing characters) for the
				macro
			- startline (int): The line the macro starts on
			- startcolumn (int): The character index the macro starts on
			- endline (int): The line the macro ends on
			- endcolumn (int): The character index the macro ends on
			- doc (Document): The document object defining the macro

		Raise:
			- ValueError:
				- The macro spec string contains a badly-formatted attribute
				- Not enough attributes were provided to the macro
			- FileNotFoundError:
				- One of the specified files in the index was not found
		'''

		# The Macro superclass will parse all of the attributes
		super(NavBarMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 2:
			raise MacroError(ValueError, 'Navbar macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Get the index
		index_path = Path(self.attrs[1])
		if not index_path.is_absolute():
			index_path = Path(self._doc.filepath).parent.joinpath(index_path)

		# Ensure the index file exists
		if not index_path.exists():
			raise MacroError(FileNotFoundError, 'Could not find the index "{0:s}" linked to by the navbar file macro'.format(str(index_path)))
		self.index_path = index_path

	def compile(self, profile='web'):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
				- The indicated index is not an index macro
			- FileNotFoundError:
				- The provided index cannot be found
				- An file in the provided index cannot be found
		'''
		# Extract the previous, next, and self links
		nextf = None # Relative path to the next file
		prevf = None # Relative path to the previous file
		index = None # Index macro for the index file
		selff = None # Absolute path of self (used to ensure we are in index)

		# Get the index's title, NSM, and 
		try:
			doc = Document(self.index_path, self._doc.aliases)
			doc.parse()
			index = doc.file_macro

			# Make the namespace macro to reference the document and return the title, NSM pair
			self.index = (index.title, NamespaceMacro.makeMacro(
				'_index', self.index_path, self._line, self._column, self._endline, self._endcolumn, self._doc, compiled=True))
		except Exception as e:
			# Rethrow (Document-based) exceptions with the information for this macro
			raise MacroError(type(e), 'Problem parsing index document:\n' + str(e))

		# Ensure we have an index macro from the index file
		if not isinstance(index, IndexMacro):
			raise MacroError(ValueError, 'Index file "{0:s}" does not have an index macro'.format(str(self.index_path)))

		# Iterate through the items in the index macro and determine the previous / self / next items
		for item in index.items:
			# Get the absolute path to the indicated file
			abspath = self.index_path.parent.joinpath(item.relpath).resolve()
			if abspath == Path(self._doc.filepath).resolve():
				selff = abspath
				continue
			if selff is None:
				prevf = abspath
			else:
				nextf = abspath
				break
		# Ensure we found ourselves in the list
		if selff is None:
			raise MacroError(ValueError, 'Navbar could not find self in index "{0:s}"'.format(str(self.index_path)))

		# Get the prevf's title
		self.prevf = None
		if not prevf is None:
			try:
				self.prevf = self.getFileTitleAndNSM(prevf, '_prevf')
			except Exception as e:
				# Rethrow (Document-based) exceptions with the information for this macro
				raise MacroError(type(e), 'Problem parsing previous file document:\n' + str(e))

		# Get the nextf's title
		self.nextf = None
		if not nextf is None:
			try:
				self.nextf = self.getFileTitleAndNSM(nextf, '_nextf')
			except Exception as e:
				# Rethrow (Document-based) exceptions with the information for this macro
				raise MacroError(type(e), 'Problem parsing previous file document:\n' + str(e))


		if profile == 'web':
			# Create the bar div
			output = '<div class="navbar">'

			# Insert the previous link
			output += '<div class="fl link">'
			if not self.prevf is None:
				output += '<a href="{0:s}">{1:s}</a>'.format(self.prevf[1].getRelPath(profile), self.prevf[0])
			output += '</div>'

			# Insert the index link
			output += '<div class="fl ilink"><a href="{0:s}">{1:s}</a></div>'.format(self.index[1].getRelPath(profile), self.index[0])

			# Insert the next link
			output += '<div class="fr link">'
			if not self.nextf is None:
				output += '<a href="{0:s}">{1:s}</a>'.format(self.nextf[1].getRelPath(profile), self.nextf[0])
			output += '</div>'

			# Close out the bar and return
			output += '<div class="clearer"></div></div>'
			return output
		else:
			raise MacroError(NotImplementedError, 'Anchor macro does not support "{0:s}" profile'.format(profile))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the anchor macro class to the list
addMacroClass(NavBarMacro)
