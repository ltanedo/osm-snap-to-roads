import sys
import os
import glob
import datetime as DT
import time

def main():
    
    POINT_COUNTER = 0
    path = os.getcwd() + '/data'
    AVG_SPEED = 0 

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                files.append(os.path.join(r, file))
                
                if len(sys.argv) == 1:
                    POINT_COUNTER, AVG_SPEED = get_total_average(files,POINT_COUNTER,AVG_SPEED)
                if len(sys.argv) == 3:
                    POINT_COUNTER, AVG_SPEED = get_specific_average(files,POINT_COUNTER,AVG_SPEED)
    
    if POINT_COUNTER != 0:
        AVG_SPEED /= POINT_COUNTER
    
    if len(sys.argv) == 3:
        print('Target_Time = "{}" Interval = "{}" Minutes'.format(sys.argv[1],sys.argv[2]))
        print('- Point Count: "{}"'.format(POINT_COUNTER))
        print('- Avg Speed  : "{}"'.format(AVG_SPEED))
    else:
        print('- Point Count: "{}"'.format(POINT_COUNTER))
        print('- Avg Speed  : "{}"'.format(AVG_SPEED))

def get_total_average(files,POINT_COUNTER,AVG_SPEED):
    for input_file in files:
        file_reader = open(input_file)
        for line in file_reader:

            args = line.split(',')
            if (len(args) < 7):
                continue

            timestamp_unix = args[1].replace('"', '')
            speed = args[4].replace('"', '')

            if (timestamp_unix != 'system_time'):
                seconds_since_epoch = int(timestamp_unix) / 1000
                timestamp = DT.datetime.utcfromtimestamp(seconds_since_epoch).isoformat()
                POINT_COUNTER += 1
                AVG_SPEED += float(speed)
                # date = DT.datetime.fromisoformat(timestamp)

    return POINT_COUNTER, AVG_SPEED 
    
             
def get_specific_average(files,POINT_COUNTER,AVG_SPEED):

    if ( isTimeFormat(sys.argv[1]) == False or isinstance(int(sys.argv[2]),int) == False or int(sys.argv[2]) > 59):
        print('WRONG FORMAT TRY -> python3 write_averages.py <TIME> <INTERVAL(Min)>')
        exit()

    target_time = sys.argv[1].split(':')
    interval_min = int(sys.argv[2])

    for input_file in files:
        file_reader = open(input_file)
        for line in file_reader:
            args = line.split(',')
            if (len(args) < 7):
                continue
            timestamp_unix = args[1].replace('"', '')
            speed = args[4].replace('"', '')
            if (timestamp_unix != 'system_time'):
                seconds_since_epoch = int(timestamp_unix) / 1000
                timestamp = DT.datetime.utcfromtimestamp(seconds_since_epoch).isoformat()
                
                #only process within target
                date = DT.datetime.fromisoformat(timestamp)
                if (check_interval(date, target_time, interval_min)):
                    POINT_COUNTER += 1
                    AVG_SPEED += float(speed)
                


    return POINT_COUNTER, AVG_SPEED 

def check_interval(datetime_object, target_time, interval):
    result = False

    target_hour = int(target_time[0])
    target_minute = int(target_time[1])

    new_hour = target_hour
    new_minute = target_minute

    if (target_minute + interval > 59):
        new_hour += 1
        new_minute = target_minute + interval - 60
    else:
        new_minute = target_minute + interval
    
    check_hour = datetime_object.hour
    check_minute = datetime_object.minute

    if (target_hour == new_hour):
        if (check_hour == target_hour):
            if (check_minute > target_minute and check_minute < new_minute):
                result = True
    if (target_hour + 1 == new_hour):
        if (check_hour == target_hour):
            if (check_minute > target_minute):
                result = True
        if (check_hour == new_hour):
            if (check_minute < new_minute):
                result = True
    
    return result

def isTimeFormat(input):
    try:
        time.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    main()