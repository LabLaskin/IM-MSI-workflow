# Visualizes raw IM-MS data with a Mass Profiler report
# Input: 1+ folders of MS data with a Mass Profiler report
# Output: An Images folder within the experimental folder
# Converts the Mass Profiler output to a format compatible with Skyline
# Uses SkylineRunner to generate a list of peaks with intensities
# Maps each intensity to a pixel in an image, one for each compound
# Pixel color is calculated by dividing its intensity by the highest intensity in that image
# A matching .txt file for every image that enables post-processing (other _ClickMe programs)
import csv
from Functions import OpenSettings
import glob
import pathlib
import os
import time
from Imaging import SaveImage, CreateTxtFile
from FileIO import OpenTSV
from subprocess import Popen
import sys
from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView, QTreeView, QApplication, QDialog)
import numpy as np
import pandas as pd
from Normalize import std_normalize, checkid, tic_normalize
# indexDT = False

# File Explorer class
class getExistingDirectories(QFileDialog):
    def __init__(self, *args):
        super(getExistingDirectories, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)


home_dir = os.getcwd()

userInput = input('Would you like to change the settings? (Y/N): ')
if userInput.lower() == 'y':
    settings = OpenSettings()
else:
    with open('SETTINGS.txt') as file:  # If you don't change settings, the defaults are used
        settings = file.read().splitlines()

print('Select the folder(s) containing your raw data and Mass Profiler output: ')
qapp = QApplication(sys.argv)
dlg = getExistingDirectories()
if dlg.exec_() == QDialog.Accepted:
    directories = (dlg.selectedFiles())

Dimensions = []
print('Input sample area aspect ratio: ')
for directory in directories:
    file = os.path.basename(directory)
    width = float(input('%s width: ' % file))

    mw = 0
    while True:
        if width / (10 ** mw) < 10:
            break
        mw += 1

    height = float(input('%s height: ' % file))

    mh = 0
    while True:
        if height / (10 ** mh) < 10:
            break
        mh += 1

    if mh > mw:
        width = width * 10**mh
        height = height * 10**mh
    else:
        width = width * 10**mw
        height = height * 10**mw

    Dimensions.append((int(width), int(height)))

startTime = time.time()

