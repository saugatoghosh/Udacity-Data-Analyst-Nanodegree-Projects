
# coding: utf-8

# In[3]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
To do so you will parse the elements in the OSM XML file, transforming them from document format to
tabular format, thus making it possible to write to .csv files.  These csv files can then easily be
imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the 
cerberus library we can validate the output against this schema to ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
  and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they should be ignored and kept as part of
  the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.

The final return value for a "node" element should look something like:

{'node': {'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
       'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
      'changeset': 5288876},
 'node_tags': [{'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'name',
                'value': "Shelly's Tasty Freeze",
                'type': 'regular'}]}

### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element

The final return value for a "way" element should look something like:

{'way': {'id': 209809850,
         'user': 'chicago-buildings',
         'uid': 674454,
         'version': '1',
         'timestamp': '2013-03-13T15:58:04Z',
         'changeset': 15353317},
 'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
 'way_tags': [{'id': 209809850,
               'key': 'housenumber',
               'type': 'addr',
               'value': '1412'},
              {'id': 209809850,
               'key': 'street',
               'type': 'addr',
               'value': 'West Lexington St.'},
              {'id': 209809850,
               'key': 'street:name',
               'type': 'addr',
               'value': 'Lexington'},
              {'id': '209809850',
               'key': 'street:prefix',
               'type': 'addr',
               'value': 'West'},
              {'id': 209809850,
               'key': 'street:type',
               'type': 'addr',
               'value': 'Street'},
              {'id': 209809850,
               'key': 'building',
               'type': 'regular',
               'value': 'yes'},
              {'id': 209809850,
               'key': 'levels',
               'type': 'building',
               'value': '1'},
              {'id': 209809850,
               'key': 'building_id',
               'type': 'chicago',
               'value': '366409'}]}
"""

import csv
import codecs
import re
import os
import pprint
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_FILE = 'new_delhi.osm'

OSM_PATH = OSM_FILE

NODES_PATH = "nodes_project.csv"
NODE_TAGS_PATH = "nodes_tags_project.csv"
WAYS_PATH = "ways_project.csv"
WAY_NODES_PATH = "ways_nodes_project.csv"
WAY_TAGS_PATH = "ways_tags_project.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Relevant functions for cleaning 'addr:street'

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")



mapping = {'Ln':'Lane',
           'Delhi-110021':'Delhi',
           'Rd,':'Road',
           'Marg,':'Marg',
           'Pahargan':'Paharganj',
           'Delhi.':'Delhi',
           'bazar':'Bazaar',
           'Bazar':'Bazaar',
           'Bazar,':'Bazaar',
           'Gali': 'Lane',
           'Gandi':'Gandhi',
           'Counnaught':'Connaught',
           '10':''
           }

def string_case(s): 
    if s.isupper():
        return s
    else:
        return s.title()

# Update streetname by splitting the string to clean streetname wherever 
# it appears in the string

def update_street_name(name, mapping):
    name = name.split(" ")
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    name = " ".join(name)
    return name

#Relevant functions for cleaning 'addr:postcode'

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

#Clean valid postcodes only
mapping2 = {
    '110 001':'110001',
    '110 021':'110021',
    '110031v':'110031',
    '1100002':'110002',
    }

def update_postcode(postcode, mapping):
    if postcode in mapping:
            postcode = mapping[postcode]
    else:
        postcode = postcode
    return postcode

# Relevant code for cleaning 'addr:city'

def is_city(elem):
    return (elem.attrib['k'] == "addr:city")

#Clean valid city name

mapping3 = {
    'Delh': 'Delhi',
    'New Delhi, Delhi':'New Delhi',
    'Pandav Nagar, New Delhi':'New Delhi',
    'Chanakyapuri, New Delhi':'New Delhi'
}

def update_city(city, mapping):
    if city in mapping:
            city = mapping[city]
            city = string_case(city)
    else:
        city = string_case(city)
    return city



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item] = element.attrib[item]
        for tag in element.iter("tag"):
            nodes_tag = {} 
            nodes_tag['id'] = element.attrib['id']
            
            if re.search(problem_chars,tag.attrib['k']) is not None:
                continue
            else:
                m = LOWER_COLON.search(tag.attrib['k'])#We try to find out if the key is made with " : " format or only word.
                if m is None:
                    nodes_tag['key'] = tag.attrib['k']
                    nodes_tag['type'] = 'regular'
                    nodes_tag['value'] = tag.attrib['v']
                else:
                    
                    if is_street_name(tag):
                        nodes_tag['value'] = update_street_name(tag.attrib['v'], mapping)
                    elif is_post_code(tag):
                        if not tag.attrib['v'].startswith('11'):
                            continue
                        else:
                            nodes_tag['value'] = update_postcode(tag.attrib['v'], mapping2)
                    elif is_city(tag):
                        if tag.attrib['v'] == 'noida':
                            continue
                        else:
                            nodes_tag['value'] = update_city(tag.attrib['v'], mapping3)
                    else:
                        nodes_tag['value'] = tag.attrib['v']
                    
                    nodes_tag['key'] = tag.attrib['k'].split(":",1)[1]
                    nodes_tag['type'] = tag.attrib['k'].split(":",1)[0]
                        
            
            tags.append(nodes_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for item in way_attr_fields:
            way_attribs[item] = element.attrib[item]
        for tag in element.iter("tag"):
            ways_tag = {}
            ways_tag['id'] = element.attrib['id']
            if re.search(problem_chars,tag.attrib['k']) is not None:
                continue
            else:
                m = LOWER_COLON.search(tag.attrib['k'])#We try to find out if the key is made with " : " format or only word.
                if m is None:
                    ways_tag['key'] = tag.attrib['k']
                    ways_tag['type'] = 'regular'
                    ways_tag['value'] = tag.attrib['v']
                else:
                    if is_street_name(tag):
                        ways_tag['value'] = update_street_name(tag.attrib['v'], mapping)
                    elif is_post_code(tag):
                        if not tag.attrib['v'].startswith('11'):
                            continue
                        else:
                            ways_tag['value'] = update_postcode(tag.attrib['v'], mapping2)
                    elif is_city(tag):
                        if tag.attrib['v'] == 'noida':
                            continue
                        else:
                            ways_tag['value'] = update_city(tag.attrib['v'], mapping3)
                        
                    else:
                        ways_tag['value'] = tag.attrib['v']
                    
                    ways_tag['key'] = tag.attrib['k'].split(":",1)[1]
                    ways_tag['type'] = tag.attrib['k'].split(":",1)[0]
            tags.append(ways_tag)
        i = 0
        for tag in element.iter("nd"):
            way_nodes_tag = {}
            way_nodes_tag['id'] = element.attrib['id']
            way_nodes_tag['node_id'] = tag.attrib['ref']
            way_nodes_tag['position'] = i
            i = i+1
            way_nodes.append(way_nodes_tag)
            
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])



    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
process_map(OSM_PATH, validate=False)



# In[ ]:



