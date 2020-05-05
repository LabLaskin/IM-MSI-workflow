# Creates an RGB overlay of 3 separate compounds
# Input: 3 .txt files corresponding to images from the same experiment
# Output: 1 image file with each of the R, G, and B channels set to the relative intensity of a different compound
from tkinter.filedialog import askopenfilenames
from tkinter import filedialog
from FileIO import OpenTxt
from Imaging import CreateRGB
import os
from Functions import OpenSettings
import numpy as np
import pandas as pd


print('Input: 3 txt files corresponding to MSi images\nOutput: 1 image, with (r,g,b) corresponding to the order the files were input\nSelect your files: ')
bigData = np.array([])
methods = np.array([])
maxInt = 0
userInput = input('Would you like to change the settings? (Y/N): ')
if userInput.lower() == 'y':
    settings = OpenSettings()
else:
    with open('SETTINGS.txt') as file: # If you don't change settings, the defaults are used
        settings = file.read().splitlines()
filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))

if len(filenames) == 3:
    j = 0
    for file in filenames:
        medData = OpenTxt(file)
        if j == 0:
            bigData = np.array([medData])
            j += 1
        else:
            bigData = np.append(bigData, [medData], axis=0)

    image = CreateRGB(bigData, False)

    while True:
        print('1) Create another image\n2) Save Results\n0) Quit')
        option = int(input('Select an option: '))
        if option == 1:
            bigData = np.array([])
            print('Select 3 files to image: ')
            filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))
            j = 0
            for file in filenames:
                medData = OpenTxt(file)
                if j == 0:
                    bigData = np.array([medData])
                    j += 1
                else:
                    bigData = np.append(bigData, [medData], axis=0)

            image = CreateRGB(bigData, False)

        elif option == 2:
            print('Select the folder in which you would like to save: ')
            os.chdir(filedialog.askdirectory())
            image.save('RGB_%s_%s_%s.png' % (bigData[0][0].mz, bigData[1][0].mz, bigData[2][0].mz))

        elif option == 0:
            break
        else:
            print("Didn't recognize your selection. Please try again.")
else:
    print('Make sure to select 3 and only 3 .txt files')
