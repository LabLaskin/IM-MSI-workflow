# Sets the same color scale for the selected images for an absolute comparison of their intensity
# Input:  1) 2+ .txt files corresponding to MSIC images
#         2) 2 folders of processed MSIC data
# Output: 1) 2+ images with the same absolute color scale
#         2) A new folder in the home directory with each common image between the 2 folders imaged absolutely compared to its analogue in the other folder


import glob
import os
from FileIO import OpenTxt
from Imaging import ShowImage, SaveImage
import pathlib
import time
from tkinter.filedialog import askopenfilenames, askdirectory
from Functions import OpenSettings
import sys
import numpy as np
import pandas as pd


userInput = input('Would you like to change the settings? (Y/N): ')
if userInput.lower() == 'y':
    settings = OpenSettings()
else:
    with open('SETTINGS.txt') as file:  # possibly take this out
        settings = file.read().splitlines()

userInput = input('1. Select your own files to compare\n2. Compare every similar file between two folders\nSelect an option: ')

if userInput == '1':
    HOMEDIRECTORY = settings[0]

    print('Input: 2+ txt files corresponding to MSi images\nOutput: 2+ images, with colors scaled to the global max intensity\nSelect your files: ')
    bigData = np.array([])
    methods = np.array([])
    maxInt = 0

    filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))
    startTime = time.time()

    j = 0
    for file in filenames:
        medData = OpenTxt(file)
        for smallData in medData:
            max_intensity_array = np.amax(smallData.intensities)
            if max_intensity_array > maxInt:
                maxInt = max_intensity_array
        if j == 0:
            bigData = np.array([medData])
            j += 1
        else:
            bigData = np.append(bigData, [medData], axis=0)

    for medData in bigData:
        medData[0].maxInt = maxInt

    os.chdir(HOMEDIRECTORY)  # You can hardcode this to be your home directory

    for medData in bigData:
        ShowImage(medData, settings)

    print('Processing time: %.2f sec.\n' % (time.time() - startTime))

    while True:
        print('1) Add another image\n2) Remove an image\n3) Save Results\n0) Quit')
        option = int(input('Select an option: '))
        if option == 1:  # Add another image
            print('Select file(s) to add: ')
            filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))
            for file in filenames:
                medData = OpenTxt(file)
                for smallData in medData:
                    max_intensity_array = np.amax(smallData.intensities)
                    if max_intensity_array > maxInt:
                        maxInt = max_intensity_array
                bigData = np.append(bigData, [medData], axis=0)

            for medData in bigData:
                medData[0].maxInt = maxInt
                ShowImage(medData, settings)

        elif option == 2:  # Remove an image
            userInput = int(input('Select file to delete (first image is 1, second is 2, etc.):'))
            bigData = np.delete(bigData, userInput-1, 0)
            # del bigData[userInput - 1]
            maxInt = 0
            for medData in bigData:
                for smallData in medData:
                    max_intensity_array = np.amax(smallData.intensities)
                    if max_intensity_array > maxInt:
                        maxInt = max_intensity_array
            for medData in bigData:
                medData[0].maxInt = maxInt
                ShowImage(medData, settings)

        elif option == 3:  # Save
            print('Select the folder in which you would like to save: ')
            os.chdir(askdirectory())
            for medData in bigData:
                SaveImage(medData, settings, 'AIC')

        elif option == 0:
            break
        else:
            print("Didn't recognize your selection. Please try again.")

