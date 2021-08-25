<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Capitalization
		========================================================================
	-->

	<!--**
		Variable to keep track of uppercase letters
	-->
	<xsl:variable name="v_uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸŽŠŒ'"/>

	<!--**
		Variable to keep track of lowercase letters
	-->
	<xsl:variable name="v_lowercase" select="'abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿžšœ'"/>

	<!--**
		Make every letter of a string lowercase

		param: text (string) The string to make lowercase
	-->
	<xsl:template name="Tall_lower">
		<xsl:param name="text"/>
		<xsl:value-of select="translate($text,$v_uppercase,$v_lowercase)"/>
	</xsl:template>

	<!--**
		Capitalizes every letter of a string

		param: text (string) The string to make all-caps
	-->
	<xsl:template name="Tall_caps">
		<xsl:param name="text"/>
		<xsl:value-of select="translate($text,$v_lowercase,$v_uppercase)"/>
	</xsl:template>

	<!--**
		Capitalizes the first letter of a string

		param: text (string) The string to capitalize the first letter of
	-->
	<xsl:template name="Tcapitalize_first">
		<xsl:param name="text"/>
		<xsl:value-of select="translate(substring($text,1,1),$v_lowercase,$v_uppercase)"/>
		<xsl:value-of select="substring($text,2,string-length($text)-1)"/>
	</xsl:template>

	<!--**
		Capitalize the starting letter of a block of text and make everything
		else lowercase

		param: text (string) The string to make capitalized
	-->
	<xsl:template name="Tcapitalize">
		<xsl:param name="text"/>
		<xsl:value-of select="translate(substring($text,1,1),$v_lowercase,$v_uppercase)"/>
		<xsl:value-of select="translate(substring($text,2,string-length($text)-1),$v_uppercase,$v_lowercase)"/>
	</xsl:template>

	<!--**
		Capitalize the starting letter of each word in a block of text, and
		make all other letters lowercase

		param: text (string) The string to make camel-case
	-->
	<xsl:template name="Tcamelcase">
		<xsl:param name="text"/>
		<xsl:choose>
			<xsl:when test="contains($text, ' ')"><!-- When the text has multiple words -->
				<!-- Capitalize the first word -->
				<xsl:call-template name="Tcapitalize">
					<xsl:with-param name="text" select="substring-before($text, ' ')"/>
				</xsl:call-template>
				<!-- Add a space -->
				<xsl:text> </xsl:text>
				<!-- And then make the rest of the word lowercase -->
				<xsl:call-template name="Tcamelcase">
					<xsl:with-param name="text" select="substring-after($text, ' ')"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise><!-- When there is only one word, capitalize it -->
				<xsl:call-template name="Tcapitalize">
					<xsl:with-param name="text" select="$text"/>
				</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>