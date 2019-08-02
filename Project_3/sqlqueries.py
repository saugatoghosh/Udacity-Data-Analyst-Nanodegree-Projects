
# coding: utf-8

# In[1]:

'''
Execute different sql queries with the database created
'''
import sqlite3

sqlite_file = 'osmdb.db'
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()


# In[2]:

# SQL queries of the database : List counts of nodes, ways, nodes_tags, ways_tags


def number_of_nodes():
    result = cur.execute('SELECT COUNT(*) FROM nodes')
    return result.fetchone()[0]
print "Number of nodes: " , number_of_nodes()

def number_of_ways():
    result = cur.execute('SELECT COUNT(*) FROM ways')
    return result.fetchone()[0]
print "Number of ways: " , number_of_ways()

def number_of_node_tags():
    result = cur.execute('SELECT COUNT(*) FROM nodes_tags')
    return result.fetchone()[0]
print "Number of node tags: " , number_of_node_tags()

def number_of_ways_tags():
    result = cur.execute('SELECT COUNT(*) FROM ways_tags')
    return result.fetchone()[0]
print "Number of ways tags: " , number_of_ways_tags()


# In[3]:

# List number of unique users, top contributing users, number of users contributing only once

def number_of_unique_users():
    result = cur.execute('SELECT COUNT(DISTINCT(e.uid))             FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e')
    return result.fetchone()[0]
print "Number of unique users: " , number_of_unique_users()

def top_contributing_users():
    users = []
    for row in cur.execute('SELECT e.user, COUNT(*) as num             FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e             GROUP BY e.user             ORDER BY num DESC             LIMIT 10'):
        users.append(row)
    return users

print "Top contributing users: " , top_contributing_users()

def number_of_users_contributing_once():
    result = cur.execute('SELECT COUNT(*)             FROM                 (SELECT e.user, COUNT(*) as num                  FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e                  GROUP BY e.user                  HAVING num=1) u')
    return result.fetchone()[0]
print "Number of users contributing once: " , number_of_users_contributing_once()


# In[4]:

# List postcodes in database

for row in cur.execute ('SELECT t.value, COUNT(*) as count             FROM (SELECT * FROM nodes_tags UNION ALL             SELECT * FROM ways_tags) t            WHERE t.key="postcode"            GROUP BY t.value            ORDER BY count DESC            LIMIT 10;'):
    print row


# In[5]:

#Top Amenities, Religions practised, Cuisine, Historical Sites

for row in cur.execute ('SELECT t.value, COUNT(*) as count             FROM (SELECT * FROM nodes_tags UNION ALL             SELECT * FROM ways_tags) t            WHERE t.key="amenity"            GROUP BY t.value            ORDER BY count DESC            LIMIT 10;'):
    print "Amenities:", row
    
#Religions practised

for row in cur.execute ('SELECT e.value, COUNT(*) as count             FROM (SELECT * FROM nodes_tags UNION ALL             SELECT * FROM ways_tags) e            WHERE e.key="religion"            GROUP BY e.value            ORDER BY count DESC            LIMIT 10;'):
    print "Religions:", row
    
#Cuisine

for row in cur.execute ('SELECT t.value, COUNT(*) as count             FROM (SELECT * FROM nodes_tags UNION ALL             SELECT * FROM ways_tags) t            WHERE t.key="cuisine"            GROUP BY t.value            ORDER BY count DESC            LIMIT 5;'):
    print "Cuisine:", row
    
#Historical sites

for row in cur.execute ('SELECT tags.value, COUNT(*) as count             FROM (SELECT * FROM nodes_tags UNION ALL             SELECT * FROM ways_tags) tags            WHERE tags.key = "historic"            GROUP BY tags.value            ORDER BY count DESC;'):
    print "Historical sites:", row


# In[ ]:

conn.close()

