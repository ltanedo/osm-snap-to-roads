"""
Look for duration between points

Written and tested in Python 3.7
"""

import os
import pandas as pd
from datetime import datetime
import pickle as pk
from collections import defaultdict
import json
from typing import List
import bisect

import matplotlib.pyplot as plt

from geopy.distance import distance

DEBUG = True


class LatLng:
    """
    Latitude and Longitude pair
    """

    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng

    def to_tuple(self):
        return (self.lat, self.lng)

    def __str__(self):
        return ",".join([str(self.lat), str(self.lng)])


class SrcDst:
    """
    Source and Destination pair
    """

    def __init__(self, source: LatLng, dest: LatLng, source_name: str, dest_name: str):
        """
        Source and destination

        The details of a source and destination pair

        Parameters
        ----------
        source : LatLng obj
            The LatLng of the source point

        dest : LatLng
            The LatLng of the destination point

        source_name : str
            The name of the source

        dest_name : str
            The name of the destination
        """

        self.source = source
        self.dest = dest
        self.source_name = source_name
        self.dest_name = dest_name

    def name(self):
        return self.source_name + "-" + self.dest_name

    def __str__(self):
        return "source: " + str(self.source) + ", destination: " + str(self.dest)


class Path:
    def __init__(self, source: LatLng, dest: LatLng):
        self.source = source
        self.dest = dest
        self.path = []
        self.time = None


def distance_between_gps(point1: LatLng, point2: LatLng) -> float:
    """
    Get the distance between two GPS points. Unit: meters

    Parameters
    ----------
    point1 : LatLng

    point2 : latLng

    Returns
    -------
    distance : float
        in meters
    """
    return distance(point1.to_tuple(), point2.to_tuple()).meters


def read_gps(filename):
    """
    Read GPS file and return a DataFrame obj

    Parameters
    -----------
    filename : str
        The full path of the gps file

    Return
    ------
    df : DataFrame
    """
    df = pd.read_csv(filename, sep=',', error_bad_lines=False, skipfooter=1)

    # the gps file may NOT have header, due to the error in generating the first gps file
    # df = df[df['provider'] == 'gps']
    df = df[df.iloc[:, -1] == 'gps']
    # print(df.head(5))
    # print(df.tail(5))
    return df


def look_for_duration(df: pd.DataFrame, sd: SrcDst, max_possible_duration: int=None):
    """
    Look for all gps traces from given gps points that fall onto the specified
    pair of source and destination.

    Parameters
    ----------
    df : DataFrame
        The DataFrame obj that contains GPS data which should not contain 'network'
        provider at this point.

    sd : SrcDst
        The source and destination of the path to look for

    Return
    -------
    traces : array, element=(start_line, end_line)
        pairs of start_line and end_line from the gps file for each trip
    """

    traces = []

    # TODO: how to locate the source and destination in the GPS data
    # TODO: how to tell when the bus/car arrives and departs
    # straightforward way is to set a threshold, e.g. 10 meters
    gps_np = df.to_numpy()
    source = sd.source
    dest = sd.dest
    threshold = 30  # meters
    data_around_station = []
    """
    for target in [source, dest]:
        # for line in gps_np:
        #     point = LatLng(line[2], line[3])
        #     if distance_between_gps(target, point) <= threshold:
        #         data_around_station.append(line)
        # for index, line in df.iterrows():
        #     point = LatLng(line[2], line[3])
        #     if distance_between_gps(target, point) <= threshold:
        #         data_around_station.append(line)
        for line in df.itertuples(index=False):
            point = LatLng(line.lat, line.lon)
            if distance_between_gps(target, point) <= threshold:
                data_around_station.append(line)

    new_df = pd.DataFrame(data_around_station, columns=df.columns)
    new_df.to_csv('gps_around_station.csv', index=False)
    """

    # TODO: how to tell whether the gps trace is from source to destination directly
    # rather than passing some other places first
    # how to determine the direction is from source to dest, or from dest to source?
    # especially under conditions that there are more than one round trips?
    # calculate the distance between points (e.g. after the source) with the source and
    # destination. Generally, the former one should get larger and larger, and the later
    # should get smaller and smaller
    # Besides, we can also make use of the bearing data
    # do we need to add some time constraint
    trips = []
    start_end_line_numbers = []
    i = 0
    while i < len(gps_np):
        # find the point departs source
        line = gps_np[i]
        point = LatLng(line[2], line[3])
        while i + 1 < len(gps_np) and distance_between_gps(source, point) > threshold:
            i += 1
            line = gps_np[i]
            point = LatLng(line[2], line[3])

        if i >= len(gps_np):
            break

        while i + 1 < len(gps_np) and distance_between_gps(source, point) <= threshold:
            i += 1
            line = gps_np[i]
            point = LatLng(line[2], line[3])

        if i >= len(gps_np):
            break

        start_point = line
        start_line_number = i - 1

        # we need to make sure that the direction is from the source to destination
        # instead of moving away from the destination
        # it is also possible that point "shaking"
        # for the next 50 points, if the majority of points are getting closer to the
        # destination, then we treat the start point as a good one
        initial_dist_to_dest = distance_between_gps(point, dest)
        # the (absolute) number of points that are getting closer to dest
        closer = 0
        count = 0
        while i + 1 < len(gps_np) and count < 50:  # TODO: update the threshold
            i += 1
            line = gps_np[i]
            point = LatLng(line[2], line[3])
            new_dist = distance_between_gps(point, dest)
            if new_dist <= initial_dist_to_dest:
                closer += 1
            else:
                closer -= 1
            count += 1

        if closer <= 0:
            # print("wrong direction")
            i += 1
            continue

        # TODO: it is possible that the bus will pass the source station
        # again after it left, even if it was moving closer to the destination
        # in some way, e.g. from the service center to West

        # find the point arrives at destination
        # TODO: actually, we can just calculate the distance from destination
        # when the distance becomes the minimum, we know that the car has arrived
        # or stayed for a while
        if i >= len(gps_np):
            break

        line = gps_np[i]
        point = LatLng(line[2], line[3])
        repass = False  # indicator if the bus passed the source again
        while i + 1 < len(gps_np) and distance_between_gps(dest, point) > threshold:
            if distance_between_gps(source, point) < threshold:
                # TODO: this is not enough
                # because the threshold might be too small when
                # data missing happens near the stop
                # so we might need to resample/interpolate
                repass = True
                break
            i += 1
            line = gps_np[i]
            point = LatLng(line[2], line[3])
        if repass:
            continue

        if i < len(gps_np):
            # we find one good candidate for destination
            dest_point = line
            trips.append((start_point, dest_point))

            end_line_number = i - 1
            start_end_line_numbers.append((start_line_number, end_line_number))

    for i, (start, end) in enumerate(trips):
        print(datetime.fromtimestamp(
            start[1] / 1000.0), end=', duration (seconds): ')
        duration = (end[1] - start[1]) // 1000
        print(duration)

        if max_possible_duration and duration >= max_possible_duration:
            # TODO: save info to log file
            # otherwise, it is hard to find this message when there are lots of trips
            print("\tlonger than maximum possible duration %d. Need double check. Ignore it." %
                  max_possible_duration)
            print("\tstart and end line numbers: %d, %d" %
                  (start_end_line_numbers[i][0], start_end_line_numbers[i][1]))
            continue
        traces.append((start, end))

    return traces


