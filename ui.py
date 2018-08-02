import wx
import io
from io import BytesIO
import time
import threading
from wx.lib.pubsub import pub as Publisher
from job import Job
from config import *
from client import *

global g_job
g_job = None

devices = {
    # vertical phone screen
    # for typical phoen which 1080x1920
    'phone': [420, 720],
}

def core_job(fd,ch):
    ret = core_process(
        fd,
        view=(devices[ch][0], devices[ch][1],
                devices[ch][0], devices[ch][1], 0, 0),
        stream_cbs=streamer_data_callbacks)

@static_vars(idx=0)
def streamer_data_callbacks(data):
    """
    screen encoded data right here
    """
    wx.CallAfter(Publisher.sendMessage,'app.update', rawdata=data)
    with open(r'static_images_ex/'+str(streamer_data_callbacks.idx)+'.jpg', 'ab') as f:
        f.write(data)
    streamer_data_callbacks.idx += 1


class CastPanel(wx.Panel):
    """
    """

    def __init__(self, *args, **kw):
        super().__init__()


class CastFrame(wx.Frame):
    def __init__(self, parent, title=None, size=None,
                 device=None, mouse_cb=None, fd=None, style=None):



        self.fd = fd
        self.mouse_cb = update_mouse
        self.is_odd = 0
        self.main_job = None

        self.image = wx.EmptyImage(f'cast and control for android.png',wx.BITMAP_TYPE_ANY)
        # self.image = wx.EmptyImage(100,100,clear=True)
        self.bitmap = self.image.ConvertToBitmap()

        width = self.image.GetWidth()
        height = self.image.GetHeight()

        super().__init__(parent, title=title,size=(width,height), style=style)

        # self.imageCtrl = wx.StaticBitmap(self, -1, self.bitmap, (0,0), (800,450))
        # self.window = wx.Window()
        # bind
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        # 注意topic的格式`app.update`  app为必须接收对象的名字
        Publisher.subscribe(self.UpdateImage, 'app.update')

        self.data_source = 0

        # MenuBar
        MenuBar = wx.MenuBar()
        menu = wx.Menu()

        phone_item = menu.Append(wx.ID_ANY, "&Android phone", "Cast from phone")
        self.Bind(wx.EVT_MENU, self.OnChoosePhone, phone_item)

        MenuBar.Append(menu, "&Choose device")
        self.SetMenuBar(MenuBar)


        self.Show()
    
    def SetDevAndReconnection(self,dev,ids = 0):

        self.dev = dev

        self.o_width = self.width = devices[dev][0]
        self.o_height = self.height = devices[dev][1]

        # self.SetSize(self.width,self.height)
        # self.Update()
        # self.Refresh(eraseBackground=False)

        if self.fd != None:
            self.fd.close()
        
        time.sleep(0.1)

        self.fd = connect_remote(
            adb_restart=True,
            interval=50,
            device=dev,
            port=13579,
            ids = ids)

        if self.main_job != None:
            self.main_job.stop()

        time.sleep(0.1)

        self.main_job = Job(target=core_job,
                            name='core link job',
                            args=(self.fd, dev),
                            loop=False
                            )

        LOGGER.info('main_job.start')

        self.main_job.start()


    def OnChoosePhone(self, event):
        self.SetDevAndReconnection('phone')


        

    def OnResize(self, event):
        sz = self.GetSize()
        self.width = sz[0] if sz[0] >= self.o_width else self.width
        self.height = sz[1] if sz[1] >= self.o_height else self.height

        # self.image.Rescale(self.width, self.height)
        self.bitmap = self.image.ConvertToBitmap()
        # self.imageCtrl.SetBitmap(self.bitmap)
        self.Refresh(eraseBackground=False)

    def OnLeftDown(self, event):
        ctrl_pos = event.GetPosition()
        LOGGER.info('down!')
        if self.mouse_cb != None and self.fd != None:
            self.mouse_cb(self.fd, ctrl_pos.x, ctrl_pos.y, 'down')
        pass

    def OnRightUp(self, event):
        LOGGER.info('right up!')
        ctrl_pos = event.GetPosition()
        if self.mouse_cb != None and self.fd != None:
            self.mouse_cb(self.fd, ctrl_pos.x, ctrl_pos.y, 'back')
        pass

    def OnLeftUp(self, event):
        ctrl_pos = event.GetPosition()
        LOGGER.info('left up!')
        if self.mouse_cb != None and self.fd != None:
            self.mouse_cb(self.fd, ctrl_pos.x, ctrl_pos.y, 'up')
        pass

    def OnMotion(self, event):
        self.is_odd += 1
        ctrl_pos = event.GetPosition()
        if self.mouse_cb != None and self.fd != None and (self.is_odd % 2 == 0):
            self.mouse_cb(self.fd, ctrl_pos.x, ctrl_pos.y, 'move')

        # LOGGER.info("ctrl_pos: " + str(ctrl_pos.x) + ", " + str(ctrl_pos.y))
        # pos = self.imageCtrl.ScreenToClient(ctrl_pos)
        # LOGGER.info ("pos relative to screen top left = ", pos)
        # screen_pos = self.panel.GetScreenPosition()
        # relative_pos_x = pos[0] + screen_pos[0]
        # relative_pos_y = pos[1] + screen_pos[1]
        # LOGGER.info ("pos relative to image top left = ", relative_pos_x, relative_pos_y)
