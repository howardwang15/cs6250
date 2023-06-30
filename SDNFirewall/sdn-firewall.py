#!/usr/bin/python
# CS 6250 Spring 2023- SDN Firewall Project with POX
# build hackers-44

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.revent import *
from pox.lib.addresses import IPAddr, EthAddr

# You may use this space before the firewall_policy_processing function to add any extra function that you 
# may need to complete your firewall implementation.  No additional functions "should" be required to complete
# this assignment.


def firewall_policy_processing(policies):
    '''
    This is where you are to implement your code that will build POX/Openflow Match and Action operations to
    create a dynamic firewall meeting the requirements specified in your configure.pol file.  Do NOT hardcode
    the IP/MAC Addresses/Protocols/Ports that are specified in the project description - this code should use
    the values provided in the configure.pol to implement the firewall.

    The policies passed to this function is a list of dictionary objects that contain the data imported from the
    configure.pol file.  The policy variable in the "for policy in policies" represents a single line from the
    configure.pol file.  Each of the configuration values are then accessed using the policy['field'] command. 
    The fields are:  'rulenum','action','mac-src','mac-dst','ip-src','ip-dst','ipprotocol','port-src','port-dst',
    'comment'.

    Your return from this function is a list of flow_mods that represent the different rules in your configure.pol file.

    Implementation Hints:
    The documentation for the POX controller is available at https://noxrepo.github.io/pox-doc/html .  This project
    is using the gar-experimental branch of POX in order to properly support Python 3.  To complete this project, you
    need to use the OpenFlow match and flow_modification routines (https://noxrepo.github.io/pox-doc/html/#openflow-messages
    for flow_mod and https://noxrepo.github.io/pox-doc/html/#match-structure for match.)  Also, do NOT wrap IP Addresses with
    IPAddr() unless you reformat the CIDR notation.  Look at the https://github.com/att/pox/blob/master/pox/lib/addresses.py
    for what POX is expecting as an IP Address.
    '''
    print(policies)
    rules = []

    for policy in policies:
        # Enter your code here to implement matching and block/allow rules.  See the links
        # in Implementation Hints on how to do this. 
        # HINT:  Think about how to use the priority in your flow modification.

        # create the OpenFlow objects
        rule = of.ofp_flow_mod() # Please note that you need to redefine this variable below to create a valid POX Flow Modification Object
        match = of.ofp_match()
        match.dl_type = 0x800
        
        # parse through the policies and construct the match object
        if policy['ipprotocol'] != '-':
            match.nw_proto = int(policy['ipprotocol'])

        if policy['mac-src'] != '-':
            match.dl_src = EthAddr(policy['mac-src'])
        
        if policy['mac-dst'] != '-':
            match.dl_dst = EthAddr(policy['mac-dst'])

        if policy['ip-src'] != '-':
            match.nw_src = policy['ip-src']
        
        if policy['ip-dst'] != '-':
            match.nw_dst = policy['ip-dst']

        if policy['port-src'] != '-':
            match.tp_src = int(policy['port-src'])

        if policy['port-dst'] != '-':
            match.tp_dst = int(policy['port-dst'])

        # Set higher priority for allowing traffic through the firewall
        if policy['action'] == 'Allow':
            rule.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
            rule.priority = 30000
        elif policy['action'] == 'Block':
            rule.priority = 1
        rule.match = match


        # End Code Here
        print('Added Rule ',policy['rulenum'],': ',policy['comment'])
        # print(rule)   #Uncomment this to debug your "rule"
        rules.append(rule)
    
    return rules
