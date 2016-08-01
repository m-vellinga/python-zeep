import pytest
from lxml import etree

from tests.utils import assert_nodes_equal, load_xml
from zeep import xsd
from zeep.exceptions import XMLParseError
from zeep.helpers import serialize_object


def test_choice_element():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType>
              <xsd:choice>
                <xsd:element name="item_1" type="xsd:string" />
                <xsd:element name="item_2" type="xsd:string" />
                <xsd:element name="item_3" type="xsd:string" />
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """.strip())
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')

    value = element(item_1="foo")
    assert value.item_1 == 'foo'
    assert value.item_2 is None
    assert value.item_3 is None

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)

    value = element.parse(node.getchildren()[0], schema)
    assert value.item_1 == 'foo'
    assert value.item_2 is None
    assert value.item_3 is None


def test_choice_element_second_elm():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType>
              <xsd:choice>
                <xsd:element name="item_1" type="xsd:string" />
                <xsd:element name="item_2" type="xsd:string" />
                <xsd:element name="item_3" type="xsd:string" />
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """.strip())
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')

    value = element(item_2="foo")
    assert value.item_1 is None
    assert value.item_2 == 'foo'
    assert value.item_3 is None

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_2>foo</ns0:item_2>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)

    value = element.parse(node.getchildren()[0], schema)
    assert value.item_1 is None
    assert value.item_2 == 'foo'
    assert value.item_3 is None


def test_choice_element_multiple():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType>
              <xsd:choice maxOccurs="3">
                <xsd:element name="item_1" type="xsd:string" />
                <xsd:element name="item_2" type="xsd:string" />
                <xsd:element name="item_3" type="xsd:string" />
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """.strip())
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')

    value = element(_value_1=[
        {'item_1': 'foo'}, {'item_2': 'bar'}, {'item_1': 'three'},
    ])
    assert value._value_1 == [
        {'item_1': 'foo'}, {'item_2': 'bar'}, {'item_1': 'three'},
    ]

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
          <ns0:item_1>three</ns0:item_1>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)

    value = element.parse(node.getchildren()[0], schema)
    assert value._value_1 == [
        {'item_1': 'foo'}, {'item_2': 'bar'}, {'item_1': 'three'},
    ]


def test_choice_element_optional():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType>
              <xsd:sequence>
                <xsd:choice minOccurs="0">
                  <xsd:element name="item_1" type="xsd:string" />
                  <xsd:element name="item_2" type="xsd:string" />
                  <xsd:element name="item_3" type="xsd:string" />
                </xsd:choice>
                <xsd:element name="item_4" type="xsd:string" />
             </xsd:sequence>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """.strip())
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    value = element(item_4="foo")

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_4>foo</ns0:item_4>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)


def test_choice_optional_values():
    schema = load_xml("""
        <xsd:schema
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:tns="http://tests.python-zeep.org/"
            targetNamespace="http://tests.python-zeep.org/"
            elementFormDefault="qualified">
          <xsd:complexType name="Transport">
            <xsd:sequence>
                <xsd:choice minOccurs="0" maxOccurs="1">
                    <xsd:element name="item" type="xsd:string"/>
                </xsd:choice>
            </xsd:sequence>
          </xsd:complexType>
        </xsd:schema>
    """)
    schema = xsd.Schema(schema)

    node = load_xml("<Transport></Transport>")
    elm = schema.get_type('ns0:Transport')
    elm.parse_xmlelement(node, schema)


