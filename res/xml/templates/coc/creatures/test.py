
import lxml.etree as etree

from pathlib import Path


source = etree.parse("test.xml")
# xsd_doc = etree.parse("coc.creature.xsd")
# xsds_doc = etree.parse("../common/xsd/rich_text.xsd")
# xsd_schema = etree.XMLSchema(xsd_doc)
xslt_dom = etree.parse("test.xslt")
transform = etree.XSLT(xslt_dom)
html = transform(source)
html.write('test.html', pretty_print=True, method='html')
print('done')