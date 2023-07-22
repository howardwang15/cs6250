#!/usr/bin/env python3

import pybgpstream

"""
CS 6250 BGP Measurements Project

Notes:
- Edit this file according to the project description and the docstrings provided for each function
- Do not change the existing function names or arguments
- You may add additional functions but they must be contained entirely in this file
"""


# Task 1A: Unique Advertised Prefixes Over Time
def unique_prefixes_by_snapshot(cache_files):
    """
    Retrieve the number of unique IP prefixes from each of the input BGP data files.

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A list containing the number of unique IP prefixes for each input file.
        For example: [2, 5]
    """
    # the required return type is 'list' - you are welcome to define additional data structures, if needed
    unique_prefixes_by_snapshot = []

    for fpath in cache_files:
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", fpath)
        unique_prefixes = set()
        for elem in stream:
            unique_prefixes.add(elem.fields["prefix"])

        unique_prefixes_by_snapshot.append(len(unique_prefixes))
        # implement your solution here


    return unique_prefixes_by_snapshot


# Task 1B: Unique Autonomous Systems Over Time
def unique_ases_by_snapshot(cache_files):
    """
    Retrieve the number of unique ASes from each of the input BGP data files.

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A list containing the number of unique ASes for each input file.
        For example: [2, 5]
    """
    # the required return type is 'list' - you are welcome to define additional data structures, if needed
    unique_ases_by_snapshot = []

    for fpath in cache_files:
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", fpath)

        # implement your solution here
        unique_as = set()
        for elem in stream:
            unique_as.update(elem.fields['as-path'].split())

        unique_ases_by_snapshot.append(len(unique_as))

    return unique_ases_by_snapshot


# Task 1C: Top-10 Origin AS by Prefix Growth
def top_10_ases_by_prefix_growth(cache_files):
    """
    Compute the top 10 origin ASes ordered by percentage increase (smallest to largest) of advertised prefixes.

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A list of the top 10 origin ASes ordered by percentage increase (smallest to largest) of advertised prefixes
        AS numbers are represented as strings. In the event of a tie, the AS with the lower number should come first.

        For example: ["777", "1", "6"]
          corresponds to AS "777" as having the smallest percentage increase (of the top ten) and AS "6" having the
          highest percentage increase (of the top ten).
      """
    # the required return type is 'list' - you are welcome to define additional data structures, if needed
    top_10_ases_by_prefix_growth = []

    def sort_as(as_item):
        as_id, as_info = as_item
        # print(as_id, as_info)
        percent_increase = (as_info['num_prefixes_last_snapshot']-as_info['num_prefixes_first_snapshot'])/as_info['num_prefixes_first_snapshot']*100
        try:
            return percent_increase, int(as_id)
        except ValueError:
            return percent_increase, 0

    # as_analytics is the data structure used to keep track of:
    # - first snapshot AS appears in
    # - last snapshot AS appears in
    # - number of prefixes in first snapshot
    # - number of prefixes in last snapshot
    as_analytics = {}
    for ndx, fpath in enumerate(cache_files):
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", fpath)
        print(f"Starting snapshot {ndx}")

        # implement your solution here
        for elem in stream:
            as_path = elem.fields['as-path'].split()
            print(elem.fields)

            if not as_path:
                continue
            origin = as_path[-1]
            if origin not in as_analytics:
                # first time AS has been seen
                as_analytics[origin] = {
                    'first_snapshot': ndx,
                    'last_snapshot': ndx,
                    'num_prefixes_first_snapshot': 1,
                    'num_prefixes_last_snapshot': 1
                }
            else:
                # Still in the first snapshot, update number of prefixes in first snapshot
                if ndx == as_analytics[origin]['first_snapshot']:
                    as_analytics[origin]['num_prefixes_first_snapshot'] += 1
                # No longer in first snapshot, has just switched to a new snapshot
                elif as_analytics[origin]['last_snapshot'] != ndx:
                    as_analytics[origin]['last_snapshot'] = ndx
                    as_analytics[origin]['num_prefixes_last_snapshot'] = 1
                # In most recent snapshot
                else:
                    as_analytics[origin]['num_prefixes_last_snapshot'] += 1

    sorted_as = sorted(as_analytics.items(), key=sort_as)
    print(sorted_as[0])
    top_10 = sorted_as[-10:]
    print(top_10)
    return [_as[0] for _as in top_10]


