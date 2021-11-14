<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="3.0"
	xmlns="http://www.w3.org/1999/xhtml"
	xmlns:coc="https://github.com/dwugofski/rpgml/coc"
	xmlns:rpgml="https://github.com/dwugofski/rpgml"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="coc:root">
		<html>
			<head>
			</head>
			<body>
				<!--
				<xsl:call-template name="foobar">
					<xsl:with-param name="target" select="coc:details/coc:name"/>
				</xsl:call-template>
			-->
				<p>First: <xsl:apply-templates select="coc:details/coc:name[1]/node()"/></p>
				<xsl:apply-templates select="coc:details/*[position()>1]"/>
			</body>
		</html>
	</xsl:template>

	<xsl:template match="coc:long">
		<strong><xsl:value-of select="."/></strong>
	</xsl:template>

	<xsl:template match="coc:short">
		<em><xsl:value-of select="."/></em>
	</xsl:template>

	<xsl:template match="coc:name">
		<p>
			<xsl:apply-templates/>
		</p>
	</xsl:template>

</xsl:stylesheet>