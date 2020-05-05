try:
    from PIL import Image, ImageDraw                    # PIL & Pillow work interchangeably
except ModuleNotFoundError:
    from Pillow import Image, ImageDraw
from Functions import CMaptoColor
import matplotlib.pyplot as plt
from IPython.core.display import display
import numpy as np
import pandas as pd


def ShowImage(medData, settings):
    width = float(medData[0].width)
    height = float(medData[0].height)
    try:
        CMAP = plt.get_cmap(settings[4])
    except TypeError:
        CMAP = plt.get_cmap('hot')

    numLines = medData.shape[0]
    numIntensities = medData[0].intensities.shape[0]
    w = numIntensities
    pixW = 1
    h = int(w / width * height)
    pixH = h / numLines
    if pixH < 1:
        pixH = 1;
        h = pixH * numLines
        w = int(h / height * width)
        pixW = w / numIntensities

    output = Image.new('RGBA', (w, h), "black")
    draw = ImageDraw.Draw(output)
    for smallData in medData:
        i = 0
        for intensity in smallData.intensities:
            try:
                color = CMaptoColor(CMAP(float(intensity) / medData[0].maxInt))
            except ZeroDivisionError:
                color = CMaptoColor(CMAP(0))
            draw.rectangle(
                ((i * pixW, (smallData.lineNum - 1) * pixH), (i * pixW + pixW, (smallData.lineNum - 1) * pixH + pixH)),
                fill=color)
            i += 1
    print('MZ_%0.4f DT_%0.2f' % (float(medData[0].mz), float(medData[0].driftTime)), end='')
    display(output)
    return()


def SaveImage(medData, settings, modifier='', AICMod=0):
    width = float(medData[0].width)
    height = float(medData[0].height)
    try:
        IMAGEFORMAT = settings[3]
        CMAP = plt.get_cmap(settings[4])
    except TypeError:
        IMAGEFORMAT = '.png'
        CMAP = plt.get_cmap('hot')

    numLines = medData.shape[0]
    numIntensities = medData[0].intensities.shape[0]

    w = numIntensities
    pixW = 1
    h = int(w / width * height)
    pixH = h / numLines
    if pixH < 1:
        pixH = 1
        h = pixH * numLines
        w = int(h / height * width)
        pixW = w / numIntensities

    output = Image.new('RGBA', (w, h), "black")
    draw = ImageDraw.Draw(output)
    for smallData in medData:
        i = 0
        for intensity in smallData.intensities:
            try:
                color = CMaptoColor(CMAP(float(intensity) / medData[0].maxInt))
            except ZeroDivisionError:
                color = CMaptoColor(CMAP(0))
            draw.rectangle(
                ((i * pixW, (smallData.lineNum - 1) * pixH), (i * pixW + pixW, (smallData.lineNum - 1) * pixH + pixH)),
                fill=color)
            i += 1
    if medData[0].driftTime:
        outputName = ('MZ_%0.4f DT_%0.2f' % (float(medData[0].mz), float(medData[0].driftTime)))
    else:
        outputName = ('MZ_%0.4f' % float(medData[0].mz))
    if modifier == 'Attenuate':
        outputName += '_Attenuate'
    elif modifier == 'Local':
        outputName += '_Local'
    elif modifier == 'Global':
        outputName += '_Global'
    elif modifier == 'AIC':
        outputName += '_AIC'
    if AICMod != 0:
        outputName += (' ' + str(AICMod))

    output.save((outputName + IMAGEFORMAT))

    return()


def CreateTxtFile(medData):
    if medData[0].driftTime:
        outputName = ('MZ_%0.4f DT_%0.2f.txt' % (float(medData[0].mz), float(medData[0].driftTime)))
    else:
        outputName = ('MZ_%0.4f.txt' % float(medData[0].mz))
    with open(outputName, 'w+') as file:
        file.write('%i\t%i\t%s\n' % (medData[0].width, medData[0].height, medData[0].name[0:-2]))
        for smallData in medData:
            for intensity in smallData.intensities:
                file.write(str(intensity) + ' ')
            file.write('\n')
    return()


def CreateRGB(bigData, save):                             # How to make sure that people only use 3 images from same exp
    width = bigData[0][0].width                   # I think the file selector should limit you to images from one folder
    height = bigData[0][0].height

    numLines = bigData[0].shape[0]
    numIntensities = bigData[0][0].intensities.shape[0]
    scale1 = 255 / bigData[0][0].maxInt
    scale2 = 255 / bigData[1][0].maxInt
    scale3 = 255 / bigData[2][0].maxInt

    w = numIntensities
    pixW = 1
    h = int(w / width * height)
    pixH = h / numLines
    if pixH < 1:
        pixH = 1
        h = pixH * numLines
        w = int(h / height * width)
        pixW = w / numIntensities

    output = Image.new('RGB', (w, h), "black")
    draw = ImageDraw.Draw(output)

    j = 0
    for smallData in bigData[2]:
        i = 0
        for intensity in smallData.intensities:
            color = (int(intensity * scale3), int(bigData[0][j].intensities[i] * scale1),
                     int(bigData[1][j].intensities[i] * scale2))
            draw.rectangle(
                ((i * pixW, (smallData.lineNum - 1) * pixH), (i * pixW + pixW, (smallData.lineNum - 1) * pixH + pixH)),
                fill=color)
            i += 1
        j += 1
    if save:
        output.save(
            'MZ_%0.4f DT_%0.2f %s.png' % (float(bigData[0][0].mz), float(bigData[0][0].driftTime), bigData[0][1].name))
    else:
        print('MZ_%0.4f DT_%0.2f' % (float(bigData[0][0].mz), float(bigData[0][0].driftTime)), end='')
        display(output)
    return(output)


def CreateAIC(bigData, settings, save):
    width = float(bigData[0][0].width)
    height = float(bigData[0][0].height)
    try:
        IMAGEFORMAT = settings[3]
        CMAP = plt.get_cmap(settings[4])
    except TypeError:
        IMAGEFORMAT = '.png'
        CMAP = plt.get_cmap('hot')

    i = 0
    for medData in bigData:
        width = medData[0].width
        height = medData[0].height
        numLines = medData.shape[0]
        numIntensities = medData[0].intensities.shape[0]
        w = numIntensities
        pixW = 1
        h = int(w / width * height)
        pixH = h / numLines
        if pixH < 1:
            pixH = 1;
            h = pixH * numLines
            w = int(h / height * width)
            pixW = w / numIntensities

        output = Image.new('RGBA', (w, h), "black")
        draw = ImageDraw.Draw(output)
        for smallData in medData:
            j = 0
            for intensity in smallData.intensities:
                try:
                    color = CMaptoColor(CMAP(float(intensity) / (medData[0].maxInt)))
                except ZeroDivisionError:
                    color = CMaptoColor(CMAP(0))
                draw.rectangle(((j * pixW, (smallData.lineNum - 1) * pixH),
                                (j * pixW + pixW, (smallData.lineNum - 1) * pixH + pixH)), fill=color)
                j += 1

        if save:
            output.save(('MZ_%0.4f DT_%0.2f %s' + IMAGEFORMAT) % (
                float(medData[0].mz), float(medData[0].driftTime), medData[1].name))
        else:
            print('MZ_%0.4f DT_%0.2f' % (float(medData[0].mz), float(medData[0].driftTime)), end='')
            display(output)
        i += 1
    return()
