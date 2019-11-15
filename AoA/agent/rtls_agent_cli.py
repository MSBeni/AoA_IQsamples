#
#  Copyright (c) 2018-2019, Texas Instruments Incorporated
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  *  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  *  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  *  Neither the name of Texas Instruments Incorporated nor the names of
#     its contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import argparse

import logging
import queue
import sys
import os
import time
from time import strftime, gmtime

from rtls import RTLSManager
from rtls import RTLSNode, Subscriber

import serial.tools.list_ports as list_ports

import curses
from curses import wrapper

#
# Command line parsing
#
parser = argparse.ArgumentParser(description="Start an RTLS/uNPI web-socket server")
parser.add_argument('-p', '--port', dest="port", type=int, default=8766, metavar="PORT",
                    help="Port for websocket ws://localhost:PORT")
parser.add_argument('-d', '--device', dest="devices", type=str, nargs=2, action="append", metavar=('PORT', 'NAME'),
                    help="Add device, eg. -d COM48 TOFMaster")
parser.add_argument('--debuglog', action='store_true', help="Saves logging info to 'socketserver_log.txt'")
parser.add_argument('-l', '--list-ports', action='store_true', help="Print list of serial ports")
parser.add_argument('--baudrate', dest='baudrate', type=int, default=115200, choices=[115200, 230400, 460800, 921600], help="Serial port baudrate. Must match setting on devices.")
parser.add_argument('-a', '--auto-connect', dest='autoconnect', action='store_true', help='Automatically query all serial ports and connect')

#
#  Pycharm workaround
#
_argv = sys.argv
if '--file' in _argv:
    _argv = _argv[_argv.index('--file')+1:]

# if len(_argv[1:]) == 0:
#     parser.print_help()
#     parser.exit()


args = parser.parse_args(_argv[1:])

if args.list_ports:
    for x in list_ports.comports():
        print(f"  {x.device} - {x.description}")
    parser.exit()

devnull = open(os.devnull, 'w')
if args.debuglog:
    logging.basicConfig(
        #stream=sys.stdout,
        filename="socketserver_log.txt",
        filemode="w",
        level=logging.DEBUG,
        format='[%(asctime)s] %(filename)-18sln %(lineno)3d %(threadName)-10s %(levelname)8s - %(message)s')


def connect_ports(ports=None, baudrate=115200, on_connect=None, on_error=None):
    ports = ports if ports is not None else list_ports.comports()
    nodes = {p.device: None for p in ports}

    for port in ports:
        node = nodes[port.device] = RTLSNode(port.device, baudrate, port.device)
        node.start()

    target_time = time.time() + 0.5
    waiters = [n for n in nodes.values()]
    while target_time > time.time() and len(waiters):
        for n in waiters:
            if n.identifyEvent.isSet():
                waiters.remove(n)
                logging.info(f"Node {n} identified")
                if on_connect:
                    port = next((x for x in ports if x.device == n.port))
                    on_connect(port, n)

    for port in ports:
        node = nodes[port.device]
        if node.exception:
            logging.info(f"Node {node} had exception")
            if on_error:
                on_error(port, node.exception, 'Error')
        elif node.identifier is None:
            node.stop()
            logging.info(f"Node {node} did not respond")
            if on_error:
                on_error(port, "No response", 'NoRsp')

    return [n for n in nodes.values() if n.identifyEvent.isSet()]


if args.devices:
    my_nodes = [RTLSNode(port, args.baudrate, name) for port, name in args.devices]
elif args.autoconnect:
    my_nodes = connect_ports(None, args.baudrate, None, None)
else:
    my_nodes = []


def update_node_status(scr, nodes):
    numId = len([n for n in nodes if n.identifier])
    scr.move(2, 0); scr.clrtoeol(); scr.addstr(2, 0, f"Connected to {numId} of {len(nodes)} nodes")
    for i, node in enumerate(nodes):
        caps = ', '.join([str(c) for c, e in node.capabilities.items() if e])
        scr.addstr(5 + i * 3, 0, f"* {node.name} @ {node.port}")
        scr.addstr(6 + i * 3, 0, f"    > {node.identifier}")
        scr.addstr(7 + i * 3, 0, f"    > {caps}")
    scr.vline(0, 48, '|', curses.LINES)
    scr.refresh()


def ws_status_update(scr, action):
    def update_ws_status(ws):
        scr.addstr(4, 0, f"Websocket {action}")
        scr.refresh()
    return update_ws_status


def ws_message(win):
    def inner(nodemsg):
        identifier = nodemsg.identifier
        msg = nodemsg.message.item
        subsys = msg.subsystem.name if hasattr(msg.subsystem, 'name') else msg.subsystem
        cmd = msg.command.name if hasattr(msg.command, 'name') else msg.command
        log_str = f"[{strftime('%H:%M:%S', gmtime())}] >> WS=>{identifier} - {subsys}/{cmd} - {len(msg.data)} bytes \r\n"
        win.addstr(log_str)
        win.refresh()
    return inner


