<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:src="https://github.com/dwugofski/p2e_mons" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- 
	============================================================================
	 Capitalization
	============================================================================
-->
<!-- variables to keep track of uppercase and lowercase letters -->
<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸŽŠŒ'"/>
<xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿžšœ'"/>

<!-- Capitalize the starting letter of a block of text -->
<xsl:template name="capitalize_first">
	<xsl:param name="text"/>
	<xsl:value-of select="translate(substring($text,1,1),$lowercase,$uppercase)"/><xsl:value-of select="substring($text,2,string-length($text)-1)"/>
</xsl:template>

<!-- Capitalize the starting letter of a block of text, make everything else lowercase -->
<xsl:template name="capitalize">
	<xsl:param name="text"/>
	<xsl:value-of select="translate(substring($text,1,1),$lowercase,$uppercase)"/><xsl:value-of select="translate(substring($text,2,string-length($text)-1),$uppercase,$lowercase)"/>
</xsl:template>

<!-- Capitalize the starting letter of each word in a block of text, and all other letters lowercase -->
<xsl:template name="camelcase">
	<xsl:param name="text"/>
	<xsl:choose>
		<xsl:when test="contains($text, ' ')"><!-- When the text has multiple words -->
			<!-- Capitalize the first word -->
			<xsl:call-template name="capitalize">
				<xsl:with-param name="text" select="substring-before($text, ' ')"/>
			</xsl:call-template>
			<!-- Add a space -->
			<xsl:text> </xsl:text>
			<!-- And then make the rest of the word lowercase -->
			<xsl:call-template name="camelcase">
				<xsl:with-param name="text" select="substring-after($text, ' ')"/>
			</xsl:call-template>
		</xsl:when>
		<xsl:otherwise><!-- When there is only one word, capitalize it -->
			<xsl:call-template name="capitalize">
				<xsl:with-param name="text" select="$text"/>
			</xsl:call-template>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- 
	============================================================================
	 Main block
	============================================================================
