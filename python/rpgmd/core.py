# Core components

import os, re, logging, inspect
import validators

from pathlib import Path
from contextlib import contextmanager
from markdown2 import markdown_path as mdconvert

from .aliasing import ValAlias

_MacroClasses = {} # Keeps track of classes which have been registered

def addMacroClass(macroClass, tag=None):
	'''Add a class to the supported macros list so that the Macro.parseMacros
	method can generate the macros as needed from text.

	Args:
		- macroClass (type): The class to add to the list of supported macros.
			Must be a subclass of the Macro class
		- [tag=None (str|None)]: The text string (should be lowercase) which
			indicates this class. If not specified, the TAG value of the
			macroClass is used instead

	Raises:
		- ValueError:
			- The provided macroClass is not a subclass of a Macro
			- A macro class is already associated with the given tag
			- No tag was specified
	'''

	# Ensure the macro class is indeed a macro class
	if not isinstance(macroClass, type):
		raise ValueError('Provided macro class is not a class')
	if not issubclass(macroClass, Macro):
		raise ValueError('Provided macro class "{0:s}" is not a subclass of a Macro'.format(str(macroClass)))

	# If we do not have a tag, get the tag of the macro class
	if tag is None:
		try:
			tag = macroClass.TAG
		except AttributeError:
			raise ValueError('No tag provided when adding macro class "{0:s}"'.format(str(macroClass)))

	# Convert tag to string
	tag = str(tag)

	# Ensure we are not adding a duplicate entry
	if tag in _MacroClasses:
		raise ValueError('Cannot track macro class "{0:s}" with tag "{1:s}" as another macro class ("{2:s}") with that tag already exists'.format(
			str(macroClass), tag, str(_MacroClasses[tag])))

	# Add the entry
	logging.info('Adding macro class {0:s} under tag "{1:s}"'.format(macroClass.__name__, tag))
	_MacroClasses[tag] = macroClass

def MacroError(basetype, message, macro=None):
	'''Create an exception for a macro

	Args:
		- basetype (type<Exception>): The type of exception to return
		- message (str): The text to display for the exception
		- macro (Macro|None): The macro raising the exception. If None, the
			macro will be assumed to be the 'self' of the calling method
	'''
	macro = inspect.stack()[1][0].f_locals['self']
	return basetype('{{{0:s} {1:s}}}\n{2:s}'.format(type(macro).__name__, macro.locStr(), message))

