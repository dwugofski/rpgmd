# Macros to handle displaying special objects

import re
import lxml.etree as etree

from pathlib import Path


from .core import *

class ImageMacro(Macro):
	'''Macro to display an image

	Attributes:
		- img (Path|str): The relative path to the image to display. If str, the
			path will be trateda as a URL to an image file
		- title (str|None): The title under the image, or None if no title
			should be displayed
		- classes (List<str>): The classes for the image
		- player_link (Path|str|None): The relative path to the image to link to
			for the image the players should see. If None, no such link will be
			shown. If str, the path will be treated as a URL to an image file
	'''

	TAG = 'img'

	@staticmethod
	def makeMacro(img, title, classes, player_link, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- img (str|Path): The relative path to the image to display
			- title (str|None): The caption under the image, or None if no
				caption should be displayed
			- classes (List<str>): The classes for the image
			- player_link (str|Path|None): The relative path to the image to
				link to for the image the players should see. If None, no such
				link will be shown
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Translate the classes to text
		classes_text = ''
		prefix = '' # Prefix used to add comma after the first item
		for classn in classes:
			classes_text += prefix + classn
			prefix = ','

		# Make the macro
		attrs = [str(img), title, classes_text, str(player_link)]
		macro_text = Macro.makeMacroText(ImageMacro.TAG, attrs)
		return ImageMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			img | [title] | [classes] | [player_link]
		Where
			- img (str): The relative path to the image to display
			- title (str): The caption under the image
			- classes (str): The classes for the image, separated by commas
			- player_link (str): The relative path to the image to link to for
				the image the players should see. If None, no such link will be
				shown

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
		super(ImageMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 1:
			raise MacroError(ValueError, 'Image macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Set the image link
		self.img = Macro.getPathOrLink(self.attrs[0])

		# Set the title (if included)
		self.title = self.attrs[1] if len(self.attrs) >= 2 else None
		self.title = None if self.title == '' else self.title

		# Create the classes list
		self.classes = Macro.extractListString(self.attrs[2]) if len(self.attrs) >= 3 else []

		# Set the player link
		self.player_link = self.attrs[3] if len(self.attrs) >= 4 else None
		self.player_link = None if not self.player_link else Macro.getPathOrLink(self.player_link)

	def compile(self, profile='web'):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		if profile == 'web':
			# Build the container and add the relevant classes
			output = '<div class="img_container '
			for classn in self.classes:
				output += classn + ' '
			output = output[:-1] + '">'

			# Add the image
			imgsrc = self.img
			# May need to convert Path to string
			if isinstance(self.img, Path):
				imgsrc = str(self.img.as_posix())
			output += '<img src="{0:s}"/>'.format(imgsrc)

			# Add the title (optional)
			if not self.title is None:
				output += '<div class="caption">{0:s}</div>'.format(self.title)

			# Add the player link (optional)
			if not self.player_link is None:
				plink = self.player_link
				# May need to convert Path to string
				if isinstance(self.player_link, Path):
					plink = str(self.player_link.as_posix())
				output += '<div class="caption"><a href="{0:s}" target="_blank">(Player version)</a></div>'.format(plink)

			# Close the container and return
			output += "</div>"
			return output
		else:
			raise MacroError(NotImplementedError, 'Image macro does not support "{0:s}" profile'.format(profile))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the image macro class to the list
addMacroClass(ImageMacro)

class TableMacro(Macro):
	'''Macro to populate a table

	Attributes:
		- items (list<list<str>>): 2D array of items to render in the table
		- headers (list<str>): Spec strings for which table items should be
			header items
		- classes (List<str>): The classes for the table
	'''

	TAG = 'table'

	@staticmethod
	def makeMacro(items, headers, classes, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- items (list<list<str>>): 2D array of items to render in the table
			- headers (list<str>): Spec strings for which table items should be
				header items
			- classes (List<str>): The classes for the table
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Translate the items to text
		items_text = ''
		for r,row in enumerate(items):
			for c,column in enumerate(row):
				# Add the item and the item delimiter (not counting the last column)
				items_text += column
				if not c == len(row) - 1:
					items_text += ',,'
			# Add the row delimiter
			items_text += ';;'
		items_text = items_text[:-2]

		# Translate the headers to text
		headers_text = ''
		for header in headers:
			headers_text += header + ';'
		headers_text = headers_text[:-1]

		# Translate the classes to text
		classes_text = ''
		for classn in classes:
			classes_text += classn + ','
		classes_text = classes_text[:-1]

		# Make the macro
		attrs = [items_text, headers_text, classes_text]
		macro_text = Macro.makeMacroText(ImageMacro.TAG, attrs)
		return ImageMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			classes | headers | items
		Where
			- classes (str): Comma-separated-values for classes to apply to the
				table
			- headers (str): Semicolon-separated-values for row/column pairs of
				which items should be header items. Each spec has the following
				format:
					row,col
				where
				- row (int|*): Is the row index to match ('*' matches all rows)
				- col (int|*): Is the column index to match ('*' matches all
					columns)
				So, to make all items on the second row be header cells, one
				would use the spec
					1,*
			- items (str): The list of strings for the items in the table. Each
				item is separated from the item in the next column by ',,', and
				each row is separated from the next by ';;'. So the following
				items string:
					foo,,bar;;Bar,,Foo
				would be displayed as
					|foo|bar|
					|Bar|Foo|

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
		super(TableMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 3:
			raise MacroError(ValueError, 'Table macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Get the classes
		self.classes = Macro.extractListString(self.attrs[0])

		# Set the headers
		self.headers = []
		headers = Macro.extractListString(self.attrs[1], delimiter=';')
		header_p = re.compile(r"[\s]*([0-9]+|\*)[\s]*,[\s]*([0-9]+|\*)[\s]*", re.DOTALL | re.MULTILINE)
		for header in headers:
			header_m = header_p.match(header)
			if header_m:
				self.headers.append(header_m.group(1) + ',' + header_m.group(2))
			else:
				raise MacroError(ValueError, 'Invalid header spec "{0:s}"'.format(header))

		# Create the items list
		self.items = []
		rows = Macro.extractListString(self.attrs[2], delimiter=';;', drop_empty=False)
		for row in rows:
			new_row = []
			items = Macro.extractListString(row, delimiter=',,', drop_empty=False)
			for item in items:
				new_row.append(item)
			self.items.append(new_row)

	def isHeader(self, row, column):
		'''Check whether a cell should be a header cell

		Args:
			- row (int): The row index of the cell
			- column (int): The column index of the cell

		Return:
			- bool: True if the cell is a header, else False
		'''
		for header in self.headers:
			(hrow, hcolumn) = header.split(',')
			# Check if there is a row mismatch
			if hrow != '*':
				if row != int(hrow):
					continue
			# Check if there is a column mismatch
			if hcolumn != '*':
				if column != int(hcolumn):
					continue
			# Otherwise, we have matched both row and column
			return True

		# If we could not find a matching rule, return False
		return False

	def compile(self, profile='web'):
		'''Method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''

		# Get the dimensions of the table
		nrows = len(self.items)
		ncols = 0
		for row in self.items:
			if len(row) > ncols:
				ncols = len(row)

		if profile == 'web':
			# Create the table with the given classes
			output = '<table'
			if not len(self.classes) == 0:
				output += ' class="'
				output += '"'
			output += '>'

			# Fill the table with rows and items
			for r,row in enumerate(self.items):
				# Add the row tag
				output += "<tr>"

				# Append out the row to the maximum number of columns
				for i in range(len(row), ncols):
					row.append('')

				# Write out the columns of the row
				for c,item in enumerate(row):
					# Need to pick tag to use based on the required type
					tagn = 'td'
					if self.isHeader(r, c):
						tagn = 'th'
					output += '<{1:s}>{0:s}</{1:s}>'.format(item, tagn)

				# End the row tag
				output += '</tr>'
			output += '</table>'
			return output
		else:
			raise MacroError(NotImplementedError, 'Image macro does not support "{0:s}" profile'.format(profile))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the table macro class to the list
addMacroClass(TableMacro)

class StatblockMacro(Macro):
	'''Macro class to handle the display of a statblock

	Attributes:
		- title (str): The id of this generator
		- source (Path): Absolute path to the source .xml file for the statblock
		- xsd (Path|None): Absolute path to the xsd validator for the statblock,
			or None if no validator should be used for the statblock
		- xslts (dict<str,Path>): Dictionary of the different templates to use
			for creating the output HTML for different profiles. Paths are
			absolute
		- imports (list<ImportMacro>): The import macros managed by this
			Statblock for its imported files
	'''

	TAG = 'statblock'

	@staticmethod
	def makeMacro(title, source, xsd, xslts, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The id of this generator
			- source (Path|str): Path to the source .xml file for the statblock
			- xsd (Path|str|None): Path to the xsd validator for the statblock,
				or None if no validator should be used for the statblock
			- xslts (dict<str,Path|str>): Dictionary of the different templates
				to use for creating the output HTML for different profiles.
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Make the source path string
		source = str(source)

		# Make the xsd path string
		if not xsd is None:
			xsd = str(xsd)

		# Make the xslts string
		xsltstr = ''
		for profile in xslts:
			xsltstr += '{0:s}::{1:s},'.format(profile, xslts[profile])
		xsltstr = xsltstr[:-1]

		# Make the macro
		attrs = [title, source, xsltstr, xsd]
		macro_text = Macro.makeMacroText(StatblockMacro.TAG, attrs)
		return StatblockMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Constructor for StatblockMacro

		Format:
			title | source | xslts [| xsd]
		Where
			- title (str): The id of this generator
			- source (str): The path to the source file for the statblock
			- xslts (str): List of different transformation templates for the
				output of the statblock. The list contains comma-separated
				entries where each entry is formatted as:
					profile::path
				where
					- profile (str): The profile to use the template for
					- path (str): The path to the template
			- xsd (str): The path to the xsd validator file for the statblock.
				If not provided, no validation will be performed

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
		'''
		super(StatblockMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		logging.debug(text)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 3:
			raise MacroError(ValueError, 'Statblock macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Save the title
		self.title = self.attrs[0]

		# Save the source, make sure it's valid, and add it to our imports list
		self.source = Path(self.attrs[1])
		if not self.source.is_absolute():
			self.source = Path(self._doc.filepath).parent.joinpath(self.source)
		self.imports = [ImportMacro.makeMacro('_sb_{0:s}_src'.format(self.title), self.attrs[1],
			self._line, self._column, self._endline, self._endcolumn, self._doc, True)]

		# For each template, make an import macro for the template
		self.xslts = {}
		xslte_p = re.compile(r"^[^:]+::.+$", re.DOTALL | re.MULTILINE)
		xslts = Macro.extractListString(self.attrs[2])
		logging.debug(self.attrs[2])
		for entry in xslts:
			# Validate format
			if not xslte_p.match(entry):
				raise MacroError(ValueError, 'Statblock macro XSLT specification string "{0:s}" is not in a valid format'.format(entry))

			# Get the profile and path, and make the import macro for the template
			(profile, path) = entry.split('::')
			self.xslts[profile] = Path(path)
			if not self.xslts[profile].is_absolute():
				self.xslts[profile] = Path(self._doc.filepath).parent.joinpath(self.xslts[profile])
			self.imports.append(ImportMacro.makeMacro('_sb_{0:s}_xslt_{1:s}'.format(self.title, profile), path,
				self._line, self._column, self._endline, self._endcolumn, self._doc, True))

		# If we have a validator, save it, make sure it's valid, and add it to
		# our imports list
		self.xsd = None
		if len(self.attrs) >= 4 and self.attrs[3]:
			self.xsd = Path(self.attrs[3])
			if not self.xsd.is_absolute():
				self.xsd = Path(self._doc.filepath).parent.joinpath(self.xsd)
			self.imports.append(ImportMacro.makeMacro('_sb_{0:s}_xsd'.format(self.title), self.xsd,
				self._line, self._column, self._endline, self._endcolumn, self._doc, True))

		# For each import macro, add it to the defining document
		for importmacro in self.imports:
			doc.addMacro(importmacro)

	def compile(self, profile='web'):
		'''Method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		# Ensure we support the given profile
		if not profile in self.xslts:
			raise MacroError(NotImplementedError, 'Statblock macro does not support "{0:s}" profile'.format(profile))

		try:
			# Catch and rethrow (e.g. XML) errors

			# Get the input document
			source = etree.parse(str(self.source))
			if not self.xsd is None:
				# Use validator with parser if we have an XSD file
				xsd_doc = etree.parse(str(self.xsd))
				xsd_schema = etree.XMLSchema(xsd_doc)
				xsd_schema.validate(source) # Will throw syntax error if invalid

			# Get the transform
			xslt_doc = etree.parse(str(self.xslts[profile]))
			xslt_transform = etree.XSLT(xslt_doc)
			output_doc = xslt_transform(source)

			# And get the output as string
			return etree.tostring(output_doc, method='html', encoding='unicode')

		except Exception as e:
			# Rethrow (e.g. XML-based) exceptions with the information for this macro
			raise MacroError(type(e), 'Problem compiling Statblock from XML:\n' + str(e))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the table macro class to the list
addMacroClass(StatblockMacro)

class StatblockListMacro(Macro):
	'''Class for a macro to display a list of statblocks

	Attributes:
		- title (str): The title text to display for this macro
		- classes (list<str>): The classes to apply to the output html of this
			macro
		- blocks (list<StatblockMacro>): The statblocks to show for this macro
	'''

	TAG = 'statblocks'

	@staticmethod
	def makeMacro(title, classes, blocks, xslts, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title text to display for this macro
			- classes (list<str>): The classes to apply to the output html of
				this macro
			- blocks (list<StatblockMacro>): The statblocks to show for this
				macro
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Make the classes string
		classestr = ''
		for classn in classes:
			classestr += classn + ','
		classestr = classestr[:-1]

		# Make the blocks string
		statblockstr = ''
		for statblock in blocks:
			statblockstr += statblock.tostring()[1:-1].replace('|', ',,') + ';;'
		statblockstr = statblockstr[:-2]

		# Make the macro
		attrs = [title, classestr, statblockstr]
		macro_text = Macro.makeMacroText(StatblockListMacro.TAG, attrs)
		return StatblockListMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Constructor for StatblockMacro

		Format:
			title | classes | statblocks
		Where
			- title (str): The title text to display for this macro
			- classes (str): The classes to modify how this list is displayed,
				provided as a comma-separated-value list
			- statblocks (str): The statblocks to include in this list, provided
				as a series of ';;'-separated values where each item is of the
				following format:
					source,,xslts[,,xsd]
				where
					- source (str): The path to the source XML file for the
						statblock
					- xslts (str): The list of tranformation templates to use
						for the statblock. See the statblock macro __init__
						method for more details.
					- xsd (str): The path to the XSD validator file to use for
						the statblock (leave empty to not use a validator

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
		'''
		super(StatblockListMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 3:
			raise MacroError(ValueError, 'Statblock list macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Get the title
		self.title = self.attrs[0]

		# Get the classes list
		self.classes = Macro.extractListString(self.attrs[1])

		# Get the statblocks
		self.blocks = []
		for statblockdef in self.attrs[2].split(';;'):
			if len(statblockdef) == 0:
				continue
			new_sbm_text = '[[{0:s}|{1:s}]]'.format(StatblockMacro.TAG, statblockdef.replace(',,', '|'))
			new_sbm = StatblockMacro(new_sbm_text, startline, startcolumn, endline, endcolumn, doc)
			# Do not add to doc; do not want it to compile on its own
			self.blocks.append(new_sbm)

	def compile(self, profile='web'):
		'''Method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		# Ensure we support the given profile
		for block in self.blocks:
			if not profile in block.xslts:
				raise MacroError(NotImplementedError, ('Statblock list macro {1:s} does not support "{0:s}" profile,'+
					'because statblock "{2:s}" does not support that profile').format(profile, self.title, block.title))

		# Create the statblocks
		if profile == 'web':
			# Start the output and add the classes
			output = '<div class="statblock_container '
			for classt in self.classes:
				output += classt + ' '
			output = output[:-1] + '">'

			# Add the title
			output += '<h1>{0:s}</h1>'.format(self.title)

			# Add the statblocks
			# Break up into left/right columns
			left_column = '<div class="column2 fl">'
			right_column = '<div class="column2 fr">'
			for i,block in enumerate(self.blocks):
				if i % 2 == 0:
					left_column += block.compile(profile)
				else:
					right_column += block.compile(profile)
			output += left_column + '</div>'
			output += right_column + '</div>'

			# Add the clearer, close the container, and finish
			output += '<div class="clearer"></div></div>'
			return output
		else:
			raise MacroError(NotImplementedError, 'Statblock list macro {1:s} does not support "{0:s}" profile'.format(profile, self.title))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the table macro class to the list
addMacroClass(StatblockListMacro)

class EncounterMacro(Macro):
	'''Class for a macro to display a list of statblocks

	Attributes:
	'''

	TAG = 'enc'

	@staticmethod
	def makeMacro(*init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title text to display for this macro
			- classes (list<str>): The classes to apply to the output html of
				this macro
			- blocks (list<StatblockMacro>): The statblocks to show for this
				macro
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		# Make the macro
		attrs = []
		macro_text = Macro.makeMacroText(EncounterMacro.TAG, attrs)
		return EncounterMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Constructor for StatblockMacro

		Format:
		Where

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
		'''
		super(EncounterMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

	def compile(self, profile='web'):
		'''Method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		return '<span>Closed for maintenance</span>'

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the table macro class to the list
addMacroClass(EncounterMacro)