-->
<!-- The main template: match each p2emon element -->
<xsl:template match="src:p2emon">
	<div class="statblock npc">
		<!-- Set the "id" attribute of the p2emon block to the "id" attribute of the p2emon element -->
		<xsl:attribute name="id">
			<xsl:text>__npc_statblock_</xsl:text><xsl:value-of select="@id"/><xsl:text>__</xsl:text>
		</xsl:attribute>
		<!-- The header, containing the name and level of the creature -->
		<div class="statblock_header">
			<h1 class="fl"><xsl:value-of select="src:name"/></h1>
			<h2 class="fr">Creature <xsl:value-of select="src:level"/></h2>
			<div class="clearer"></div>
		</div>
		<!-- Display the traits in boxes below the header -->
		<div class="statblock_tags">
			<!-- Need to translate between rarity levels. If the rarity is common, then we can ignore it -->
			<xsl:choose>
				<xsl:when test="src:rarity = 'uncommon'"><div class="statblock_tag rarity">Unommon</div></xsl:when>
				<xsl:when test="src:rarity = 'rare'"><div class="statblock_tag rarity">Rare</div></xsl:when>
				<xsl:when test="src:rarity = 'legendary'"><div class="statblock_tag rarity">Legendary</div></xsl:when>
				<xsl:when test="src:rarity = 'unique'"><div class="statblock_tag rarity">Unique</div></xsl:when>
			</xsl:choose>
			<!-- Need to translate alignment types -->
			<xsl:choose>
				<xsl:when test="src:alignment = 'lg'"><div class="statblock_tag alignment">LG</div></xsl:when>
				<xsl:when test="src:alignment = 'ng'"><div class="statblock_tag alignment">NG</div></xsl:when>
				<xsl:when test="src:alignment = 'cg'"><div class="statblock_tag alignment">CG</div></xsl:when>
				<xsl:when test="src:alignment = 'ln'"><div class="statblock_tag alignment">LN</div></xsl:when>
				<xsl:when test="src:alignment = 'n'"><div class="statblock_tag alignment">N</div></xsl:when>
				<xsl:when test="src:alignment = 'cn'"><div class="statblock_tag alignment">CN</div></xsl:when>
				<xsl:when test="src:alignment = 'le'"><div class="statblock_tag alignment">LE</div></xsl:when>
				<xsl:when test="src:alignment = 'ne'"><div class="statblock_tag alignment">NE</div></xsl:when>
				<xsl:when test="src:alignment = 'ce'"><div class="statblock_tag alignment">CE</div></xsl:when>
			</xsl:choose>
			<!-- Need to translate sizes -->
			<xsl:choose>
				<xsl:when test="src:size = 'tiny'"><div class="statblock_tag size">Tiny</div></xsl:when>
				<xsl:when test="src:size = 'small'"><div class="statblock_tag size">Small</div></xsl:when>
				<xsl:when test="src:size = 'medium'"><div class="statblock_tag size">Medium</div></xsl:when>
				<xsl:when test="src:size = 'large'"><div class="statblock_tag size">Large</div></xsl:when>
				<xsl:when test="src:size = 'huge'"><div class="statblock_tag size">Huge</div></xsl:when>
				<xsl:when test="src:size = 'gargantuan'"><div class="statblock_tag size">Gargantuan</div></xsl:when>
			</xsl:choose>
			<!-- Special creature tags are listed here -->
			<xsl:apply-templates select="src:traits" mode="tag"/>
			<!-- The type of the creature (e.g. undead) is listed here -->
			<xsl:for-each select='src:types/src:type'>
				<div class="statblock_tag type"><xsl:value-of select='.'/></div>
			</xsl:for-each>
		</div>
		<!-- Specify the upper portion of the creature block -->
		<div class="statblock_npc_background">
			<!-- Perception can be of the form
				Perception +18 (+23 in special circumstances); darkvision 120 feet, blindsight 30 feet
			-->
			<p>
				<strong>Perception </strong>
				<xsl:apply-templates select="src:perception" mode="quantity"/>
			</p>
			<!-- Languages are just a list of strings -->
			<xsl:if test="count(src:languages/src:language) &gt; 0">
				<p>
					<strong>Languages </strong>
					<xsl:for-each select='src:languages/src:language'>
						<xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
						<xsl:call-template name="capitalize_first">
							<xsl:with-param name="text" select="."/>
						</xsl:call-template>
					</xsl:for-each>
				</p>
			</xsl:if>
			<!-- Skills are of the following form
				Skills Athletics +4 (+5 in special cases), Stealth +3, ...
			-->
			<xsl:if test="count(src:skills/src:skill) &gt; 0">
				<p>
					<strong>Skills </strong>
					<xsl:for-each select="src:skills/src:skill">
						<xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
						<xsl:call-template name="camelcase">
							<xsl:with-param name="text" select="src:name"/>
						</xsl:call-template>
						<xsl:text> </xsl:text>
						<xsl:apply-templates select="." mode="quantity"/>
					</xsl:for-each>
				</p>
			</xsl:if>
			<!--
				The ability modifiers are listed together

				Ability modifiers are presented in the following format
				STR +4 (+5 in special cases), DEX +3, CON +2, ...
			-->
			<p>
				<strong>STR </strong><xsl:apply-templates select="src:abilities/src:strength" mode="quantity"/><xsl:text>, </xsl:text>
				<strong>DEX </strong><xsl:apply-templates select="src:abilities/src:dexterity" mode="quantity"/><xsl:text>, </xsl:text>
				<strong>CON </strong><xsl:apply-templates select="src:abilities/src:constitution" mode="quantity"/><xsl:text>, </xsl:text>
				<strong>INT </strong><xsl:apply-templates select="src:abilities/src:intelligence" mode="quantity"/><xsl:text>, </xsl:text>
				<strong>WIS </strong><xsl:apply-templates select="src:abilities/src:wisdom" mode="quantity"/><xsl:text>, </xsl:text>
				<strong>CHA </strong><xsl:apply-templates select="src:abilities/src:charisma" mode="quantity"/>
			</p>
			<!-- Items are shown here -->
			<xsl:if test="count(src:items/src:item) != 0">
				<p>
					<strong>Items </strong>
					<xsl:apply-templates select="src:items/src:item"/>
				</p>
			</xsl:if>
			<!--
				Interactions cover details about how the creature interacts with the world (e.g. becoming broken, being used a certain way) that are typically not relevant in combat

				Interactions are of the form
				[Interaction Name] [Description of interactions]
			-->
			<xsl:apply-templates select="src:interactions/src:feat"/>
		</div>
		<!-- 
			The middle section covers AC, saves, hitpoints, immunities, weaknesses, resistances, and features that tend to proc off-turn
		-->
		<div class="statblock_npc_offturns">
			<!--
				AC and saves are listed together, as well as universal modifiers to saves
				
				AC is of the form:
				AC 14 (18 with mage armor), all-around vision

				Saves are of the form:
				[Fort|Ref|Will] +4 (+8 in special cases)

				Unversial modifier to saves are displayed
				(+1 to all saves against magic)
			-->
			<p>
				<strong>AC </strong><xsl:apply-templates select="src:armors/src:armor" mode="quantity_flat"/>
				<xsl:text>; </xsl:text>
				<strong>Fort </strong><xsl:apply-templates select="src:saves/src:fortitude" mode="quantity"/>
				<xsl:text>, </xsl:text>
				<strong>Ref </strong><xsl:apply-templates select="src:saves/src:reflex" mode="quantity"/>
				<xsl:text>, </xsl:text>
				<strong>Will </strong><xsl:apply-templates select="src:saves/src:will" mode="quantity"/>
				<xsl:if test="count(src:saves/src:modifier) &gt; 0">
					<xsl:text> (</xsl:text><xsl:value-of select="src:saves/src:modifier"/><xsl:text>)</xsl:text>
				</xsl:if>
				<xsl:if test="count(src:saves/src:specials/src:special) &gt; 0">
					<xsl:text>; </xsl:text>
					<xsl:for-each select="src:saves/src:specials/src:special">
						<xsl:if test="position() &gt; 1">
							<xsl:text>, </xsl:text>
						</xsl:if>
						<xsl:apply-templates/>
					</xsl:for-each>
				</xsl:if>
			</p>
			<!--
				HP, immunities, weaknesses, and saves are all displayed together

				Hitpoints are displayed in the following format:
				HP 300 (184 in special cases), negative healing

				Immunities are displayed in the following format:
				Immunities fire, cold, electricity, ...

				Weaknesses and Resistances are displayed in the following format:
				[Weaknesses|Resistances] fire 10, cold 13 (15 in special cases)
			-->
			<p>
				<strong>HP </strong><xsl:apply-templates select="src:hitpoints" mode="quantity_flat"/>
				<xsl:if test="count(src:hardness) &gt; 0">
					<xsl:text>; </xsl:text>
					<strong>Hardness </strong><xsl:apply-templates select="src:hardness" mode="quantity_flat"/>
				</xsl:if>
				<xsl:if test="count(src:immunities/src:immunity) &gt; 0">
					<xsl:text>; </xsl:text>
					<strong>Immunities </strong><xsl:apply-templates select="src:immunities" mode="list_csv"/>
				</xsl:if>
				<xsl:if test="count(src:weaknesses/src:weakness) &gt; 0">
					<xsl:text>; </xsl:text>
					<strong>Weaknesses </strong><xsl:apply-templates select="src:weaknesses" mode="list_quantity"/>
				</xsl:if>
				<xsl:if test="count(src:resistances/src:resistance) &gt; 0">
					<xsl:text>; </xsl:text>
					<strong>Resistances </strong><xsl:apply-templates select="src:resistances" mode="list_quantity_flat"/>
				</xsl:if>
			</p>
			<!--
				List feats here that are mostly relevant on other creatures' turns
			-->
			<xsl:apply-templates select="src:offturn/src:feat"/>
		</div>
		<!-- The lower section covers speed, actions, spells, and feats relevant on a creature's turn -->
		<div class="statblock_npc_onturns">
			<!--
				If the creature has some form of speed definition (which they always should)
				Display the speed, including non-land speeds

				The speed spec is displayed as follows:
				Speed 40 ft; flying 120 ft; climb 30 ft; ...
			-->
			<xsl:if test="count(src:speeds/src:speed) != 0">
				<p>
					<strong>Speed </strong>
					<xsl:for-each select="src:speeds/src:speed">
						<xsl:if test="position() &gt; 0">, </xsl:if>
						<xsl:if test="src:name != 'land'"><xsl:value-of select="src:name"/><xsl:text> </xsl:text></xsl:if>
						<xsl:apply-templates select="src:base" mode="int_num"/>
						<xsl:if test="count(src:modifier) != 0">
							<xsl:text> (</xsl:text><xsl:value-of select="src:modifier"/><xsl:text>)</xsl:text>
						</xsl:if>
						<xsl:text> </xsl:text>
						<xsl:if test="count(src:units) != 0"><xsl:value-of select="src:units"/></xsl:if>
						<xsl:if test="count(src:units) = 0"><xsl:value-of select="../src:units"/></xsl:if>
					</xsl:for-each>
					<xsl:if test="count(src:speeds/src:special) != 0">
						<xsl:text>; </xsl:text>
						<xsl:for-each select="src:speeds/src:special">
							<xsl:if test="position() &gt; count(../src:speed)">, </xsl:if>
							<xsl:value-of select="."/>
						</xsl:for-each>
					</xsl:if>
				</p>
			</xsl:if>
			<!--
				Display the actions

				Actions are displayed as follows:
				[Melee | Ranged] action name [>|>>|>>>|-|<-] +18 (trait1, trait2, ...), [Damage | Effect] [Damage description]
			-->
			<xsl:for-each select="src:actions/*">
				<xsl:apply-templates select="."/>
			</xsl:for-each>
			<!--
				Display spell repertories
			-->
			<xsl:apply-templates select="src:spells/src:spelllist"/>
			<!--
				Display feats relating to thing the creature can do on their turn
			-->
			<xsl:apply-templates select="src:onturn/src:feat"/>
		</div>
	</div>
