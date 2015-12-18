#Used for separating illustrations from real life images. Illustrations usually have
#a very low 'photo' tag probability, so we only take the photos with a low prob.
#might not be needed since i could just check the photo tag when tagging and not those in db?

import subprocess
import sys
import hashlib
import sqlite3
import re
import os # os.listdir() is probably simpler than subprocess
#i2vfolder = "" for illustration2vec
sys.path.append(i2vfolder)
#sys.path.append('caffe python folder') #if caffe not in path
from PIL import Image
import i2v

imagefolder = ""
ps = subprocess.Popen(["ls", imagefolder], stdout=subprocess.PIPE)
image_names = subprocess.check_output(["grep", "-e", ".jpg$", "-e", ".png$", 
	"-e", ".jpeg$"], stdin=ps.stdout).split("\n")
ps.wait()

illust2vec = i2v.make_i2v_with_caffe(
     i2vfolder + "illust2vec_tag.prototxt", i2vfolder + "illust2vec_tag_ver200.caffemodel",
     i2vfolder + "tag_list.json")

with open("photoprobabilities.txt", "w") as f:
	for image_name in image_names:
		img = Image.open(imagefolder + image_name)
		try:
			#IRL images often have low probabilities in everything (except rating), better to divide that way?
			prob = illust2vec.estimate_specific_tags([img], ["photo"])[0]["photo"]
			f.write(image_name + "," + str(prob) + "\n")
		except Exception as e:
			print(e)
