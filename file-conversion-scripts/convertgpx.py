import sys
import datetime as DT

def main():

    # initial filenames
    script_name = ''
    input_file = ''
    output_file = ''
    name = ''

    # get args
    if len(sys.argv) == 2:
        print('- number of arguments:        ', len(sys.argv))
        script_name = sys.argv[0]
        input_file = sys.argv[1]
        output_file = input_file.strip('txt') + 'gpx'
        name = input_file.strip('.txt')
    elif len(sys.argv) == 3:
        print('number of arguments: ', len(sys.argv))
        script_name = sys.argv[0]
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        name = output_file.strip('.gpx')
        if name == 's':
            name = 'gps'
    else:
        print('ERROR: WRONG ARGUMENTS')
        sys.exit(0)

    # wrtie to file
    file_reader = open(input_file)
    open(output_file, 'w').close()
    with open(output_file, 'a') as out:
        
        # write header
        out.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
        out.write('<gpx version="1.0" creator="GPS Visualizer http://www.gpsvisualizer.com/" xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n')
        out.write('<trk>\n')
        
        # write filename
        out.write('  <name>' + name + '</name>\n')
        out.write('  <trkseg>\n')

        # write gps points
        point_counter = 0
        for line in file_reader:

            # strip chars
            line = line.rstrip()
            line = line.replace('"', '')
            args = line.split(",")

            if len(args) == 7:
                write_to_gpx(args,out)
            
            # count points
            point_counter += 1

        print("- number of points converted: ",point_counter)

        # write closers
        out.write('  </trkseg>\n')
        out.write('</trk>\n')
        out.write('</gpx>\n')

    file_reader.close()

# write individual points
def write_to_gpx(args, out):
    
    # store 7 values
    timestamp = args[0]
    system_time = args[1]
    lat = args[2]
    lon = args[3]
    speed = args[4]
    bearing = args[5]
    provider = args[6]

    if (lat != 'lat'):
        # 1 -> <trkpt lat="42.99859992" lon="-78.81866368">
        lat.strip(",")
        temp = str('    <trkpt lat="' + lat + '" lon="' + lon + '">\n')
        out.write(temp)

        #2 -> <time>2018-11-14T14:41:42Z</time>
        seconds_since_epoch = int(timestamp) / 1000
        timestamp = DT.datetime.utcfromtimestamp(seconds_since_epoch).isoformat()
        temp = str('      <time>' + timestamp + '</time>\n')
        out.write(temp)

        #3 -> <course>96.2</course>
        #temp = str('      <course> </course>\n')
        #out.write(temp)

        #4 -> <speed>0.35</speed>
        temp = str('      <speed>' + speed +'</speed>\n')
        out.write(temp)

        #</trkpt>
        out.write('    </trkpt>\n')

    return

if __name__ == "__main__":
    main()