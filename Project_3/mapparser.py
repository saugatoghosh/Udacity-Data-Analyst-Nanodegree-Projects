
# coding: utf-8

# In[1]:

'''
Parse the OSM , count unqiue tags and types of keys present

'''

import xml.etree.cElementTree as ET
import pprint
import re

#Count the different types of tags in the present file

OSM_FILE = 'new_delhi.osm'

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags

pprint.pprint(count_tags(OSM_FILE))


# In[2]:

# List the different types of keys in the data with counts

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        if re.search(problemchars,element.attrib['k']) is not None:
            keys['problemchars'] +=1
        elif re.search(lower_colon,element.attrib['k']) is not None:
            keys['lower_colon'] +=1
        elif re.search(lower,element.attrib['k']) is not None:
            keys['lower'] +=1
        else:
            keys['other'] +=1
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

def test():
    keys = process_map(OSM_FILE)
    pprint.pprint(keys)
    
test()


# In[ ]:



