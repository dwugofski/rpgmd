<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="3.0"
	xmlns="http://www.w3.org/1999/html"
	xmlns:src="https://github.com/dwugofski/rpgml/coc" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:import href="../common/xslt/text_transform.xslt"/>
	<xsl:import href="../common/xslt/html/rich_text.xslt"/>

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Stat Block Header Bar
		========================================================================
	-->

	<!--**
		Displays the statblock
	-->
	<xsl:template match="src:creature">
		<div class="statblock creature">
			<!-- Give the ID of the creature -->
			<xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>

			<!-- Give the Name, Subname of the creature -->
			<div class="header">
				<!-- Give the Name of the creature in all caps -->
				<xsl:call-template name="Tall_caps">
					<xsl:with-param name="text" select="./src:name"/>
				</xsl:call-template>
				<!-- Give the Subname of the creature, with the first letter in caps -->
				<xsl:value-of select="./src:name"/>
				<xsl:if test="./src:subname">
					<xsl:text>, </xsl:text>
					<xsl:call-template name="Tcapitalize_first">
						<xsl:with-param name="text" select="./src:subname"/>
					</xsl:call-template>
				</xsl:if>
			</div>

			<!-- Give the characteristics of the creature -->
			<div class="characteristics">
				<p><strong>STR</strong></p>
			</div>

		</div>
	</xsl:template>

</xsl:stylesheet>