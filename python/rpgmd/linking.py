# Macros related to creating hypertext links

import os, re
import urllib.parse

from pathlib import Path

from .core import *

class AnchorMacro(Macro):
	'''Macro to create an anchor around some text

	Attributes:
		- id (str): The ID of the anchor
		- text (str): The text to display for this anchor
	'''

	TAG = 'a'

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			anchor | [anchor_text]
		Where
			- anchor (str): The ID of the anchor to use
			- anchor_text (str): The text to use to display this anchor

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
		super(AnchorMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 1:
			raise MacroError(ValueError, 'Anchor macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Set the id
		self.id = self.attrs[0]

		# Set the anchor text
		self.text = self.attrs[1] if len(self.attrs) > 1 else self.id

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
			return '<span class="anchor" id="{0:s}">{1:s}</span>'.format(self.id, self.text)
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
addMacroClass(AnchorMacro)

class NamespaceMacro(ImportMacro):
	'''Macro to create an alias for an rpgmd document to import
	'''

	TAG = 'namespace'

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			module_name | module_path
		Where
			- module_name (str): The alias of the document to import
			- module_path (str): The path to the document

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

		# Build off of base class
		super(NamespaceMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Get the path to the import as a relative path from the defining document
		self._relpath = Path(os.path.relpath(Path(self.path), Path(doc.filepath)))

	def getRelPath(self, profile='web'):
		'''Get a text string version of the relative path to the desired output
		file, based on the given profile

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		if profile == 'web':
			return str(self._relpath.with_suffix('.html').as_posix())
		else:
			raise MacroError(NotImplementedError, 'Namespace macro getRelPath does not support "{0:s}" profile'.format(profile))

	# def compile(self): # Inherit from ImportMacro

	# def iscompileable(self): # Inherit from ImportMacro

# Add the anchor macro class to the list
addMacroClass(NamespaceMacro)

class LinkMacro(Macro):
	'''Macro to link to an anchor

	Attributes:
		- anchor_id (str): The name of the anchor to link to
		- text (str): The text of the link
		- namespace (str): The name of the namespace to link to
	'''

	TAG = 'l'

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			[namespace::]anchor | [link_text]
		Where
			- namespace (str): The name of the rpgmd document to link to
			- anchor (str): The ID of the anchor to use
			- anchor_text (str): The text to use to display this anchor

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
		# Pattern to extract the namespace and anchor from the first item
		nsanch_p = re.compile(r"((.+)::)?(.+)")

		# The Macro superclass will parse all of the attributes
		super(LinkMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc)

		# Check to make sure we have enough attributes
		if len(self.attrs) < 1:
			raise MacroError(ValueError, 'Link macro does not have enough attributes, only has {0:d} attributes'.format(
				len(self.attrs)))

		# Set the id
		nsanch_m = nsanch_p.match(self.attrs[0])
		self.anchor_id = nsanch_m.group(3)
		self.namespace = nsanch_m.group(2) # Will be None if there is no namespace specified

		# Set the anchor text
		self.text = self.attrs[1] if len(self.attrs) > 1 else self.anchor_id

	def compile(self, profile='web'):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
			- ValueError: The document for the macro does not contain a
				namespace with the given alias
		'''
		if profile == 'web':
			# Get the link to the file, which, if namespace is specified, will require determining path to that document
			file_link = ''
			if not self.namespace is None:
				# Ensure we have a link to that namespace
				if not self.namespace in self._doc.imports:
					raise MacroError(ValueError, 'Cannot find namespace "{0:s}" in document "{1:s}"'.format(
						self.namespace, self._doc.filepath))
				# Get the link (with the # for the anchor)
				file_link = self._doc.imports[self.namespace].getRelPath(profile)

			# Convert to URL string
			file_link = urllib.parse.quote_plus(file_link + '#' + urllib.parse.quote_plus(self.anchor_id, safe=''), safe='/#')

			# Output the link
			return '<a href="{0:s}">{1:s}</a>'.format(file_link, self.text)
		else:
			raise MacroError(NotImplementedError, 'Link macro does not support "{0:s}" profile'.format(profile))

	def iscompileable(self):
		'''Protoype method for compiling a macro into markdown / HTML

		Return:
			'True' if the macro can be compiled, otherwise 'False'. For this
			class, always return 'True'
		'''
		return True

# Add the anchor macro class to the list
addMacroClass(LinkMacro)