#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import uuid
import sqlite3
import logging
import threading

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")

class SQLService():

    def __init__(self, badgeId=None, token=None, database="/app/db/notiz.db"):
        self.badgeId = badgeId
        self.token = token
        self.name = None
        self.value = None
        self.name_color = None
        self.value_color = None
        self.conn = sqlite3.connect(database)

    def executeSQL(self, sql, args=(), fetchall=False):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, args)
        except Exception as error:
            logging.error("Could not execute SQL statement ... %s" % (error))
            self.conn.rollback()
        else:
            self.conn.commit()
            if fetchall:
                return cur.fetchall()
            else:
                return cur.fetchone()
        finally:
            cur.close()

    def createTable(self):
        query = """CREATE TABLE IF NOT EXISTS
                   badges(ID TEXT PRIMARY KEY NOT NULL,
                          DATE TEXT NOT NULL,
                          TOKEN TEXT NOT NULL CHECK(DATA > ' '))
                          NAME TEXT NOT NULL CHECK(DATA > ' '))
                          VALUE TEXT NOT NULL CHECK(DATA > ' '))
                          NCOLOR TEXT NOT NULL CHECK(DATA > ' '))
                          VCOLOR TEXT NOT NULL CHECK(DATA > ' '))"""
        self.executeSQL(query)

    def checkDupId(self):
        if self.readMessage(self.badgeId):
            self.badgeId = None
            return True
        return False

    def generateBadge(self):
        while (not self.hashval):
            hash_value   = str(uuid.uuid4())
            self.badgeId = hash_value[:8]
            self.token   = hash_value[-12:]
            self.checkDupId()

        self.saveBadge()

    def saveBadge(self):
        query = "INSERT INTO badges (ID, DATE, TOKEN) VALUES (?, ?, ?)"
        args = ('%s' % self.badgeId,
                time.strftime('%Y-%m-%d'),
                '%s' % self.token)
        self.executeSQL(query, args)

    def updateBadge(self, name, value, ncolor = None, vcolor = None):
        query = """UPDATE badges 
                     SET NAME = ?, VALUE = ?, NCOLOR = ?, VCOLOR = ?
                     WHERE ID = ? AND TOKEN = ?"""
        args = ("%s" % name, 
                "%s" % value,
                "%s" % ncolor,
                "%s" % vcolor,
                '%s' % self.badgeId,
                '%s' % self.token)
        self.executeSQL(query, args)

    def getBadge(self):
        query = "SELECT * FROM badges WHERE ID = ? AND TOKEN ?"
        return self.executeSQL(query, (self.badgeId,self.token,))
 
    def readMessage(self, pk_id):
        query = "SELECT * FROM badges WHERE ID = ?"
        return self.executeSQL(query, (pk_id,))

    def readAllMessages(self):
        query = "SELECT * FROM badges"
        return self.executeSQL(query, fetchall=True)

    def deleteMessage(self):
        query = "DELETE FROM badges WHERE ID = ? AND TOKEN = ?"
        return self.executeSQL(query, (self.badgeId,self.token,))

    def countMessage(self):
        query = "SELECT count(*) FROM badges"
        return self.executeSQL(query)

    def deleteOldMessages(self):
        query = "DELETE FROM badges WHERE date <= date('now', '-90 day')"
        return self.executeSQL(query)