</xsl:template>

<!-- 
	============================================================================
	 Actions
	============================================================================
-->


<!-- 
	Produce the indicator representing the number of actions an action/activity/reaction takes
-->
<xsl:template name="count">
	<xsl:param name="countVal"/>
	<xsl:choose>
		<xsl:when test="$countVal = 'passive'"></xsl:when>
		<xsl:when test="$countVal = 'free'"><xsl:text>(free) </xsl:text></xsl:when>
		<xsl:when test="$countVal = 'reaction'"><xsl:text>(reaction) </xsl:text></xsl:when>
		<xsl:when test="$countVal = 1"><xsl:text>(1) </xsl:text></xsl:when>
		<xsl:when test="$countVal = 2"><xsl:text>(2) </xsl:text></xsl:when>
		<xsl:when test="$countVal = 3"><xsl:text>(3) </xsl:text></xsl:when>
	</xsl:choose>
</xsl:template>

<!--
	Count-matching front end
-->
<xsl:template match="src:count">
	<xsl:call-template name="count">
		<xsl:with-param name="countVal" select="."/>
	</xsl:call-template>
</xsl:template>

<!--
	Take a complicated results list and produce an outcome string. This can take the following form, for example

	Damage: 1d4+5 fire
	Damage: 1d4+5 fire plus 1d8 cold
	Damage: 1d4+5 fire plus 1d8 cold and 1d12 lightning
	Damage: 1d4+5 fire plus 1d8 cold, 1d12 lightning, and Grab

	or

	Effect: Special Effect
	Effect: Special Effect plus Grab
	Effect: Special Effect plus Grab and Knockdown
	Effect: Special Effect plus Grab, Knockdown, and Other Effect
