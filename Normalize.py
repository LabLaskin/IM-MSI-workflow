import numpy as np
import pandas as pd


def checkid(bigdata_raw, normalization_id, tolerance):
    #  checks whether the given id is suitable for normalization, also returns the array to be used for normalization
    # all intensity rows night have different length, so a normalization array is created with all rows having same
    # length, which equals the length of the longest intensity row. This approach makes it easier to generate the
    # normalization array. When this array is actually used as a divisor to normalize, extra values at the end of
    # rows are deleted to make each row length equal to the original length. This is done by keeping an index of
    # actual row lengths in length_intesities array

    # generating the length_intesities array
    length_intensities = bigdata_raw[0][0].intensities.shape[0]
    for i in range(1, bigdata_raw.shape[1]):
        length_intensities = np.append(length_intensities, [bigdata_raw[0][i].intensities.shape[0]])
    # print(length_intensities)

    max_length_intensities = np.amax(length_intensities)  # maximum length of the intensities rows

    #  generating the first row of the intensities array. Subsequent rows will be appended
    normalization_array_to_append = np.append(bigdata_raw[normalization_id-1][0].intensities,
                                              np.zeros((max_length_intensities - length_intensities[0])))
    normalization_array = np.array([normalization_array_to_append])
    # print(normalization_array_to_append.shape)
    # print(normalization_array.shape)

    for i in range(1, bigdata_raw.shape[1]):
        normalization_array_to_append = np.append(bigdata_raw[normalization_id-1][i].intensities,
                                                  np.zeros((max_length_intensities - length_intensities[i])))
        # print(normalization_array_to_append.shape)
        normalization_array = np.append(normalization_array, [normalization_array_to_append], axis=0)
        # print(normalization_array.shape)

    (rows, columns) = normalization_array.shape

    # if the number of zeros is more than the tolerance, the id is not suitable for normalization
    # tolerance is a percentage, varying between 0 and 100
    if np.count_nonzero(normalization_array)/normalization_array.size * 100 >= 100-tolerance:
        id_normalization_suitability = True
    else:
        id_normalization_suitability = False

    # the zeros in the normalizing array are to be replaced with the mean of the nearest neighbours
    # since we wish to take the mean of numbers originally in the array, a copy has been created
    # values will be taken from the normalization_array, and their mean will be put in the normalization_array_return
    # the function returns normalization_array_return

    normalization_array_return = normalization_array

    if id_normalization_suitability:
        # normalizing the first row, last column element
        if normalization_array[0][0] == 0:
            normalization_array_return[0][0] = np.mean(
                np.array([normalization_array[0][1], normalization_array[1][0], normalization_array[1][1]]))
            if normalization_array_return[0][0] == 0:
                id_normalization_suitability = False

        # normalizing the first row, last column element
        if normalization_array[0][columns - 1] == 0:
            normalization_array_return[0][columns - 1] = np.mean(np.array(
                [normalization_array[0][columns - 2], normalization_array[1][columns - 1],
                 normalization_array[1][columns - 2]]))
            if normalization_array_return[0][columns - 1] == 0:
                id_normalization_suitability = False

        # normalizing the last row, first column element
        if normalization_array[rows - 1][0] == 0:
            normalization_array_return[rows - 1][0] = np.mean(np.array(
                [normalization_array[rows - 2][0], normalization_array[rows - 1][1], normalization_array[rows - 2][1]]))
            if normalization_array_return[rows - 1][0] == 0:
                id_normalization_suitability = False

        # normalizing the last row, last column element
        if normalization_array[rows - 1][columns - 1] == 0:
            normalization_array_return[rows - 1][columns - 1] = np.mean(np.array(
                [normalization_array[rows - 2][columns - 1], normalization_array[rows - 1][columns - 2],
                 normalization_array[rows - 2][columns - 2]]))
            if normalization_array_return[rows - 1][columns - 1] == 0:
                id_normalization_suitability = False

    # normalizing the first and the last rows
    if id_normalization_suitability:
        for i in range(1, columns-1):
            if normalization_array[0][i] == 0:
                normalization_array_return[0][i] = np.mean(np.array(
                    [normalization_array[0][i - 1], normalization_array[0][i + 1], normalization_array[1][i - 1],
                     normalization_array[1][i], normalization_array[1][i + 1]]))
                if normalization_array_return[0][i] == 0:
                    id_normalization_suitability = False
                    break

            if normalization_array[rows - 1][i] == 0:
                normalization_array_return[rows - 1][i] = np.mean(np.array(
                    [normalization_array[rows - 1][i - 1], normalization_array[rows - 1][i + 1],
                     normalization_array[rows - 2][i - 1], normalization_array[rows - 2][i],
                     normalization_array[rows - 2][i + 1]]))
                if normalization_array_return[rows - 1][i] == 0:
                    id_normalization_suitability = False
                    break

    # normalizing the first and last columns
    if id_normalization_suitability:
        for i in range(1, rows-1):
            if normalization_array[i][0] == 0:
                normalization_array_return[i][0] = np.mean(np.array(
                    [normalization_array[i - 1][0], normalization_array[i + 1][0], normalization_array[i - 1][1],
                     normalization_array[i][1], normalization_array[i + 1][1]]))
                if normalization_array_return[i][0] == 0:
                    id_normalization_suitability = False
                    break

            if normalization_array[i][columns - 1] == 0:
                normalization_array_return[i][columns - 1] = np.mean(np.array(
                    [normalization_array[i - 1][columns - 1], normalization_array[i + 1][columns - 1],
                     normalization_array[i - 1][columns - 2], normalization_array[i][columns - 2],
                     normalization_array[i + 1][columns - 2]]))
                if normalization_array_return[i][columns - 1] == 0:
                    id_normalization_suitability = False
                    break

    # normalizing the remaining elements
    if id_normalization_suitability:
        for i in range(1, rows-1):
            for j in range(1, columns-1):
                if normalization_array[i][j] == 0:
                    normalization_array_return[i][j] = np.mean(np.array(
                        [normalization_array[i - 1][j - 1], normalization_array[i - 1][j],
                         normalization_array[i - 1][j + 1], normalization_array[i][j - 1],
                         normalization_array[i][j + 1],
                         normalization_array[i + 1][j - 1], normalization_array[i + 1][j],
                         normalization_array[i + 1][j + 1]]))
                    if normalization_array_return[i][j] == 0:
                        id_normalization_suitability = False
                        break
            else:
                continue
            break

    return normalization_array_return, id_normalization_suitability, length_intensities


