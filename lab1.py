from __future__ import annotations
import plab1_sim as sim
from typing import Any
import yaml
import networkx as nx # type: ignore
import sys

#Citation: Adapted from the Psuedo-code provided at the end of the Note of Lecture 3: Handling Cycles
#Title: Lecture 3: Handling Cycles psuedo code
#Author: Aurojit Panda
#Date of Retrieval: 09/23/2019
#URL: https://cs.nyu.edu/courses/fall19/CSCI-UA.0480-008/lecture/lec3/

class Data(object):
    def __init__(self, root_id,id, distance):
        self.root_id = root_id #root
        self.id = id #interface id
        self.distance = distance #distance from root of the packet
    
    def __repr__(self):
        # TODO: While not required, we strongly suggest updating
        # repr to return readable text, since this is useful when
        # debugging.
        return "%s" % {"root_id": self.root_id} #show the root

class ControlLogic(sim.ControlPlane):

    def __init__(self):
        self.root = None
        self.dfr = 0
        self.cpr = -1
    
    
    def broadcast_packet(self, sw: sim.SwitchRep, pkt: Data) -> None:
        # This is a convenience function for sending packets out all interfaces. Note that even though
        # we iterate over all interfaces here, `send_control` will silently drop packets sent to an
        # interface that is down.
        for i in range(sw.iface_count()):
            sw.send_control(i, pkt)

    def initialize(self, sw: sim.SwitchRep) -> None:
        self.root = sw.id #initialize the program by choosing the id of the switch as the root
        d = Data(self.root, sw.id,0)#the first packet
        self.broadcast_packet(sw, d)
# TODO: Send any initial messages here. Please note that unless you send control messages here,
# process_control_packet will never be invoked.

    def process_control_packet(
                           self, sw: sim.SwitchRep, iface_id: int, data: Any
                           ) -> None:
        if data.root_id < self.root:#find new root
            self.root = data.root_id#change to the new root
            self.dfr = data.distance+1#distance increases
            self.cpr = iface_id
            for i in range(sw.iface_count()):
                sw.iface_up(i)#enable all interfaces
                if i!=iface_id:
                    sw.send_control(i, Data(self.root,i,self.dfr))#message sent out
        elif data.root_id == self.root:# if root confirmed
            if self.dfr > data.distance+1:
                self.dfr = data.distance+1#accept shorter path
                old = self.cpr
                self.cpr = iface_id
                if old != -1:#eliminate a loop
                    sw.iface_down(old)
                for i in range(sw.iface_count()):
                    if i!=iface_id:
                        sw.send_control(i, Data(self.root,i,self.dfr))
            else:
                sw.iface_down(iface_id)#eliminate the loop


        # TODO: You can decide what to do with received packets here.
        # Your options are
        # - Do nothing
        # - Set a port up by calling sw.iface_up(id)
        # - Set a port down by calling sw.iface_down(id)
        # - Send packets (sw.send_control as shown above in broadcast_packet)
        # Do some computation.



def create_and_run(topology):
    # This creates a new simulation, using your control logic when running it.
    setup = sim.SimulationSetup.from_yml_file(topology, True, ControlLogic)
    # This has a host send out a single packet, useful in seeing if things are working.
    setup.send_host_ping("h1")
    # This starts running the simulation.
    setup.run()
    return setup


def main():
    setup = create_and_run(sys.argv[1])
    # Once the simulation is done running this checks whether the resulting forwarding
    # graph is loop free.
    assert setup.check_algorithm()


if __name__ == "__main__":
    main()
