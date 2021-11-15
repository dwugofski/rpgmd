
import saxonc, os

from pathlib import Path

processor = saxonc.PySaxonProcessor(license=False)
processor.set_cwd(os.getcwd())
transformer = processor.new_xslt30_processor()
transformer.transform_to_file(
	source_file='./crocodile.example.xml',
	stylesheet_file='coc.creature.smallblock.xslt',
	output_file='test.html')
print(transformer.exception_count())
i = 0
while transformer.get_error_message(i):
	print(transformer.get_error_message(i))
	i += 1

val = transformer.apply_templates_returning_value(
	source_file='./crocodile.example.xml',
	stylesheet_file='coc.creature.smallblock.xslt')
subtree = val.item_at(0) # This will get us the subtree... str(subtree.get_node_value()) should give us a string for the HTML code

html_wrapping = processor.parse_xml(xml_text='<?xml version="1.0" encoding="utf-8"?><html><head></head><body></body></html>')
body_wrapping = html_wrapping.children[0].children[1]
body_wrapping.add_xdm_item(subtree)
# print(str(body_wrapping.item_at(0).get_node_value().children))
print(str(subtree.get_node_value()))
