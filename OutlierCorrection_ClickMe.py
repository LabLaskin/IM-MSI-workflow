from tkinter.filedialog import askopenfilenames
from FileIO import OpenTxt
from Imaging import ShowImage, SaveImage
import os
# from numpy import std, mean, median
import time
from Functions import OpenSettings
import numpy as np
import pandas as pd

userInput = input('Would you like to change the settings? (Y/N): ')
if userInput.lower() == 'y':
    settings = OpenSettings()
else:
    with open('SETTINGS.txt') as file:
        settings = file.read().splitlines()

HOMEDIRECTORY = settings[0]


def RemoveSpikesLocal(medData):
    # Finds the local mean intensity and std. of each area of an image
    # boxSize determines how many pixels away will be included in the mean calculation
    # For each pixel, all of its neighbours within the box will be taken into account when calculating the mean
    # The box moves around, centered on the pixel being evaluated
    # Outlier = mu + 3 sigma
    # Finds all outliers and set them equal to
    # The median of their 8 nearest neighbours
    temp = medData
    boxSize = max(5, int(medData[0].intensities.shape[0] / 10))  # Tweakable
    if boxSize % 2 == 0:
        boxSize += 1
    offset = int(1 / 2 * (boxSize - 1))

    i = 0
    a = 0
    for smallData in medData:
        j = 0
        for intensity in smallData.intensities:
            try:
                neighbours = np.array([])
                p = -offset
                while p <= offset:
                    q = -offset
                    while q <= offset:
                        if p != 0 or q != 0:
                            if a == 0:
                                neighbours = np.array([medData[i + p].intensities[j + q]])
                                a += 1
                            else:
                                neighbours = np.append(neighbours, [medData[i + p].intensities[j + q]], axis=0)
                        q += 1
                    p += 1

                MU = np.mean(neighbours)
                STDEV = np.std(neighbours)
                upperBound = MU + (3 * STDEV)

                if intensity > upperBound and intensity > 1000:
                    # Doesn't affect pixels with intensity less than 1000, this can be changed as you see fit
                    neighbours = np.array([[medData[i-1].intensities[j-1]],
                                           [medData[i-1].intensities[j]],
                                           [medData[i-1].intensities[j+1]],
                                           [medData[i].intensities[j+1]],
                                           [medData[i+1].intensities[j+1]],
                                           [medData[i+1].intensities[j]],
                                           [medData[i+1].intensities[j-1]],
                                           [medData[i].intensities[j-1]]])
                    temp[i].intensities[j] = np.median(neighbours)
            except IndexError:
                # Will not remove error from edges
                pass
            j += 1
        i += 1

    maxInt = 0
    for smallData in temp:
        max_intensity_array = np.amax(smallData.intensities)  # finds max intensity from intensity array generated above
        if max_intensity_array > maxInt:
            maxInt = max_intensity_array
    temp[0].maxInt = maxInt

    return temp


def RemoveSpikesGlobal(medData):
    # Finds the global mean intensity and std. of an image
    # Outlier = mu + 3 sigma
    # Finds all outliers and set them equal to
    # The median of their 8 nearest neighbours
    temp = medData
    intList = np.array([])
    a = 0
    for smallData in medData:
        for intensity in smallData.intensities:
            if a == 0:
                intList = np.array([intensity])
                a += 1
            else:
                intList = np.append(intList, [intensity], axis=0)

    MU = np.mean(intList)
    STDEV = np.std(intList)
    upperBound = MU + 3 * STDEV

    i = 0
    for smallData in medData:
        j = 0
        for intensity in smallData.intensities:
            if intensity > upperBound:
                try:
                    neighbours = np.array([[medData[i-1].intensities[j-1]],
                                           [medData[i-1].intensities[j]],
                                           [medData[i-1].intensities[j+1]],
                                           [medData[i].intensities[j+1]],
                                           [medData[i+1].intensities[j+1]],
                                           [medData[i+1].intensities[j]],
                                           [medData[i+1].intensities[j-1]],
                                           [medData[i].intensities[j-1]]])
                    temp[i].intensities[j] = np.median(neighbours)
                except IndexError:
                    pass
            j += 1
        i += 1
    maxInt = 0
    for smallData in temp:
        max_intensity_array = np.amax(smallData.intensities)  # finds max intensity from intensity array generated above
        if max_intensity_array > maxInt:
            maxInt = max_intensity_array
    temp[0].maxInt = maxInt

    return temp