def test_choice_in_sequence():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="Address">
            <xsd:complexType>
              <xsd:sequence>
                <xsd:element name="something" type="xsd:string" />
                <xsd:choice>
                  <xsd:element name="item_1" type="xsd:string" />
                  <xsd:element name="item_2" type="xsd:string" />
                  <xsd:element name="item_3" type="xsd:string" />
                </xsd:choice>
              </xsd:sequence>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """.strip())
    schema = xsd.Schema(node)
    address_type = schema.get_element('ns0:Address')

    assert address_type.type.signature() == (
        'something: xsd:string, ({item_1: xsd:string} | {item_2: xsd:string} | {item_3: xsd:string})')  # noqa
    address_type(item_1="foo")


def test_choice_with_sequence():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice>
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:sequence>
                    <xsd:element name="item_3" type="xsd:string"/>
                    <xsd:element name="item_4" type="xsd:string"/>
                </xsd:sequence>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    assert element.type.signature() == (
        '({item_1: xsd:string, item_2: xsd:string} | {item_3: xsd:string, item_4: xsd:string})')
    value = element(item_1='foo', item_2='bar')

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)


def test_choice_with_sequence_once():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:sequence>
                <xsd:element name="item_0" type="xsd:string"/>
                <xsd:choice>
                  <xsd:sequence>
                      <xsd:element name="item_1" type="xsd:string"/>
                      <xsd:element name="item_2" type="xsd:string"/>
                  </xsd:sequence>
                </xsd:choice>
              </xsd:sequence>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    assert element.type.signature() == (
        'item_0: xsd:string, ({item_1: xsd:string, item_2: xsd:string})')
    value = element(item_0='nul', item_1='foo', item_2='bar')

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_0>nul</ns0:item_0>
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)


def test_choice_with_sequence_second():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice>
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:sequence>
                    <xsd:element name="item_3" type="xsd:string"/>
                    <xsd:element name="item_4" type="xsd:string"/>
                </xsd:sequence>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    assert element.type.signature() == (
        '({item_1: xsd:string, item_2: xsd:string} | {item_3: xsd:string, item_4: xsd:string})')
    value = element(item_3='foo', item_4='bar')

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_3>foo</ns0:item_3>
          <ns0:item_4>bar</ns0:item_4>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)


def test_choice_with_sequence_invalid():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice>
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:sequence>
                    <xsd:element name="item_3" type="xsd:string"/>
                    <xsd:element name="item_4" type="xsd:string"/>
                </xsd:sequence>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    assert element.type.signature() == (
        '({item_1: xsd:string, item_2: xsd:string} | {item_3: xsd:string, item_4: xsd:string})')

    with pytest.raises(TypeError):
        element(item_1='foo', item_4='bar')


def test_choice_with_sequence_change():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name='ElementName'>
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice>
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:sequence>
                    <xsd:element name="item_3" type="xsd:string"/>
                    <xsd:element name="item_4" type="xsd:string"/>
                </xsd:sequence>
                <xsd:element name="nee" type="xsd:string"/>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:ElementName')

    elm = element(item_1='foo', item_2='bar')
    assert serialize_object(elm) == {
        'item_3': None,
        'item_2': 'bar',
        'item_1': 'foo',
        'item_4': None,
        'nee': None
    }

    elm.item_1 = 'bla-1'
    elm.item_2 = 'bla-2'

    expected = """
      <document>
        <ns0:ElementName xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>bla-1</ns0:item_1>
          <ns0:item_2>bla-2</ns0:item_2>
        </ns0:ElementName>
      </document>
    """
    node = etree.Element('document')
    element.render(node, elm)
    assert_nodes_equal(expected, node)


def test_choice_with_sequence_change_named():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name='ElementName'>
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice>
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:element name="item_3" type="xsd:string"/>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:ElementName')
    elm = element(item_3='foo')
    elm = element(item_1='foo', item_2='bar')
    assert elm['item_1'] == 'foo'
    assert elm['item_2'] == 'bar'

    elm['item_1'] = 'bla-1'
    elm['item_2'] = 'bla-2'

    expected = """
      <document>
        <ns0:ElementName xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>bla-1</ns0:item_1>
          <ns0:item_2>bla-2</ns0:item_2>
        </ns0:ElementName>
      </document>
    """
    node = etree.Element('document')
    element.render(node, elm)
    assert_nodes_equal(expected, node)


def test_choice_with_sequence_multiple():
    node = load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice maxOccurs="2">
                <xsd:sequence>
                    <xsd:element name="item_1" type="xsd:string"/>
                    <xsd:element name="item_2" type="xsd:string"/>
                </xsd:sequence>
                <xsd:sequence>
                    <xsd:element name="item_3" type="xsd:string"/>
                    <xsd:element name="item_4" type="xsd:string"/>
                </xsd:sequence>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """)
    schema = xsd.Schema(node)
    element = schema.get_element('ns0:container')
    assert element.type.signature() == (
        '({item_1: xsd:string, item_2: xsd:string} | {item_3: xsd:string, item_4: xsd:string})[]')
    value = element(_value_1=[
        dict(item_1='foo', item_2='bar'),
        dict(item_3='foo', item_4='bar'),
    ])

    expected = """
      <document>
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
          <ns0:item_3>foo</ns0:item_3>
          <ns0:item_4>bar</ns0:item_4>
        </ns0:container>
      </document>
    """
    node = etree.Element('document')
    element.render(node, value)
    assert_nodes_equal(expected, node)


