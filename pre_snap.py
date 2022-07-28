import sys
import re
import os
import glob
import datetime as DT
from math import sin, cos, sqrt, atan2, radians


def main():
    list_gpx_files = []
    list_txt_files = []

    path = os.getcwd() + '/data'

    for r, d, f in os.walk(path):
        for file in f:
            if '.gpx' in file:
                list_gpx_files.append(os.path.join(r, file))

    for r, d, f in os.walk(path):
        for file in f:
            if 'gps.txt' in file:
                list_txt_files.append(os.path.join(r, file))



    # print('=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=> ALL FILES') 
    # print('all gpx files: ', list_gpx_files)
    # print('all txt files: ', list_txt_files)

    print('=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=> CONVERTING') 

    for txt_file_name in list_txt_files:
        if txt_file_name.replace('.txt', '.gpx') not in list_txt_files:
            run(txt_file_name)

    print('=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=>=> ALL COMPLETED ')

def run(input_file):

    file_reader = open(input_file)
    output_file = input_file.replace('.txt', '.gpx')
    
    #point to list
    list_points = []
    list_time = []
    for line in file_reader:
        
        # points to list
        point = line_to_point(line, list_points, list_time)

    #remove outliers
    remove_outliers(list_points, list_time)

    print("-  number of points converted: ", len(list_points))

    open(output_file, 'w').close()
    with open(output_file, 'a') as out:

        write_header(input_file.replace('.txt', ''), out)
        write_body(list_points, list_time, out)

        # write closers
        out.write('  </trkseg>\n')
        out.write('</trk>\n')
        out.write('</gpx>\n')

    file_reader.close()
    print('   [', input_file, ' -> CONVERTED ]')

def write_body(list_points, list_time, out):
    # 1 -> <trkpt lat="42.99859992" lon="-78.81866368">
    # lat.strip(",")
    # temp = str('    <trkpt lat="' + lat + '" lon="' + lon + '">\n')
    # out.write(temp)

    # #2 -> <time>2018-11-14T14:41:42Z</time>
    # temp = str('      <time>' + timestamp + '</time>\n')
    # out.write(temp)

    # #3 -> <course>96.2</course>
    # #temp = str('      <course> </course>\n')
    # #out.write(temp)

    # #4 -> <speed>0.35</speed>
    # temp = str('      <speed>' + speed +'</speed>\n')
    # out.write(temp)

    # #</trkpt>
    # out.write('    </trkpt>\n')

    for idx, point in enumerate(list_points):
        
        temp = str('    <trkpt lat="' + point[0] + '" lon="' + point[1] + '">\n')
        out.write(temp)

        #2 -> <time>2018-11-14T14:41:42Z</time>
        seconds_since_epoch = int(list_time[idx]) / 1000
        timestamp = DT.datetime.utcfromtimestamp(seconds_since_epoch).isoformat()
        temp = str('      <time>' + str(timestamp) + '</time>\n')
        out.write(temp)

        out.write('    </trkpt>\n')

def write_header(name, out):
    
    # write header
    out.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
    out.write('<gpx version="1.0" creator="GPS Visualizer http://www.gpsvisualizer.com/" xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n')
    out.write('<trk>\n')
    
    # write filename
    out.write('  <name>' + name + '</name>\n')
    out.write('  <trkseg>\n')
    

def remove_outliers(list_points, list_time):

    previousDistance = 0
    for idx in range(1, len(list_points)):

        if (idx == len(list_points)):
            break
        if idx > len(list_points):
            break

        # print(idx)
        # print(len(list_points))
        previousPoint = list_points[idx - 1]
        currentPoint = list_points[idx]

        # remove when greater than 10
        if ( dist(previousPoint, currentPoint) > 1.5):
            list_points.pop(idx)
            list_time.pop(idx)
            idx -= 1

        

def line_to_point(line, list_points, time):
    # print(line)
    if '"timestamp"' not in line:
        args = line.split(',')
        if len(args) > 4:
            system_time = args[1].replace('"', '')
            lat = args[2].replace('"', '')
            lon = args[3].replace('"', '')
            speed = args[4].replace('"', '')

            time.append((system_time))
            list_points.append([lat,lon])
        
def dist(point_one, point_two):
    # approximate radius of earth in km
    R = 6373.0

    #lat1 = radians(52.2296756)
    #lon1 = radians(21.0122287)
    #lat2 = radians(52.406374)
    #lon2 = radians(16.9251681)

    lat1 = float(point_one[0])
    lon1 = float(point_one[1])

    lat2 = float(point_two[0])
    lon2 = float(point_two[1])

    dlon = float(lon2) - float(lon1)
    dlat = float(lat2) - float(lat1)

    dlon = float(dlon) 
    dlat = float(dlat)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    #print("Result:", distance)
    # print("Should be:", 278.546, "km")

    return distance

if __name__ == '__main__':
    main()