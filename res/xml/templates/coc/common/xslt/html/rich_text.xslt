<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="3.0"
	xmlns="http://www.w3.org/1999/html"
	xmlns:rpgml="https://github.com/dwugofski/rpgml"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Translate inline rich text elements
		========================================================================
	-->

	<!--**
		Displays integer data
	-->
	<xsl:template match='rpgml:int'>
		<span class="int"><xsl:value-of select="."/></span>
	</xsl:template>

	<!--**
		Displays decimal data
	-->
	<xsl:template match='rpgml:dec'>
		<span class="dec"><xsl:value-of select="."/></span>
	</xsl:template>

	<!--**
		Displays boolean data
	-->
	<xsl:template match='rpgml:bool'>
		<span class="bool"><xsl:value-of select="."/></span>
	</xsl:template>

	<!--**
		Displays var information
	-->
	<xsl:template match='rpgml:var'>
		<span class="var"><xsl:value-of select="@ref"/></span>
	</xsl:template>

	<!--**
		Displays roll data
	-->
	<xsl:template match='rpgml:roll'>
		<span class="roll"><xsl:apply-templates/></span>
	</xsl:template>

	<!--**
		Displays modifier information
	-->
	<xsl:template match='rpgml:modifier'>
		<span class="modifier"><xsl:apply-templates/></span>
	</xsl:template>

	<!--**
		Displays extra information
	-->
	<xsl:template match='rpgml:extra'>
		<span class="extra"><xsl:apply-templates/></span>
	</xsl:template>

	<!-- 
		========================================================================
		Translate HTML-based rich text elements
		========================================================================
	-->

	<!--**
		Displays strong (i.e. bold) text
	-->
	<xsl:template match='rpgml:strong'>
		<strong>
			<xsl:apply-templates/>
		</strong>
	</xsl:template>

	<!--**
		Displays emphasized (i.e. italics) text
	-->
	<xsl:template match='rpgml:em'>
		<em>
			<xsl:apply-templates/>
		</em>
	</xsl:template>

	<!--**
		Displays unarticulated (i.e. underlined) text
	-->
	<xsl:template match='rpgml:u'>
		<u>
			<xsl:apply-templates/>
		</u>
	</xsl:template>

	<!--**
		Displays citational (i.e. underlined) text
	-->
	<xsl:template match='rpgml:cite'>
		<cite>
			<xsl:apply-templates/>
		</cite>
	</xsl:template>

	<!--**
		Displays marked (i.e. highlighted) text
	-->
	<xsl:template match='rpgml:mark'>
		<mark>
			<xsl:apply-templates/>
		</mark>
	</xsl:template>

	<!--**
		Displays a list item
	-->
	<xsl:template match='rpgml:li'>
		<li>
			<xsl:apply-templates/>
		</li>
	</xsl:template>

	<!--**
		Displays an unordered (i.e. bulletted) list
	-->
	<xsl:template match='rpgml:ul'>
		<ul>
			<xsl:apply-templates/>
		</ul>
	</xsl:template>

	<!--**
		Displays an ordered (i.e. numbered) list
	-->
	<xsl:template match='rpgml:ol'>
		<ol>
			<xsl:apply-templates/>
		</ol>
	</xsl:template>

	<!--**
		Displays a paragraph of text
	-->
	<xsl:template match='rpgml:p'>
		<p>
			<xsl:apply-templates/>
		</p>
	</xsl:template>

</xsl:stylesheet>