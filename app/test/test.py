#!/usr/bin/env python
#-*- coding: utf-8 -*-

from libs.sqlite import SQLService
init = SQLService(database = ":memory:")

testmessage = "This is a test."

def test_generateId():
    assert len(init.generateId()) == 8


def test_initCount():
    init.createTable()
    assert init.countMessage() == (0,)


def test_initSave():
    init.saveMessage(testmessage)
    assert init.readMessage(init.hashval)[2] == testmessage


def test_initReadAll():
    assert init.readAllMessages()[0][2] == testmessage


def test_initDelete():
    assert init.deleteMessage(init.hashval) == None


def test_initFinalDelete():
    assert init.readMessage(init.hashval) == None


def test_initDeleteOld():
    assert init.deleteOldMessages() == None


def test_generateId2():
    init.saveMessage(testmessage)
    init.checkDupId()
    assert init.hashval == None
