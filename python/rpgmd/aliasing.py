# Component to translate alias values into strings

import os, re, logging, json

from pathlib import Path, PosixPath, WindowsPath

_ValAliases = {} # Keeps track of classes which have been registered

def addAliasClass(aliasClass, tag=None):
	'''Add a class to the supported alias list so that the ValAlias.makeAlias
	method can generate the aliases as needed from text.

	Args:
		- aliasClass (type): The class to add to the list of supported aliases.
			Must be a subclass of the ValAlias class
		- [tag=None (str|None)]: The text string (should be lowercase) which
			indicates this class. If not specified, the TAG value of the
			aliasClass is used instead

	Raises:
		- ValueError:
			- The provided aliasClass is not a subclass of a ValAlias
			- A nalias class is already associated with the given tag
			- No tag was specified
	'''

	# Ensure the alias class is indeed an alias class
	if not isinstance(aliasClass, type):
		raise ValueError('Provided alias class is not a class')
	if not issubclass(aliasClass, ValAlias):
		raise ValueError('Provided alias class "{0:s}" is not a subclass of a ValAlias'.format(str(aliasClass)))

	# If we do not have a tag, get the tag of the alias class
	if tag is None:
		try:
			tag = aliasClass.TAG
		except AttributeError:
			raise ValueError('No tag provided when adding alias class "{0:s}"'.format(str(aliasClass)))

	# Convert tag to string
	tag = str(tag)

	# Ensure we are not adding a duplicate entry
	if tag in _ValAliases:
		raise ValueError('Cannot track alias class "{0:s}" with tag "{1:s}" as another alias class ("{2:s}") with that tag already exists'.format(
			str(aliasClass), tag, str(_ValAliases[tag])))

	# Add the entry
	logging.info('Adding alias class {0:s} under tag "{1:s}"'.format(aliasClass.__name__, tag))
	_ValAliases[tag] = aliasClass

