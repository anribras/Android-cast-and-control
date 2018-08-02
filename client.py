import os
import threading
import time
import socket

import struct
from enum import Enum
import ctypes as ct
from ctypes import *

from job import Job
from adbwapper import adbWapper
from config import *


def struct2stream(s):
    length = ct.sizeof(s)
    p = ct.cast(ct.pointer(s), ct.POINTER(ct.c_char * length))
    return p.contents.raw


def stream2struct(string, stype):
    if not issubclass(stype, ct.Structure):
        raise ValueError('Not a ctypes.Structure')
    length = ct.sizeof(stype)
    stream = (ct.c_char * length)()
    stream.raw = string
    p = ct.cast(stream, ct.POINTER(stype))
    return p.contents


class CommandHeader(Structure):
    _pack_ = 4
    _fields_ = [
        # Size of this descriptor (in bytes)
        ('MsgCommand', c_int),
        ('MsgParam', c_int),
        ('unkown', c_short),
        ('unkown1', c_short),
        ('startx', c_short),
        ('starty', c_short),
        ('width', c_short),
        ('height', c_short),
        ('len', c_int)
    ]


class ClientCommands(Enum):
    StartH264Trans = 0x200,
    StopH264Trans = 0x201,
    UPDATE_MOUSE = 0x102,


class ClientParas(Enum):
    Send2PhoneEvent_SetProperty_Display = 0x300,
    Send2PhoneEvent_mouseMove = 0x4,
    Send2PhoneEvent_mouseDown = 0x5,
    Send2PhoneEvent_mouseUp = 0x6,
    Send2PhoneEvent_mouseBack = 11,


class ServerCommands(Enum):
    UpdateImage = 0x104,
    LinkUsable = 0x1FF,


class StructConverter():
    def __init__(self):
        pass

    @classmethod
    def encoding(self, raw, struct):
        """
            'encode' means raw binary stream to ctype structure. 
        """
        if raw != None and struct != None:
            return stream2struct(raw, struct)
        else:
            return None

    @classmethod
    def decoding(self, data):
        """
            'decode means ctpye structure to raw binary stream
        """
        if data != None:
            return struct2stream(data)
        else:
            return None


def streamer_threading(*args):
    fd = args[0]
    cb = args[1]
    raw = fd.recv(sizeof(CommandHeader))
    header = StructConverter.encoding(raw, CommandHeader)
    RECEIVE_MAX_PACKET_SIZE = (1024 * 8 * 2)
    # a image or streamer head
    if header.MsgCommand == ServerCommands.UpdateImage.value[0]:
        pkg = b''

        left = total_len = header.len
#             LOGGER.info('total_len ',total_len, 'left ',left)
        while(left > 0):
            if left < RECEIVE_MAX_PACKET_SIZE:
                raw = fd.recv(left)
#                     assert(len(raw)==left)
                processed = len(raw)
            else:
                raw = fd.recv(RECEIVE_MAX_PACKET_SIZE)
#                     assert(len(raw)==RECEIVE_MAX_PACKET_SIZE)
                processed = len(raw)

            pkg += raw
            left -= processed
        # data callback
        cb(pkg)


def connect_remote(adb_restart=False,interval=50,device='phone',ids = 0,port=10000):
    """
    adb_restart : means restart adb deaemon streamer everytime
    interval:  staitic jpeg frame per interval ms from Android source
    device: device type,now defined 'phone only' :
    """

    if device=='phone': port=10000

    adbWapper.adb_root()

    if adbWapper.is_adb_online() != True:
        LOGGER.info('adb device not ready')
        return None
    v = adbWapper.get_android_v()
    exe = r'streamer-'+str(v)+'.0'
    LOGGER.info('exec name: %s', exe)
    if adbWapper.is_remote_alive(exe) == False or adb_restart == True:

        adbWapper.kill_remote(exe)

        adbWapper.push(exe)

        adbWapper.forward(port)

        # for windows compatibility. adb exec will be suspended. So we use a job here
        def exec():
            adbWapper.execute(exe,interval,port,device,ids)

        Job(target=exec,name='exec job',loop=False).start()
        
    time.sleep(1)  

    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # fd.connect(('10.1.11.200', ports))
        # fd.connect(('10.1.11.241', ports))
        fd.connect(('127.0.0.1', port))
    except socket.error as e:
        LOGGER.info('connect error')
        return None
    finally:
        LOGGER.info(fd)
        return fd


