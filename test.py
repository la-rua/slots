#!/usr/bin/env python3.5
# -*- coding:utf-8 -*-
import slots
import gc
class A (object):
    def askB(self):
        slots.Signal(self,"askB")
class B (object):
    def BSpeck(self):
        print("B speck")
class A1 (object):
    def askB(self):
        slots.Signal(self,"askB")
    def __del__(self):
        print("A del")
class B1 (object):
    def BSpeck(self):
        print("B speck")
    def __del__(self):
        print("B del")
class Test(object):
    def add(self):
        a = A()
        b = B()
        slots.addSlot(a,"askB",b,B.BSpeck)
        a.askB()
    def addThenDel(self):
        a = A()
        b = B()
        slots.addSlot(a,"askB",b,B.BSpeck)
        slots.addSlot(a,"askB",b,B.BSpeck)
        slots.delSlot(a,"askB",b,B.BSpeck)
        a.askB()
    def addThenGC(self):
        a = A()
        b = B()
        slots.addSlot(a,"askB",b,B.BSpeck)
        del b
        gc.collect()
        a.askB()
    def testGc(self):
        a1 = A()
        a2 = A()
        a3 = A()
        b1 = B()
        b2 = B()
        b3 = B()
        slots.addSlot(a1,"askB",b1,B.BSpeck)
        slots.addSlot(a2,"askB",b1,B.BSpeck)
        slots.addSlot(a3,"askB",b1,B.BSpeck)
        del b1
        a1.askB()
        a2.askB()
        a3.askB()
        del a1
        del a2
        del a3
        del b2
        del b3
    def testGc1(self):
        a1 = A()
        a2 = A()
        a3 = A()
        b1 = B()
        b2 = B()
        b3 = B()
        slots.addSlot(a1,"askB",b1,B.BSpeck)
        slots.addSlot(a2,"askB",b1,B.BSpeck)
        slots.addSlot(a3,"askB",b1,B.BSpeck)
        del a1
        del a2
        del a3
        slots.CommonSlots.classOrdDelFun
        slots.CommonSlots.objectRef
        slots.CommonSlots.slots
        del b1
        del b2
        del b3
    def testGc2(self):
        a1 = A1()
        a2 = A1()
        a3 = A1()
        b1 = B1()
        b2 = B1()
        b3 = B1()
        slots.addSlot(a1,"askB",b1,B.BSpeck)
        slots.addSlot(a2,"askB",b1,B.BSpeck)
        slots.addSlot(a3,"askB",b1,B.BSpeck)
        del a1
        del a2
        del a3
        slots.CommonSlots.classOrdDelFun
        slots.CommonSlots.objectRef
        slots.CommonSlots.slots
        del b1
        del b2
        del b3
t = Test()
#t.add()
#t.addThenDel()
#t.addThenGC()
t.testGc2()