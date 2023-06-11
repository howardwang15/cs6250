# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *

NEGATIVE_INFINITY = -99

class Message:
    def __init__(self, source, path_dest, distance):
        """
        Constructs a Message object

        source: the sender of the Message
        path_dest: the other node in the path
        distance: cost of the path between source and path_dest
        """
        self.source = source
        self.path_dest = path_dest
        self.distance = distance

    def __repr__(self) -> str:
        return f'[MESSAGE] FROM: {self.source}, TO: {self.path_dest}, COST: {self.distance}'

class DistanceVector(Node):
    def _print(self, msg):
        print(f'[{self.name}] - {msg}')
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        self.distance_vectors = {name: 0}
        self.incoming_links_cost = {link.name: int(link.weight) for link in incoming_links}
        self.outgoing_links_cost = {link.name: int(link.weight) for link in outgoing_links}
        # self._print(incoming_links)
        
        # TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data

    def queue_messages_for_upstream(self, msg):
        messages = []
        for upstream_neighbor in self.incoming_links:
            messages.append([msg, upstream_neighbor.name])
        return messages

    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """
        for upstream_neighbor in self.incoming_links:
            self.send_msg(Message(
                source=self.name,
                path_dest=self.name,
                distance=0
            ), upstream_neighbor.name)

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py

    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages
        new_messages = []
        for msg in self.messages:
            # self._print(f'RECEIVED {msg}')
            # check if msg's dest is in distance vectors map...
            # if not, then add to map. Cost will be distance + link cost
            if not msg.path_dest in self.distance_vectors:
                initial_cost = msg.distance + self.outgoing_links_cost[msg.source]
                self.distance_vectors[msg.path_dest] = initial_cost
                new_messages.extend(self.queue_messages_for_upstream(
                    Message(source=self.name, path_dest=msg.path_dest, distance=initial_cost)
                ))
            else:
                if msg.path_dest != self.name:
                    potential_cost = msg.distance + self.outgoing_links_cost[msg.source]
                    # if the distance using new path is less...
                    if msg.distance == NEGATIVE_INFINITY:
                        # self._print(self.distance_vectors)
                        if self.distance_vectors[msg.path_dest] != NEGATIVE_INFINITY:
                            self.distance_vectors[msg.path_dest] = NEGATIVE_INFINITY
                            new_messages.extend(self.queue_messages_for_upstream(
                                Message(source=self.name, path_dest=msg.path_dest, distance=NEGATIVE_INFINITY)
                            ))
                    elif potential_cost < self.distance_vectors[msg.path_dest] and self.distance_vectors[msg.path_dest] != NEGATIVE_INFINITY:
                        self.distance_vectors[msg.path_dest] = potential_cost
                        new_messages.extend(self.queue_messages_for_upstream(
                            Message(source=self.name, path_dest=msg.path_dest, distance=potential_cost)
                        ))

        # Empty queue
        self.messages = []
        # self._print(self.distance_vectors)
        # TODO 2. Send neighbors updated distances
        for msg, neighbor in new_messages:
            self.send_msg(msg, neighbor)

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:A0,B1,C2
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """

        distances = ','.join([f'{k}{v}' for k, v in self.distance_vectors.items()])
        add_entry(self.name, distances)
