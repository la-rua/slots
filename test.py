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
t = Test()
#t.add()
#t.addThenDel()
#t.addThenGC()