class ValAlias(object):
	'''Class to handle parsing an alias spec in a value string

	Alias specs follow the given format:
		{alias_name:options}
	Where
		- alias_name (str): The name of the alias to use
		- options (str): An options string specifying the options for the alias
	Please note that escaped braces like \\{ and \\} will be ignored and treated
	as braces literals

	Attributes:
		- type (str): The main type of the alias
		- subtypes (list<str>): Qualifiers to the main type
		- parameters (dict<str,*>): Dictionary of parameters the alias uses to
			evaluate itself
		- file (Path): The file which defined this alias
	'''

	@staticmethod
	def makeAliasDictionary(file):
		'''Create an alias dictionary from an alias dictionary .json file

		Args:
			- file (str|Path): The path to the file to create the dictionary
				from

		Returns:
			- dict<ValAlias>: The aliases contained in the file, indexed by
				their names

		Raises:
			- FileNotFoundError: The provided file could not be found
			- ValueError:
				- The provided file format does not match an alias dictionary
					file
				- One or more alias definitions is not formed correctly
		'''
		# Ensure we have the file
		file = Path(file)
		if not file.is_file():
			raise FileNotFoundError('Could not find file "{0:s}" for making an alias dictionary'.format(str(file)))

		# Open and parse the file
		ret = {}
		with open(file, 'r') as json_file:
			aliases = json.load(json_file)
			for alias_name in aliases:
				ret[alias_name] = ValAlias.makeAlias(aliases[alias_name], file)

		# Return output dictionary
		return ret

	@staticmethod
	def makeAlias(definition, file):
		'''Create an alias from a given definition

		Args:
			- definition (dict<str,str>): The definition of the alias. Can
				contain:
				- 'type': (str) (required) The main type of the alias
				- 'subtypes': (list<str>) (optional) Qualifiers to the main
					type for the alias
				- other: (*) (optional) Parameters the alias uses to evaluate
					itself
			- file (str|Path): The absolute file path to the file the alias is
				defined in.

		Return:
			- ValAlias: An alias object

		Raises:
			- ValueError:
				- No alias of the given type has been found
				- The alias cannot be created from the given dictionary
		'''
		# Ensure we can find the relevant class
		if not 'type' in definition:
			raise ValueError('Definition for alias does not specify type')
		if not definition['type'] in _ValAliases:
			raise ValueError('Could not find alias of type "{0:s}" in list of supported aliases'.format(definition['type']))

		# Make and return the alias
		return _ValAliases[definition['type']](definition, file)

	@staticmethod
	def evaluateAliases(value, aliases, parents=None):
		'''Parse a value string, replacing aliases with their desired values

		Args:
			- value (str): The string to replace aliases for
			- aliases (list<dict<str,ValAlias>>): The alias dictionaries to use.
				If an alias is used across multiple dictionaries, the last
				dictionary to define that alias will be used.
			- parents=[] (list<str>): A history of aliases whose evaluation
				depends on the given value being evaluated

		Return:
			- (str): The value string with aliases replaced

		Raises:
			- ValueError: An issue occurred trying to evaluate an alias
			- NotImplementedError: One of the provided aliases cannot be
				evaluated
		'''
		# Need to make this list so we can traverse it backwards
		alias_iterations = []
		if parents is None:
			parents = []

		# Debug log
		parentstr = ''
		for parent in parents:
			parentstr += parent + ' '
		parentstr = parentstr[:-1]
		logging.debug('Evaluating aliase "{0:s}" [{1:s}]'.format(value, parentstr))

		# Get each alias option and iterate though
		alias_pattern = re.compile(r"(?<!\\)\{([^:\}]+)(:([^\{\}]+))?(?<!\\)\}", re.MULTILINE)
		alias_strings = alias_pattern.finditer(value)
		for alias_m in alias_strings:
			# Get the name / options from the match
			alias_name = value[alias_m.start(1):alias_m.end(1)]
			alias_options = value[alias_m.start(3):alias_m.end(3)]

			# Check for circular dependency
			if alias_name in parents:
				raise ValueError('A circular dependency exists while evaluating alias "{0:s}"'.format(alias_name))
			new_parents = parents.copy()
			new_parents.append(alias_name)

			# Find the matching alias
			alias = None
			for alias_dict in aliases:
				if alias_name in alias_dict:
					alias = alias_dict[alias_name]

			# Throw exception if we could not find the right alias
			if alias is None:
				raise ValueError('Could not find alias named "{0:s}" in provided alias dictionaries'.format(alias_name))

			# Otherwise evaluate the alias
			converted_value = alias.evaluate(alias_options, aliases, new_parents)

			# Add it to the list
			alias_iterations.append((converted_value, alias_m))

		# Going backwards, replace the values in the string
		for (converted_value,alias_m) in reversed(alias_iterations):
			value = value[:alias_m.start(0)] + converted_value + value[alias_m.end(0):]
			logging.debug(value)
		
		# Return
		logging.debug(value)
		return value.replace('\\{', '{').replace('\\}', '}')

	def __init__(self, definition, file):
		'''Fill out the basic attributes of the alias

		Args:
			- definition (dict<str,str>): The definition of the alias. Can
				contain:
				- 'type': (str) (required) The main type of the alias
				- 'subtypes': (list<str>) (optional) Qualifiers to the main
					type for the alias
				- other: (*) (optional) Parameters the alias uses to evaluate
					itself
			- file (str|Path): The absolute file path to the file the alias is
				defined in.

		Raises:
			- ValueError: The provided dictionary does not have a 'type' entry
		'''
		# Save the file
		self.file = Path(file)

		# Ensure we have a type
		if not 'type' in definition:
			raise ValueError('Cannot make alias without a specified type')
		self.type = definition['type']

		# Save details
		self.subtypes = []
		self.parameters = {}
		for parameter in definition:
			pvalue = definition[parameter]
			if parameter == 'type':
				# We've already saved the type
				continue
			elif parameter == 'subtypes':
				# Get the subtypes; either append (for a single value) or copy list
				if not isinstance(pvalue, list):
					self.subtypes.append(pvalue)
				else:
					self.subtypes = pvalue
			else:
				# Copy over remaining parameters
				self.parameters[parameter] = pvalue

	def evaluate(self, options, other_aliases, parents):
		'''Extract the string value an alias evaluates to

		TODO: Check to make sure that infinite alias recursion is not possible.

		Arguments:
			- options (str): The string text for a given option
			- other_aliases (list<dict<str,ValAlias>>): The other aliases
				available for use when defining values. This is useful for
				recursive aliases.
			- parents (list<str>): A history of aliases whose evaluation depends
				on the given value being evaluated

		Return:
			- str: The value the alias evaluates to

		Raises:
			- ValueError:
				- The alias does not have enough options to evaluate
				- The alias's options are not in the correct format for the
					alias
				- An issue occurred evaluating the alias
				- A circular dependency exists in this evaluation
			- NotImplementedError: this type of alias cannot be evaluated
		'''
		raise NotImplementedError('Cannot evaluate alias of base value alias class')

