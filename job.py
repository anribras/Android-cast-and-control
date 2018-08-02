"""
    job.py
"""
import threading
import time
from config import *

class Job(threading.Thread):
    """
    wapper for Thread support pause resume and stop
    target: run entity
    loop: True  run loop else execute only 1 time.
    args and kwargs: parameters for the target
    """

    def __init__(self, loop=True,group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super(Job, self).__init__(group=group,name=name, daemon=daemon)
        self.__flag = threading.Event()     
        self.__flag.set()       
        self.__running = threading.Event() 
        self.__running.set()      
        self.target= target
        self.args =  args
        self.loop = loop
        self.kwargs =  kwargs
        LOGGER.info (type(self.args))
        
    def run(self):
        while self.__running.isSet():
#             LOGGER.info('run pause')
            self.__flag.wait()      
#             LOGGER.info('running!')
            if self.kwargs != None:
                self.target(*self.args,**self.kwargs)
            else:
                self.target(*self.args)
            if self.loop: continue
            else: break
                
    def pause(self):
        self.__flag.clear() if self.loop else None
    def resume(self):
        self.__flag.set() if self.loop else None  

    def stop(self):
        if self.loop:
            self.__flag.set()       
            self.__running.clear()   


if __name__ =='__main__':

    global idx
    idx = 0
    def test(id,say=None):
        global idx
        LOGGER.info('%d time (%d) %s',id,idx,say)
        time.sleep(1)
        idx+=1
    job = Job(loop=True,target=test,name='thread test',args=(1,),kwargs={'say':'hello'})

    job.start()
    time.sleep(5)
    job.pause()
    time.sleep(2)
    job.resume()
    time.sleep(2)
    job.stop()
