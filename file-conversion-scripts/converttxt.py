import sys
from datetime import datetime
import dateutil.parser as dp

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
        output_file = input_file.strip('gpx') + 'txt'
        name = input_file.strip('.gpx')
    else:
        print('ERROR: WRONG ARGUMENTS')
        sys.exit(0)

    # wrtie to file
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
            if '<trkpt' in line:
                line = line.split()
                line.pop(0)
                line[1] = line[1].strip('>')

                lat = line[0].strip('lat=')
                lon = line[1].strip('lon=')
                lat = lat.replace('"','')
                lon = lon.replace('"','')

            if '<time>' in line:
                line = line.replace(' ','')
                line = line.strip('<time>')
                line = line.strip('</time>\n')
                # line = line.strip('Z')
                # line = line + '.00Z'

                # utc_dt = datetime.strptime(line, '%Y-%m-%dT%H:%M:%S.%fZ')
                # timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
                parsed_t = dp.parse(line)
                t_in_seconds = parsed_t.strftime('%s')
                timestamp = t_in_seconds

            if '<course>' in line:
                line = line.replace(' ','')
                line = line.strip('<course>')
                line = line.strip('</course>\n')

      
            if '<speed>' in line:
                line = line.replace(' ','')
                line = line.strip('<speed>')
                line = line.strip('</speed>\n')
                speed = line


            # ending
            if '</trkpt>' in line:
                point_counter += 1
                write_coord(timestamp, lat, lon, speed, out)

        print("- number of points converted: ",point_counter)

    file_reader.close()

# write individual points
def write_coord(timestamp, lat, lon, speed, out):
    
    temp = ('"{}","0000000000000","{}","{}","{}","0.0","gps"\n').format(timestamp, lat, lon, speed)
    out.write(temp)
    return

if __name__ == "__main__":
    main()