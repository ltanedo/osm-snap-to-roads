import sys
import os
import glob
from datetime import datetime


def main():

    list_files = []


    path = os.getcwd() + '/data'

    for r, d, f in os.walk(path):
        for file in f:
            if 'gps.txt' not in file:
                list_files.append(os.path.join(r, file))

    for file in list_files:
        os.remove(file)
        print("- REMOVED! => {}".format(file))

if __name__ == '__main__':
    main()
