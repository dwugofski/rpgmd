<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	version="2.0"
	xmlns:src="https://github.com/dwugofski/p2e" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<!-- Documentation intended for XslDoc -->

	<!-- This requires XSLT 2.0 so cannot be done for now -->

	<!-- 
		========================================================================
		Lists of P2E Traits
		========================================================================
	-->

	<!--**
		 traits for P2E
	-->
	<xsl:variable name="v__traits" select="^()$"/>

	<!--**
		General traits for P2E
	-->
	<xsl:variable name="v_general_traits" select="^(additive|archetype|attack|aura|cantrip|charm|companion|complex|concentrate|consecration|curse|darkness|death|dedication|detection|disease|downtime|emotion|environmental|exploration|extradimensional|fear|flourish|focused|fortune|general|haunt|healing|incapacitation|infused|legacy|light|lineage|linguistic|magical|manipulate|mechanical|mental|metamagic|minion|misfortune|morph|move|multiclass|polymorph|possession|precious|prediction|press|reckless|resonant|revelation|scrying|secret|skill|sleep|social|splash|stamina|summoned|telepathy|teleportation|trap|vigilante|virulent|vocal)$"/>

	<!--**
		Alignment traits for P2E
	-->
	<xsl:variable name="v_alignment_traits" select="^(chaotic|evil|good|lawful)$"/>

	<!--**
		Ancestry traits for P2E
	-->
	<xsl:variable name="v_ancestry_traits" select="^(aasimar|android|aphorite|azaketi|beastkin|catfolk|changeling|conrasu|dhampir|duskwalker|dwarf|elf|fetchling|fleshwarp|ganzi|geniekin|gnome|goblin
		half-elf|halfling|half-orc|hobgoblin|human|ifrit|kitsune|kobold|leshy|lizardfolk|orc|oread|ratfolk|shoony|sprite|strix|suli|sylph|tengu|tiefling|undine)$"/>

	<!--**
		Armor traits for P2E
	-->
	<xsl:variable name="v_armor_traits" select="^(bulwark|comfort|flexible|noisy)$"/>

	<!--**
		Class traits for P2E
	-->
	<xsl:variable name="v_class_traits" select="^(alchemist|barbarian|bard|champion|cleric|druid|fighter|investigator|monk|oracle|ranger|rogue|sorcerer|swashbuckler|witch|wizard)$"/>

	<!--**
		Class-specific traits for P2E
	-->
	<xsl:variable name="v_class_specific_traits" select="^(composition|cursebound|finisher|hex|instinct|litany|oath|rage|stance)$"/>

	<!--**
		Creature type traits for P2E
	-->
	<xsl:variable name="v_creature_type_traits" select="^(aberration|animal|astral|beast|celetial|construct|dragon|dream|elemental|ethereal|fey|fiend|fungus|giant|humanoid|monitor|negative|ooze|petitioner|plant|positive|spirit|time|undead)$"/>

	<!--**
		Elemental traits for P2E
	-->
	<xsl:variable name="v_elemental_traits" select="^(air|earth|fire|water)$"/>

	<!--**
		Energy traits for P2E
	-->
	<xsl:variable name="v_energy_traits" select="^(acid|cold|electricity|fire|force|negative|positive|sonic)$"/>

	<!--**
		Equipment traits for P2E
	-->
	<xsl:variable name="v_equipment_traits" select="^(alchemical|apex|artifact|bomb|consumable|contract|cursed|drug|elixir|intelligent|invested|mutagen|oil|potion|saggorak|scroll|snare|staff|structure|talisman|tattoo|wand)$"/>

	<!--**
		Monster traits for P2E
	-->
	<xsl:variable name="v_monster_traits" select="^(aasimar|acid|aeon|aesir|agathion|air|alchemical|amphibious|anadi|angel|aquatic|arcane|archon|asura|azata|boggard|calgini|catfolk|changeling|charau-ka|clockwork|cold|couatl|daemon|demon|dero|devil|dhampir|dinosaur|div|drow|duergar|dustwalker|earth|electricity|fetchling|fire|genie|ghoran|ghost|ghoul|gnoll|golem|gremlin|grioth|grippli|hag|herald|ifrit|illusion|incorporeal|inevitable|kami|kobold|kovintus|leshy|lizardfolk|locathah|merfolk|mindless|morlock|mortic|mummy|munavri|mutant|nagaji|nymph|oni|orc|oread|paaridar|phantom|protean|psychopomp|qlippoth|rakshasa|ratfolk|sahkil|samsaran|sea devil|serpentfolk|seugathi|shabti|sikempora|skeleton|skelm|skulk|sonic|soulbound|spriggan|sprite|stheno|suli|swarm|sylph|tane|tanggal|tengu|tiefling|titan|troll|troop|undine|urdefhan|vampire|velstrac|vishkanya|water|wayang|werecreature|wight|wraith|wyrwood|xulgath|zombie)$"/>

	<!--**
		Planar traits for P2E
	-->
	<xsl:variable name="v_planar_traits" select="^(air|earth|erratic|finite|fire|flowing|high gravity|immeasurable|low gravity|metamorphic|microgravity|negative|positive|sentient|shadow|static|strange gravity|subjective gravity|timeless|unbounded|water)$"/>

	<!--**
		Poison traits for P2E
	-->
	<xsl:variable name="v_poison_traits" select="^(contact|ingested|inhaled|injury|poison)$"/>

	<!--**
		Rarity traits for P2E
	-->
	<xsl:variable name="v_rarity_traits" select="^(common|rare|uncommon|unique)$"/>

	<!--**
		School traits for P2E
	-->
	<xsl:variable name="v_school_traits" select="^(abjuration|conjuration|divination|enchantment|evocation|illusion|necromancy|transmutation)$"/>

	<!--**
		Sense traits for P2E
	-->
	<xsl:variable name="v_sense_traits" select="^(auditory|olfactory|visual)$"/>

	<!--**
		Settlement traits for P2E
	-->
	<xsl:variable name="v_settlement_traits" select="^(city|metropolis|town|village)$"/>

	<!--**
		Tradition traits for P2E
	-->
	<xsl:variable name="v_tradition_traits" select="^(arcane|divine|occult|primal)$"/>

	<!--**
		Versatile heritage traits for P2E
	-->
	<xsl:variable name="v_versatile_heritage_traits" select="^(aasimar|changeling|dhampir|duskwalker|tiefling)$"/>

	<!--**
		Weapon traits for P2E
	-->
	<xsl:variable name="v_weapon_traits" select="^(agile|attached|azarketi|backstabber|backswing|brutal|catfolk|climbing|concealable|conrasu|deadly|disarm|dwarf|elf|fatal|finesse|forceful|free-hand|geniekin|gnome|goblin|grapple|halfling|hampering|jousting|kobold|modular|monk|nonlethal|parry|propulsive|range|ranged trip|reach|reload|repeating|shove|sweep|tethered|thrown|trip|twin|tow-hand|unarmed|versatile|volley)$"/>

	<xsl:variable name="v_trait_type_regex_map">
		<general><xsl:value-of select="$v_general_traits"/></general>
		<alignment><xsl:value-of select="$v_alignment_traits"/></alignment>
		<ancestry><xsl:value-of select="$v_ancestry_traits"/></ancestry>
		<armor><xsl:value-of select="$v_armor_traits"/></armor>
		<class><xsl:value-of select="$v_class_traits"/></class>
		<class_specific><xsl:value-of select="$v_class_specific_traits"/></class_specific>
		<creature><xsl:value-of select="$v_creature_traits"/></creature>
		<elemental><xsl:value-of select="$v_elemental_traits"/></elemental>
		<energy><xsl:value-of select="$v_energy_traits"/></energy>
		<equipment><xsl:value-of select="$v_equipment_traits"/></equipment>
		<monster><xsl:value-of select="$v_monster_traits"/></monster>
		<planar><xsl:value-of select="$v_planar_traits"/></planar>
		<poison><xsl:value-of select="$v_poison_traits"/></poison>
		<rarity><xsl:value-of select="$v_rarity_traits"/></rarity>
		<school><xsl:value-of select="$v_school_traits"/></school>
		<sense><xsl:value-of select="$v_sense_traits"/></sense>
		<settlement><xsl:value-of select="$v_settlement_traits"/></settlement>
		<tradition><xsl:value-of select="$v_tradition_traits"/></tradition>
		<versatile_heritage><xsl:value-of select="$v_versatile_heritage_traits"/></versatile_heritage>
		<weapon><xsl:value-of select="$v_weapon_traits"/></weapon>
	</xsl:variable>

	<!--**
		Template to get the type for a particular trait

		param: types (element) A comprehensive list of types to consider, in the
			form of the following XML element:
				<types>
					<type>type1</type1>
					<type>type2</type1>
					...
					<type>typeN</type1>
				</types>
			Leave unspecified to consider all types.
	-->
	<!--<xsl:template name="Ttrait_type">
		<xsl:param name="types">
			<types>
				<type>general</type>
				<type>alignment</type>
				<type>ancestry</type>
				<type>armor</type>
				<type>class</type>
				<type>class_specific</type>
				<type>creature</type>
				<type>elemental</type>
				<type>energy</type>
				<type>equipment</type>
				<type>monster</type>
				<type>planar</type>
				<type>poison</type>
				<type>rarity</type>
				<type>school</type>
				<type>sense</type>
				<type>settlement</type>
				<type>tradition</type>
				<type>versatile_heritage</type>
				<type>weapon</type>
			</types>
		</xsl:param>
		<xsl:for-each select="$types/type">
			<xsl:if test=""
		</xsl:for-each>
	</xsl:template>-->

</xsl:stylesheet>