def test_element_ref_in_choice():
    node = etree.fromstring("""
        <?xml version="1.0"?>
        <schema xmlns="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                targetNamespace="http://tests.python-zeep.org/"
                   elementFormDefault="qualified">
          <element name="foo" type="string"/>
          <element name="bar" type="string"/>
          <element name="container">
            <complexType>
              <sequence>
                <choice>
                  <element ref="tns:foo"/>
                  <element ref="tns:bar"/>
                </choice>
              </sequence>
            </complexType>
          </element>
        </schema>
    """.strip())

    schema = xsd.Schema(node)

    foo_type = schema.get_element('{http://tests.python-zeep.org/}foo')
    assert isinstance(foo_type.type, xsd.String)

    custom_type = schema.get_element('{http://tests.python-zeep.org/}container')

    value = custom_type(foo='bar')
    assert value.foo == 'bar'
    assert value.bar is None

    node = etree.Element('document')
    custom_type.render(node, value)
    expected = """
        <document>
            <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
                <ns0:foo>bar</ns0:foo>
            </ns0:container>
        </document>
    """
    assert_nodes_equal(expected, node)


def test_parse_dont_loop():
    schema = xsd.Schema(load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice maxOccurs="unbounded">
                <xsd:element name="item_1" type="xsd:string"/>
                <xsd:element name="item_2" type="xsd:string"/>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """))

    element = schema.get_element('ns0:container')
    expected = load_xml("""
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
          <ns0:item_3>foo</ns0:item_3>
          <ns0:item_4>bar</ns0:item_4>
        </ns0:container>
    """)
    with pytest.raises(XMLParseError):
        element.parse(expected, schema)


def test_parse_check_unexpected():
    schema = xsd.Schema(load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:choice maxOccurs="unbounded">
                <xsd:element name="item_1" type="xsd:string"/>
                <xsd:element name="item_2" type="xsd:string"/>
              </xsd:choice>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """))

    element = schema.get_element('ns0:container')
    expected = load_xml("""
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
          <ns0:item_3>foo</ns0:item_3>
        </ns0:container>
    """)
    with pytest.raises(XMLParseError):
        element.parse(expected, schema)


def test_parse_check_mixed():
    schema = xsd.Schema(load_xml("""
        <?xml version="1.0"?>
        <xsd:schema
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://tests.python-zeep.org/"
                elementFormDefault="qualified"
                targetNamespace="http://tests.python-zeep.org/">
          <xsd:element name="container">
            <xsd:complexType xmlns:xsd="http://www.w3.org/2001/XMLSchema">
              <xsd:sequence>
                <xsd:choice maxOccurs="unbounded">
                  <xsd:element name="item_1" type="xsd:string"/>
                  <xsd:element name="item_2" type="xsd:string"/>
                </xsd:choice>
                <xsd:element name="item_3" type="xsd:string"/>
              </xsd:sequence>
            </xsd:complexType>
          </xsd:element>
        </xsd:schema>
    """))

    element = schema.get_element('ns0:container')
    expected = load_xml("""
        <ns0:container xmlns:ns0="http://tests.python-zeep.org/">
          <ns0:item_1>foo</ns0:item_1>
          <ns0:item_2>bar</ns0:item_2>
          <ns0:item_3>foo</ns0:item_3>
        </ns0:container>
    """)
    element.parse(expected, schema)
