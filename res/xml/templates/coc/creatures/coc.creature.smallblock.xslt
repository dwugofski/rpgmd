<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="3.0"
	xmlns="http://www.w3.org/1999/xhtml"
	xmlns:coc="https://github.com/dwugofski/rpgml/coc"
	xmlns:rpgml="https://github.com/dwugofski/rpgml"
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
	<xsl:template match="coc:creature">
		<div class="statblock creature">
			<!-- Give the ID of the creature -->
			<xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>

			<!-- Give the Name, Subname of the creature -->
			<div class="header">
				<h1>
					<!-- Give the Name of the creature in all caps -->
					<xsl:call-template name="Tall_caps">
						<xsl:with-param name="text" select="./rpgml:name"/>
					</xsl:call-template>
					<!-- Give the Subname of the creature, with the first letter in caps -->
					<xsl:if test="./coc:subname">
						<xsl:text>, </xsl:text>
						<xsl:value-of select="./coc:subname"/>
					</xsl:if>
				</h1>
			</div>

			<!-- Give the characteristics of the creature -->
			<div class="characteristics">
				<p>
					<xsl:for-each select="./coc:characteristics/coc:char">
						<xsl:apply-templates select="."/>
						<xsl:if test="position() != last()">
							<xsl:text> </xsl:text>
						</xsl:if>
					</xsl:for-each>
				</p>
			</div>

			<!-- Give the core stats of the creature -->
			<div class="core_stats">
				<xsl:if test="./coc:sanity">
					<!-- Sanity -->
					<p>
						<strong>SAN:</strong><xsl:text> </xsl:text>
						<xsl:apply-templates select="./coc:sanity"/>
					</p>
				</xsl:if>
				<p>
					<!-- Hit points -->
					<strong>HP:</strong><xsl:text> </xsl:text>
					<xsl:apply-templates select="./coc:hitpoints"/>
				</p>
				<p>
					<!-- Damage Bonus -->
					<strong>Damage Bonus:</strong><xsl:text> </xsl:text>
					<xsl:apply-templates select="./coc:damage-bonus"/>
				</p>
				<p>
					<!-- Build -->
					<strong>Build:</strong><xsl:text> </xsl:text>
					<xsl:apply-templates select="./coc:build"/>
				</p>
				<p>
					<!-- Move -->
					<strong>Move:</strong><xsl:text> </xsl:text>
					<xsl:apply-templates select="./coc:move"/>
				</p>
				<xsl:if test="./coc:horror">
					<!-- Sanity loss -->
					<p>
						<strong>Sanity Loss:</strong>
						<xsl:text> </xsl:text>
						<xsl:apply-templates select="./coc:horror"/>
					</p>
				</xsl:if>
			</div>

			<!-- Actions, attacks, and maneuvers -->
			<div class="actions">
				<p>
					<!-- Attacks -->
					<strong>Attacks:</strong><xsl:text> </xsl:text>
					<xsl:apply-templates select="./coc:attacks"/>
				</p>
				<xsl:if test="./coc:fighting">
					<!-- Fighting -->
					<p>
						<strong>Fighting:</strong><xsl:text> </xsl:text>
						<xsl:apply-templates select="./coc:fighting"/>
					</p>
				</xsl:if>
				<xsl:if test="./coc:dodge">
					<!-- Dodge -->
					<p>
						<strong>Dodge:</strong><xsl:text> </xsl:text>
						<xsl:apply-templates select="./coc:dodge"/>
					</p>
				</xsl:if>
				<xsl:if test="./coc:armor">
					<!-- Armor -->
					<p>
						<strong>
							<xsl:text>Armor (</xsl:text>
							<xsl:value-of select="./coc:armor/rpgml:name"/>
							<xsl:text>):</xsl:text>
						</strong>
						<xsl:text> </xsl:text>
						<xsl:apply-templates select="./coc:armor"/>
					</p>
				</xsl:if>
				<xsl:apply-templates select="./coc:maneuvers/coc:maneuver"/>
			</div>

			<!-- Skills -->
			<div class="skills">
				<p>
					<strong><xsl:text>Skills:</xsl:text></strong>
					<xsl:text> </xsl:text>
					<xsl:for-each select="./coc:skills/coc:skill">
						<xsl:call-template name="Tcamelcase">
							<xsl:with-param name="text" select="./rpgml:name"/>
						</xsl:call-template>
						<xsl:text> </xsl:text>
						<xsl:apply-templates select="."/>
						<xsl:if test="position() != last()">
							<xsl:text>, </xsl:text>
						</xsl:if>
					</xsl:for-each>
				</p>
			</div>

			<!-- Descriptive Flavor Text -->
			<div class="specials">
				<xsl:apply-templates select="./coc:specials/coc:special"/>
			</div>

		</div>
	</xsl:template>

	<!--**
		Translates a characteristic
	-->
	<xsl:template match="coc:char">
		<span class="characteristic">
			<strong>
				<xsl:choose>
					<xsl:when test="@name = 'strength'"><xsl:text>STR</xsl:text></xsl:when>
					<xsl:when test="@name = 'constitution'"><xsl:text>CON</xsl:text></xsl:when>
					<xsl:when test="@name = 'size'"><xsl:text>SIZ</xsl:text></xsl:when>
					<xsl:when test="@name = 'dexterity'"><xsl:text>DEX</xsl:text></xsl:when>
					<xsl:when test="@name = 'power'"><xsl:text>POW</xsl:text></xsl:when>
				</xsl:choose>
			</strong>
			<xsl:text> </xsl:text>
			<xsl:apply-templates select="./rpgml:dec | ./rpgml:int | ./rpgml:na | ./rpgml:nan | ./rpgml:null | ./rpgml:varies | ./coc:chance"/>
			<xsl:if test="./rpgml:modifier">
				<xsl:text> (</xsl:text>
				<xsl:value-of select="./rpgml:modifier"/>
				<xsl:text>)</xsl:text>
			</xsl:if>
		</span>
	</xsl:template>

	<!--**
		Translates a percent chance for something
	-->
	<xsl:template match="coc:chance">
		<span class="value chance"><xsl:value-of select="."/><xsl:text>%</xsl:text></span>
		<xsl:text> (</xsl:text>
		<span class="int">
			<xsl:choose>
				<xsl:when test="../coc:hard">
					<xsl:value-of select="../coc:hard"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="floor(number(.) div 2)"/>
				</xsl:otherwise>
			</xsl:choose>
		</span>
		<xsl:text>/</xsl:text>
		<span class="int">
			<xsl:choose>
				<xsl:when test="../coc:extreme">
					<xsl:value-of select="../coc:extreme"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="floor(number(.) div 5)"/>
				</xsl:otherwise>
			</xsl:choose>
		</span>
		<xsl:text>)</xsl:text>
	</xsl:template>

	<!--**
		Translates a modified value
	-->
	<xsl:template name="modifiedValue" match="coc:hitpoints | coc:damage-bonus | coc:build | coc:move | coc:alternate | coc:attacks | coc:fighting | coc:dodge | coc:armor | coc:skill | coc:sanity | coc:magic | coc:horror">
		<xsl:apply-templates select="./rpgml:dec | ./rpgml:int | ./rpgml:roll | ./rpgml:na | ./rpgml:nan | ./rpgml:null | ./rpgml:varies | ./coc:chance"/>
		<xsl:if test="./rpgml:modifier">
			<xsl:text> (</xsl:text>
			<xsl:apply-templates select="./rpgml:modifier"/>
			<xsl:text>)</xsl:text>
		</xsl:if>
		<xsl:if test="./coc:effect">
			<xsl:text> </xsl:text>
			<xsl:apply-templates select="./coc:effect/node()"/>
		</xsl:if>
		<xsl:if test="./rpgml:extra">
			<xsl:text>. </xsl:text>
			<xsl:apply-templates select="./rpgml:extra"/>
		</xsl:if>
	</xsl:template>

	<!--**
		Translate a special
	-->
	<xsl:template match="coc:special">
		<div class="special">
			<p>
				<strong>
					<xsl:value-of select="./rpgml:name"/>
				</strong>
				<xsl:choose>
					<xsl:when test="@type='maneuver'">
						<strong><xsl:text> (mnvr)</xsl:text></strong>
					</xsl:when>
				</xsl:choose>
				<xsl:text>: </xsl:text>
				<xsl:apply-templates select="rpgml:description/rpgml:p[1]/node()"/>
			</p>
			<xsl:apply-templates select="rpgml:description/*[position()>1]"/>
		</div>
	</xsl:template>

	<!--**
		Translate a maneuver
	-->
	<xsl:template match="coc:maneuver">
		<div class="maneuver">
			<p>
				<strong>
					<xsl:value-of select="./rpgml:name"/>
					<xsl:text> (mnvr)</xsl:text>
				</strong>
				<xsl:text>: </xsl:text>
				<xsl:apply-templates select="rpgml:description/rpgml:p[1]/node()"/>
			</p>
			<xsl:apply-templates select="rpgml:description/*[position()>1]"/>
		</div>
	</xsl:template>

	<!--**
		Translate a sanity check into text
	-->
	<xsl:template match="coc:horror">
		<xsl:choose>
			<xsl:when test="count(./rpgml:int | ./rpgml:roll) > 1">
				<xsl:apply-templates select="(./rpgml:int | ./rpgml:roll)[1]"/>
				<xsl:text>/</xsl:text>
				<xsl:apply-templates select="(./rpgml:int | ./rpgml:roll)[2]"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates select="./rpgml:int | ./rpgml:roll"/>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:if test="./rpgml:modifier">
			<xsl:text> (</xsl:text>
			<xsl:apply-templates select="./rpgml:modifier"/>
			<xsl:text>)</xsl:text>
		</xsl:if>
		<xsl:if test="./coc:effect">
			<xsl:text> </xsl:text>
			<xsl:apply-templates select="./coc:effect/node()"/>
		</xsl:if>
		<xsl:if test="./rpgml:extra">
			<xsl:text>. </xsl:text>
			<xsl:apply-templates select="./rpgml:extra"/>
		</xsl:if>
	</xsl:template>

	<!--**
		Translate the damage bonus variable into text
	-->
	<xsl:template match="rpgml:var[@ref='dmg_bonus']">
		<span class="var dmg_bonus">
			<xsl:choose>
				<xsl:when test="../ancestor::coc:creature/coc:damage-bonus/rpgml:roll">
					<xsl:apply-templates select="../ancestor::coc:creature/coc:damage-bonus/rpgml:roll"/>
				</xsl:when>
				<xsl:when test="../ancestor::coc:creature/coc:damage-bonus/rpgml:int">
					<xsl:apply-templates select="../ancestor::coc:creature/coc:damage-bonus/rpgml:int"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:text>damage bonus</xsl:text>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:if test="../ancestor::coc:creature/coc:damage-bonus/rpgml:modifier">
				<xsl:text>*</xsl:text>
			</xsl:if>
		</span>
	</xsl:template>

</xsl:stylesheet>