def connect_com_ports(scr):
    global my_nodes
    global args
    scr.clear()
    scr.addstr(0, 0, "Connect to a COM port by pressing the corresponding key")
    scr.addstr(1, 0, "ENTER to continue, Ctrl+C to exit")

    ports = list_ports.comports()[:min(curses.LINES-7,26)]
    connected = []
    baudrate = args.baudrate

    scr.addstr(5, 0, f"       a)  Auto-detect RTLS nodes")
    for i, x in enumerate(ports):
        scr.addstr(6+i, 0, f"       {chr(i+ord('b'))})  {x.device} - {x.description}")

    def on_error(port, msg, symbol):
        logging.info("Error callback")
        idx = ports.index(port)
        scr.addstr(3, 0, f"> Error: {msg}")
        scr.addstr(6 + idx, 0, symbol)

    def on_connect(port, rtlsnode):
        logging.info("Connected callback")
        idx = ports.index(port)
        connected.append(idx)
        my_nodes.append(rtlsnode)
        scr.addstr(6 + idx, 0, "OK")

    def connect(idx):
        if idx not in connected:
            connect_ports([ports[idx]], baudrate, on_connect=on_connect, on_error=on_error)

        elif idx in connected:
            node = next((x for x in my_nodes if x.port == ports[idx].device))
            node.stop()
            node.join()
            my_nodes.remove(node)
            connected.remove(idx)
            scr.addstr(6+idx, 0, '       ')

    while True:
        try:
            key = scr.getkey()
            if len(key) == 1:
                if ord(key) in [3, 26]: raise KeyboardInterrupt
                if ord(key) == 10: break;
                if ord(key) == ord('A') or ord(key) == ord('a'):
                    not_connected_already = [port for port in ports if not len([n for n in my_nodes if n.port == port.device])]
                    connect_ports(not_connected_already, baudrate, on_connect=on_connect, on_error=on_error)
                if ord('b') <= ord(key) <= ord('z'):
                    connect(ord(key) - ord('b'))
                if ord('B') <= ord(key) <= ord('Z'):
                    connect(ord(key) - ord('B'))

        except KeyboardInterrupt as e:
            for node in my_nodes:
                node.stop()
                node.join()
            sys.exit(1)

        except Exception as e:
            for node in my_nodes:
                node.stop()
                node.join()
            raise e


def main(scr):
    curses.curs_set(0)
    if len(my_nodes) == 0:
        connect_com_ports(scr)

    # log = curses.newwin(curses.LINES//2, curses.COLS, curses.LINES//2, 0)  # Horizontal
    log = curses.newwin(curses.LINES, curses.COLS - 50, 0, 50)  # Vertical
    log.scrollok(True)
    log.idlok(1)

    scr.clear()
    scr.nodelay(True)
    scr.addstr(0, 0, f"WebSocket Server, ws://localhost:{args.port}")
    scr.addstr(2, 0, f"Connecting to {len(my_nodes)} nodes and identifying..")
    scr.vline(0, 48, '|', curses.LINES)
    scr.refresh()

    log.addstr("Waiting for data...\r\n")
    log.refresh()

    manager = None
    managerSub = Subscriber(queue=queue.PriorityQueue(), interest=None, transient=False, eventloop=None)
    try:
        manager = RTLSManager(my_nodes, args.port)
        manager.auto_params = True

        manager.add_subscriber(managerSub)
        manager.on_ws_connect = ws_status_update(scr, 'connected')
        manager.on_ws_disconnect = ws_status_update(scr, 'disconnected')
        manager.on_ws_message = ws_message(log)
        manager.start()
        for node in manager.nodes:
            logging.info(node.identifier)

        update_node_status(scr, my_nodes)

        while True:
            try:
                #
                # Check for interrupt keypress
                #
                try:
                    key = scr.getkey()
                    if len(key) == 1 and ord(key) in [3, 26]: raise KeyboardInterrupt
                    if key == 'KEY_RESIZE':
                        newy, newx = scr.getmaxyx()
                        curses.resize_term(newy, newx)
                        scr.refresh()
                        log.mvwin(0, newx // 2)
                        log.resize(newy, newx // 2)
                        log.refresh()

                    # scr.addstr(0, 20, key); scr.refresh()

                except KeyboardInterrupt as e:
                    # Disable any stderr outputs, because websocket tries to access logger after destruct
                    sys.stderr = devnull
                    break

                except Exception:
                    pass



                #
                # Get messages from manager
                #
                node_msg = managerSub.pend(block=True, timeout=0.05)
                from_node = node_msg.identifier
                pri = node_msg.message.priority
                msg = node_msg.message.item
                logging.info(node_msg.as_json())

                #
                # Print to console
                #
                log_str = f"[{strftime('%H:%M:%S', gmtime())}] >> {from_node} - {msg.subsystem}/{msg.command} - {len(msg.data)} bytes \r\n"
                log.addstr(log_str); log.refresh()

            except queue.Empty:
                pass

    finally:
        if manager:
            manager.stop()
            manager.join()


if __name__ == "__main__":
    wrapper(main)

