import os
from job import Job
from client import core_process,connect_remote,update_mouse,static_vars
from ui import CastApp
import time
import wx
from wx.lib.pubsub import pub as Publisher
from adbwapper import adbWapper
from config import *


@static_vars(idx=0)
def streamer_data_callbacks(data):
    """
    screen encoded data right here
    """
    wx.CallAfter(Publisher.sendMessage,'app.update', rawdata=data)
    # with open(r'pyf/'+str(streamer_data_callbacks.idx)+'.jpg', 'ab') as f:
    #     f.write(data)
    # streamer_data_callbacks.idx += 1




if __name__ =='__main__':

    print(wx.Platform)

    if wx.Platform == '__WXGTK__':
        os.system('export GIO_EXTRA_MODULES=/usr/lib/x86_64-linux-gnu/gio/modules/')


    # ch = 'phone'

    # def core_job(fd):
    #     ret = core_process(
    #     fd,
    #     view=(devices[ch][0], devices[ch][1], devices[ch][0], devices[ch][1], 0, 0),
    #     stream_cbs=streamer_data_callbacks)

    # fd = connect_remote(
    #     adb_restart=True,
    #     interval=50,
    #     device=ch,
    #     port=13579)

    # Job(target=core_job,
    #     name='core link job',
    #     args=(fd,),
    #     loop=False
    #     ).start()

    CastApp().MainLoop()
    
