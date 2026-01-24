## eXtensible Stylesheet Language Transformation (XSLT) is a language enabling the transformation of XML documents. For instance, it can select specific nodes from an XML document and change the XML structure.

- xsl:template>: This element indicates an XSL template. It can contain a match attribute that contains a path in the XML document that the template applies to
- <xsl:value-of>: This element extracts the value of the XML node specified in the select attribute
- <xsl:for-each>: This element enables looping over all XML nodes specified in the select attribute
- <xsl:sort>: This element specifies how to sort elements in a for loop in the select argument. Additionally, a sort order may be specified in the order argument
- <xsl:if>: This element can be used to test for conditions on a node. The condition is specified in the test argument.

## XSLT Injection
As the name suggests, XSLT injection occurs whenever user input is inserted into XSL data before the XSLT processor generates output. This enables an attacker to inject additional XSL elements into the XSL data, which the XSLT processor will execute during the output generation process.
