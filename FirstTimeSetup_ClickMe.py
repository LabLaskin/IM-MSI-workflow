# Run this if it is your first time using MSIC
# This just runs the command-line code to install the Python dependencies
# Most of these should come with Anaconda, so if you know what you are doing
# You can open the bat file and simply install the ones you need

from subprocess import Popen
import os

p = Popen('setup.bat', cwd=os.getcwd())
stdout, stderr = p.communicate()

print("All dependencies installed")
