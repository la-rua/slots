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
    #classOrdDelFun{className:[(__del__),times]}
def addSlot(srcObject = None,signal ="",dstObject = None,slot = lambda : None ):
    srcId = -1
    dstId = -1
    if not srcObject == None:
        srcId = id(srcObject)
    if not dstObject == None:
        dstId = id(dstObject)    
    CommonSlots.slotsRLock.acquire()
    if not (srcId,signal) in CommonSlots.slots:
        CommonSlots.slots[(srcId,signal)] = set()
    funSet = CommonSlots.slots[(srcId,signal)]
    CommonSlots.slots[(srcId,signal)] = funSet | set([(dstId,slot),])
    CommonSlots.slotsRLock.release()
    addObject(srcObject)
    addObject(dstObject)


def delSlot(srcObject = None,signal = None,dstObject = None,slot =  lambda : None):
    srcId = -1
    dstId = -1
    if srcObject != None:
        srcId= id(srcObject)
    if dstObject != None:
        dstId= id(dstObject)
    #should first del slot
    CommonSlots.slotsRLock.acquire()
    if not (srcId,signal) in CommonSlots.slots:
        CommonSlots.slotsRLock.release()
        return
    funSet = CommonSlots.slots[(srcId,signal)]
    CommonSlots.slots[(srcId,signal)] = funSet - set([(dstId,slot),])
    if len(funSet) == 0:
        del CommonSlots.slots[(srcId,signal)]
    CommonSlots.slotsRLock.release()
    delObject(srcObject)
    delObject(dstObject)

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
            dstObject = CommonSlots.objectRef[dstId][0]()
            f(dstObject,*args,**kw)

def returnDelFun(self):
    res = None
    t = type(self)  
    fun = CommonSlots.classOrdDelFun[t][0]
    if fun != None:
        res = fun()
    ObejctGc(self)
    return res
def returnOrdDelFun(self):
    t = type(self)  
    if not t in CommonSlots.classOrdDelFun:
        return None
    return CommonSlots.classOrdDelFun[t][0]

def ObejctGc(self):
    delId = id(self)
    needRemoveObject = []
    needRemoveObject.append(self)
    needDelSlot = []
    CommonSlots.slotsRLock.acquire()
    for k in CommonSlots.slots:
        srcId,signal = k
        if srcId == delId:
            for v in CommonSlots.slots[k]:
                dstId,_ = v
                dstObject = CommonSlots.objectRef[dstId][0]()
                needRemoveObject.append(dstObject)
            needDelSlot.append((srcId,signal))
        else:
            needRemoveSet = set()
            for v in CommonSlots.slots[k]:
                 dstId,slot = v
                 if dstId == delId:
                    needRemoveSet = needRemoveSet |set([(dstId,slot),])
            CommonSlots.slots[k] = CommonSlots.slots[k] - needRemoveSet
            if len(CommonSlots.slots[k]) == 0:
                srcObject = CommonSlots.objectRef[srcId][0]()
                needRemoveObject.append(srcObject)
    for i in needDelSlot:
        del CommonSlots.slots[i]
    CommonSlots.slotsRLock.release()
    for o in needRemoveObject:
        delObject(o)

def addObject(self):
    if self == None:
        return 
    addId = id(self)
    CommonSlots.objectRLock.acquire()
    if not addId in CommonSlots.objectRef:
        CommonSlots.objectRef[addId] = [weakref.ref(self),0]
    CommonSlots.objectRef[addId][1] += 1
    if not type(self) in CommonSlots.classOrdDelFun:
        CommonSlots.classOrdDelFun[type(self)] = [type(self).__del__,0]
        setattr(type(self),"__del__",returnDelFun)
    CommonSlots.classOrdDelFun[type(self)] += 1
    CommonSlots.objectRLock.release()
    
def delObject(self):
    if self == None:
        return 
    delId = id(self)
    CommonSlots.objectRLock.acquire()
    if delId in CommonSlots.objectRef:
        CommonSlots.objectRef[delId][1] -= 1
    if CommonSlots.objectRef[delId][1] == 0:
        del CommonSlots.objectRef[delId]
    if type(self) in CommonSlots.classOrdDelFun:
        CommonSlots.classOrdDelFun[type(self)][1] -= 1
        if CommonSlots.classOrdDelFun[type(self)][1] == 0:
            fun = CommonSlots.classOrdDelFun[type(self)][0]
            if fun == None:
                delattr(type(self),"__del__")
            else:
                setattr(type(self),"__del__",fun)
            del CommonSlots.classOrdDelFun[type(self)]
    CommonSlots.objectRLock.release()

