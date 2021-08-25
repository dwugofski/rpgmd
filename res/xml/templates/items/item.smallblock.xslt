<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:import href="../common/xslt/smallblock/header.xslt"/>
	<xsl:import href="../common/xslt/smallblock/action.xslt"/>
	<xsl:import href="../common/xslt/smallblock/rich_text.xslt"/>

	<!-- Documentation intended for XslDoc -->

	<!-- 
		========================================================================
		Stat Block Header Bar
		========================================================================
	-->

	<!--**
		Displays the header bar of a statblock
	-->
	<xsl:template match="src:item">
		<div class="statblock item">
			<!-- Give the ID of the item -->
			<xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
			<!-- Make the header -->
			<xsl:choose>
				<xsl:when test="./src:level = 'var'">
					<xsl:call-template name="header">
						<xsl:with-param name="name" select="./src:name"/>
						<xsl:with-param name="type">Item</xsl:with-param>
						<xsl:with-param name="level" select="./src:variants/src:variant[1]/src:level"/>
						<xsl:with-param name="var" select="1"/>
					</xsl:call-template>
				</xsl:when>
				<xsl:otherwise>
					<xsl:call-template name="header">
						<xsl:with-param name="name" select="./src:name"/>
						<xsl:with-param name="type">Item</xsl:with-param>
						<xsl:with-param name="level" select="./src:level"/>
					</xsl:call-template>
				</xsl:otherwise>
			</xsl:choose>
			<!-- Trait list -->
			<div class="statblock_tags">
				<xsl:for-each select="src:traits/src:trait">
					<xsl:choose>
						<xsl:when test="@type != ''">
							<div class="statblock_tag {@type}"><xsl:value-of select="."/></div>
						</xsl:when>
						<xsl:otherwise>
							<div class="statblock_tag"><xsl:value-of select="."/></div>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:for-each>
			</div>
			<!-- Item header information -->
			<!-- The price (for a non-variant item) -->
			<div class="statblock_section">
				<xsl:if test="src:price">
					<p class="reverse_indent"><xsl:apply-templates select="src:price"/></p>
				</xsl:if>
				<p class="reverse_indent">
					<!-- How to use the item -->
					<xsl:if test="src:usage">
						<xsl:apply-templates select="src:usage"/>
						<xsl:if test="src:bulk">
							<xsl:text>; </xsl:text>
						</xsl:if>
					</xsl:if>
					<xsl:apply-templates select="src:bulk"/>
				</p>
			</div>
			<!-- Item description -->
			<div class="statblock_section">
				<xsl:apply-templates select="src:description"/>
			</div>
			<!-- Item variant information -->
			<xsl:for-each select="src:variants/src:variant">
				<div class="statblock_section">
					<p class="reverse_indent">
						<strong><xsl:text>Type </xsl:text></strong>
						<xsl:value-of select="src:type"/>
						<xsl:if test="src:level">
							<xsl:if test="src:type">
								<xsl:text>; </xsl:text>
							</xsl:if>
							<strong><xsl:text>Level </xsl:text></strong>
							<xsl:value-of select="src:level"/>
						</xsl:if>
						<xsl:if test="src:price">
							<xsl:if test="(src:level) or (src:type)">
								<xsl:text>; </xsl:text>
							</xsl:if>
							<xsl:apply-templates select="src:price"/>
						</xsl:if>
					</p>
					<xsl:apply-templates select="src:description"/>
				</div>
			</xsl:for-each>
		</div>
	</xsl:template>

	<!--**
		Description text
	-->
	<xsl:template match="src:description">
		<xsl:apply-templates/>
	</xsl:template>

	<!--**
		Describes how an item is activated
	-->
	<xsl:template match="src:activate">
		<p>
			<strong><xsl:text>Activate </xsl:text></strong>
			<xsl:call-template name="action_count">
				<xsl:with-param name="num" select="./src:action/src:act_count"/>
			</xsl:call-template>
			<xsl:value-of select="./src:action/src:name"/><xsl:text>; </xsl:text>
			<xsl:if test="./src:action/src:trigger">
				<strong><xsl:text>Trigger </xsl:text></strong>
				<xsl:value-of select="./src:action/src:trigger"/><xsl:text>; </xsl:text>
			</xsl:if>
			<strong><xsl:text>Effect </xsl:text></strong>
			<!-- Add the first paragraph in-line -->
			<xsl:apply-templates select="./src:effect/src:p[1]" mode="enclosed_rich_paragraph"/>
		</p>
		<!-- Should add the rest of the effect description as separate paragraphs -->
		<xsl:for-each select="./src:effect/src:p">
			<xsl:if test="position() > 1">
				<xsl:apply-templates/>
			</xsl:if>
		</xsl:for-each>
	</xsl:template>

	<!--**
		Provides the price of an item
	-->
	<xsl:template match="src:price">
		<strong><xsl:text>Price </xsl:text></strong>
		<xsl:value-of select="src:int"/>
		<xsl:text> </xsl:text>
		<xsl:value-of select="src:money"/>
		<xsl:if test="src:special">
			<xsl:text> </xsl:text>
			<xsl:value-of select="src:special"/>
		</xsl:if>
	</xsl:template>

	<!--**
		Describes how an item is used
	-->
	<xsl:template match="src:usage">
		<strong><xsl:text>Usage </xsl:text></strong>
		<xsl:choose>
			<xsl:when test="src:held">
				<!-- For held items -->
				<xsl:text>held in </xsl:text>
				<xsl:choose>
					<xsl:when test="src:held != 1"><xsl:value-of select="src:held"/><xsl:text> hands</xsl:text></xsl:when>
					<xsl:otherwise><xsl:text>1 hand</xsl:text></xsl:otherwise>
				</xsl:choose>
			</xsl:when>
		</xsl:choose>
	</xsl:template>

	<!--**
		Describes the bulk of an item
	-->
	<xsl:template match="src:bulk">
		<strong><xsl:text>Bulk </xsl:text></strong>
		<xsl:choose>
			<xsl:when test=". = none">&#8212;</xsl:when>
			<xsl:when test=". = light">L</xsl:when>
			<xsl:otherwise><xsl:value-of select="."/></xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>