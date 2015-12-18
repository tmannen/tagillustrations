import subprocess
import sys
import hashlib
import sqlite3
import os
#i2vfolder = ""
sys.path.append(i2vfolder)
#sys.path.append('caffe python folder') #if caffe not in path
from PIL import Image
import i2v

def create_database(dbname="tags.db"):
    connection = sqlite3.connect(dbname)
    try:
       connection.execute('''CREATE TABLE tags
            (hash TEXT,
             filename TEXT,
             tag TEXT,
             tag_type TEXT,
             tag_probability REAL)''')

    except sqlite3.OperationalError as e:
        print "Probably failed to create database or database exists. Error: \n"
        print(e)

def get_tagger():
    illust2vec = i2v.make_i2v_with_caffe(
         i2vfolder + "illust2vec_tag.prototxt", i2vfolder + "illust2vec_tag_ver200.caffemodel",
         i2vfolder + "tag_list.json")

    return illust2vec

def create_tags(illust2vec, dbname="tags.db"):
    imagefolder = u""
    image_names = os.listdir(imagefolder)
    taglist = []

    with open("tagsbackup.txt", "w") as f:
        for image_name in image_names:
            try:
                img = Image.open(imagefolder + image_name)
                print imagefolder + image_name
                tags = illust2vec.estimate_plausible_tags([img], threshold=0.1)[0]
                imghash = hashlib.md5(img.tobytes()).hexdigest()

                for tag_type in tags.keys(): #change just to id's in database?
                    for tag, prob in tags[tag_type]:
                        info = (imghash, image_name, tag, tag_type, str(prob))
                        taglist.append(info)
                        #if db fails somehow.. save the tags to a file
                        f.write(",".join(info) + "\n")

            except Exception as e:
                print "Failed to produce tags for " + image_name
                print(e)

    with sqlite3.connect(dbname) as connection:
        try:
            cur = connection.cursor()
            cur.executemany("INSERT INTO tags VALUES (?, ?, ?, ?, ?)", taglist)
            connection.commit()
        except Exception as e:
            print "Failed to save tags to database"
            print(e)

create_database()
tagger = get_tagger()
create_tags(tagger)