
import lxml.etree as etree

from pathlib import Path


source = etree.parse("crocodile.example.xml")
xsd_doc = etree.parse("coc.creature.xsd")
# xsds_doc = etree.parse("../common/xsd/rich_text.xsd")
xsd_schema = etree.XMLSchema(xsd_doc)
xsd_schema.assert_(source)

xslt_dom = etree.parse("coc.creature.smallblock.xslt")
transform = etree.XSLT(xslt_dom)
html = transform(source)
html.write('test.html', pretty_print=True, method='html')

with open('example.html' ,'wb') as outf:
	outf.write('<?xml version="1.0" encoding="utf-8"?><html><head></head><body>'.encode('utf-8'))
	html.write(outf, pretty_print=True, method='html', encoding='utf-8')
	outf.write('</body></html>'.encode('utf-8'))
