import csv
from Functions import IsNumber
import numpy as np
import pandas as pd


class SmallData:
    # Each SmallData object corresponds to a line of intensities for 1 unique compound
    def __init__(self, ID=None, mz=None, driftTime=None, intensities=None, name=None, lineNum=None, maxInt=None,
                 width=None, height=None):

        if ID is None:
            ID = 0
        self.ID = ID

        if mz is None:
            mz = ''
        self.mz = mz

        if driftTime is None:  # Not required, samples with a drift time will be marked so
            driftTime = 0
        self.driftTime = driftTime

        if intensities is None:
            intensities = np.array([])
        self.intensities = intensities

        if name is None:  # Name of experiment, from filename.d
            name = ''
        self.name = name

        if lineNum is None:
            lineNum = 0
        self.lineNum = lineNum

        if maxInt is None:  # Only the first SmallData per medData has a maxInt(ensity)
            maxInt = 0
        self.maxInt = maxInt

        if width is None:  # Width of sample area
            width = 0
        self.width = width

        if height is None:  # Height of sample area (must have the same units as width)
            height = 0
        self.height = height


def OpenTSV(filename, indexDT):
    # Reads in a .tsv Skyline export
    medData = np.array([])   # One medData has all the data for one unique m/z image
    bigData = np.array([[]])  # Holds all the data
    maxInt = 0

    df = pd.read_csv(filename, sep='\t')  # reading .tsv using pandas
    reader = df.values  # array creation after reading .tsv, values will be of type string
    i = 0
    # Scan the data into an array of smallData objects, File must be .tsv with comma separated sublists
    for line in reader:
        smallData = SmallData()
        smallData.ID = line[0]  # can be moved to a single line
        smallData.mz = line[1]
        if indexDT:
            smallData.driftTime = float(line[2])

            # converting comma separated string to numpy array with integer data
            smallData.intensities = np.fromstring(line[4], dtype=float, count=-1, sep=',').astype(int)

            smallData.name = line[5]
        else:
            # if drift time not available in data, will be assigned 0 by default
            smallData.driftTime = float(0)

            # converting comma separated string to numpy array with integer data
            smallData.intensities = np.fromstring(line[2], dtype=float, count=-1, sep=',').astype(int)

            smallData.name = line[3]

        max_intensity_array = np.amax(smallData.intensities)  # finds max intensity from intensity array generated above
        if max_intensity_array > maxInt:
            maxInt = max_intensity_array

        # Determines line number by scanning the last places of the filename.
        # Assumes filename in the vein of experiment_conditions_line999.d

        if indexDT:
            if IsNumber(line[6][-3]):  # Just add another if statement if you have more than 1000 lines
                smallData.lineNum = int(line[6][-3:])
            elif IsNumber(line[6][-2]):
                smallData.lineNum = int(line[6][-2:])
            else:
                smallData.lineNum = int(line[6][-1])
        else:
            if IsNumber(line[4][-3]):  # Just add another if statement if you have more than 1000 lines
                smallData.lineNum = int(line[4][-3:])
            elif IsNumber(line[4][-2]):
                smallData.lineNum = int(line[4][-2:])
            else:
                smallData.lineNum = int(line[4][-1])

        try:
            if smallData.ID == medData[-1].ID:
                medData = np.append(medData, [smallData], axis=0)
            else:
                # An empty numpy array is difficut to append to, hence first row needs to be explicitly assigned.
                # Subsequent rows can be then appended
                if i == 0:
                    medData[0].maxInt = maxInt
                    bigData = np.array([medData])
                    maxInt = 0
                    medData = np.array([])
                    medData = np.append(medData, [smallData], axis=0)
                    i += 1
                else:
                    medData[0].maxInt = maxInt
                    bigData = np.append(bigData, [medData], axis=0)
                    maxInt = 0
                    medData = np.array([])
                    medData = np.append(medData, [smallData], axis=0)
                # i += 1
        except IndexError:
            medData = np.append(medData, [smallData], axis=0)
    i = 0
    medData[0].maxInt = maxInt
    bigData = np.append(bigData, [medData], axis=0)
    # print(bigData.shape)
    return bigData


def OpenTxt(filename):
    # Reads in a txt file (created in Imaging.py)
    medData = np.array([])
    settings = np.array([])

    # reading .tsv using pandas
    df_settings = pd.read_csv(filename, sep='\t', nrows=1, header=None)  # settings DataFrame
    reader_settings = df_settings.values  # read settings DataFrame
    settings = reader_settings[0]

    df_intensities = pd.read_csv(filename, sep=' ', skiprows=1, header=None)  # intensities DataFrame
    # read intensities DataFrame as int, the last element of each row is not a valid int (it is a space)
    reader_intensities = df_intensities.values.astype(int)

    i = 1
    for line in reader_intensities:
        smallData = SmallData()
        smallData.lineNum = i
        smallData.intensities = np.delete(line, -1)  # removing the last invalid integer from the row
        if 'DT' in filename:
            smallData.mz = filename[-21:-13]
            smallData.driftTime = filename[-9:-4]
        else:
            smallData.mz = filename[-9:-4]
        medData = np.append(medData, [smallData], axis=0)
        i += 1

    maxInt = 0

    for smallData in medData:
        max_intensity_array = np.amax(smallData.intensities)  # finds max intensity from intensity array generated above
        if max_intensity_array > maxInt:
            maxInt = max_intensity_array
        smallData.name = settings[2]
        smallData.width = int(settings[0])
        smallData.height = int(settings[1])

    medData[0].maxInt = maxInt

    return medData
