<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
<xsl:output method="xml" indent="yes" encoding="utf-8" omit-xml-declaration="yes" />

<xsl:param name="source_language" />
<xsl:param name="target_language" />
<xsl:param name="rev_parent" />

<xsl:key name="speaker-table" match="speaker" use="@id"/>

<xsl:template match="/">
<xsl:text>{"resource":
{"cards":{
"array":[</xsl:text>
	<xsl:apply-templates />
<xsl:text>]},
"headings":{"array":[{"text":"phrase"},{"text":"audio"},{"text":"language"},{"text":"speaker"}]},
"tags": {"array": [{"value": "source:</xsl:text><xsl:value-of select="$source_language" />
<xsl:text>"}, {"value": "target:</xsl:text><xsl:value-of select="$target_language" />
<xsl:text>"},{"value": "wikibabel"}]},
"interactions":{"array":[{"resource":{"audio":"1","transcript":"0","@create":"{http://wikiotics.org/ns/2011/flashcards}audio_lesson_interaction"}}]},
</xsl:text>
<xsl:if test="$rev_parent = '' ">
	<xsl:text>"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard_deck"</xsl:text>
</xsl:if>
<xsl:if test="string($rev_parent) != '' ">
	<xsl:text>"@patch":"</xsl:text><xsl:value-of select="$rev_parent" /><xsl:text>"</xsl:text>
</xsl:if>
<xsl:text>}}</xsl:text>
</xsl:template>


<xsl:template match="head/lessontitle">
	<!-- do nothing here, but this prevents the title from being printed at the beginning of the html output -->
</xsl:template>
<xsl:template match="Lesson/sentence">
<xsl:choose>
<xsl:when test="string(source) != '' or string(source/@sound) != ''">
	<xsl:text>{"resource":{"sides":{"array":[</xsl:text>
			<!-- text of the line -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="source" /><xsl:text>"}}},</xsl:text>
			<!-- audio -->
			<xsl:if test="string(source/@sound) != '' ">
			<xsl:text>{"href":"</xsl:text><xsl:value-of select="source/@sound" /><xsl:text>"},</xsl:text>
			</xsl:if>
			<xsl:if test="string(source/@sound) = '' ">
			<xsl:text>{"resource":null},</xsl:text>
			</xsl:if>
			<!-- language -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="$source_language" /><xsl:text>"}}},</xsl:text>
			<!-- speaker -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text>
				<!--<xsl:value-of select="key('speaker-table',source/@speaker)/@name"/>-->
			<xsl:text>"}}}
	]},
	"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard"
	}},</xsl:text>
</xsl:when>
</xsl:choose>
<xsl:text>{"resource":{"sides":{"array":[</xsl:text>
                <!-- text of the line -->
                <xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="target" /><xsl:text>"}}},</xsl:text>
		<!-- audio -->
                <xsl:if test="string(target/@sound) != '' ">
		<xsl:text>{"href":"</xsl:text><xsl:value-of select="target/@sound" /><xsl:text>"},</xsl:text>
		</xsl:if>
		<xsl:if test="string(target/@sound) = '' ">
		<xsl:text>{"resource":null},</xsl:text>
		</xsl:if>
		<!-- language -->
		<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="$target_language" /><xsl:text>"}}},</xsl:text>
		<!-- speaker -->
		<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text>
			<!--<xsl:variable name="trgspkr" select="key('speaker-table',target/@speaker)/@name"/>
			<xsl:choose>
				<xsl:when test="$trgspkr != ''"><xsl:value-of select="$trgspkr" />: </xsl:when>
				<xsl:when test="$trgspkr = ''"><xsl:value-of select="target/@speaker" />: </xsl:when>
			</xsl:choose>-->
		<xsl:text>"}}}
]},
"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard"
}},</xsl:text>
</xsl:template>

<xsl:template match="Lesson/comment">
	<xsl:text>{"resource":{"sides":{"array":[</xsl:text>
		<!-- text of the line -->
		<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="text" /><xsl:text>"}}},</xsl:text>
		<xsl:if test="string(text/@sound) != '' ">
			<!-- audio -->
			<xsl:text>{"href":"</xsl:text><xsl:value-of select="text/@sound" /><xsl:text>"},</xsl:text>
			<!-- language -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="$source_language" /><xsl:text>"}}},</xsl:text>
			<!-- speaker -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text>
				<xsl:value-of select="@speaker" />
				<!--<xsl:variable name="commspkr" select="key('speaker-table',text/@speaker)/@name"/>
				<xsl:choose>
					<xsl:when test="$commspkr != ''"><xsl:value-of select="$commspkr" /> : </xsl:when>
					<xsl:when test="$commspkr = ''"><xsl:value-of select="text/@speaker" /> : </xsl:when>
				</xsl:choose>-->
			<xsl:text>"}}}</xsl:text>
		</xsl:if>
		<xsl:if test="string(text/@sound) = '' ">
			<!-- audio -->
			<xsl:text>{"resource":null},</xsl:text>
			<!-- language -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text><xsl:value-of select="$source_language" /><xsl:text>"}}},</xsl:text>
			<!-- speaker -->
			<xsl:text>{"resource":{"@create":"{http://wikiotics.org/ns/2011/phrase}phrase", "phrase":{"text":"</xsl:text>
				<!--<xsl:value-of select="key('speaker-table',text/@speaker)/@name"/>-->
			<xsl:text>"}}}</xsl:text>
		</xsl:if>
		<xsl:text>]},
"@create":"{http://wikiotics.org/ns/2011/flashcards}flashcard"
}},</xsl:text>
</xsl:template>
</xsl:stylesheet>