-->
<xsl:template match="src:results">
	<xsl:if test="count(src:damage) != 0">
		<strong>Damage </strong>
	</xsl:if>
	<xsl:if test="count(src:damage) = 0">
		<strong>Effect </strong>
	</xsl:if>
	<xsl:for-each select="src:damage | src:effect">
		<xsl:if test="position() = 2"><xsl:text> plus </xsl:text></xsl:if>
		<xsl:if test="position() > 2 and count(../src:damage | ../src:effect) > 3">
			<xsl:text>, </xsl:text>
			<xsl:if test="position() != last()"><xsl:text> </xsl:text></xsl:if>
		</xsl:if>
		<xsl:if test="position() = last() and count(../src:damage | ../src:effect) > 2">and </xsl:if>
		<xsl:if test="local-name() = 'damage'">
			<xsl:value-of select="src:dice"/><xsl:text> </xsl:text><xsl:value-of select="src:type"/>
		</xsl:if>
		<xsl:if test="local-name() != 'damage'">
			<xsl:value-of select="."/>
		</xsl:if>
	</xsl:for-each>
</xsl:template>

<!--
	For an attack, the information is displayed

	{'Melee' | 'Ranged'} <ActionCount> <Name> +<AttackMod>[ (<Traits>)], {'Damage' | 'Effect'} <ResultsDesc>
