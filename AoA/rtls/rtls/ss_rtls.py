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

import enum

from construct import Struct, Enum, Int8ul, Int8sl, Int32ul, Int16ul, Int16sl, Byte, this, Float64l, FlagsEnum, \
    GreedyRange

from unpi.unpi.npirequest_mixins import AsyncReq, FromNwp, FromAp, SyncRsp, SyncReq
from unpi.unpi.serialnode import builder_class
from unpi.unpi.unpiparser import NpiSubSystem, NpiRequest, NpiSubSystems, NiceBytes, ReverseBytes


class Commands(enum.IntEnum):
    RTLS_CMD_IDENTIFY = 0x00
    RTLS_CMD_CONN_PARAMS = 0x02
    RTLS_CMD_CONNECT = 0x03
    RTLS_CMD_SCAN = 0x04
    RTLS_CMD_SCAN_STOP = 0x05
    RTLS_CMD_TOF_RESULT_DIST = 0x06
    RTLS_CMD_TOF_RESULT_STAT = 0x07
    RTLS_CMD_TOF_RESULT_RAW = 0x08
    RTLS_CMD_TOF_SET_SEC_SEED = 0x09
    RTLS_CMD_TOF_GET_SEC_SEED = 0x10
    RTLS_CMD_TOF_SET_PARAMS = 0x11
    RTLS_CMD_TOF_ENABLE = 0x12
    RTLS_CMD_AOA_SET_PARAMS = 0x13
    RTLS_CMD_AOA_ENABLE = 0x14
    RTLS_CMD_RESET_DEVICE = 0x20
    RTLS_CMD_ERROR = 0x21
    RTLS_CMD_TERMINATE_LINK = 0x22
    RTLS_CMD_AOA_RESULT_ANGLE = 0x23
    RTLS_CMD_AOA_RESULT_RAW = 0x24
    RTLS_CMD_AOA_RESULT_PAIR_ANGLES = 0x25
    RTLS_CMD_TOF_CALIBRATE = 0x26


class Capabilities(enum.IntFlag):
    CM = 1
    AOA_TX = 2
    AOA_RX = 4
    TOF_SLAVE = 8
    TOF_PASSIVE = 16
    TOF_MASTER = 32
    RTLS_SLAVE = 64
    RTLS_MASTER = 128
    RTLS_PASSIVE = 256


RtlsStatus = Enum(Int8ul,
                  RTLS_SUCCESS=0,
                  RTLS_FAIL=1,
                  RTLS_LINK_LOST=2,
                  RTLS_LINK_ESTAB_FAIL=3,
                  RTLS_LINK_TERMINATED=4,
                  RTLS_OUT_OF_MEMORY=5,
                  RTLS_ILLEGAL_CMD=6,
                  )


class TofRole(enum.IntEnum):
    TOF_SLAVE = 0
    TOF_MASTER = 1
    TOF_PASSIVE = 2


class AoaRole(enum.IntEnum):
    AOA_SLAVE = 0
    AOA_MASTER = 1
    AOA_PASSIVE = 2


class TofResultMode(enum.IntEnum):
    TOF_MODE_DIST = 0
    TOF_MODE_STAT = 1
    TOF_MODE_RAW = 2


class TofRunMode(enum.IntEnum):
    TOF_MODE_CONT = 0
    TOF_MODE_ONE_SHOT = 1
    TOF_MODE_AUTO = 2


class TofSecMode(enum.IntEnum):
    TOF_MODE_SINGLE_BUF = 0
    TOF_MODE_DBL_BUF = 1


class AoaResultMode(enum.IntEnum):
    AOA_MODE_ANGLE = 0
    AOA_MODE_PAIR_ANGLES = 1
    AOA_MODE_RAW = 2