def core_process(fd, view=None, stream_cbs=None):
    if fd == None or view == None or stream_cbs == None:
        LOGGER.info('core_process para error')
        return
    """
    Should be a block loop at final
    """
    raw = None
    LOGGER.info('recving...')
    raw = fd.recv(sizeof(CommandHeader))
    LOGGER.info('recving done')

    header = None
    header = StructConverter.encoding(raw, CommandHeader)
    LOGGER.info('1st msgcmd(%d) phone w(%d) h(%d)'%(header.MsgCommand, header.width, header.height))
    # server tell client 10000 ok
    if header.MsgCommand == ServerCommands.LinkUsable.value[0]:

        # client tell server  its screen paras
        resp = CommandHeader()
        resp.MsgCommand = ClientCommands.UPDATE_MOUSE.value[0]
        resp.MsgParam = ClientParas.Send2PhoneEvent_SetProperty_Display.value[0]
        # view=(1280,720,1280,720,0,0),
        # full weight and height
        resp.unkown = view[0]
        resp.unkown1 = view[1]
        # view
        resp.width = view[2]
        resp.height = view[3]
        # base
        resp.startx = view[4]
        resp.starty = view[5]

        ret = fd.send(StructConverter.decoding(data=resp))
        LOGGER.info('sending paras.')


        resp = CommandHeader()
        # client tell server  to start h264 streamer
        resp.MsgCommand = ClientCommands.StartH264Trans.value[0]

        ret = fd.send(StructConverter.decoding(data=resp))
        LOGGER.info('sending start-streamer.')
        # client prepare for streaming show

        # client prepare a job thread to recv lots of streaming data from 10000
        streamerJob = Job(target=streamer_threading,
                        args=(fd, stream_cbs), loop=True)
        streamerJob.start()
        LOGGER.info('start client streamerJob..')
        streamerJob.join()
        LOGGER.info('client streamerJob done')
    else:
        LOGGER.info('Try again')
        return -1

    return 0


def pause_remote_streamer(fd):
    resp = CommandHeader()
    # client tell server  to start h264 streamer
    resp.MsgCommand = ClientCommands.StopH264Trans.value[0]
    LOGGER.info(StructConverter.decoding(data=resp))
    ret = fd.send( StructConverter.decoding(data=resp))
    return

def resume_remote_streamer(fd):
    resp = CommandHeader()
    # client tell server  to start h264 streamer
    resp.MsgCommand = ClientCommands.StartH264Trans.value[0]
    LOGGER.info(StructConverter.decoding(data=resp))
    ret = fd.send( StructConverter.decoding(data=resp))
    return

@static_vars(down_flag=0)
def update_mouse(fd, x, y, event=None):
    if event == None:
        LOGGER.info('update_mouse event None')
        return

    resp = CommandHeader()

    resp.MsgCommand = ClientCommands.UPDATE_MOUSE.value[0]
    if event == 'up':
        update_mouse.down_flag = 0
        resp.MsgParam = ClientParas.Send2PhoneEvent_mouseUp.value[0]
    if event == 'down':
        update_mouse.down_flag = 1
        resp.MsgParam = ClientParas.Send2PhoneEvent_mouseDown.value[0]
    if event == 'move' and update_mouse.down_flag :
        resp.MsgParam = ClientParas.Send2PhoneEvent_mouseDown.value[0]
    if event == 'back':
        resp.MsgParam = ClientParas.Send2PhoneEvent_mouseBack.value[0]

    # full weight and height
    resp.unkown = x
    resp.unkown1 = y

    ret = fd.send(StructConverter.decoding(data=resp))


def streamer_data_callbacks(data):
    """
    screen encoded data right here
    """
    with open('test.h264', 'ab+') as f:
        f.write(data)


if __name__ == '__main__':

    # os.system('rm test.h264')

    fd = connect_remote(adb_restart=False)
    
    ret = core_process(
        fd,
        view=(1280, 720, 1280, 720, 0, 0),
        stream_cbs=streamer_data_callbacks
    )

    LOGGER.info('core_process failed')
