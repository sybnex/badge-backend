#!/usr/bin/env python
#-*- coding: utf-8 -*-

from libs.sqlite import SQLService
init = SQLService(database = ":memory:")

test_name  = "Test"
test_value = "success"

def test_sqlerror():
    assert init.readMessage(test_name) is None

def test_initCount():
    init.createTable()
    assert init.countMessage() == (0,)

def test_generateBadge():
    init.generateBadge()
    assert len(init.badgeId) == 8

def test_validateToken_pos():
    assert init.validateToken() is not None

def test_updateBadge():
    init.name = test_name
    init.value = test_value
    init.updateBadge()
    assert init.readMessage(init.badgeId)[4] == test_value

def test_initGetBadge():
    init.getBadge()
    assert init.name == test_name

def test_initReadAll():
    assert init.readAllMessages()[0][2] == init.token

def test_initDelete():
    assert init.deleteMessage() == None

def test_initFinalDelete():
    assert init.readMessage(init.badgeId) == None

def test_initDeleteOld():
    assert init.deleteOldMessages() == None

def test_initDupId():
    init.generateBadge()
    assert init.checkDupId() == True

def test_emtpyState():
    init.badgeId = "1234"
    assert init.getBadge() == False

def test_validateToken_neg():
    init.token = "1234"
    assert init.validateToken() is None

