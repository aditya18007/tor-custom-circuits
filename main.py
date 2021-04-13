from platform import node
import stem.process

from stem.util import term
from stem.control import Controller

def print_bootstrap_lines(line):
    #From https://stem.torproject.org/tutorials.html
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.RED))


print(term.format("Starting Tor:\n", term.Attr.BOLD))

SOCKS_PORT = 9050
CONTROL_PORT = 9051
LARGE_VALUE = str(999999)
TRUE = str(1)
FALSE = str(0)

tor_process = stem.process.launch_tor_with_config(
    config = {
        'SocksPort': str(SOCKS_PORT)
        ,'ControlPort':str(CONTROL_PORT)
    },
    init_msg_handler = print_bootstrap_lines,
)

with Controller.from_port('127.0.0.1',CONTROL_PORT) as controller:
    print("Creating Circuit")
    controller.authenticate()
    #Source : https://iphelix.medium.com/hacking-the-tor-control-protocol-fb844db6a606
    controller.set_conf('__DisablePredictedCircuits',TRUE)
    controller.set_conf('MaxOnionsPending',FALSE)
    controller.set_conf('newcircuitperiod',LARGE_VALUE)
    controller.set_conf('maxcircuitdirtiness',LARGE_VALUE)
    active_circuits = []
    for i in controller.get_circuits():
        for controlLine in i:
            id = controlLine.split(' ')[1]
            active_circuits.append(id)

    for id in active_circuits:
        controller.close_circuit(id)

    circuitLength = int(input('Enter length of your circuit : '))
    nodes = list()
    
    for _ in range(circuitLength-1):
        gm = input('Enter fingerprint of a guard or middle relay : ')
        nodes.append(gm)
    exit = input('Enter fingerprint of exit node : ')
    nodes.append(exit)
    newID = controller.extend_circuit('0', nodes)
    print("New Circuit created with ID = "+str(newID))
#Press enter to exit tor process
quit = str(input('Press any key to kill tor process ...'))
tor_process.kill() 