elif userInput == '2':
    megaData = np.array([])

    print('Accepts 2 folders of images, automatically compares images with the same identity and exports them to ./Images/AIC/ExperimentName.')
    print('Select the first folder')
    folder1 = askdirectory()
    os.chdir(folder1)  # + '/Images')
    listOfFiles = np.array([])

    j = 0
    for filename in glob.glob('*.txt'):
        if j == 0:
            listOfFiles = np.array([filename])
            j += 1
        else:
            listOfFiles = np.append(listOfFiles, [filename], axis=0)
        # listOfFiles.append(filename)

    listOfFiles_approx = np.empty((listOfFiles.shape[0]), dtype=object)

    for i in range(listOfFiles.shape[0]):
        filename_temp = listOfFiles[i]
        if "DT" in filename_temp:
            if int(filename_temp[filename_temp.find(" ")-1]) < 5:
                mz_approx = float(filename_temp[filename_temp.find("MZ_") + 3:filename_temp.find(" ") - 1] + "1")
            else:
                mz_approx = float(filename_temp[filename_temp.find("MZ_") + 3:filename_temp.find(" ") - 1] + "1") + 0.001

            if int(filename_temp[filename_temp.find(".txt")-1]) < 5:
                dt_approx = float(filename_temp[filename_temp.find("DT_") + 3:filename_temp.find(".txt") - 1] + "1")
            else:
                dt_approx = float(filename_temp[filename_temp.find("DT_") + 3:filename_temp.find(".txt") - 1] + "1") + 0.1
            listOfFiles_approx[i] = "MZ_" + str(mz_approx) + " " + "DT_" + str(dt_approx) + ".txt"

        else:
            if int(filename_temp[filename_temp.find(".txt") - 1]) < 5:
                mz_approx = float(filename_temp[filename_temp.find("MZ_") + 3:filename_temp.find(".txt") - 1] + "1")
            else:
                mz_approx = float(filename_temp[filename_temp.find("MZ_") + 3:filename_temp.find(".txt") - 1] + "1") + 0.001
            listOfFiles_approx[i] = "MZ_" + str(mz_approx) + ".txt"

    with open(listOfFiles[-1]) as txt:
        experiment1 = (txt.readline().split())[2]

    print('Select the second folder')
    folder2 = askdirectory()
    os.chdir(folder2)  # + '/Images')
    startTime = time.time()
    print('Scanning both directories for similar files')

    j = 0
    for filename in glob.glob('*.txt'):
        bigData = np.array([])
        medData = np.array([])
        maxInt = 0

        if filename in listOfFiles:
            medData = OpenTxt(folder1 + "/" + filename)
            bigData = np.array([medData])
            medData = OpenTxt(filename)
            bigData = np.append(bigData, [medData], axis=0)
            for medData in bigData:
                medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
            if j == 0:
                megaData = np.array([bigData])
                j += 1
            else:
                megaData = np.append(megaData, [bigData], axis=0)
            # megaData.append(bigData)

        if "DT" in filename:
            if int(filename[filename.find(" ") - 1]) < 5:
                mz_val = float(filename[filename.find("MZ_") + 3:filename.find(" ") - 1] + "1")
            else:
                mz_val = float(filename[filename.find("MZ_") + 3:filename.find(" ") - 1] + "1") + 0.001

            if int(filename[filename.find(".txt") - 1]) < 5:
                dt_val = float(filename[filename.find("DT_") + 3:filename.find(".txt") - 1] + "1")
            else:
                dt_val = float(filename[filename.find("DT_") + 3:filename.find(".txt") - 1] + "1") + 0.1
            filename_temp1 = "MZ_" + str(mz_val + 0.001) + " " + "DT_" + str(dt_val + 0.1) + ".txt"
            filename_temp2 = "MZ_" + str(mz_val - 0.001) + " " + "DT_" + str(dt_val + 0.1) + ".txt"
            filename_temp3 = "MZ_" + str(mz_val + 0.001) + " " + "DT_" + str(dt_val - 0.1) + ".txt"
            filename_temp4 = "MZ_" + str(mz_val - 0.001) + " " + "DT_" + str(dt_val - 0.1) + ".txt"
            if filename_temp1 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp1)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)
            elif filename_temp2 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp2)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)
            elif filename_temp3 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp3)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)
            elif filename_temp4 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp4)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)
        else:
            if int(filename[filename.find(".txt") - 1]) < 5:
                mz_val = float(filename[filename.find("MZ_") + 3:filename.find(".txt") - 1] + "1")
            else:
                mz_val = float(filename[filename.find("MZ_") + 3:filename.find(".txt") - 1] + "1") + 0.001
            filename_temp1 = "MZ_" + str(mz_val + 0.001) + ".txt"
            filename_temp2 = "MZ_" + str(mz_val - 0.001) + ".txt"
            if filename_temp1 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp1)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)
            elif filename_temp2 in listOfFiles_approx:
                medData = OpenTxt(folder1 + "/" + listOfFiles[list(listOfFiles_approx).index(filename_temp2)])
                bigData = np.array([medData])
                medData = OpenTxt(filename)
                bigData = np.append(bigData, [medData], axis=0)
                for medData in bigData:
                    medData[0].maxInt = max(bigData[-2][0].maxInt, bigData[-1][0].maxInt)
                if j == 0:
                    megaData = np.array([bigData])
                    j += 1
                else:
                    megaData = np.append(megaData, [bigData], axis=0)

    experiment2 = bigData[-1][0].name

    pathlib.Path(settings[0] + '/Images_Comparison_' + experiment1 + '_vs_' + experiment2).mkdir(parents=True, exist_ok=True)
    os.chdir(settings[0] + '/Images_Comparison_' + experiment1 + '_vs_' + experiment2)

    i = 1
    AICMod1 = folder1.split('/')[-1]
    AICMod2 = folder2.split('/')[-1]
    for bigData in megaData:
        sys.stdout.write('\rProcessing image %d of %d' % ((i + megaData.shape[0]), (megaData.shape[0] * 2)))
        SaveImage(bigData[0], settings, 'AIC', AICMod1)
        SaveImage(bigData[1], settings, 'AIC', AICMod2)
        i += 1

    print('\nProcessing time: %.2f' % (time.time() - startTime))