-->
<xsl:template match="src:attack">
	<p>
		<strong>
			<!-- 'melee' or 'ranged' inputs are enforced by schema -->
			<xsl:call-template name='camelcase'>
				<xsl:with-param name='text' select='src:type'/>
			</xsl:call-template>
			<xsl:text> </xsl:text>
		</strong>
		<xsl:apply-templates select="src:count"/>
		<xsl:value-of select="src:name"/><xsl:text> </xsl:text>
		<xsl:apply-templates select="src:modifier" mode="modifier_num"/>
		<xsl:if test="count(src:traits) &gt; 0">
			<xsl:text> (</xsl:text><xsl:apply-templates select="src:traits" mode="list_csv"/><xsl:text>)</xsl:text>
		</xsl:if>
		<xsl:text>, </xsl:text>
		<xsl:apply-templates select="src:results"/>
	</p>
</xsl:template>

<!--
	A constrict special action takes the form

	Constrict <ActionCount> <ResultsDesc>, DC <DC>[ (<Qualifier>)]
-->
<xsl:template match="src:constrict">
	<p>
		<strong>Constrict </strong>
		<xsl:call-template name="count">
			<xsl:with-param name="countVal">1</xsl:with-param>
		</xsl:call-template>
		<xsl:apply-templates select="src:results"/>
		<xsl:text>, DC </xsl:text>
		<xsl:value-of select="src:base"/>
		<xsl:if test="count(src:qualifier) &gt; 0">
			<xsl:text> (</xsl:text><xsl:value-of select="src:qualifier"/><xsl:text>)</xsl:text>
		</xsl:if>
	</p>
</xsl:template>

<!-- 
	============================================================================
	 Spell Repertoires
	============================================================================
-->

<!-- 
	Each creature with spells has one or more lists of spells they can cast. Each list is a "repertoire" of spells. The repertoires are specified by tradtion (e.g. "arcane") and casting type (e.g. "spontaneous")
	
	The repertoire is displayed as follows:
	<Tradition> <Castingtype> Spell[s] DC <DC>[, attack +<attack> [(<modifier text>)][; <trait1>, <trait2>, ...]]; <slotlevel1>th[ (<height>th)][ (<slot count> slot[s])] <spell1>, <spell2>, ...; <slotlevel2>th...

	Where spell names are in italics
