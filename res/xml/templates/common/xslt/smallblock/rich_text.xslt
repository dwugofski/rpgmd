<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Rich Text Output
		========================================================================
	-->

	<!--**
		Displays strong (i.e. bold) text
	-->
	<xsl:template match='src:strong'>
		<strong>
			<xsl:apply-templates/>
		</strong>
	</xsl:template>

	<!--**
		Displays emphasized (i.e. italics) text
	-->
	<xsl:template match='src:em'>
		<em>
			<xsl:apply-templates/>
		</em>
	</xsl:template>

	<!--**
		Displays unarticulated (i.e. underlined) text
	-->
	<xsl:template match='src:u'>
		<u>
			<xsl:apply-templates/>
		</u>
	</xsl:template>

	<!--**
		Displays citational (i.e. underlined) text
	-->
	<xsl:template match='src:cite'>
		<cite>
			<xsl:apply-templates/>
		</cite>
	</xsl:template>

	<!--**
		Displays marked (i.e. highlighted) text
	-->
	<xsl:template match='src:mark'>
		<mark>
			<xsl:apply-templates/>
		</mark>
	</xsl:template>

	<!--**
		Displays a list item
	-->
	<xsl:template match='src:li'>
		<li>
			<xsl:apply-templates/>
		</li>
	</xsl:template>

	<!--**
		Displays an unordered (i.e. bulletted) list
	-->
	<xsl:template match='src:ul'>
		<ul>
			<xsl:apply-templates/>
		</ul>
	</xsl:template>

	<!--**
		Displays an ordered (i.e. numbered) list
	-->
	<xsl:template match='src:ol'>
		<ol>
			<xsl:apply-templates/>
		</ol>
	</xsl:template>

	<!--**
		Displays a paragraph of text
	-->
	<xsl:template match='src:p'>
		<p class='plaintext'>
			<xsl:apply-templates/>
		</p>
	</xsl:template>

	<!--**
		Displays a paragraph of text
	-->
	<xsl:template match='src:p//text()'>
		<xsl:value-of select="."/>
	</xsl:template>

	<!--**
		Displays a rich text paragraph, but without any enclosing paragraph tags
	-->
	<xsl:template name="enclosed_rich_paragraph">
		<xsl:apply-templates/>
	</xsl:template>

	<!--**
		Displays a rich text paragraph with enclosing paragraph tags
	-->
	<xsl:template name="rich_paragraph">
		<p>
			<xsl:apply-templates/>
		</p>
	</xsl:template>

</xsl:stylesheet>