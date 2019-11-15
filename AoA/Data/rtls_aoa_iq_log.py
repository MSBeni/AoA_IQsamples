#
#  Copyright (c) 2019, Texas Instruments Incorporated
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

############################
#  NOTE ABOUT THIS EXAMPLE
############################
#
# This example uses configures the device to output the raw AoA samples
# as received over the air.
#
# This takes a while to print over the serial port, so it is recommended that
# you modify the rtls_master project and increase the connection interval
# giving more time for UART between AoA packets.
#
# rtls_master.c :: RTLSMaster_init()
# {
#    ...
#    GAP_SetParamValue(TGAP_CONN_EST_INT_MIN, 400); //change to 500ms connection interval
#    GAP_SetParamValue(TGAP_CONN_EST_INT_MAX, 400); //change to 500ms connection interval
#    ...


import logging
import sys
import csv
import queue
from collections import namedtuple

# from rtls import RTLSManager, RTLSNode
from rtls.rtls.rtlsmanager import RTLSManager
from rtls.rtls.rtlsnode import RTLSNode

# Uncomment the below to get raw serial transaction logs

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#                     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


if __name__ == '__main__':
    # Initialize, but don't start RTLS Nodes to give to the RTLSManager
    # my_nodes = [RTLSNode('COM51', 115200), RTLSNode('COM48', 115200), RTLSNode('COM53', 115200),
    #             RTLSNode('COM49', 115200)]
    my_nodes = [RTLSNode('/dev/tty.usbmodemL5000YTV1', 115200), RTLSNode('/dev/tty.usbmodemL5000YUE1', 115200)]


    # Initialize references to the connected devices
    master_node = None
    passive_nodes = []

    # Prepare csv file to save data
    filename = 'rtls_raw_iq_samples_AoA_test.csv'
    outfile = open(filename, 'w', newline='')

    csv_fieldnames = ['pkt', 'sample_idx', 'rssi', 'ant_array', 'channel', 'i', 'q']
    SampleRow = namedtuple('CsvRow', csv_fieldnames)

    csv_writer = csv.DictWriter(outfile, fieldnames=csv_fieldnames)
    csv_writer.writeheader()
    
    # Temporary storage of iq samples
    dump_rows = []

    # How many AoA sample buffers should be stored.
    # None means infinite. Press Ctrl+C to terminate in this case.
    pkt_limit = 1 # None  # 5

    # Preferred RTLS Slave BLE address, or None for any
    slave_addr = None # '54:6C:0E:A0:4B:B2'

    # Running packet counter
    pkt_cnt = 0

    # Storage for latest discovered slave device
    address = None
    addressType = None

    # Initialize manager reference, because on Exception we need to stop the manager to stop all the threads.
    manager = None
    try:
        # Start an RTLSManager instance without WebSocket server enabled
        manager = RTLSManager(my_nodes, websocket_port=None)
        # Create a subscriber object for RTLSManager messages
        subscriber = manager.create_subscriber()
        # Start RTLS Node threads, Serial threads, and manager thread
        manager.start()

        # Wait until nodes have responded to automatic identify command and get reference
        # to single master RTLSNode and list of passive RTLSNode instances
        master_node, passive_nodes, failed = manager.wait_identified()
        if len(failed):
            print(f"ERROR: {len(failed)} nodes could not be identified. Are they programmed?")

        # Exit if no master node exists
        if not master_node:
            raise RuntimeError("No RTLS Master node connected")

        #
        # At this point the connected devices are initialized and ready
        #

        # Display list of connected devices
        print(f"{master_node.identifier} {', '.join([str(c) for c, e in master_node.capabilities.items() if e])}")
        for pn in passive_nodes:
            print(f"{pn.identifier} {', '.join([str(c) for c, e in pn.capabilities.items() if e])}")

        print("\nSending example command RTLS_CMD_IDENTIFY; responses below\n")

        # Send an example command to each of them, from commands listed at the bottom of rtls/ss_rtls.py
        for n in passive_nodes + [master_node]:
            n.rtls.identify()

        while True:
            # Get messages from manager
            try:
                identifier, msg_pri, msg = subscriber.pend(block=True, timeout=0.05).as_tuple()
                print(msg.as_json())

                # After example identify is received, we start scanning
                if msg.command == 'RTLS_CMD_IDENTIFY':
                    master_node.rtls.scan()

                # Once we start scanning, we will save the address of the
                # last scan response
                if msg.command == 'RTLS_CMD_SCAN' and msg.type == 'AsyncReq':
                    address = msg.payload.addr
                    addressType = msg.payload.addrType

                # Once the scan has stopped and we have a valid address, then connect
                if msg.command == 'RTLS_CMD_SCAN_STOP':
                    if address is not None and addressType is not None and (slave_addr is None or slave_addr == address):
                        master_node.rtls.connect(addressType, address)
                    else:
                        # If we didn't find the device, keep scanning.
                        master_node.rtls.scan()

                # Forwarding the connection parameters to the passives
                if msg.command == 'RTLS_CMD_CONN_PARAMS' and msg.type == 'AsyncReq' and msg.payload.accessAddress is not 0:
                    if identifier == master_node.identifier:
                        for node in passive_nodes:
                            node.rtls.set_ble_conn_info(msg.payload.accessAddress, msg.payload.connInterval,
                                                        msg.payload.hopValue, msg.payload.mSCA, msg.payload.currChan,
                                                        msg.payload.chanMap)

                # Once we are connected and slave setup is completed, we can enable AoA
                if msg.command == 'RTLS_CMD_CONNECT' and msg.type == 'AsyncReq':
                    if msg.payload.status == 'RTLS_SUCCESS':
                        if identifier == master_node.identifier:
                            master_node.rtls.aoa_set_params('AOA_MASTER', 'AOA_MODE_RAW', 4, 4, 20)
                            master_node.rtls.aoa_start(1)
                        else:
                            # Iterate over all passive nodes, send ToF params
                            for node in passive_nodes:
                                node.rtls.aoa_set_params('AOA_PASSIVE', 'AOA_MODE_RAW', 4, 4, 20)
                                node.rtls.aoa_start(1)
                    else:
                        # The connection failed, keep scanning.
                        master_node.rtls.scan()

                # Saving I/Q samples into csv file
                if msg.command == 'RTLS_CMD_AOA_RESULT_RAW':
                    payload = msg.payload
                    # Extract first sample index in this payload
                    offset = payload.offset

                    # If we have data, and offset is 0, we are done with one dump
                    if offset == 0 and len(dump_rows):
                        pkt_cnt += 1

                        # Make sure the samples are in order
                        dump_rows = sorted(dump_rows, key=lambda s: s.sample_idx)

                        # Write to file
                        for sample_row in dump_rows:
                            csv_writer.writerow(sample_row._asdict())

                        # Reset payload storage
                        dump_rows = []

                        # Stop script now if there was a limit configured
                        if pkt_limit is not None and pkt_cnt > pkt_limit:
                            break

                    # Save samples for writing when dump is complete
                    for sub_idx, sample in enumerate(payload.samples):
                        sample = SampleRow(pkt=pkt_cnt, sample_idx=offset + sub_idx, rssi=payload.rssi, ant_array=payload.antenna, channel=payload.channel, i=sample.i, q=sample.q)
                        dump_rows.append(sample)

            except queue.Empty:
                pass

    finally:
        outfile.flush()
        outfile.close()

        if manager:
            manager.stop()