class StringAlias(ValAlias):
	'''Class to handle a basic string replacement alias

	Attributes:
		- value (str): The string value this alias evaluates to
	'''

	TAG = 'string'

	def __init__(self, definition, file):
		'''Fill out the basic attributes of the alias

		Subtypes:

		Parameters:
			- value (str): The value

		Args:
			- definition (dict<str,str>): The definition of the alias. Can
				contain:
				- 'type': (str) (required) The main type of the alias
				- 'subtypes': (list<str>) (optional) Qualifiers to the main
					type for the alias
				- other: (*) (optional) Parameters the alias uses to evaluate
					itself
			- file (str|Path): The absolute file path to the file the alias is
				defined in.

		Raises:
			- ValueError: The alias cannot be created from the given dictionary

		'''
		# Call the base constructor
		super(StringAlias, self).__init__(definition, file)

		# Ensure we have a value
		if not 'value' in self.parameters:
			raise ValueError('Cannot make a string alias without a value parameter')

		# Set the value
		self.value = self.parameters['value']

	def evaluate(self, options, other_aliases, parents):
		'''Extract the string value an alias evaluates to

		TODO: Check to make sure that infinite alias recursion is not possible.

		Arguments:
			- options (str): The string text for a given option
			- other_aliases (list<dict<str,ValAlias>>): The other aliases
				available for use when defining values. This is useful for
				recursive aliases.
			- parents (list<str>): A history of aliases whose evaluation depends
				on the given value being evaluated

		Return:
			- str: The value the alias evaluates to

		Raises:
			- ValueError:
				- The alias does not have enough options to evaluate
				- The alias's options are not in the correct format for the
					alias
				- An issue occurred evaluating the alias
				- A circular dependency exists in this evaluation
			- NotImplementedError: this type of alias cannot be evaluated
		'''
		return ValAlias.evaluateAliases(self.value, other_aliases, parents)

addAliasClass(StringAlias)

class PathAlias(ValAlias):
	'''Alias to represent a path

	Attributes:
		- path (Path): The path to use for evaluation
	'''

	TAG = 'path'

	def __init__(self, definition, file):
		'''Fill out the basic attributes of the alias

		Subtypes:
			abs|rel, [dir|file]
		Where the subtypes mean
			- abs: The path should be evaluated as an absolute file
			- rel: The path should be treated as a relative path
			- dir: The path is a directory
			- file: The path is a file

		Parameters:
			- value (str): The string value of the path

		Args:
			- definition (dict<str,str>): The definition of the alias. Can
				contain:
				- 'type': (str) (required) The main type of the alias
				- 'subtypes': (list<str>) (optional) Qualifiers to the main
					type for the alias
				- other: (*) (optional) Parameters the alias uses to evaluate
					itself
			- file (str|Path): The absolute file path to the file the alias is
				defined in.

		Raises:
			- ValueError: The alias cannot be created from the given dictionary

		'''
		# Call the base constructor
		super(PathAlias, self).__init__(definition, file)

		# Ensure we have a value
		if not 'value' in self.parameters:
			raise ValueError('Cannot make a path alias without a value parameter')

		# Get the path
		self.path = Path(self.parameters['value'])

		# Make absolute if required, evaluated relative to definition file
		if 'abs' in self.subtypes:
			if not self.path.is_absolute():
				self.path = self.file.parent.joinpath(self.path)

	def evaluate(self, options, other_aliases, parents):
		'''Extract the string value an alias evaluates to

		TODO: Check to make sure that infinite alias recursion is not possible.

		Arguments:
			- options (str): The string text for a given option
			- other_aliases (list<dict<str,ValAlias>>): The other aliases
				available for use when defining values. This is useful for
				recursive aliases.
			- parents (list<str>): A history of aliases whose evaluation depends
				on the given value being evaluated

		Return:
			- str: The value the alias evaluates to

		Raises:
			- ValueError:
				- The alias does not have enough options to evaluate
				- The alias's options are not in the correct format for the
					alias
				- An issue occurred evaluating the alias
				- A circular dependency exists in this evaluation
			- NotImplementedError: this type of alias cannot be evaluated
		'''
		# Get the output string
		output = ValAlias.evaluateAliases(str(self.path), other_aliases, parents)

		# Add slash for directories if a slash is not already there
		if 'dir' in self.subtypes:
			if not output[-1] == '/' and not output[-1] == '\\':
				output += '/' if isinstance(self.path, PosixPath) else '\\'
		return output

addAliasClass(PathAlias)

