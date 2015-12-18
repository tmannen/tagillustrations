import subprocess
import sys
import hashlib
import sqlite3
import os
import re
import shutil
import ConfigParser
config = ConfigParser.ConfigParser(allow_no_value=True)
config.read('config.txt')
print config.get("values", "i2vpath")
i2vfolder = config.get("values", "i2vpath")
sys.path.append(i2vfolder)
import i2v
#sys.path.append(config.get("values", "caffepath")) #if caffe not in path
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
        print "Failed to create database or database already exists. Error: \n"
        print(e)

def get_tagger():
    i2vfolder = config.get("values", "i2vpath")
    illust2vec = i2v.make_i2v_with_caffe(
         i2vfolder + "illust2vec_tag.prototxt", i2vfolder + "illust2vec_tag_ver200.caffemodel",
         i2vfolder + "tag_list.json")

    return illust2vec

def create_tags(illust2vec, dbname="tags.db"):
    imagefolder = config.get("values", "imagefolderpath").encode('utf-8')
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
                        info = [x.encode('utf-8') for x in info]
                        taglist.append(tuple(info))
                        #if db fails somehow.. save the tags to a file:
                        f.write(",".join(info) + "\n")

            except Exception as e:
                print "Failed to produce tags for " + image_name + ". Error: \n"
                print(e)

    with sqlite3.connect(dbname) as connection:
        try:
            cur = connection.cursor()
            cur.executemany("INSERT INTO tags VALUES (?, ?, ?, ?, ?)", taglist)
            connection.commit()
        except Exception as e:
            print "Failed to save tags to database. Error: \n"
            print(e)

#used for saving tags to db from a file. I had unicode problems at one point, so this can be used to
#save the tags to a database if the function above fails.

def save_from_file(dbname="tags.db"):
    taglist = []

    with open("tagsbackup.txt", "r") as f:
        try:
            for infos in f:
                unicoded = [x.encode('utf-8') for x in infos.strip().split(",")]
                taglist.append(tuple(unicoded))
        except Exception as e:
            print e


    with sqlite3.connect(dbname) as connection:
        try:
            cur = connection.cursor()
            cur.executemany("INSERT INTO tags VALUES (?, ?, ?, ?, ?)", taglist)
            connection.commit()
        except Exception as e:
            print "Failed to save tags to database"
            print(e)

def detect_illustrations(illust2vec):
    sourcefolder = config.get("values", "sourcefolderpath").encode('utf-8')
    imagefolder = config.get("values", "imagefolderpath").encode('utf-8')
    image_re = re.compile("\.(jpg|jpeg|png)$")
    image_names = [filename for filename in os.listdir(sourcefolder) if image_re.search(filename)]

    #TODO: no need for file, just copy or move the files to image folder
    with open("photoprobabilities.txt", "w") as f:
        for image_name in image_names:
            try:
                img = Image.open(sourcefolder + image_name)
                #IRL images often have low probabilities in everything (except rating), better to divide that way?
                prob = illust2vec.estimate_specific_tags([img], ["photo"])[0]["photo"]
                if prob < 0.1:
                    shutil.copy(sourcefolder + image_name, imagefolder + image_name)
                f.write(image_name + "," + str(prob) + "\n")
            except Exception as e:
                print(e)

def create_thumbnails():
    size = 256, 256
    imagefolder = config.get("values", "imagefolderpath").encode('utf-8')

    for infile in os.listdir(imagefolder):
        outfile = "thumb" + infile
        if infile != outfile:
            try:
                im = Image.open(imagefolder + infile)
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(imagefolder + "thumbnails/" + outfile)
            except IOError as e:
                print e
                print "cannot create thumbnail for '%s'" % infile

#used in case of taking the probabilities from file
def copy_from_file():
    sourcefolder = config.get("values", "sourcefolderpath")
    targetfolder = config.get("values", "imagefolderpath")
    filepath = "gg"

    with open(filepath, "r") as probs:
        for line in probs:
            splat = line.strip().split(",")
            filename, prob = splat[0], float(splat[1])
            if prob < 0.1:
                shutil.copyfile(sourcefolder + filename, targetfolder + filename)

#create_database()
#tagger = get_tagger()
#create_tags(tagger)