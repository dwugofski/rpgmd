<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Stat Block Header Bar
		========================================================================
	-->

	<!--**
		Displays the header bar of a statblock
	-->
	<xsl:template name="header">
		<xsl:param name="name"/>
		<xsl:param name="type"/>
		<xsl:param name="level" select="NaN"/>
		<xsl:param name="var" select="0"/>
		<!-- Header -->
		<div class="statblock_header">
			<h1 class="fl"><xsl:value-of select="$name"/></h1>
			<h2 class="fr">
				<xsl:value-of select="$type"/>
				<xsl:text> </xsl:text>
				<xsl:value-of select="$level"/>
				<!-- Add a + if we have a number of variants -->
				<xsl:if test="$var > 0"><xsl:text>+</xsl:text></xsl:if>
			</h2>
			<div class="clearer"></div>
		</div>
	</xsl:template>

</xsl:stylesheet>