-->
<xsl:template match="src:spelllist">
	<p>
		<strong>
			<xsl:choose>
				<xsl:when test="src:tradition = 'arcane'">Arcane</xsl:when>
				<xsl:when test="src:tradition = 'divine'">Divine</xsl:when>
				<xsl:when test="src:tradition = 'occult'">Occult</xsl:when>
				<xsl:when test="src:tradition = 'primal'">Primal</xsl:when>
			</xsl:choose>
			<xsl:text> </xsl:text>
			<xsl:choose>
				<xsl:when test="src:type = 'prepared'">Prepared</xsl:when>
				<xsl:when test="src:type = 'spontaneous'">Spontaneous</xsl:when>
				<xsl:when test="src:type = 'innate'">Innate</xsl:when>
				<xsl:when test="src:type = 'focus'">Focus</xsl:when>
				<xsl:when test="src:type = 'ritual'">Ritual</xsl:when>
			</xsl:choose>
			<xsl:text> </xsl:text>
			<xsl:choose>
				<xsl:when test="count(.//src:spell) &gt; 1">
					<xsl:text>Spells </xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:text>Spell </xsl:text>
				</xsl:otherwise>
			</xsl:choose>
		</strong>
		<xsl:text>DC </xsl:text><xsl:value-of select="src:difficulty"/>
		<xsl:if test="count(src:attack) != 0">
			<xsl:text>, attack </xsl:text><xsl:apply-templates select="src:attack" mode="quantity"/>
		</xsl:if>
		<xsl:text>; </xsl:text>
		<xsl:for-each select="src:group">
			<strong>
				<xsl:apply-templates select="src:level" mode="enumeration"/>
				<xsl:if test="count(src:height) != 0">
					<xsl:text> (</xsl:text>
					<xsl:apply-templates select="src:height" mode="enumeration"/>
					<xsl:text>)</xsl:text>
				</xsl:if>
			</strong>
			<xsl:if test="count(src:slots) != 0">
				<xsl:choose>
					<xsl:when test="src:slots = 1"><xsl:text> (1 slot)</xsl:text></xsl:when>
					<xsl:otherwise> (<xsl:value-of select="src:slots"/> slots)</xsl:otherwise>
				</xsl:choose>
			</xsl:if>
			<xsl:text> </xsl:text>
			<xsl:for-each select="src:spell">
				<xsl:if test="position() != 1"><xsl:text>, </xsl:text></xsl:if>
				<em><xsl:value-of select="src:name"/></em>
				<xsl:if test="count(src:slots) != 0">
					<xsl:text> </xsl:text>
					<xsl:text>(x</xsl:text><xsl:value-of select="."/><xsl:text>)</xsl:text>
				</xsl:if>
			</xsl:for-each>
			<xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
		</xsl:for-each>
	</p>
</xsl:template>

<!--
	Present the modifier "th" suffix following a number (e.g. for spell levels)

	Form:
	<number><"st" | "nd" | "rd" | "th">
-->
<xsl:template match="*" mode="enumeration">
	<xsl:choose>
		<xsl:when test=". = 1"><xsl:text>1st</xsl:text></xsl:when>
		<xsl:when test=". = 2"><xsl:text>2nd</xsl:text></xsl:when>
		<xsl:when test=". = 3"><xsl:text>3rd</xsl:text></xsl:when>
		<xsl:when test=". &gt;= 4"><xsl:value-of select="."/><xsl:text>th</xsl:text></xsl:when>
		<xsl:otherwise>
			<xsl:call-template name="camelcase">
				<xsl:with-param name="text" select="."/>
			</xsl:call-template>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- 
	============================================================================
	 Lists
	============================================================================
-->

<!--
	List values, separated by commas
-->
<xsl:template match="*" mode="list_csv">
	<xsl:for-each select="./*">
		<xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
		<xsl:value-of select="."/>
	</xsl:for-each>
</xsl:template>

<!--
	List values, separated by spaces
-->
<xsl:template match="*" mode="list_space">
	<xsl:for-each select="./*">
		<xsl:if test="position() &gt; 1"><xsl:text> </xsl:text></xsl:if>
		<xsl:value-of select="."/>
	</xsl:for-each>
</xsl:template>

