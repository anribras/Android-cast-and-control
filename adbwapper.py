import os,re
from config import LOGGER
import time
class adbWapper():
    def __init__(self):
        pass
    @classmethod
    def get_prod_name(self):
        out=os.popen('adb shell' + r'"getprop ro.vendor.product.name"').read()
        return out
    @classmethod
    def adb_root(self):
        os.system('adb root')
    @classmethod
    def is_adb_online(self):
        out=os.popen('adb devices')
        lines = [ o for o in out.readlines()]
        # first online device  
        if 'device' in lines[1]:
            return True
        else:
            return False
    @classmethod
    def forward(self,*ports):
        [os.system('adb forward '+'tcp:'+str(p)+' tcp:'+str(p)) for p in ports]
    @classmethod
    def push(self,file):
        cmd = r'adb push '+file+r' /data/local/tmp/'
        return os.system(cmd)
    @classmethod
    def get_android_v(self):
        ver = os.popen('adb shell '+r'"getprop ro.build.version.release"').readline()
        return int(ver[0])
    @classmethod
    def execute(self,file,interval,port,device,device_id):
        path = r'/data/local/tmp/'+file
        cmd1 = 'adb shell ' + r'"' + 'chmod a+x '+path + r'"' 
        ret = os.system(cmd1)
        if ret != 0: return ret
        # adb shell /data/local/tmp/streamer-8.0 70 phone &
        cmd2 = 'adb shell -x '+ path + ' ' + str(interval) + ' ' + device + ' ' \
        + str(port) + ' ' + str(device_id) +  r' >/dev/null 2>&1 &'
        return os.system(cmd2)
    @classmethod
    def is_remote_alive(self,keywords):
        out = os.popen(r'adb shell ' + r'"ps |grep '+ keywords + r'"').read()
        if keywords in out: 
            return True
        else:
            return False
    @classmethod
    def kill_remote(self,keywords):
        cmd = r'adb shell ' + r'"ps |grep '+ keywords + r'"'
        out = os.popen(cmd)
        lines = [o.split(' ') for o in out.readlines()]
        if lines != []:
            for line in lines:
                #first not shell and '', should be the pid
                pid = [l for l in line if l != 'shell' and l != '' and l != 'root'][0]
                cmd = 'adb shell ' + r'" kill '+ pid + r'"'
                ret = os.system(cmd)
            return ret