#         LOGGER.info(e.GetEventType())

    def UpdateImage(self, filename=None, rawdata=None, rotate=None):
        self.data_source = 1
        if filename != None:
            # LOGGER.info(filename)
            assert(rawdata == None)
            # from memory
            with open(filename, 'rb') as f:
                buf = f.read()
                bio = BytesIO(buf)
                self.image = wx.ImageFromStream(bio)
                self.o_width = self.width = self.image.GetWidth()
                self.o_height = self.height = self.image.GetHeight()
        if rawdata != None:
            assert(filename == None)
            bio = BytesIO(rawdata)
            image = wx.ImageFromStream(bio)
            if image.IsOk():
                self.image = image

            if self.dev == 'phone':
                pass

        if self.image.IsOk():

            self.width = self.image.GetWidth()
            self.height = self.image.GetHeight()
            self.SetSize(self.width,self.height)

            self.bitmap = self.image.ConvertToBitmap()
            # self.SetSize(self.width,self.height)
            self.Refresh(eraseBackground=False)
            # self.bitmap.Destroy()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.bitmap)
        # dc.Clear()
        # dc.DrawBitmap(self.bitmap ,0,0 )
        pass

    def OnClose(self, event):
        # click left top x ...
        if event.CanVeto():
            if wx.MessageBox("Really closing?",
                             "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
                event.Veto()
                return

            if g_job != None:
                g_job.stop()

            if self.fd:
                self.fd.close()
                self.fd = None

            self.Destroy()


class CastApp(wx.App):
    """
    mouse_cb: callback for mouse event.
    fd: fd for the connected socket
    """

    def __init__(self, redirect=False, device=None, filename=None, size=None, mouse_cb=None, fd=None):

        super(CastApp, self).__init__(redirect, filename)

        self.frame = CastFrame(None,
                               title='Cast and Control for Android',
                               size=size,
                               style=wx.DEFAULT_FRAME_STYLE,
                               device=device,
                               mouse_cb=mouse_cb,
                               fd=fd)

        self.SetTopWindow(self.frame)

        self.frame.Show(True)


global i
i = 0
def update_images_job():
    global i
    j = (i % 100)
    imageFile = r'static_images_ex/' + str(j) + r'.jpg'
    # very import step to avoid lots of weird crash
    try:
        wx.CallAfter(Publisher.sendMessage, 'app.update', filename=imageFile)
    except:
        LOGGER.info('some error occured')
    time.sleep(0.06)
    i += 1


if __name__ == '__main__':
    g_job = Job(target=update_images_job, name='update job')
    """
    # export GIO_EXTRA_MODULES=/usr/lib/x86_64-linux-gnu/gio/modules/
    """
    WIDTH = 800
    HEIGHT = 450
    app = CastApp(size=(WIDTH, HEIGHT), device='phone')
    g_job.start()
    app.MainLoop()
    # del app
