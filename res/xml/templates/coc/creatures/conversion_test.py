
import lxml.etree as etree

from pathlib import Path


source = etree.parse("crocodile.example.xml")
xsd_doc = etree.parse("coc.creature.xsd")
xsds_doc = etree.parse("../common/xsd/rich_text.xsd")
xsd_schema = etree.XMLSchema(xsd_doc)
xsd_schema.validate(source)