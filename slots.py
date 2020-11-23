# -*- coding:utf-8 -*-
# +++++++++++++++++++++++++++++++++++++++++++++++++
# ++             Slots Moudle                    ++
# ++   this moudle is designed to make two class ++
# ++ without relavent communicate                ++
# ++                                 11/2020     ++
# ++                                 la-rua      ++
# +++++++++++++++++++++++++++++++++++++++++++++++++
import weakref
from threading import RLock
class CommonSlots (object):
    objectRef = {}
    objectRLock = RLock()
    #objectRef:{id:(ref,times)}
    slots = {}
    slotsRLock = RLock()
    #slots{(id,signal):(id,slot)}
    classOrdDelFun = {}
    #classOrdDelFun{className:(__del__)}
def addSlot(srcObject = None,signal ="",dstObject = None,slot = lambda : None ):
    srcId = -1
    dstId = -1
    CommonSlots.objectRLock.acquire()
    if srcObject != None:
        srcId = id(srcObject)
        setattr( type(srcObject),"__del__",returnDelFun(srcObject))
    if dstObject != None:
        dstId = id(dstObject)
        setattr( type(dstObject),"__del__",returnDelFun(dstObject))
    if not srcId in CommonSlots.objectRef:
        CommonSlots.objectRef[srcId] = weakref.ref(srcObject)
    if not dstId in CommonSlots.objectRef:
        CommonSlots.objectRef[dstId] = weakref.ref(dstObject)
    CommonSlots.objectRLock.release()
    CommonSlots.slotsRLock.acquire()
    if not (srcId,signal) in CommonSlots.slots:
        CommonSlots.slots[(srcId,signal)] = set()
    funSet = CommonSlots.slots[(srcId,signal)]
    CommonSlots.slots[(srcId,signal)] = funSet | set([(dstId,slot),])
    CommonSlots.slotsRLock.release()

def delSlot(srcObject = None,signal = None,dstObject = None,slot =  lambda : None):
    srcId = -1
    dstId = -1
    CommonSlots.objectRLock.acquire()
    if srcObject != None:
        srcId = id(srcObject)
        fun = returnOrdDelFun(srcObject)
        if fun == None:
            delattr(type(srcObject),"__del__")
        else:
            setattr(type(srcObject),"__del__",fun)
    if dstObject != None:
        dstId = id(dstObject)
        fun = returnOrdDelFun(dstObject)
        if fun == None:
            delattr(type(dstObject),"__del__")
        else:
            setattr(type(dstObject),"__del__",fun)
    if not srcId in CommonSlots.objectRef:
        CommonSlots.objectRLock.release()
        return
    if not dstId in CommonSlots.objectRef:
        CommonSlots.objectRLock.release()
        return
    CommonSlots.objectRLock.release()
    CommonSlots.slotsRLock.acquire()
    if not (srcId,signal) in CommonSlots.slots:
        CommonSlots.slotsRLock.release()
        return
    funSet = CommonSlots.slots[(srcId,signal)]
    CommonSlots.slots[(srcId,signal)] = funSet - set([(dstId,slot),])
    CommonSlots.slotsRLock.release()

def Signal(self,signal,*args,**kw):
    srcId = -1
    if self != None:
        srcId = id(self)
    if not srcId in CommonSlots.objectRef:
        return
    if not (srcId,signal) in CommonSlots.slots:
        return
    funSet = CommonSlots.slots[(srcId,signal)]
    for song in funSet:
        dstId,f = song
        if dstId == -1:
            f(*args,**kw)
        else:
            if not dstId in CommonSlots.objectRef:
                return
            dstObject = CommonSlots.objectRef[dstId]
            f(dstObject(),*args,**kw)

def returnDelFun(self):
    fun = None
    if self != None and hasattr(type(self),"__del__"):
        fun = getattr(type(self),"__del__")
    t = type(self)  
    if not t in CommonSlots.classOrdDelFun:
        CommonSlots.classOrdDelFun[t] = fun if fun!= None else None
    def delFun(self):
        res = None
        fun = CommonSlots.classOrdDelFun[t]
        if fun != None:
            res = fun()
        ObejctGc(self)
        return res
    return delFun
def returnOrdDelFun(self):
    t = type(self)  
    if not t in CommonSlots.classOrdDelFun:
        return None
    return CommonSlots.classOrdDelFun[t]

def ObejctGc(self):
    delId = id(self)
    if delId in CommonSlots.objectRef:
        del CommonSlots.objectRef[delId]
