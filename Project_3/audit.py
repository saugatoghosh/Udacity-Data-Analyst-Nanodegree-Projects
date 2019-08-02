
# coding: utf-8

# In[1]:

'''
Audit the keys 'addr:street', 'postcodes' and 'city' to remove errors and inconsistencies 

'''

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#Auditing functions for street types

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Avenue", "Bagh", "Bazaar", "Chowk", "Circle", "Circus", "Colony", "Complex","Delhi", "Estate", "Extension","Janpath","Lane", "Marg",
           "Market", "Nagar", "Park", "Path", "Place", "Road"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


# In[2]:

OSM_FILE = 'new_delhi.osm'
st_types = audit(OSM_FILE)
pprint.pprint(dict(st_types))


# In[3]:

# Mapping and functions for cleaning street types

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


# change string into titleCase except for UpperCase

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
    


# In[5]:

def test():
    st_types = audit(OSM_FILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_street_name(name, mapping)
            print name, "=>", better_name

test()


# In[10]:

# Audit postal codes

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def auditpostcode(osmfile):
    osm_file = open(osmfile, "r")
    postcodes = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_post_code(tag):
                    if tag.attrib['v'] not in postcodes:
                        postcodes[tag.attrib['v']]=1
                    else:
                        postcodes[tag.attrib['v']] +=1
                    
    osm_file.close()
    return postcodes


# In[11]:

postalcodes = auditpostcode(OSM_FILE)
pprint.pprint(postalcodes)


# In[12]:

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
        
def test():
    postalcodes = auditpostcode(OSM_FILE)
    for k,v in postalcodes.iteritems():
        better_code = update_postcode(k,mapping2)
        print k, "=>", better_code

test()


# In[13]:

#Audit 'value' of key  'city'

def is_city(elem):
    return (elem.attrib['k'] == "addr:city")


def auditcity(osmfile):
    osm_file = open(osmfile, "r")
    city = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city(tag):
                    if tag.attrib['v'] not in city:
                        city[tag.attrib['v']]=1
                    else:
                        city[tag.attrib['v']] +=1
                    
    osm_file.close()
    return city


# In[14]:

cities = auditcity(OSM_FILE)
pprint.pprint(cities)


# In[15]:

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

def test():
    cities = auditcity(OSM_FILE)
    for k,v in cities.iteritems():
        better_city = update_city(k,mapping3)
        print k, "=>", better_city

test()


# In[ ]:



