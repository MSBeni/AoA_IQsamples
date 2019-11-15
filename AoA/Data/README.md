## Running Out of Box Demo
* To run out of box demo with prebuild binary, you need to program all the boards
with RTLS Master, RTLS Slave and RTLS Passive projects first.
* For uNPI serial <=> websocket server, find precompiled binary `rtls_agent_cli(.exe)` under `\tools\blestack\rtls_agent`
* Double click on the binary to run the demo, and then you will see the following
![](resource/rtls_agent_cli_binary.png)
* You can press A to have the agent connect to all serial ports and check for a response, or choose
  the ports for passive and master devices manually. For this case, the COM ports of interest
  are 48 and 51, found by auto-detection. COM53 is open in another process.

To get the help function under Git Bash, you can type
`winpty ./rtls_agent_cli.exe -h`
```text
$ ./rtls_agent_cli.exe -h
usage: rtls_agent_cli.exe [-h] [-p PORT] [-d PORT NAME] [--debuglog] [-l]
                          [--baudrate {115200,230400,460800,921600}] [-a]

Start an RTLS/uNPI web-socket server

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port for websocket ws://localhost:PORT
  -d PORT NAME, --device PORT NAME
                        Add device, eg. -d COM48 TOFMaster
  --debuglog            Saves logging info to 'socketserver_log.txt'
  -l, --list-ports      Print list of serial ports
  --baudrate {115200,230400,460800,921600}
                        Serial port baudrate. Must match setting on devices.
  -a, --auto-connect    Automatically query all serial ports and connect
```

**NOTE**: In some cases the default websocket port can be in use already. To change websocket port, you can do `winpty ./rtls_agent_cli.exe -p 8777`, for example.

* After selecting the correct COM ports, you can see the
![](resource/rtls_agent_cli_running.png)

* Then go to [dev.ti.com/gallery](https://dev.ti.com/gallery/) and look for RTLS Monitor project.
After opening the GUI, make sure the circled port number is set to the same
as the port value in the terminal. Then hit CONNECT.
![](resource/rtls_monitor_startup.png)

* For ToF demo, due to the calibration process, it will take a while
till the GUI starts showing data. After hitting CONNECT, place RTLS Slave 1m apart from RTLS Master/Passive.
Then when there is data showing in the GUI, you can start moving slave around to see the response from the GUI.
![](resource/rtls_monitor_running.png)

* The steps for running AoA demo is the same. The GUI composer will automatically show angles once the RTLS AoA software is programmed
on to the devices.


## Setting up Python Development Environment
* Install Python 3.7 or higher
* Make a virtual-env or install the requirements globally
  * `py -3.7 -m venv .venv` creates a new virtual env using python 3
  * Activate virtualenv to make `python` point to the virtual environment
    * `source .venv/Scripts/activate` or
    * `.venv\Scripts\activate.bat`
  * `pip [--proxy <www.proxy.com>] install -r requirements.txt`
    * Note: On mac/linux it may be necessary to manually call `pip install <line>`
            for each line in requirements.txt

## Using

You can run `python agent/rtls_agent_cli.py -d COMxx MyTofMaster -d COMxx
MyTofPassive -d COMxx AnAoAPassive` to start up a websocket server running on
`ws://localhost:8766` by default.

If you are using `Git Bash` you may need to use `winpty` as the launcher due to
some inconsistencies in how console output is handled.

```
$ winpty python agent/rtls_agent_cli.py -d COM48 ConnMon -d COM51 TofMaster


WebSocket Server

Connecting to 2 nodes..


Node ConnMon @ COM48 - 54:6C:0E:A0:49:07
Node TofMaster @ COM51 - 54:6C:0E:A0:50:6A

```

### Simple Websocket connection test

You can use the Chrome debug console (press F12 to make it visible)
to quickly prototype or just test the websocket agent's connection to your
serial devices.

```js
> ws = new WebSocket('ws://localhost:8766'); ws.onmessage = m => console.log(JSON.stringify(JSON.parse(m.data), null, 2)); ws.onclose = () => console.log('closed');
// Send a websocket "meta" command to the RTLSManager: LIST_DEVICES
> ws.send('{"control": {"req": "LIST_DEVICES"}}')
{
  "control": {
    "req": "LIST_DEVICES",
    "devices": [
      {
        "name": "COM53",
        "port": "COM53",
        "identifier": "98:07:2D:AA:50:57",
        "caps": [
          "TOF_MASTER",
          "RTLS_MASTER"
        ]
      },
      {
        "name": "COM48",
        "port": "COM48",
        "identifier": "54:6C:0E:A0:49:07",
        "caps": [
          "CM",
          "TOF_PASSIVE",
          "RTLS_PASSIVE"
        ]
      }
    ]
  }
}

// Tell the RTLS_MASTER capable device to perform a scan for RTLS Slave devices
> ws.send(JSON.stringify({identifier: "98:07:2D:AA:50:57", message: {type: "SyncReq", subsystem: "RTLS", command: "RTLS_CMD_SCAN", payload: {}}}))

// Scan command status
{
  "identifier": "98:07:2D:AA:50:57",
  "message": {
    "originator": "Nwp",
    "type": "SyncRsp",
    "subsystem": "RTLS",
    "command": "RTLS_CMD_SCAN",
    "payload": {
      "status": "RTLS_SUCCESS"
    }
  }
}

// One of the results
{
  "identifier": "98:07:2D:AA:50:57",
  "message": {
    "originator": "Nwp",
    "type": "AsyncReq",
    "subsystem": "RTLS",
    "command": "RTLS_CMD_SCAN",
    "payload": {
      "eventType": 0,
      "addrType": 0,
      "addr": "54:6C:0E:A0:50:6A",
      "rssi": -34,
      "dataLen": 3,
      "data": "02:01:06"
    }
  }
}

// Scan completed message
{
  "identifier": "98:07:2D:AA:50:57",
  "message": {
    "originator": "Nwp",
    "type": "AsyncReq",
    "subsystem": "RTLS",
    "command": "RTLS_CMD_SCAN_STOP",
    "payload": {
      "status": "RTLS_SUCCESS"
    }
  }
}
```

### WebSocket GUI

Please find the `RTLS Monitor` GUI application on the GUI Composer Gallery
browser at dev.ti.com/gallery. Find the source code for the GUI (at the time of
the SDK release) under `gui/RTLS_Monitor/app` in this folder, or import `RTLS
Monitor` to your own GUI Composer workspace using the gallery browser.

The javascript application under `gui/RTLS_Monitor/app/app.js` shows how you can
send and receive uNPI commands to the serial devices connected to your computer
and attached to the `rtls_agent_cli` application.

### Python scripting of RTLS

All of the uNPI commands are available through WebSocket and directly from
Python. For developing and prototyping RTLS algorithms, TI recommends using
the Python classes `RTLSManager` and `RTLSNode` directly.

In the `examples/` folder there exists two examples of using Python classes directly

 * `rtls_example.py` : Setup RTLS connection and perform either AoA or ToF based on reported capabilities
 * `rtls_aoa_iq_log.py`: Read AoA data in RAW mode (IQ samples) and save to CSV file

These examples and the Python framework are discussed in depth in the
[RTLS SimpleLink Academy Labs](http://dev.ti.com/tirex/#/?link=Software%2FSimpleLink%20CC2640R2%20SDK%2FSimpleLink%20Academy)

## uNPI Commands

Please see `rtls/ss_rtls.py` for a list and description of the available uNPI
commands and responses for the RTLS Subsystem.