q = 0
for directory in directories:

    # Normalization Prompt
    normalize = 0
    while True:
        normalization_prompt = input('Would you like to generate: \n1. Raw Images Only \n2. Raw + TIC Normalized Images'
                                     ' \n3. Raw + Standards Based Normalized Images \n4. Raw + Both Normalization Types'
                                     '\nInput the desired option and press enter...')
        if normalization_prompt == '1':
            normalize = 0
            break
        elif normalization_prompt == '2':
            normalize = 1
            normalization_type = 'tic'
            break
        elif normalization_prompt == '3':
            normalize = 1
            normalization_type = 'std'
            normalization_ids_prompt = input(
                'Input comma separated values of IDs to be used for normalization: ')
            # 1 Dimensional Numpy array containing IDs to be used for normalization
            normalization_ids = np.fromstring(normalization_ids_prompt, dtype=int, count=-1, sep=',')
            # removing 0 and lower values as IDs can only be positive
            normalization_ids = normalization_ids[normalization_ids > 0]
            # removing repeated IDs and arranging in ascending order
            normalization_ids = np.unique(normalization_ids)
            break
        elif normalization_prompt == '4':
            normalize = 1
            normalization_type = 'both'
            normalization_ids_prompt = input(
                'Input comma separated values of IDs to be used for standards based normalization: ')
            # 1 Dimensional Numpy array containing IDs to be used for normalization
            normalization_ids = np.fromstring(normalization_ids_prompt, dtype=int, count=-1, sep=',')
            # removing 0 and lower values as IDs can only be positive
            normalization_ids = normalization_ids[normalization_ids > 0]
            # removing repeated IDs and arranging in ascending order
            normalization_ids = np.unique(normalization_ids)
        else:
            print("Please enter a valid input; Enter either 1, 2, 3, or 4 \n")

    if '                                 ' in directory:  # prompt to have directories without any space in their names
        print('Error: Please remove spaces from folder path: %s' % directory)
    else:
        os.chdir(directory)
        experiment = directory[directory.rfind("/") + 1:]
        newFile = (experiment + '_TL.csv')
        # Scan in MP export and generate transition list
        for file in glob.glob('*.xls'):
            with open(file) as CSV:
                reader = csv.reader(CSV)
                header = next(reader)
                if header[0][0:12] == 'MassProfiler':  # if file is MP export
                    for i in range(3):
                        # Skip the rest of the default MP header
                        next(reader)
                    columns = str(next(reader))[2:-2].split('\\t')  # Identifies column headers
                    i = 0
                    indexDT = False
                    indexZ = 0
                    for item in columns:
                        if item == 'ID':
                            indexID = i
                        elif item == 'DT':
                            indexDT = i
                        # in some cases m/z has header Mass, modify code according to the .xls
                        elif item == 'm/z' or item == 'Mass':
                            indexMZ = i
                        elif item == 'Z':
                            indexZ = i
                        i += 1

                    # prompt asking whether to use drift time or not to generate images, if the data contains dt
                    # if the data does not have dt column, this prompt will be skipped
                    if indexDT:
                        consider_drift_time = input(
                            "Would you like to use drift time data as well to generate images? (Y/N): ")
                        while True:
                            if consider_drift_time.lower() == 'n':
                                indexDT = False
                                print("Ignoring drift time to generate images and proceeding further \n")
                                break
                            elif consider_drift_time.lower() == 'y':
                                print("Using drift time to generate images and proceeding further \n")
                                break
                            else:
                                print("Please enter a valid input; Select either 'Y/y' or 'N/n' \n")

                    with open(newFile, 'w', newline='') as exportCSV:
                        writer = csv.writer(exportCSV)

                        # if the data does not have values of z, it is automatically assigned 1
                        if indexZ == 0:
                            if indexDT:
                                # Transition list header, Skyline can auto-detect these column headers
                                writer.writerow(['Precursor Name' + '\t' + 'Explicit Drift Time (msec)' + '\t'
                                                 + 'Precursor m/z' + '\t' + 'Precursor Charge'])
                                for line in reader:
                                    newLine = str(line)
                                    newLine = newLine[2:-2].split('\\t')
                                    writer.writerow([newLine[indexID] + '\t' + newLine[indexDT] + '\t'
                                                     + newLine[indexMZ] + '\t' + '1'])
                            else:
                                # Transition list header, Skyline can auto-detect these column headers
                                writer.writerow(['Precursor Name' + '\t' + 'Precursor m/z' + '\t' + 'Precursor Charge'])
                                for line in reader:
                                    newLine = str(line)
                                    newLine = newLine[2:-2].split('\\t')
                                    writer.writerow([newLine[indexID] + '\t' + newLine[indexMZ] + '\t' + '1'])
                        else:
                            if indexDT:
                                # Transition list header, Skyline can auto-detect these column headers
                                writer.writerow(['Precursor Name' + '\t' + 'Explicit Drift Time (msec)' + '\t'
                                                 + 'Precursor m/z' + '\t' + 'Precursor Charge'])
                                for line in reader:
                                    newLine = str(line)
                                    newLine = newLine[2:-2].split('\\t')
                                    writer.writerow([newLine[indexID] + '\t' + newLine[indexDT] + '\t'
                                                     + newLine[indexMZ] + '\t' + newLine[indexZ]])
                            else:
                                # Transition list header, Skyline can auto-detect these column headers
                                writer.writerow(['Precursor Name' + '\t' + 'Precursor m/z' + '\t' + 'Precursor Charge'])
                                for line in reader:
                                    newLine = str(line)
                                    newLine = newLine[2:-2].split('\\t')
                                    writer.writerow([newLine[indexID] + '\t' + newLine[indexMZ] + '\t'
                                                     + newLine[indexZ]])
                else:  # if not a mass profiler export file
                    pass

    try:
        with open(str(os.getcwd() + "\\" + newFile)) as transition_list:
            tl_reader = csv.reader(transition_list)
            tl_columns = next(tl_reader)
            if "Explicit Drift Time" in tl_columns[0]:
                indexDT = True
            else:
                indexDT = False
        transition_list.close()
    except FileNotFoundError:
        try:
            with open(str(os.getcwd() + "\\" + str(experiment) + ".tsv")) as skyline_report:
                sk_reader = csv.reader(skyline_report, delimiter='\t')
                sk_columns = next(sk_reader)
                if "Raw Times" in sk_columns[0]:
                    indexDT = True
                else:
                    indexDT = False
            skyline_report.close()
        except FileNotFoundError:
            pass

    try:
        with open(str(str(os.getcwd()) + "\\" + str(experiment) + '.tsv')) as sklnfile:
            print("\nSkyline report already exists, proceeding further...\n")
            pass
    except FileNotFoundError:
        try:
            with open("CreateReport.bat") as report_creator:
                pass
        except FileNotFoundError:
            # Create SkylineRunner bat file
            if indexDT:
                # SkylineRunner bat file if dt is present
                with open('CreateReport.bat', 'w') as bat:
                    # Could make this into one bat.write() command but minimal gain
                    bat.write('"' + settings[2] + '"')
                    bat.write(' --in=' + '"' + settings[1] + '"')
                    bat.write(' --import-transition-list=' + '"' + os.getcwd() + "\\" + newFile + '"')
                    bat.write(' --out=' + '"' + os.getcwd() + "\\" + experiment + '.sky' + '"')
                    bat.write('\n')
                    bat.write('"' + settings[2] + '"')
                    bat.write(' --in=' + '"' + os.getcwd() + "\\" + experiment + '.sky' + '"')
                    bat.write(' --save')
                    bat.write(' --import-process-count=' + str(os.cpu_count()))
                    bat.write(' --import-all-files=' + '"' + os.getcwd() + '"')
                    bat.write(' --report-name=PythonTemplate --report-add=' + '"' + home_dir + '\\PythonTemplate.skyr' + '"')
                    bat.write(' --report-conflict-resolution=overwrite')
                    bat.write(' --report-file=' + '"' + os.getcwd() + "\\" + experiment + '.tsv' + '"')
                    bat.write(' --report-format=TSV')
                    bat.write(' --chromatogram-file=' + '"' + os.getcwd() + "\\" + experiment + "_TIC" + ".tsv" + '"')
                    bat.write(' --chromatogram-tics')

            else:
                # SkylineRunner bat file if dt is not present
                with open('CreateReport.bat', 'w') as bat:
                    bat.write('"' + settings[2] + '"')
                    bat.write(' --in=' + '"' + settings[1] + '"')
                    bat.write(' --import-transition-list=' + '"' + os.getcwd() + "\\" + newFile + '"')
                    bat.write(' --out=' + '"' + os.getcwd() + "\\" + experiment + '.sky' + '"')
                    bat.write('\n')
                    bat.write('"' + settings[2] + '"')
                    bat.write(' --in=' + '"' + os.getcwd() + "\\" + experiment + '.sky' + '"')
                    bat.write(' --save')
                    bat.write(' --import-process-count=' + str(os.cpu_count()))
                    bat.write(' --import-all-files=' + '"' + os.getcwd() + '"')
                    bat.write(' --report-name=PythonTemplateNoDrift --report-add=' + '"' + home_dir + '\\PythonTemplateNoDrift.skyr' + '"')
                    bat.write(' --report-conflict-resolution=overwrite')
                    bat.write(' --report-file=' + '"' + os.getcwd() + "\\" + experiment + '.tsv' + '"')
                    bat.write(' --report-format=TSV')
                    bat.write(' --chromatogram-file=' + '"' + os.getcwd() + "\\" + experiment + "_TIC" + ".tsv" + '"')
                    bat.write(' --chromatogram-tics')

        # Run bat file
        print('\n\033[4m%s\033[0m\nCreating Skyline report, this will take several minutes..' % os.path.basename(
            directory))
        p = Popen("CreateReport.bat", cwd=os.getcwd())
        stdout, stderr = p.communicate()

    tic_path = str(os.getcwd() + "\\" + experiment + "_TIC" + ".tsv")

    # Open TSV (Skyline Report)
    TSVname = ('%s\\%s.tsv' % (os.getcwd(), experiment))
    bigData_raw = OpenTSV(TSVname, indexDT)

    print('\n')

    # Create Images

    # Raw Images
    bigData = bigData_raw
    pathlib.Path('./Images_Raw_Not_Normalized').mkdir(parents=True, exist_ok=True)
    os.chdir('./Images_Raw_Not_Normalized')
    print('\n Creating raw images \n')

    i = 1
    for medData in bigData:
        medData[0].width = Dimensions[q][0]
        medData[0].height = Dimensions[q][1]
        SaveImage(medData, settings)
        CreateTxtFile(medData)
        sys.stdout.write('\rProcessing image %d of %d' % (i, bigData.shape[0]))
        i += 1

    # Normalized Images
    if normalize == 1:
        if normalization_type == 'tic':
            bigData = tic_normalize(bigData_raw, tic_path)
            os.chdir('..')
            try:
                with open(str(os.getcwd() + "\\" + str(experiment) + "_TIC" + ".tsv")) as tic_chromatogram:
                    print("\nTIC Chromatogram already exists, proceeding further...\n")
                    # time.sleep(2)
                    pass
            except FileNotFoundError:
                with open('GetTIC.bat', 'w') as bat:
                    bat.write(settings[2])
                    bat.write(' --in=' + os.getcwd() + "\\" + experiment + '.sky')
                    bat.write(' --save')
                    bat.write(' --chromatogram-file=' + os.getcwd() + "\\" + experiment + "_TIC" + ".tsv")
                    bat.write(' --chromatogram-tics')
                print("Generating TIC Chromatogram...")
                p = Popen("GetTIC.bat", cwd=os.getcwd())
                stdout, stderr = p.communicate()

            pathlib.Path('./Images' + '_Normalized_To_' + 'TIC').mkdir(parents=True, exist_ok=True)
            os.chdir('./Images' + '_Normalized_To_' + 'TIC')
            print('\n' + 'Creating images normalized to TIC Chromatogram' + '\n')

            i = 1
            for medData in bigData:
                medData[0].width = Dimensions[q][0]
                medData[0].height = Dimensions[q][1]
                SaveImage(medData, settings)
                CreateTxtFile(medData)
                sys.stdout.write('\rProcessing image %d of %d' % (i, bigData.shape[0]))
                i += 1

        elif normalization_type == 'std':
            # looping over all the normalization ids
            for value in normalization_ids:
                # checkid returns the array to be used for normalization, whether the give standard is suitable for
                # normalization, and an array containing the lengths of intensities - so that the normalization array
                # can be suitable trimmed before dividing
                (normalization_array, normalization_suitability, length_intensities) = checkid(bigData_raw, value, 95)
                if normalization_suitability:
                    bigData = std_normalize(bigData_raw, normalization_array, length_intensities)
                    value_mz = bigData[value - 1][0].mz
                    pathlib.Path('../Images' + '_Normalized_To_' + 'MZ_' + str(value_mz)).mkdir(parents=True,
                                                                                                exist_ok=True)
                    os.chdir('../Images' + '_Normalized_To_' + 'MZ_' + str(value_mz))
                    print('\n' + 'Creating images normalized to m/z = ' + str(value_mz) + '\n')

                    i = 1
                    for medData in bigData:
                        medData[0].width = Dimensions[q][0]
                        medData[0].height = Dimensions[q][1]
                        SaveImage(medData, settings)
                        CreateTxtFile(medData)
                        sys.stdout.write('\rProcessing image %d of %d' % (i, bigData.shape[0]))
                        i += 1

        elif normalization_type == 'both':
            bigData = tic_normalize(bigData_raw, tic_path)
            os.chdir('..')
            try:
                with open(str(os.getcwd() + "\\" + str(experiment) + "_TIC" + ".tsv")) as tic_chromatogram:
                    print("\nTIC Chromatogram already exists, proceeding further...\n")
                    # time.sleep(2)
                    pass
            except FileNotFoundError:
                with open('GetTIC.bat', 'w') as bat:
                    bat.write(settings[2])
                    bat.write(' --in=' + os.getcwd() + "\\" + experiment + '.sky')
                    bat.write(' --save')
                    bat.write(' --chromatogram-file=' + os.getcwd() + "\\" + experiment + "_TIC" + ".tsv")
                    bat.write(' --chromatogram-tics')
                print("Generating TIC Chromatogram...")
                p = Popen("GetTIC.bat", cwd=os.getcwd())
                stdout, stderr = p.communicate()

            pathlib.Path('./Images' + '_Normalized_To_' + 'TIC').mkdir(parents=True, exist_ok=True)
            os.chdir('./Images' + '_Normalized_To_' + 'TIC')
            print('\n' + 'Creating images normalized to TIC Chromatogram' + '\n')

            i = 1
            for medData in bigData:
                medData[0].width = Dimensions[q][0]
                medData[0].height = Dimensions[q][1]
                SaveImage(medData, settings)
                CreateTxtFile(medData)
                sys.stdout.write('\rProcessing image %d of %d' % (i, bigData.shape[0]))
                i += 1

            # looping over all the normalization ids
            for value in normalization_ids:
                # checkid returns the array to be used for normalization, whether the give standard is suitable for
                # normalization, and an array containing the lengths of intensities - so that the normalization array
                # can be suitable trimmed before dividing
                (normalization_array, normalization_suitability, length_intensities) = checkid(bigData_raw, value, 95)
                if normalization_suitability:
                    bigData = std_normalize(bigData_raw, normalization_array, length_intensities)
                    value_mz = bigData[value - 1][0].mz
                    pathlib.Path('../Images' + '_Normalized_To_' + 'MZ_' + str(value_mz)).mkdir(parents=True,
                                                                                                exist_ok=True)
                    os.chdir('../Images' + '_Normalized_To_' + 'MZ_' + str(value_mz))
                    print('\n' + 'Creating images normalized to m/z = ' + str(value_mz) + '\n')

                    i = 1
                    for medData in bigData:
                        medData[0].width = Dimensions[q][0]
                        medData[0].height = Dimensions[q][1]
                        SaveImage(medData, settings)
                        CreateTxtFile(medData)
                        sys.stdout.write('\rProcessing image %d of %d' % (i, bigData.shape[0]))
                        i += 1

    print('\ndone\n')

print('Processing time: %.2f sec' % (time.time() - startTime))