def Attenuate(medData, percentage):
    # Find the 1st and 2nd highest peaks in an image
    # Set the 1st highest peak's intensity equal to
    # Percentage times 2nd highest peak
    CORRECTIONFACTOR = percentage
    maxInt = 0
    penultInt = 0
    for smallData in medData:
        for intensity in smallData.intensities:
            if intensity > maxInt:
                penultInt = maxInt
                maxInt = intensity
            elif intensity > penultInt:
                penultInt = intensity
    i = 0
    for smallData in medData:
        j = 0
        for intensity in smallData.intensities:
            if intensity == maxInt:
                if intensity > (penultInt * CORRECTIONFACTOR):
                    medData[i].intensities[j] = (penultInt * CORRECTIONFACTOR)
                    medData[0].maxInt = (penultInt * CORRECTIONFACTOR)
            j += 1
        i += 1

    return medData


os.chdir(HOMEDIRECTORY)
filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))
startTime = time.time()

for file in filenames:
    medData = RemoveSpikesLocal(OpenTxt(file))
    ShowImage(medData, settings)

print('Outliers corrected in %.2f seconds.' % (time.time() - startTime))

userInput = -1
lastChoice = 4


while userInput != '0':
    outlierType = ''
    userInput = input('1) Save image(s)\n2) Use attenuation algorithm \n3) Use global spike finder\n4) Use local spike finder\n5) Select different file(s)\n0) Quit w/o saving\n\nSelect an option: ')
    if userInput == '1' or userInput == '4':
        for file in filenames:
            if lastChoice == 4:
                medData = RemoveSpikesLocal(OpenTxt(file))
                outlierType = 'Local'
            elif lastChoice == 2:
                medData = Attenuate(OpenTxt(file), percentage)
                outlierType = 'Attenuate'
            elif lastChoice == 3:
                medData = RemoveSpikesGlobal(OpenTxt(file))
                outlierType = 'Global'
            maxInt = 0
            for smallData in medData:
                max_intensity_array = np.amax(
                    smallData.intensities)  # finds max intensity from intensity array generated above
                if max_intensity_array > maxInt:
                    maxInt = max_intensity_array
            medData[0].maxInt = maxInt
            SaveImage(medData, settings, outlierType)
            print('Images saved.')
    elif userInput == '2':
        percentage = float(input('Input: a ratio (ex 1.05). The highest peak will be scaled back to this much times the second highest peak.  '))
        for file in filenames:
            medData = Attenuate(OpenTxt(file), percentage)
            maxInt = 0
            for smallData in medData:
                max_intensity_array = np.amax(
                    smallData.intensities)  # finds max intensity from intensity array generated above
                if max_intensity_array > maxInt:
                    maxInt = max_intensity_array
            medData[0].maxInt = maxInt
            ShowImage(medData, settings)
            lastChoice = 2
    elif userInput == '3':
        for file in filenames:
            maxInt = 0
            medData = OpenTxt(file)
            for smallData in medData:
                max_intensity_array = np.amax(
                    smallData.intensities)  # finds max intensity from intensity array generated above
                if max_intensity_array > maxInt:
                    maxInt = max_intensity_array
            medData[0].maxInt = maxInt
            medData = RemoveSpikesGlobal(medData)
            ShowImage(medData, settings)
            lastChoice = 3
    elif userInput == '4':
        for file in filenames:
            maxInt = 0
            medData = OpenTxt(file)
            for smallData in medData:
                max_intensity_array = np.amax(
                    smallData.intensities)  # finds max intensity from intensity array generated above
                if max_intensity_array > maxInt:
                    maxInt = max_intensity_array
            medData[0].maxInt = maxInt
            medData = RemoveSpikesLocal(medData)
            ShowImage(medData, settings)
            lastChoice = 4
    elif userInput == '5':
        filenames = askopenfilenames(filetypes=((".txt", "*.txt"), ("all files", "*.*")))
        for file in filenames:
            medData = RemoveSpikesLocal(OpenTxt(file))
            ShowImage(medData, settings)
    elif userInput == '0':
        break
    else:
        print("Didn't recognize that, please try again")
