
'''This tools is not safe for a website backend. Some things to keep in mind if
or when this is moved to a public forum:

- Need to make sure that the output HTML code is safe by
 	1. Stripping, encoding, and/or limiting the HTML entities in the original
 		source file, likely via preprocessing
 	2. Ensuring that all links are internal to the site, or at least that any
 		external links are flagged and validated to protect against XSS or
 		fishing.
- Safety concerns to keep in mind:
	- XSS attacks
	- Fishing
- It is already assumed some community moderation is at play to make sure that
	the content itself is acceptable
'''

from .aliasing import *
from .core import *
from .linking import *
from .indexing import *
from .display import *