<!--
	List quantities, separated by commas

	Will be of the form:
	[<quanity1 name> ]<+ or -><abs(quantity1)>[ (<quantity1 modifier>)][ q1t1, q1t2, ...], [<quantity2 name>]<+ or -><abs(quantity2)>...
-->
<xsl:template match="*" mode="list_quantity">
	<xsl:for-each select="./*">
		<xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
		<xsl:if test="count(src:name) != 0">
			<xsl:value-of select="src:name"/>
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:apply-templates select='.' mode="quantity"/>
	</xsl:for-each>
</xsl:template>

<!--
	List quantities, separated by commas, but do not prefix positive values with "+"

	Will be of the form:
	[<quanity1 name> ]<quantity1>[ (<quantity1 modifier>)][ q1t1, q1t2, ...], [<quantity2 name>][-]<quantity2>...
-->
<xsl:template match="*" mode="list_quantity_flat">
	<xsl:for-each select="./*">
		<xsl:if test="position() &gt; 1"><xsl:text>, </xsl:text></xsl:if>
		<xsl:if test="count(src:name) != 0">
			<xsl:value-of select="src:name"/>
			<xsl:text> </xsl:text>
		</xsl:if>
		<xsl:apply-templates select='.' mode="quantity_flat"/>
	</xsl:for-each>
</xsl:template>

<!-- 
	============================================================================
	 Quantities
	============================================================================
-->

<!--
	Present a numeric quantity

	The quantity will be of the form
	<+ or -><abs(quantity)>[ (<quantity modifier>)][ trait1, trait2, ...]
-->
<xsl:template match="*" mode="quantity">
	<xsl:apply-templates select="src:base" mode="modifier_num"/>
	<xsl:if test="count(src:modifier) &gt; 0">
		<xsl:text> (</xsl:text><xsl:value-of select="src:modifier"/><xsl:text>)</xsl:text>
	</xsl:if>
	<xsl:if test="count(src:traits/src:trait) &gt; 0">
		<xsl:text>, </xsl:text>
		<xsl:apply-templates select="src:traits" mode="list_space"/>
	</xsl:if>
	<xsl:if test="count(src:specials/src:special) &gt; 0">
		<xsl:text>; </xsl:text>
		<xsl:for-each select="src:specials/src:special">
			<xsl:if test="position() &gt; 1">
				<xsl:text>, </xsl:text>
			</xsl:if>
			<xsl:apply-templates/>
		</xsl:for-each>
	</xsl:if>
</xsl:template>

<!--
	Present a numeric quantity without the + sign for a positive quantity

	The quantity will be of the form
	<quantity>[ (<quantity modifier>)][ trait1, trait2, ...]
-->
<xsl:template match="*" mode="quantity_flat">
	<xsl:apply-templates select="src:base" mode="int_num"/>
	<xsl:if test="count(src:modifier) &gt; 0">
		<xsl:text> (</xsl:text><xsl:value-of select="src:modifier"/><xsl:text>)</xsl:text>
	</xsl:if>
	<xsl:if test="count(src:traits/src:trait) &gt; 0">
		<xsl:text>, </xsl:text>
		<xsl:apply-templates select="src:traits" mode="list_space"/>
	</xsl:if>
	<xsl:if test="count(src:specials/src:special) &gt; 0">
		<xsl:text>; </xsl:text>
		<xsl:for-each select="src:specials/src:special">
			<xsl:if test="position() &gt; 1">
				<xsl:text>, </xsl:text>
			</xsl:if>
			<xsl:apply-templates/>
		</xsl:for-each>
	</xsl:if>
</xsl:template>

<!--
	Present a numeric quantity without the + sign for a positive quantity, with
	traits listed as comma-separated values

	The quantity will be of the form
	[-]<quantity>[ (<quantity modifier>)][ trait1, trait2, ...]
