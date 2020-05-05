# Change the aspect ratio of a folder of images
# Input: The images folder within an experimental data folder
# *Requires Main_ClickMe.py to be run first
# Output: The same images folder with resized images


from tkinter.filedialog import askdirectory
import os
from FileIO import OpenTxt
from Imaging import SaveImage, CreateTxtFile
import time
import glob
import sys
import numpy as np
import pandas as pd


with open('SETTINGS.txt') as file:  # The defaults are used because it shouldn't change anything
    settings = file.read().splitlines()
print('Input: the images folder within the experimental folder\nOutput: The same images with a different aspect ratio')

os.chdir(askdirectory())
width = int(input('Input the width of the sample area: '))
height = int(input('Input the height of the sample area: '))

startTime = time.time()

numImages = 0
for file in glob.glob('*.txt'):
    numImages += 1

i = 1
for file in glob.glob('*.txt'):
    medData = OpenTxt(file)
    medData[0].width = width
    medData[0].height = height
    SaveImage(medData, settings)
    CreateTxtFile(medData)
    sys.stdout.write('\rProcessing image %d of %d' % (i, numImages))
    i += 1

print('\nProcessing time: %.2f sec' % (time.time() - startTime))
