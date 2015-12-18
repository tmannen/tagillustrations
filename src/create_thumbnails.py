import os, sys
from PIL import Image

size = 256, 256
imagefolder = u""

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