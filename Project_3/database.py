
# coding: utf-8

# In[5]:

'''
Import csv files into sqlite database
'''
import sqlite3
import csv

sqlite_file = 'osmdb.db'
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()


# In[6]:


#Create tables nodes, nodes_tags, ways, ways_tags, ways_nodes

cur.execute ('DROP TABLE IF EXISTS nodes')
conn.commit()

cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")
with open('nodes_project.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8"))              for i in dr]
    
cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp)                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
conn.commit()

cur.execute ('DROP TABLE IF EXISTS nodes_tags')
conn.commit()
cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")
with open('nodes_tags_project.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()

cur.execute ('DROP TABLE IF EXISTS ways')
conn.commit()

cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")
with open('ways_project.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
conn.commit()

cur.execute ('DROP TABLE IF EXISTS ways_tags')
conn.commit()
cur.execute("CREATE TABLE ways_tags (id, key, value, type);")
with open('ways_tags_project.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()

cur.execute ('DROP TABLE IF EXISTS ways_nodes')
conn.commit()

cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")
with open('ways_nodes_project.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), i['position'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", to_db)
conn.commit()

conn.close()


# In[ ]:



