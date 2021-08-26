# Macros to handle a directory index

from .core import *
from .linking import NamespaceMacro

class IndexMacro(FileMacro):
	'''Macro to create an index macro

	Attributes:
		- items (list<NamespaceMacro>): The import macros to the files under the
			index
	'''

	TAG = 'index'

	@staticmethod
	def makeMacro(title, items, *init_args, **init_kwargs):
		'''Make an import macro from the provided details

		Args:
			- title (str): The title to display for this document
			- items (list<str>): The relative paths to the modules to include
				under this index, in the order they are specified. Items should
				be separated by commas (',')
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

		# Make the macro
		attrs = [title, items]
		macro_text = Macro.makeMacroText(IndexMacro.TAG, attrs)
		return IndexMacro(macro_text, *init_args, **init_kwargs)

	def __init__(self, text, startline, startcolumn, endline, endcolumn, doc):
		'''Create a macro object from the text containing it.

		Format:
			title | items
		Where
			- title (str): The title to display for this document
			- items (str): The relative paths to the modules to include under
				this index, in the order they are specified. Items should be
				separated by commas (',')

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

	def compile(self, profile='web', depth=0):
		'''Prototype method for compiling a macro into markdown / HTML

		Args:
			- profile='web' (str): The compiling profile for the macro. Options
				are listed in the Document.compile documentation
			- depth=0 (int): The recursive depth down we have gone in indexing

		Raise:
			- NotImplementedError:
				- The compiling profile is not supported
		'''
		if profile == 'web':
			output = ''
			# Only output the title if we are at max depth
			if depth == 0:
				output += '<div class="index"><h1>{0:s}</h1>'.format(self.title)

			# Create the unordered list for the indexed items
			output += '<ul class="index">'
			for item in self.items:
				# Get the path to the linked item
				link_path = item.getRelPath(profile='web')
				output += '<li>'
				try:
					# Make and parse the document to get the file info for it
					doc = Document(item.path)
					doc.parse()
					# Need to get the file info for the item
					finfo = doc.file_macro
					# Add in the title
					output += '<a href="{0:s}">{1:s}</a>'.format(link_path, finfo.title)
					if isinstance(finfo, IndexMacro) and depth < 4:
						output += finfo.compile(profile='web', depth=depth+1)
				except Exception as e:
					# Rethrow (Document-based) exceptions with the information for this macro
					raise MacroError(type(e), e.message)
				output += '</li>'
			output += '</ul>'

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