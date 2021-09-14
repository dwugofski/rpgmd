# Macros to handle displaying special objects

import re

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
		header_p = re.compile(r"[\s]*([0-9]*|\*)[\s]*,[\s]*(\*|[0-9]*)[\s]*", re.DOTALL | re.MULTILINE)
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