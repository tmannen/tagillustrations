#used for saving tags to db from a file

import hashlib
import sqlite3
import os

taglist = []
with open("tagsbackup.txt", "r") as f:
	try:
	    for infos in f:
	    	unicoded = [x.encode('utf-8') for x in infos.strip().split(",")]
	    	taglist.append(tuple(unicoded))
	except Exception as e:
		print e


with sqlite3.connect("tags.db") as connection:
    try:
        cur = connection.cursor()
        cur.executemany("INSERT INTO tags VALUES (?, ?, ?, ?, ?)", taglist)
        connection.commit()
    except Exception as e:
        print "Failed to save tags to database"
        print(e)