#!/usr/bin/env python
#-*- coding: utf-8 -*-

from libs.sqlite import SQLService
init = SQLService(database = ":memory:")

test_name  = "Test"
test_value = "success"

def test_initCount():
    init.createTable()
    assert init.countMessage() == None

def test_generateBadge():
    init.generateBadge()
    assert len(init.badgeId) == 8

def test_updateBadge():
    init.updateBadge(test_name, test_value)
    assert init.readMessage(init.badgeId)[4] == test_value

def test_initReadAll():
    assert init.readAllMessages()[0][2] == init.token

def test_initDelete():
    assert init.deleteMessage() == None

def test_initFinalDelete():
    assert init.readMessage(init.badgeId) == None

def test_initDeleteOld():
    assert init.deleteOldMessages() == None

