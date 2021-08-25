
import os, logging

from pathlib import Path

# Start logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(asctime)s\n{{%(filename)s[%(lineno)d] %(funcName)s}}\n%(message)s')

# Now import rpgmd (need to log details from it)
from rpgmd import Document

# Suffixes
MD_SUFFIX = '.md'
TMP_SUFFIX = '.tmp.md'
HTML_SUFFIX = '.html'

# Get the md, tmp, and html directories
md_dir = Path(__file__).resolve().parent.joinpath('../md')
tmp_dir = Path(__file__).resolve().parent.joinpath('../tmp')
html_dir = Path(__file__).resolve().parent.joinpath('../html')

# Ensure the md directory exists
if not md_dir.exists():
	md_dir.mkdir()

# Change to md directory
orig_wd = os.getcwd()
os.chdir(md_dir)

# try... finally to ensure we return to original cwd
try:
	# Parse and copy out the files
	for root,d_names,f_names in os.walk('./'):
		# First ensure the tmp / html directories exist
		new_tmp_dir = tmp_dir.joinpath(root)
		if not new_tmp_dir.exists():
			new_tmp_dir.mkdir()
		new_html_dir = html_dir.joinpath(root)
		if not new_html_dir.exists():
			new_html_dir.mkdir()

		# Now parse and compile the files
		for file in f_names:
			# Determine the source file and skip if not an md file
			srcpath = md_dir.joinpath(root).joinpath(file)
			if not srcpath.suffix.lower() == MD_SUFFIX:
				continue

			# Get and parse the document
			doc = Document(srcpath)
			doc.parse()

			# Now get the paths to the tmp and output files
			tmppath = Path(tmp_dir).joinpath(root).joinpath(file).with_suffix(TMP_SUFFIX)
			outpath = Path(html_dir).joinpath(root).joinpath(file).with_suffix(HTML_SUFFIX)

			# Check if we need to compile (not used now)
			# if not doc.needsCompiling(outpath):
			# 	continue

			# Compile
			doc.compile(tmppath, outpath)
finally:
	# Return cwd to original
	os.chdir(orig_wd)

'''
inpath = Path('../md/test.md').resolve()
tmppath = Path('../tmp/test.tmp.md').resolve()
outpath = Path('../html/test.html').resolve()
doc = Document('../md/test.md')
doc.parse()
doc.compile(tmppath, outpath)
'''