def get_durations(root: str, src_dests: List[SrcDst], output_file: str):
    """
    Get trip durations.

    Get trip durations for all (source, destination) pairs for all trips
    under root, and save the result to <output_file>.

    Parameters
    ----------
    root : str
        The path that data is saved

    src_dests : list[SrcDst]
        A list of the SrcDst

    output_file : str
        The file to store the result
    """

    trip_start_end = defaultdict(lambda: defaultdict(list))
    for parent, _, _ in os.walk(root):
        gps_file = os.path.join(parent, "gps.txt")
        if os.path.isfile(gps_file):
            print("deal with: %s" % parent)
            if os.stat(gps_file).st_size == 0:
                print("\tEmpty file.")
                continue

            df = read_gps(gps_file)

            for src_dest in src_dests:
                print(src_dest)

                # TODO: put the max possible time in a dict?
                start_end_pairs = look_for_duration(df, src_dest, 1000)
                trip_start_end[parent][src_dest.name()] = start_end_pairs

    with open(output_file, "wb") as fp:
        pk.dump(dict(trip_start_end), fp)


def load_durations(filename) -> dict:
    """
    Load the durations

    Parameters
    ----------
    filename : str
        File that stores the durations
    """

    with open(filename, "rb") as fp:
        trip_start_end = pk.load(fp)

    '''
    for trip, station_ods in trip_start_end.items():
        print('------------------------')
        print(trip)
        for station, start_end_pairs in station_ods.items():
            print('\t', station)
            for start, end in start_end_pairs:
                print('\t\t', datetime.fromtimestamp(
                    start[1] / 1000.0), end[1] - start[1])
    '''

    return trip_start_end