def std_normalize(bigdata_raw, normalization_array, length_intensities):  # performs standard based normalization
    # normalize bigData using the given normalization array and the intensity length array

    bigdata = bigdata_raw

    for i in range(bigdata_raw.shape[0]):
        for j in range(bigdata_raw.shape[1]):
            bigdata[i][j].intensities = bigdata_raw[i][j].intensities * 10 / normalization_array[j][:(length_intensities[j])]

    return bigdata


def tic_normalize(bigdata_raw, tic_path):
    # normalize using the total ion current chromatogram
    bigdata = bigdata_raw
    df = pd.read_csv(tic_path, sep='\t')  # reading .tsv using pandas
    reader = df.values

    # an array to collect the max common factors (multiples of 10) in all intensities
    common_factor_array = np.zeros((bigdata_raw.shape[0], bigdata_raw.shape[1]))

    for i in range(bigdata_raw.shape[0]):
        for j in range(bigdata_raw.shape[1]):
            divisor_intensties = np.fromstring(reader[j][9], dtype=float, count=-1, sep=',')
            bigdata[i][j].intensities = bigdata_raw[i][j].intensities / divisor_intensties
            intensities_power_array = np.zeros((divisor_intensties.shape[0]))
            for k in range(divisor_intensties.shape[0]):
                m = 0
                while True:
                    if divisor_intensties[k] / (10 ** m) < 10:
                        break
                    m += 1
                intensities_power_array[k] = 10**m
            common_factor_array[i][j] = np.mean(intensities_power_array)

    # normalizing factor is the average number (as a multiple of 10) which is present in all TIC intensities
    normalization_factor = np.mean(common_factor_array)
    for i in range(bigdata.shape[0]):
        for j in range(bigdata.shape[1]):
            bigdata[i][j].intensities = bigdata[i][j].intensities * normalization_factor

    return bigdata
