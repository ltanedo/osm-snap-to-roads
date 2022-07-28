import sys
import os
import glob
from datetime import datetime


def main():

    list_gpx_files = []
    list_txt_files = []

    path = os.getcwd() + '/data'

    for r, d, f in os.walk(path):
        for file in f:
            if 'gps.gpx.res.gpx' in file:
                list_gpx_files.append(os.path.join(r, file))

    for r, d, f in os.walk(path):
        for file in f:
            if 'gps.txt' in file:
                list_txt_files.append(os.path.join(r, file))

    for gpx_file_name in list_gpx_files:
        # if '<speed>' not in open(gpx_file_name).read():
        #     has_txt(gpx_file_name, list_txt_files)
        # else: 
        #     print('-> "{}" already has <speed>')
        has_txt(gpx_file_name, list_txt_files)
    
    print_analytics()

def has_txt(gpx_file_name, list_txt_files):

    # strip 'gpx' + add 'txt'
    txt_file_name = gpx_file_name.replace('.gpx.res.gpx','.txt')

    # check name
    if txt_file_name in list_txt_files:
        add_speed(txt_file_name, gpx_file_name)
        print('=> "{}" - adding speed ...'.format(txt_file_name))
    else:
        print('=> "{}" - has no equivalent ".txt"'.format(gpx_file_name))

def print_analytics():
    print('--finished--')

def add_speed(txt_file_name, gpx_file_name):
    
    time_speed_dict = return_speed_time_dict(txt_file_name)

    # wrtie to file
    input_file = gpx_file_name
    output_file = gpx_file_name.replace('.gpx.res.gpx','_matched.txt')
    file_reader = open(input_file)
    open(output_file, 'w').close()
    with open(output_file, 'a') as out:
        
        # write header
        out.write('"timestamp","system_time","lat","lon","speed","bearing","provider"\n')

        # vars
        point_counter = 0
        timestamp = 0
        lat = 0
        lon = 0
        speed = 0

        for line in file_reader:
            
            # beginninvg
            # <trkpt lat="43.0981332" lon="-78.9782267">
            if '<trkpt' in line:
                line = line.replace('<trkpt lat="','')
                line = line.replace('" lon="',', ')
                line = line.replace('">','')
                line = line.replace('<time>',',')
                line = line.replace('</time>','')
                line = line.replace('</trkpt>','')
                line = line.replace(' ','')
                line = line.strip('\n')
                args = line.split(',')

                lat = args[0].replace(' ', '')
                lon = args[1]
                timestamp = args[2]

                point_counter += 1
                write_coord(timestamp, lat, lon, speed, out, time_speed_dict)

        print("- number of points converted: ",point_counter)

    file_reader.close()

# write individual points
def write_coord(timestamp, lat, lon, speed, out, time_speed_dict):
    
    try:
        timestamp = timestamp.strip('Z')
        # print('try: ', timestamp)

        speed = time_speed_dict[timestamp]
    except KeyError:
        speed = "N/A"
    pass
    # speed = time_speed_dict[timestamp]
    
    timestamp = datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S')
    timestamp = timestamp.timestamp() * 1000
    temp = ('"0000000000000","{}","{}","{}","{}","0.0","gps"\n').format(int(timestamp), lat, lon, speed)
    out.write(temp)
    return



def return_speed_time_dict(txt_file_name):
    
    return_dict = {}
    with open(txt_file_name) as f:
        for line in f:

            #print (line)
            args = line.split(',')
            if len(args) > 4: 

                timestamp_unix = args[1].replace('"', '')
                speed = args[4].replace('"', '')
     
                if (timestamp_unix != 'system_time'):
                    seconds_since_epoch = int(timestamp_unix) / 1000
                    timestamp = datetime.utcfromtimestamp(seconds_since_epoch).isoformat()
                    timestamp = timestamp[:-7]

                    key_value = {timestamp: speed}
                    return_dict.update(key_value)

    return return_dict

if __name__ == "__main__":
    main()