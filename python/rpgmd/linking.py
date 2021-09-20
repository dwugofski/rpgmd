# Macros related to creating hypertext links

import os, re, logging
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

	@staticmethod
	def makeMacro(anchor, anchor_text, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- anchor_text (str): The text to use to display this anchor
			- anchor (str|None): The ID of the anchor to use, if none, the
				anchor text will be used
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		aid = anchor_text if anchor is None else anchor
		attrs = [anchor_text, aid]
		macro_text = Macro.makeMacroText(AnchorMacro.TAG, attrs)
		return AnchorMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			anchor_text | [anchor]
		Where
			- anchor_text (str): The text to use to display this anchor
			- anchor (str): The ID of the anchor to use. If not provided, the
				text will be used for the anchor

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
		self.text = self.attrs[0]

		# Set the anchor text
		self.id = self.attrs[1] if len(self.attrs) > 1 else self.attrs[0]

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

	Attributes:
		- relpath (Path): The path to the item (Note: Use getRelPath to convert
			this to a string for compiling)
	'''

	TAG = 'namespace'

	@staticmethod
	def makeMacro(module_name, module_path, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- module_name (str): The alias of the document to import
			- module_path (str|Path): The path to the document
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		attrs = [module_name, str(module_path)]
		macro_text = Macro.makeMacroText(NamespaceMacro.TAG, attrs)
		return NamespaceMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc, compiled=False):
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
			- [compiled=False (bool)]: Whether this containing document needs to
				be recompiled if the imported file is changed

		Raise:
			- ValueError:
				- The macro spec string contains a badly-formatted attribute
				- Not enough attributes were provided to the macro
			- FileNotFoundError: The imported file could not be found
		'''

		# Build off of base class
		super(NamespaceMacro, self).__init__(text, startline, startcolumn, endline, endcolumn, doc, compiled=compiled)

		# Get the path to the import as a relative path from the defining document
		self.relpath = Path(os.path.relpath(Path(self.path), Path(doc.filepath).parent))

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
			return str(self.relpath.with_suffix('.html').as_posix())
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

	@staticmethod
	def makeMacro(namespace, anchor, anchor_text, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- namespace (str|None): The name of the rpgmd document to link to.
				If None, the anchor will be given without a namespace qualifier.
			- anchor (str): The ID of the anchor to use
			- anchor_text (str): The text to use to display this anchor
			- *init_args (varargs): The arguments for the macro definition. See
				the __init__ function for more details
			- **init_kwargs (varargs): The keyword arguments for the macro
				definition. See the __init__ function for more details
		'''
		attrs = [namespace + "::" + anchor if not namespace is None else anchor, module_path]
		macro_text = Macro.makeMacroText(LinkMacro.TAG, attrs)
		return LinkMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			[link_text] | [namespace::]anchor
		Where
			- namespace (str): The name of the rpgmd document to link to
			- anchor_text (str): The text to use to display this anchor
			- anchor (str): The ID of the anchor to use

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

		# Get the link from either the first or second field
		link_text = self.attrs[0]
		if len(self.attrs) > 1:
			link_text = self.attrs[1]

		# Set the id
		nsanch_m = nsanch_p.match(link_text)
		self.anchor_id = nsanch_m.group(3)
		self.namespace = nsanch_m.group(2) # Will be None if there is no namespace specified

		# Set the anchor text
		self.text = self.attrs[0] if len(self.attrs) > 1 else self.anchor_id

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
			# file_link = urllib.parse.quote_plus(file_link + '#' + urllib.parse.quote_plus(self.anchor_id, safe=''), safe='/#')
			file_link = file_link + '#' + urllib.parse.quote(self.anchor_id, safe='')

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