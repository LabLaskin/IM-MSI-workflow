def IsNumber(number):
    # Check if a variable is a number
    try:
        float(number)
        return True
    except ValueError:
        return False


def IsEmpty(list):
    # Check if a list is empty
    try:
        list[-1]
        return False
    except IndexError:
        return True


def CMaptoColor(cmapOutput):
    # Input is the output of matplotlib.pyplot.get_cmap(value)
    # Returns an RGBA color in the form of a tuple
    color = []

    for number in cmapOutput:
        color.append(int(number * 255))

    return tuple(color)


def TypeChange(list, Type):
    # Change every element in a list to a new type
    newList = []

    for item in list:
        newList.append(Type(item))
    return newList


def ShowSettings(settings):
    print('\n#) Setting Name:          Current Setting')
    print('-----------------------------------------')
    print('1) Home Directory:    ' + settings[0])
    print('2) Skyline Template:  ' + settings[1])
    print('3) SkylineRunner.exe: ' + settings[2])
    print('4) Image Save Format: ' + settings[3])
    print('5) Color Map Style:   ' + settings[4])
    print('\n6) Save and Continue')
    print('7) Restore Defaults')
    print('8) Set Current as Default')
    print('0) Quit w/o saving')


def OpenSettings():
    settings = []
    with open('SETTINGS.txt') as file:
        settings = file.read().splitlines()

    while True:
        ShowSettings(settings)
        selection = int(input('Select a setting to change: '))
        if selection == 1:
            settings[0] = input('Enter path to home directory (ex. X:\\Drive\\Data): ')
        elif selection == 2:
            settings[1] = input('Enter path to Skyline Template (use \\ or /): ')
        elif selection == 3:
            settings[2] = input('Enter path to SkylineRunner.exe (use \\ or /): ')
        elif selection == 4:
            settings[3] = str(input('Enter image save format (ex. .png, must include the .): '))
        elif selection == 5:
            settings[4] = input('Enter color map style (from matplotlib.pyplot.get_cmap): ').lower()
        elif selection == 6:
            # Save settings
            print('Settings saved.\n')
            return(settings)
        elif selection == 7:
            # Reset to default settings
            settings[0] = 'C:\\'
            settings[1] = 'Z:\\RESEARCH\\Code\\Skyline\\template.sky'
            settings[2] = 'E:\\Downloads\\SkylineDailyRunner.exe'
            settings[3] = '.png'
            settings[4] = 'hot'
            print('Settings reset to default.')
        elif selection == 8:
            # Save as default settings
            print('Settings saved as default')
            with open('SETTINGS.txt', 'w+') as file:   ## This *might* be a problem if printing a short item on top of a long one (might not overwrite the whole line leaving you with dangling characters)
                for item in settings:
                    file.write(item + '\n')
        elif selection == 0:
            print('No changes made.')
            return(settings)
            break
        else:
            print('Didn\'t recognize your selection. Please try again.')