# Task 2: Routing Table Growth: AS-Path Length Evolution Over Time
def shortest_path_by_origin_by_snapshot(cache_files):
    """
    Compute the shortest AS path length for every origin AS from input BGP data files.

    Retrieves the shortest AS path length for every origin AS for every input file.
    Your code should return a dictionary where every key is a string representing an AS name and every value is a list
    of the shortest path lengths for that AS.

    Note: If a given AS is not present in an input file, the corresponding entry for that AS and file should be zero (0)
    Every list value in the dictionary should have the same length.

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A dictionary where every key is a string representing an AS name and every value is a list, containing one entry
        per file, of the shortest path lengths for that AS
        AS numbers are represented as strings.

        For example: {"455": [4, 2, 3], "533": [4, 1, 2]}
        corresponds to the AS "455" with the shortest path lengths 4, 2 and 3 and the AS "533" with the shortest path
        lengths 4, 1 and 2.
    """
    # the required return type is 'dict' - you are welcome to define additional data structures, if needed
    shortest_path_by_origin_by_snapshot = {}

    for ndx, fpath in enumerate(cache_files):
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", fpath)
        print(f"Starting snapshot {ndx}")

        for elem in stream:
            as_path = elem.fields['as-path'].split()
            if not as_path:
                continue
            origin = as_path[-1]
            unique_as = set(as_path)
            path_length = len(unique_as)
            if path_length <= 1:
                continue
            if origin not in shortest_path_by_origin_by_snapshot:
                shortest_path_by_origin_by_snapshot[origin] = [0] * len(cache_files)
                shortest_path_by_origin_by_snapshot[origin][ndx] = path_length
            # just moved on to the next snapshot
            else:
                shortest_path_by_origin_by_snapshot[origin][ndx] = min(shortest_path_by_origin_by_snapshot[origin][ndx], path_length) \
                    if shortest_path_by_origin_by_snapshot[origin][ndx] != 0 else path_length
    return shortest_path_by_origin_by_snapshot


# Task 3: Announcement-Withdrawal Event Durations
def aw_event_durations(cache_files):
    def key(peer, prefix):
        return f'{peer}|{prefix}'
    """
    Identify Announcement and Withdrawal events and compute the duration of all explicit AW events in the input BGP data

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A dictionary where each key is a string representing the address of a peer (peerIP) and each value is a
        dictionary with keys that are strings representing a prefix and values that are the list of explicit AW event
        durations (in seconds) for that peerIP and prefix pair.

        For example: {"127.0.0.1": {"12.13.14.0/24": [4.0, 1.0, 3.0]}}
        corresponds to the peerIP "127.0.0.1", the prefix "12.13.14.0/24" and event durations of 4.0, 1.0 and 3.0.
    """
    # the required return type is 'dict' - you are welcome to define additional data structures, if needed
    aw_event_durations = {}
    announce_event_timestamp = {}

    for ndx, fpath in enumerate(cache_files):
        print(f"Starting snapshot {ndx}")
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "upd-file", fpath)
        for elem in stream:
            if elem.type not in ('A', 'W'):
                continue

            timestamp = elem.record.time
            peer_ip = elem.peer_address
            prefix = elem.fields['prefix']
            if elem.type == 'A':
                # add the announcement to announce_event_timestamp
                announce_event_timestamp[key(peer_ip, prefix)] = timestamp
            elif elem.type == 'W':
                announce_timestamp_key = key(peer_ip, prefix)
                if announce_timestamp_key in announce_event_timestamp:
                    # compute the duration between current withdrawl with latest announcement
                    duration = timestamp - announce_event_timestamp[announce_timestamp_key]
                    if duration == 0:
                        del announce_event_timestamp[announce_timestamp_key]
                        continue

                    # have a matching withdrawl & announcement, update aw_event_durations
                    if peer_ip not in aw_event_durations:
                        aw_event_durations[peer_ip] = {prefix: [duration]}
                    else:
                        # prefix is not associated with peer yet
                        if prefix not in aw_event_durations[peer_ip]:
                            aw_event_durations[peer_ip][prefix] = [duration]
                        else:
                            aw_event_durations[peer_ip][prefix].append(duration)

                    # remove the matched announcement
                    del announce_event_timestamp[announce_timestamp_key]

    return aw_event_durations


# Task 4: RTBH Event Durations
def rtbh_event_durations(cache_files):
    """
    Identify blackholing events and compute the duration of all RTBH events from the input BGP data

    Identify events where the prefixes are tagged with at least one Remote Triggered Blackholing (RTBH) community.

    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names

    Returns:
        A dictionary where each key is a string representing the address of a peer (peerIP) and each value is a
        dictionary with keys that are strings representing a prefix and values that are the list of explicit RTBH event
        durations (in seconds) for that peerIP and prefix pair.

        For example: {"127.0.0.1": {"12.13.14.0/24": [4.0, 1.0, 3.0]}}
        corresponds to the peerIP "127.0.0.1", the prefix "12.13.14.0/24" and event durations of 4.0, 1.0 and 3.0.
    """
    # the required return type is 'dict' - you are welcome to define additional data structures, if needed
    rtbh_event_durations = {}

    for fpath in cache_files:
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "upd-file", fpath)

        # implement your solution here


    return rtbh_event_durations


# The main function will not be run during grading.
# You may use it however you like during testing.
#
# NB: make sure that check_solution.py runs your
#     solution without errors prior to submission
if __name__ == '__main__':
    # do nothing
    pass
