"""
====================================================================
 JIRA: SVC-1910 — Fix Legacy XML Parser Character Encoding
====================================================================
 P1 | Points: 2 | Labels: legacy, python

 XML feed from legacy ERP system uses ISO-8859-1 encoding but parser
 assumes UTF-8. Special characters (é, ñ, ü) corrupt data.

 ACCEPTANCE CRITERIA:
 - [ ] Auto-detect encoding from XML declaration
 - [ ] Handle BOM (Byte Order Mark)
 - [ ] Fall back to ISO-8859-1 if no declaration
====================================================================
"""

import xml.etree.ElementTree as ET

class LegacyXmlParser:
    def parse(self, xml_string):
        # BUG: Always assumes UTF-8 — crashes on ISO-8859-1 characters
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            # BUG: Swallows error — returns empty dict instead of failing
            return {}

        return self._element_to_dict(root)

    def _element_to_dict(self, element):
        result = {}
        for child in element:
            # BUG: Overwrites duplicate elements — only keeps last value
            # XML like <items><item>A</item><item>B</item></items> loses 'A'
            result[child.tag] = child.text or ''
            if len(child) > 0:
                result[child.tag] = self._element_to_dict(child)
        return result

    def parse_file(self, filepath):
        # BUG: Reads as text (UTF-8 default) — binary read with encoding detection needed
        with open(filepath, 'r') as f:
            content = f.read()
        return self.parse(content)


# Tests
if __name__ == '__main__':
    xml = '<root><name>José García</name><items><item>A</item><item>B</item></items></root>'
    parser = LegacyXmlParser()
    result = parser.parse(xml)
    assert result.get('name') == 'José García', f"FAIL: Encoding issue: {result.get('name')}"
    print("XML parser tests passed!")
