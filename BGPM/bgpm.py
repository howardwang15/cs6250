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

    def sort_origins(origin_growths):
        origin, growth = origin_growths
        try:
            return growth, int(origin)
        except ValueError:
            return growth, 0

    # store origin => first snapshot origin appears in
    # store origin => last snapshot origin appears in
    # store origin => all unique prefixes of first snapshot origin appears in
    # store origin => all unique prefixes of last snapshot origin appears in

    origin_first_appearance = {}
    origin_last_appearance = {}
    origin_first_appearance_prefixes = {}
    origin_last_appearance_prefixes = {}

    for ndx, fpath in enumerate(cache_files):
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", fpath)

        # implement your solution here
        for elem in stream:
            as_path = elem.fields['as-path'].split()
            prefix = elem.fields['prefix']

            if not as_path:
                continue
            origin = as_path[-1]

            if origin not in origin_first_appearance:

                origin_first_appearance[origin] = ndx
                origin_first_appearance_prefixes[origin] = set([prefix])
            # operating on the first snapshot origin appears in
            elif origin_first_appearance[origin] == ndx:
                origin_first_appearance_prefixes[origin].add(prefix)

            # origin appears in a later snapshot
            elif origin not in origin_last_appearance or ndx != origin_last_appearance[origin]:
                origin_last_appearance[origin] = ndx
                origin_last_appearance_prefixes[origin] = set([prefix])
            else:
                origin_last_appearance_prefixes[origin].add(prefix)

    origin_differences_growth = {}
    for origin, last_prefixes in origin_last_appearance_prefixes.items():
        num_last_prefixes = len(last_prefixes)
        num_first_prefixes = len(origin_first_appearance_prefixes[origin])
        growth = (num_last_prefixes - num_first_prefixes)/num_first_prefixes * 100
        origin_differences_growth[origin] = growth

    sorted_growths = sorted(origin_differences_growth.items(), key=sort_origins)
    top_10 = sorted_growths[-10:]
    return [origin[0] for origin in top_10]


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

        for elem in stream:
            as_path = elem.fields['as-path'].split()
            if not as_path:
                continue
            origin = as_path[-1]
            unique_as = set(as_path)
            path_length = len(unique_as)
            if path_length > 1:
                # The origin has not been seen yet, build up the data structure with 0 prefixes initially for all data files
                if origin not in shortest_path_by_origin_by_snapshot:
                    shortest_path_by_origin_by_snapshot[origin] = [0] * len(cache_files)
                    shortest_path_by_origin_by_snapshot[origin][ndx] = path_length
                else:
                    # Possibly update the shortest path
                    shortest_path_by_origin_by_snapshot[origin][ndx] = min(shortest_path_by_origin_by_snapshot[origin][ndx], path_length) \
                        if shortest_path_by_origin_by_snapshot[origin][ndx] != 0 else path_length
    return shortest_path_by_origin_by_snapshot


# Task 3: Announcement-Withdrawal Event Durations
def aw_event_durations(cache_files):
    # Simple function to combine the peer address and prefix advertised into a single key, useful for quick lookups for the pairing
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

    # aw_event_durations => return value
    # announce_event_timestamp => stores the latest keyed peer address/prefix advertised pairing to the timestamp it was recorded 
    aw_event_durations = {}
    announce_event_timestamp = {}

    for ndx, fpath in enumerate(cache_files):
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "upd-file", fpath)
        for elem in stream:
            if elem.type not in ('A', 'W'):
                continue

            # Pull the relevant pieces from the element in the stream
            timestamp = elem.record.time
            peer_ip = elem.peer_address
            prefix = elem.fields['prefix']
            announce_timestamp_key = key(peer_ip, prefix)

            # Process the announcement event
            if elem.type == 'A':
                # add the announcement to announce_event_timestamp
                announce_event_timestamp[announce_timestamp_key] = timestamp

            # process the withdrawal event
            elif elem.type == 'W':
                if announce_timestamp_key in announce_event_timestamp:
                    # compute the duration between current withdrawl with latest announcement for the pair
                    duration = timestamp - announce_event_timestamp[announce_timestamp_key]
                    if duration != 0:
                        # have a matching withdrawl & announcement, update aw_event_durations
                        if peer_ip not in aw_event_durations:
                            aw_event_durations[peer_ip] = {prefix: [duration]}
                        else:
                            # prefix is not associated with peer yet
                            if prefix not in aw_event_durations[peer_ip]:
                                aw_event_durations[peer_ip][prefix] = [duration]
                            else:
                                # prefix and pair already exist, add another duration to the list
                                aw_event_durations[peer_ip][prefix].append(duration)

                    # remove the matched announcement
                    del announce_event_timestamp[announce_timestamp_key]

    return aw_event_durations


# Task 4: RTBH Event Durations
def rtbh_event_durations(cache_files):
    # Simple function to combine the peer address and prefix advertised into a single key, useful for quick lookups for the pairing
    def key(peer, prefix):
        return f'{peer}|{prefix}'

    # Determines if the element in the stream is a blackholing event
    def is_blackholing_event(elem):
        for community in elem.fields['communities']:
            if community.split(':')[-1] == BLACKHOLE_COMMUNITY:
                return True
        return False
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
    rtbh_announce_event_timestamp = {}
    
    # According to https://datatracker.ietf.org/doc/html/rfc7999#section-5
    BLACKHOLE_COMMUNITY = '666'

    for ndx, fpath in enumerate(cache_files):
        stream = pybgpstream.BGPStream(data_interface="singlefile")
        stream.set_data_interface_option("singlefile", "upd-file", fpath)
        for elem in stream:
            # We only care about Announcement and Withdrawal events
            if elem.type not in ('A', 'W'):
                continue

            # Pull the relevant fields
            timestamp = elem.record.time
            peer_ip = elem.peer_address
            prefix = elem.fields['prefix']
            rtbh_announce_event_key = key(peer_ip, prefix)

            # Process an Announcement event
            if elem.type == 'A':
                # Add the timestamp if the Announcement is a blackholing event
                if is_blackholing_event(elem):
                    rtbh_announce_event_timestamp[rtbh_announce_event_key] = timestamp
                # If not, then (possibly) remove the old RTBH event
                else:
                    rtbh_announce_event_timestamp.pop(rtbh_announce_event_key, None)
            elif elem.type == 'W':
                # The Withdrawal event has a matching RTBH Announcement event
                if rtbh_announce_event_key in rtbh_announce_event_timestamp:
                    duration = timestamp - rtbh_announce_event_timestamp[rtbh_announce_event_key]
                    if duration != 0:
                        if peer_ip not in rtbh_event_durations:
                            rtbh_event_durations[peer_ip] = {prefix: [duration]}
                        else:
                            # prefix is not associated with peer yet
                            if prefix not in rtbh_event_durations[peer_ip]:
                                rtbh_event_durations[peer_ip][prefix] = [duration]
                            else:
                                rtbh_event_durations[peer_ip][prefix].append(duration)

                    del rtbh_announce_event_timestamp[rtbh_announce_event_key]

    return rtbh_event_durations


# The main function will not be run during grading.
# You may use it however you like during testing.
#
# NB: make sure that check_solution.py runs your
#     solution without errors prior to submission
if __name__ == '__main__':
    # do nothing
    pass