-->
<xsl:template match="*" mode="quantity_csv">
	<xsl:apply-templates select="src:base" mode="int_num"/>
	<xsl:if test="count(src:modifier) &gt; 0">
		<xsl:text> (</xsl:text><xsl:value-of select="src:modifier"/><xsl:text>)</xsl:text>
	</xsl:if>
	<xsl:if test="count(src:traits/src:trait) &gt; 0">
		<xsl:text>; </xsl:text>
		<xsl:apply-templates select="src:traits" mode="list_csv"/>
	</xsl:if>
	<xsl:if test="count(src:specials/src:special) &gt; 0">
		<xsl:text>; </xsl:text>
		<xsl:for-each select="src:specials/src:special">
			<xsl:if test="position() &gt; 1">
				<xsl:text>, </xsl:text>
			</xsl:if>
			<xsl:apply-templates/>
		</xsl:for-each>
	</xsl:if>
</xsl:template>

<!--
	Present a number, but placing a + sign in front of a positive number and a - sign in front of a negative one

	Form:
	<value's sign><abs(value)>
-->
<xsl:template match="*" mode="modifier_num">
	<xsl:if test='. &gt;= 0'>
		<xsl:text>+</xsl:text>
	</xsl:if>
	<xsl:apply-templates select="." mode="int_num"/>
</xsl:template>

<!--
	Output a number with proper commas
-->
<xsl:template match="*" mode="int_num">
	<xsl:choose>
		<xsl:when test='. &gt; 9999'>
			<xsl:value-of select="format-number(., '###,##0')"/>
		</xsl:when>
		<xsl:when test='. &lt; -9999'>
			<xsl:value-of select="format-number(., '###,##0')"/>
		</xsl:when>
		<xsl:otherwise>
			<xsl:value-of select="format-number(., '###0')"/>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- 
	============================================================================
	 Feats and Descriptions
	============================================================================
-->
<!-- 
	Present a feat

	Form:
	<feat name> [<action icon> ][(<trait1>, <trait2>, ...) ]<description>
-->
<xsl:template match="src:feat">
	<p>
		<strong><xsl:value-of select="src:name"/><xsl:text> </xsl:text></strong>
		<xsl:apply-templates select="src:count"/>
		<xsl:if test="count(src:traits/src:trait) != 0">
			<xsl:text>(</xsl:text><xsl:apply-templates select="src:traits" mode="list_csv"/><xsl:text>) </xsl:text>
		</xsl:if>
		<xsl:apply-templates select="src:description"/>
	</p>
</xsl:template>

<!--
	Present a list of traits in tag form
-->
<xsl:template match="src:traits" mode="tag">
	<xsl:for-each select="src:trait">
		<div class="statblock_tag trait"><xsl:value-of select="."></xsl:value-of></div>
	</xsl:for-each>
</xsl:template>

<!--
 Translate bold text
-->
<xsl:template match='src:b'>
	<strong>
		<xsl:apply-templates/>
	</strong>
</xsl:template>

<!--
 Translate italicized text
-->
<xsl:template match='src:i'>
	<em>
		<xsl:apply-templates/>
	</em>
</xsl:template>

<!--
	Present a complex (html-formatted) description block
-->
<xsl:template match="src:description">
	<span class="desc">
		<xsl:apply-templates/>
	</span>
</xsl:template>

<!--
	Present a complex (html-formatted) special block
-->
<xsl:template match="src:special">
	<span class="desc">
		<xsl:apply-templates/>
	</span>
</xsl:template>

<!-- 
	Handle the "entry" type of sub-description
-->
<xsl:template match="src:entry">
	<p>
		<strong><xsl:value-of select="src:name"/></strong>
		<xsl:apply-templates select="src:description"/>
	</p>
</xsl:template>

<!--
	Handle an "item" object, which can be italicized
-->
<xsl:template match="src:item">
	<span class="desc">
		<!--<xsl:copy-of select="node() | @*"/>-->
		<xsl:apply-templates />
		<xsl:if test="position() != last()">
			<xsl:text>, </xsl:text>
		</xsl:if>
	</span>
</xsl:template>


</xsl:stylesheet>