def deal_with_durations(trip_start_end: dict, root: str):
    """
    Analyse the durations

    Parameters
    ----------
    trip_start_end : dict
        {trip: {source_dest: [(start_line_of_gps_file, end_line)]}},
        where trip is the full path of the trip (TODO: it is not portable),
        source_dest is a string that contains the name of the source station
        and the destination station, e.g. "service_maynard".

    root : str
        The path to save analysed results
    """

    trip_duration = defaultdict(list)

    time_range = get_time_range("00:00", "23:59", "30min")
    segmented_trip_duration = defaultdict(lambda: defaultdict(list))  # {source_dest: {time: [durations]}}
    od_day_time_durations = []

    for trip, station_ods in trip_start_end.items():
        for source_dest, start_end_pairs in station_ods.items():
            for start, end in start_end_pairs:
                trip_start_time = datetime.fromtimestamp(start[1] / 1000.0)
                weekday = trip_start_time.date().weekday()  # Monday is 0, and Sunday is 6
                duration = int((end[1] - start[1]) // 1000)
                trip_duration[source_dest].append([trip_start_time, duration])

                # find out the time slot that the trip falls into
                cur_time = trip_start_time.time()
                insert_slot = bisect.bisect_right(time_range, cur_time) - 1
                # print(cur_time, end=" -- ")
                # print(time_range[insert_slot])
                segmented_trip_duration[source_dest][time_range[insert_slot]].append(duration)
                od_day_time_durations.append([source_dest, weekday, time_range[insert_slot], duration])

    for source_dest, start_duration in trip_duration.items():
        df = pd.DataFrame(start_duration, columns=['start', 'duration'])
        df = df.sort_values(['start'])
        # print(df.head(30))
        # print()
        # print(df.tail(30))
        times = pd.to_datetime(df.start)
        d = df.groupby([times.dt.weekday]).mean()
        # d = df.groupby([times.dt.weekday, times.dt.hour]).mean()
        # d = df.groupby([df['start'], pd.TimeGrouper(freq='30Min')])
        print(d.head(200))
        # d.to_csv(source_dest + '_trip_grouped.csv', index=False)

    for source_dest, time_durations in segmented_trip_duration.items():
        print(source_dest)
        for time_slot, durations in time_durations.items():
            print(time_slot, end=": ")
            print(durations)

    df = pd.DataFrame(od_day_time_durations, columns=['source_dest', 'weekday', 'time', 'duration'])
    df.to_excel(os.path.join(root, 'od_day_time_durations.xlsx'), index=False)

    grouped_daily = df.groupby([df.source_dest, df.weekday]).mean()
    print(grouped_daily.head(14))
    grouped_daily.reset_index()[['source_dest', 'weekday', 'duration']].to_excel(os.path.join(root, "od_day_duration_mean.xlsx"), index=False)

    # group by source_dest and time, i.e. don't care weekday
    grouped_hourly = df.groupby([df.source_dest, df.time]).mean()
    # print(grouped_hourly.head(20))
    grouped_hourly = grouped_hourly.reset_index()[['source_dest', 'time', 'duration']]
    grouped_hourly.to_excel(os.path.join(root, "od_time_duration_mean.xlsx"), index=False)

    # group by most details
    grouped_detail = df.groupby([df.source_dest, df.weekday, df.time]).mean()
    # print(grouped_detail.head(30))
    # print(grouped_detail.tail(20))
    grouped_detail = grouped_detail.reset_index()
    grouped_detail.to_excel(os.path.join(root, "od_day_time_duration_mean.xlsx"), index=False)
    plot_od_day_time_duration(grouped_detail.values)


def plot_od_day_time_duration(od_day_time_duration: dict):
    """
    For each source_dest, plot the trip duration of each time slot for each day

    Parameters
    ----------
    od_day_time_duration : dict
        {od: {day: {time: duration}}}
    """

    dict_od_day_time_duration = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for line in od_day_time_duration:
        dict_od_day_time_duration[line[0]][line[1]][line[2]] = line[3]

    for source_dest, day_time_duration in dict_od_day_time_duration.items():
        plot_day_time_duration(day_time_duration, source_dest)


def plot_day_time_duration(day_time_duration: dict, title: str):
    """
    Plot trip duration of each time slot for each day

    Parameters
    ----------
    day_time_duration : dict
        {day: {time: duration}}
    title : str
        The title used in plot
    """

    for day, time_duration in day_time_duration.items():
        times = []
        durations = []
        for time in sorted(time_duration):
            times.append(time)
            durations.append(time_duration[time])
        plt.plot(times, durations, '*', label=day)
        plt.title(title)

    plt.legend()
    plt.show()


def get_time_range(start, end, freq):
    """
    Get time range

    Get time range using given time span and frequency

    Parameters
    ----------
    start : Datetime-style str
        The start time
    end : Datetime-style str
        The end time
    freq : str
        The duration of each time segment

    Returns
    -------
    array
        A list of time object
    """

    time_range = pd.date_range(start=start, end=end, freq=freq).time
    return time_range


if __name__ == "__main__":
    service_center = LatLng(42.99277, -78.792362)
    maynard = LatLng(42.96651, -78.810812)
    # gps_file = os.path.join(os.getcwd(), "data/stampede/stampede-4117/358239057888069-part01/VehSenseData2019_01_11_05_06_12/gps.txt")

    # root = "/mnt/Seagate/Playground"
    # root = "/Users/weida/Documents/QuicRoad/Playground/stampede/stampede-4117/358239057888069-part01/VehSenseData2019_01_11_05_06_12"
    # root = "/Users/weida/Documents/QuicRoad/Playground"
    root = "/Users/weida/Downloads/trip_data_check/data/stampede-4112/"
    root = "/media/weida/Seagate8T/VehSenseTraffic/stampede"

    src_dests = []
    src_dests.append(SrcDst(service_center, maynard, 'service', 'maynard'))
    src_dests.append(SrcDst(maynard, service_center, 'maynard', 'service'))

    output_file = os.path.join(root, "trip_start_end.pickle")
    get_durations(root, src_dests, output_file)

    trip_start_end = load_durations(output_file)
    deal_with_durations(trip_start_end, root)

    '''
    with open("trip_start_end.json", "w") as fp:
        json.dump(trip_start_end, fp)
    '''