# noinspection PyPep8Naming
class RTLS(NpiSubSystem):
    type = NpiSubSystems.RTLS.value

    def __init__(self, sender):
        self.sender = sender

    #
    # Responses
    #
    class IdentifyRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_IDENTIFY
        struct = Struct(
            "capabilities" / FlagsEnum(Int16ul, Capabilities),
            "identifier" / NiceBytes(ReverseBytes(Byte[6])),
        )

    class ConnRsp(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_CONNECT
        struct = Struct(
            "status" / RtlsStatus,
        )

    class ErrorRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_ERROR
        struct = Struct(
            "status" / RtlsStatus,
        )

    class DeviceInfoRsp(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_SCAN
        struct = Struct(
            "eventType" / Int8ul,
            "addrType" / Enum(Int8ul),
            "addr" / NiceBytes(ReverseBytes(Byte[6])),
            "rssi" / Int8sl,
            "dataLen" / Int8ul,
            "data" / NiceBytes(Byte[this.dataLen])
        )

    class ScanRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_SCAN
        struct = Struct(
            "status" / RtlsStatus,
        )

    class ResetDeviceRes(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_RESET_DEVICE
        struct = Struct(
            "status" / RtlsStatus,
        )

    class ScanStopRsp(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_SCAN_STOP
        struct = Struct(
            "status" / RtlsStatus,
        )

    class ConnectRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_CONNECT
        struct = Struct(
            "status" / RtlsStatus,
        )

    class SetConnParamsRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_CONN_PARAMS
        struct = Struct(
            "status" / RtlsStatus,
        )

    class ConnParamsRsp(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_CONN_PARAMS
        struct = Struct(
            "accessAddress" / Int32ul,
            "connInterval" / Int16ul,
            "hopValue" / Int8ul,
            "mSCA" / Int16ul,
            "currChan" / Int8ul,
            "chanMap" / Byte[5],
            "crcInit" / Int32ul,
        )

    class AoaStartRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_AOA_ENABLE
        struct = Struct(
            "status" / RtlsStatus,
        )

    class AoaSetParamsRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_AOA_SET_PARAMS
        struct = Struct(
            "status" / RtlsStatus,
        )

    class AoaResultAngle(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_AOA_RESULT_ANGLE
        struct = Struct(
            "angle" / Int16sl,
            "rssi" / Int8sl,
            "antenna" / Int8ul,
            "channel" / Int8ul,
        )

    class AoaResultPairAngle(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_AOA_RESULT_PAIR_ANGLES
        struct = Struct(
            "rssi" / Int8sl,
            "antenna" / Int8ul,
            "channel" / Int8ul,
            "pairAngle" / Int16sl[3],
        )

    class AoaResultRaw(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_AOA_RESULT_RAW
        struct = Struct(
            "rssi" / Int8sl,
            "antenna" / Int8ul,
            "channel" / Int8ul,
            "offset" / Int16ul,
            "samplesLength" / Int16ul,
            "samples" / GreedyRange(Struct(
                "q" / Int16sl,
                "i" / Int16sl,
            )),
        )

    class TofStartRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_TOF_ENABLE
        struct = Struct(
            "status" / RtlsStatus,
        )

    class TofResultStatistics(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_TOF_RESULT_STAT
        struct = Struct(
            "stats" / GreedyRange(Struct(
                "freq" / Int16ul,
                "tick" / Float64l,
                "tickVariance" / Float64l,
                "rssi" / Int8sl,
                "numOk" / Int32ul,
            )),
        )

    class TofResultDistance(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_TOF_RESULT_DIST
        struct = Struct(
            "distance" / Float64l,
            "rssi" / Int8sl,
        )

    class TofResultRaw(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_TOF_RESULT_RAW
        struct = Struct(
            "tick" / Int32ul,
            "freqIdx" / Int8ul,
            "rssi" / Int8sl,
        )

    class TofSetParamsRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_TOF_SET_PARAMS
        struct = Struct(
            'status' / RtlsStatus,
        )

    class TofSetSecSeedRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_TOF_SET_SEC_SEED
        struct = Struct(
            "status" / RtlsStatus,
        )

    class TofGetSecSeedRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_TOF_GET_SEC_SEED
        struct = Struct(
            "seed" / NiceBytes(Int8ul[32]),
        )

    class TofCalibEnabledRsp(NpiRequest, SyncRsp, FromNwp):
        command = Commands.RTLS_CMD_TOF_CALIBRATE
        struct = Struct(
            "status" / RtlsStatus,
        )

    class TofCalibCompleteRsp(NpiRequest, AsyncReq, FromNwp):
        command = Commands.RTLS_CMD_TOF_CALIBRATE
        struct = Struct(
            "calibVals" / GreedyRange(Struct(
                "freq" / Int16ul,
                "tick" / Float64l,
                "tickVariance" / Float64l,
                "rssi" / Int8sl,
                "numOk" / Int32ul,
            )),
        )

    #
    # Requests
    #

    class IdentifyReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_IDENTIFY
        struct = None

    class ScanReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_SCAN
        struct = None

    class ResetDeviceReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_RESET_DEVICE
        struct = None

    class ConnectReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_CONNECT
        struct = Struct(
            'addrType' / Enum(Int8ul),
            'peerAddr' / NiceBytes(ReverseBytes(Byte[6]))
        )

    class TerminateLinkReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TERMINATE_LINK
        struct = None

    class AoaStartReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_AOA_ENABLE
        struct = Struct(
            "enable" / Int8ul,
        )

    class AoaSetParamsReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_AOA_SET_PARAMS
        struct = Struct(
            "aoaRole" / Enum(Int8ul, AoaRole),
            "aoaResultMode" / Enum(Int8ul, AoaResultMode),
            "cteScanOvs" / Int8ul,
            "cteOffset" / Int8ul,
            "cteTime" / Int16ul,
        )

    class TofCalibReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TOF_CALIBRATE
        struct = Struct(
            "enable" / Int8ul,
            "samplesPerFreq" / Int16ul,
            "calibDistance" / Int8ul,
        )

    class TofStartReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TOF_ENABLE
        struct = Struct(
            "enable" / Int8ul,
        )

    class TofSetParamsReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TOF_SET_PARAMS
        struct = Struct(
            'tofRole' / Enum(Int8ul, TofRole),
            'numSamples' / Int16ul,
            'numFreq' / Int8ul,
            'autoTofRssiThresh' / Int8sl,
            'resultMode' / Enum(Int8ul, TofResultMode),
            'runMode' / Enum(Int8ul, TofRunMode),
            'frequencies' / Int16ul[this.numFreq],
        )

    class SetConnInfoReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_CONN_PARAMS
        struct = Struct(
            "accessAddress" / Int32ul,
            "connInterval" / Int16ul,
            "hopValue" / Int8ul,
            "mSCA" / Int16ul,
            "currChan" / Int8ul,
            "chanMap" / Byte[5],
            "crcInit" / Int32ul,
        )

    class TofSetSecSeedReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TOF_SET_SEC_SEED
        struct = Struct(
            "seed" / NiceBytes(Int8ul[32]),
        )

    class TofGetSecSeedReq(NpiRequest, SyncReq, FromAp):
        command = Commands.RTLS_CMD_TOF_GET_SEC_SEED
        struct = None

    @builder_class(IdentifyReq)
    def identify(self): pass

    @builder_class(ScanReq)
    def scan(self): pass

    @builder_class(ConnectReq)
    def connect(self, addrType, peerAddr): pass

    @builder_class(TerminateLinkReq)
    def terminate_link(self): pass

    @builder_class(TofStartReq)
    def tof_start(self, enable): pass

    @builder_class(TofSetParamsReq)
    def tof_set_params(self, tofRole, numSamples, numFreq, autoTofRssiThresh, resultMode, runMode, frequencies): pass

    @builder_class(AoaStartReq)
    def aoa_start(self, enable): pass

    @builder_class(AoaSetParamsReq)
    def aoa_set_params(self, aoaRole, aoaResultMode, cteScanOvs, cteOffset, cteTime): pass

    @builder_class(SetConnInfoReq)
    def set_ble_conn_info(self, accessAddress, connInterval, hopValue, mSCA, currChan, chanMap, crcInit): pass

    @builder_class(TofSetSecSeedReq)
    def tof_set_sec_seed(self, seed): pass

    @builder_class(TofGetSecSeedReq)
    def tof_get_sec_seed(self): pass

    @builder_class(TofCalibReq)
    def tof_calib(self, enable, samplesPerFreq, calibDistance): pass

    @builder_class(ResetDeviceReq)
    def reset_device(self): pass

