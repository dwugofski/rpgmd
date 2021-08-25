<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Action items
		========================================================================
	-->

	<!--**
		Displays the action points an action takes

		param: num (int[1:3]/string) Either the number of action points the
			action takes (if int) or the string description of what the action
			takes (e.g. 'passive', 'free', or 'reaction')
	-->
	<xsl:template name="action_count">
		<xsl:param name="num"/>
		<xsl:choose>
			<xsl:when test="$num = 'passive'"></xsl:when>
			<xsl:when test="$num = 'free'"><xsl:text>(free) </xsl:text></xsl:when>
			<xsl:when test="$num = 'reaction'"><xsl:text>(reaction) </xsl:text></xsl:when>
			<xsl:when test="$num = 1"><xsl:text>(1) </xsl:text></xsl:when>
			<xsl:when test="$num = 2"><xsl:text>(2) </xsl:text></xsl:when>
			<xsl:when test="$num = 3"><xsl:text>(3) </xsl:text></xsl:when>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>