class Macro(object):
	'''Base class for all macros in an original text

	Attributes:
		- tag: The tag / macro type for the macro
		- attrs: The attributes for the macro (used by subclass)
	'''

	OPENING_SEQUENCE = "[["
	CLOSING_SEQUENCE = "]]"
	DELIMITER = "|"

	@staticmethod
	def makeMacroText(tag, attrs):
		'''Create the description text for a macro

		Args:
			- tag (str): The string of the tag to make the text for
			- attrs (list<str>): The attribute text for each attribute of the
				macro

		Return:
			- str: The text that would make the given macro
		'''
		# Set the opening sequence and tag
		output = Macro.OPENING_SEQUENCE + tag

		# Add the attributes, separating by delimiter
		for attr in attrs:
			if attr is None:
				attr = ''
			output += Macro.DELIMITER + attr

		# Return the tag + attributes list with the closing sequence
		return output + Macro.CLOSING_SEQUENCE

	@staticmethod
	def getPathOrLink(teststr):
		'''Check if a provided string is a path link or a web link

		Args:
			- teststr (str): The path or web link to check

		Return:
			- Path: The path for the given text
			- str: The web link
		'''
		if not validators.url(teststr) and not validators.url('http://' + teststr):
			return Path(teststr)
		else:
			return teststr

	@staticmethod
	def extractListString(list_str, trim=True, drop_empty=True, delimiter=','):
		'''Extract a list from a list string (e.g. a comma-separated-value list)

		Args:
			- list_str (str): The list string to use
			- trim=True (bool): Whether to trim whitespace from the start/end of
				each item in the list string
			- drop_empty=True (bool): Whether to drop empty strings from the
				output list
			- delimiter=',' (str): The delimiter to use for the values

		Return:
			- list<str>: The list of the items in the list string
		'''
		ret = []
		item_p = re.compile(r"[\s]*(.*[^\s])[\s]*", re.DOTALL | re.MULTILINE) # Regex to extract the non-whitespace part of the item
		for item in list_str.split(delimiter):
			# Trim the whitespace from beginning / end
			if trim:
				item_m = item_p.match(item)
				if item_m:
					item = item_m.group(1)
				else:
					item = ''

			# Add the item to the list
			if not item == '' or not drop_empty:
				ret.append(item)

		return ret

	def locStr(self):
		'''Get the string description of the macro's file and lcoation therein

		Return:
			A string indicating where the macro is defined: file, line, and
				character index
		'''
		return '{0:s}[{1:d},{2:d}]'.format(self._file, self._line+1, self._column)

	def span(self):
		'''Get the position information for the macro in the defining file

		Return:
			A tuple containing
				- (int) The line the macro starts on
				- (int) The character index in that line the macro starts on
				- (int) The line the macro ends on
				- (int) The character index in that line immediately after the
					macro
		'''
		return self._line, self._column, self._endline, self._endcolumn

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Args:
			- text (str): The text (including the containing characters) for the
				macro
			- startline (int): The line the macro starts on
			- startcolumn (int): The character index the macro starts on
			- endline (int): The line the macro ends on
			- endcolumn (int): The character index the macro ends on
			- doc (Document): The document object defining the macro

		Raise:
			- ValueError: The macro spec string contains a badly-formatted
				attribute
		'''
		# Trimming pattern for an attribute
		attr_pattern = re.compile(r"[\s]*(.*[^\s])[\s]*$", re.DOTALL | re.MULTILINE)

		# Keep track of file position for debug info
		self._text = text
		self._doc = doc
		self._file = doc.filepath
		self._line = startline
		self._column = startcolumn
		self._endline = endline
		self._endcolumn = endcolumn

		logging.debug('Creating {0:s} macro from {1:s}'.format(type(self).__name__, self.locStr()))

		# Extract just the macro spec string
		text = text[len(Macro.OPENING_SEQUENCE):-len(Macro.CLOSING_SEQUENCE)]
		logging.debug(text)

		# Split the macro spec string and record the spec elements
		self.attrs = []
		self.tag = None
		for attr in text.split(Macro.DELIMITER):
			# Trim the attribute text
			attr_match = attr_pattern.match(attr)
			if attr_match:
				# If it matches the format of an attribute, we can continue
				if self.tag is None:
					self.tag = attr_match.group(1)
				else:
					logging.debug(attr_match.group(1))
					new_attr = ValAlias.evaluateAliases(attr_match.group(1), self._doc.aliases)
					self.attrs.append(new_attr)
			else:
				# If not, we should just add an empty string (as that meant the item was just white space)
				logging.info('Empty macro attribute string "{0:s}" found in "{1:s}"'.format(attr, self.locStr()))
				self.attrs.append('')

		logging.debug('Created macro with tag "{0:s}" and the following attributes: {1:s}'.format(str(self.tag), str(self.attrs)))

	def compile(self, profile='web'):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- Always, since the base class is not compilable
				- The compiling profile is not supported
		'''
		raise MacroError(NotImplementedError, 'Cannot compile macro from Macro base class')

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'False'
		'''
		return False

	def tostring(self):
		'''Method to convert a macro to its text representation in the source
		document.

		Return:
			- str: The text which would create this macro
		'''
		return Macro.makeMacroText(self.tag, self.attrs)

class Document(object):
	'''Class to wrap information and operations for a given macro-containing
	text file.

	Attributes:
		- filepath (str): The absolute path to the file
		- macros (list[Macro]): The list of the document's macros
		- imports (dict{str:ImportMacro}): Dictionary mapping import name to the
			related import macro
		- file_macro (FileMacro): The file description macro for the document
		- aliases (list<dir<ValAlias>>): The aliases to use when evaluating
			values for the document
	'''

	def __init__(self, filepath, aliases):
		'''Create a document wrapper object

		Arguments:
			- filepath (str|Path): The path to the file for the document. A
				relative path string will be evaluated relative to the current
				working directory
			- aliases (list<dict<ValAlias>>): The aliases to use when parsing
				macros for this document

		Raise:
			- FileNotFoundError: No file exists at the path specified
		'''
		# Extract the absolute path string to the file
		self.filepath = str(Path(filepath).resolve())

		# Set the macro list and import dict to empty
		self.macros = []
		self.imports = {}
		self.file_macro = None
		self.aliases = aliases

	def addMacro(self, new_macro):
		'''Add a macro to this document's macro lists

		Args:
			- new_macro (Macro): The macro to add
		'''
		self.macros.append(new_macro)

		# Track with special macro containers
		if isinstance(new_macro, ImportMacro):
			# Add import macros
			self.imports[new_macro.alias] = new_macro
		if isinstance(new_macro, FileMacro):
			# add file detail macro
			if not self.file_macro is None:
				raise ValueError("Duplicate file macro found\n{0:s}".format(new_macro.locStr()))
			else:
				self.file_macro = new_macro

	def parse(self):
		'''Extract the macros from a document

		Raise:
			- ValueError: A file detail macro was not found, or multiple file
				detail macros were found
		'''
		tag_pattern = re.compile(r"\[\[\s*(\w+)\s*\|.*\]\]", re.DOTALL | re.MULTILINE)

		logging.info('Parsing document from file "{0:s}"'.format(self.filepath))

		# Keep track of whether we have opened a macro, as well as the starting information of the last macro opened
		opened = False
		macrotext = ""
		macroline = 0
		macrocolumn = 0

		with self.open() as file:
			# Iterate over lines
			for linenum,line in enumerate(file):
				# Reset column pointer to start of line
				column = 0
				# While loop used to cover multiple macros on single line
				while True:
					# If we have not opened a macro
					if not opened:
						# Try to find the start of a macro
						# Here, column will have end of previous macro for multi-line
						column = line.find(Macro.OPENING_SEQUENCE, column)
						# If none, we can move on to next line
						if column < 0:
							break
						else:
							# Otherwise, we need to parse the macro, possibly over multiple lines
							# Mark ourselves as having opened a macro
							macrotext = ""
							macroline = linenum
							macrocolumn = column
							opened = True
							continue
					else:
						# We have started a macro, so need to look for end
						end = line.find(Macro.CLOSING_SEQUENCE, column)
						if end < 0:
							# If no match, append the portion of the line's text inside the sequence (inclusive)
							# And then move to next line
							macrotext += line[column:]
							break
						else:
							# If ending sequence encountered, append that text, create the macro, and continue
							macrotext += line[column:end] + Macro.CLOSING_SEQUENCE

							# Attempt to get the tag
							tag_match = tag_pattern.match(macrotext)
							if not tag_match:
								raise ValueError(('Could not find tag for the following macro text :\n'+
									'File "{0:s}"\nLine: {1:d} Column: {2:d}'+
									'"{3:s}"').format(self.filepath, macroline, macrocolumn, macrotext))
							tag = tag_match.group(1)

							# Verify support for macro type
							if not tag in _MacroClasses:
								raise ValueError(('Could not find macro class for tag "{0:s}"\n'+
									'File: {1:s}\nLine: {2:d} Column: {3:d}').format(tag, self.filepath, macroline, macrocolumn))

							# Move column pointer to end of macro
							column = end + len(Macro.CLOSING_SEQUENCE)

							# Create the macro object and add it to the list
							logging.debug('Creating macro with tag "{0:s}" and text\n{1:s}'.format(tag, macrotext))
							new_macro = _MacroClasses[tag](macrotext, macroline, macrocolumn, linenum, column, self)
							self.addMacro(new_macro)

							# Close our consideration and continue reading the line
							opened = False
							continue

		# Ensure we found a file macro for the document
		if self.file_macro is None:
			raise ValueError('No file macro found for file: "{0:s}"'.format(self.filepath))

	def needsCompiling(self, outfile):
		'''Check whether the document needs to be re-compiled, based on whether
		the source file and any dependent files have been updated since the
		last time the output file has been changed.

		Note: This method should only be run after the Document.parse method

		Args:
			- outfile (str|Path): The path to the output file to generate.
				Relative paths will be evaluated relative to the source document

		Raise:
			- FileNotFoundError:
				- The source file does not exist
				- One or more dependency files does not exist
		'''
		# Get the source and output files as pathlib paths
		srcfile = Path(self.filepath).resolve()
		outfile = Path(outfile)
		if not outfile.is_absolute():
			outfile = srcfile.joinpath(outfile)

		# If the output file does not exist, we can return early
		if not outfile.exists():
			return True
		outfile.resolve()

		# Get the modification date of the destination file
		dest_mt = outfile.stat().st_mtime

		# If the source file has changed since last compiling, return early
		if srcfile.stat().st_mtime > dest_mt:
			return True

		# Iterate through imports, checking those file compilation times relative to the destination file
		for importn in self.imports:
			importm = self.imports[importn]
			# Check if the import requires recompiling (e.g. if a macro uses that file to generate content)
			if not importm.is_compiled:
				continue
			importp = Path(importm.path)
			# Check if the imported file has been updated relative to the output file
			if srcfile.joinpath(importm.path).resolve().stat().st_mtime > dest_mt:
				return True

		# Otherwise we have not encountered a reason to recompile, so don't
		return False

	def compile(self, tmpfile, outfile, profile='web'):
		'''Compile the document with its macros.

		Note: This method should only be run after the Document.parse method

		Args:
			- tmpfile (str|Path): The path to the intermediate file to generate.
				Relative paths will be evaluated relative to the source document
			- outfile (str|Path): The path to the file to generate. Relative
				paths will be evaluated relative to the source document
			- profile='web' (str): The type of document to compile out to.
				Options include
				- 'web': A web HTML document
		'''

		logging.info('Compiling document from file "{0:s}"'.format(self.filepath))

		# Sort the macros to ensure they are output in order
		self.macros.sort(key=lambda mac:mac.span())

		# Get the source and output files as pathlib paths
		srcfile = Path(self.filepath)
		tmpfile = Path(tmpfile)
		if not tmpfile.is_absolute():
			tmpfile = srcfile.joinpath(tmpfile)
		outfile = Path(outfile)
		if not outfile.is_absolute():
			outfile = srcfile.joinpath(outfile)

		# Open input and temp files for editing
		with self.open() as inf:
			with open(tmpfile, 'w') as outf:
				# Keep track of which macro we are compiling
				macroi = 0
				macro = None
				at_macro = False

				# Get the first macro (if we have one)
				if len(self.macros) > 0:
					macro = self.macros[0]
					mline, mcolumn, meline, mecolumn = macro.span()

				# Iterate through the lines of the source file
				for linenum,line in enumerate(inf):
					# Reset the input column to the beginning of the line for new lines
					column = 0

					# Necessary for multiple macros on a single line
					while True:
						if not at_macro:  # Skipping to a macro
							# If we are not at the next macro's line yet, copy out the line directly and move to next line
							if macro is None or linenum < mline:
								outf.write(line[column:])
								break

							# If we are at the macro's line, copy out up to the macro
							outf.write(line[column:mcolumn])

							# Compile the macro and output it, then progress to "skipping macro"
							if macro.iscompileable() and not isinstance(macro, HeaderMacro):
								outf.write(macro.compile())
							at_macro = True
							continue

						else: # Skipping a macro
							# If we are not at the ending line, move to next line
							if linenum < meline:
								break

							# Otherwise, move the next macro and jump to the character index of the end of the macro and continue from there
							at_macro = False
							macro = None
							macroi += 1
							column = mecolumn

							# If we have run out of macros to compile, leave early
							if macroi >= len(self.macros):
								continue

							# Get the next macro's starting position
							macro = self.macros[macroi]
							mline, mcolumn, meline, mecolumn = self.macros[macroi].span()

		# Convert the temp file into the output file
		if profile == 'web':
			# Get the format for the HTML file
			html_format = ''
			with open(Path(__file__).parent.joinpath('format.html'), 'r') as ffile:
				html_format = ffile.read()

			# Get the header details
			html_header = ''
			for macro in self.macros:
				if isinstance(macro, HeaderMacro) and macro.iscompileable():
					html_header += macro.compile(profile)

			# Make the Title
			html_title = ''
			if self.file_macro.title:
				html_header += '<title>{0:s}</title>'.format(self.file_macro.title)
				html_title = '<div id="title">{0:s}</div>'.format(self.file_macro.title)

			# Get the body
			html_body = mdconvert(str(tmpfile))

			# Write out the code
			with open(outfile, 'w') as outf:
				outf.write(html_format.format(html_header, html_title, html_body))

	@contextmanager
	def open(self):
		'''Open a document for editing.

		This generator changes the working directory to the file's parent
		directory and yields the file of interest
		'''
		# Get the file path of the new file
		filepath = Path(self.filepath)

		# Switch working directories for ease of access
		past_cwd = os.getcwd()
		os.chdir(filepath.parent)

		# Open the file and yield it; close on conclusion
		f = open(filepath, 'r')
		try:
			yield f
		finally:
			# Return to previous cwd on conclusion
			f.close()
			os.chdir(past_cwd)

class ImportMacro(Macro):
	'''Macro to handle links / imports to other macros

	Attributes:
		- is_compiled (bool): Whether the document needs to be recompiled if
			the imported file is changed
		- alias (str): The name used to represent the import
		- path (str): The absolute path to the import
	'''

	TAG = 'import'

	@staticmethod
	def makeMacro(import_name, import_path, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- import_name (str): The alias used by the import
			- import_path (str|Path): The path to the file to import
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		attrs = [import_name, str(import_path)]
		macro_text = Macro.makeMacroText(ImportMacro.TAG, attrs)
		return ImportMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc, compiled=False):
		'''Create a macro object from the text containing it.

		Format:
			import_name | import_path
		Where
			- import_name (str): The string id of the import
			- import_path (str): The path to the file to import. Relative paths
				are evaluated relative to the source document

		Args:
			- text (str): The text (including the containing characters) for the
				macro
			- startline (int): The line the macro starts on
			- startcolumn (int): The character index the macro starts on
			- endline (int): The line the macro ends on
			- endcolumn (int): The character index the macro ends on
			- doc (Document): The document object defining the macro
			- [compiled=False (bool)]: Whether this containing document needs to
				be recompiled if the imported file is changed

		Raise:
			- ValueError:
				- The macro spec string contains a badly-formatted attribute
				- Not enough attributes were provided to the macro
			- FileNotFoundError: The imported file could not be found
		'''
		# The Macro superclass will parse all of the attributes
		super(ImportMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Set the is_compiled attribute
		self.is_compiled = compiled

		# Check to make sure we have enough attributes
		if len(self.attrs) < 2:
			raise MacroError(ValueError, 'Import macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Set the alias
		self.alias = self.attrs[0]

		# Get the absolute path to the file (may through FileNotFoundError)
		self.path = str(Path(doc.filepath).parent.joinpath(Path(self.attrs[1])).resolve())

	# def compile(self): # Inherit from Macro

	# def iscompileable(self): # Inherit from Macro

class FileMacro(Macro):
	'''Macro to handle the details of a document file

	Attributes:
		- title (str): The title for this file
	'''

	TAG = 'file'

	@staticmethod
	def makeMacro(title, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title to display for this document
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		attrs = [title]
		macro_text = Macro.makeMacroText(FileMacro.TAG, attrs)
		return FileMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			title
		Where
			- title (str): The title to display for this document

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
			- FileNotFoundError: The imported file could not be found
		'''

		# The Macro superclass will parse all of the attributes
		super(FileMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 1:
			raise MacroError(ValueError, 'File detail macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Set the title
		self.title = self.attrs[0]

	# def compile(self): # Inherit from Macro

	# def iscompileable(self): # Inherit from Macro

# Add the import and file detail macros
addMacroClass(ImportMacro)
addMacroClass(FileMacro)

class HeaderMacro(Macro):
	'''Passthrough macro to differentiate from macros meant to be compiled in
	the body
	'''

class CSSMacro(HeaderMacro):
	'''Macro to handle the details of a document file

	Attributes:
		- profiles (list<str>): The profiles for which this CSS file should be
			included
		- file (Path): The path to the css file to import
	'''
	TAG = 'css'

	@staticmethod
	def makeMacro(profiles, file, *init_args, **init_kwargs):
		'''Make a css macro from the provided details

		Args:	
			- profiles (list<str>): The profiles for which this CSS file should
				be included
			- file (str|Path): The relative path to the css file to import
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Get the profiles as a string
		profs = ''
		for profile in profiles:
			profs += profile + ','
		# Make the macro
		attrs = [profs[:-1], str(file)]
		macro_text = Macro.makeMacroText(CSSMacro.TAG, attrs)
		return CSSMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			profiles | file
		Where
			- profiles (str): A comma-separated-value list of profiles to
				include this macro for
			- file (str): The relative path to the css file to import

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
		'''

		# The Macro superclass will parse all of the attributes
		super(CSSMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 2:
			raise MacroError(ValueError, 'CSS macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Get the profiles
		self.profiles = Macro.extractListString(self.attrs[0])

		# Set the file
		self.file = Path(self.attrs[1])

	def compile(self, profile='web'):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		if profile in self.profiles:
			if profile == 'web':
				return '<link rel="stylesheet" href="{0:s}"/>'.format(str(self.file.as_posix()))
			else:
				raise MacroError(NotImplementedError, 'CSS macro does not support "{0:s}" profile'.format(profile))
		else:
			return ''

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the CSS macro
addMacroClass(CSSMacro)