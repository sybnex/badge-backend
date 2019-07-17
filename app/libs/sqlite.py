#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import uuid
import sqlite3
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")


class SQLService():

    def __init__(self, badgeId=None, token=None, database="/app/db/notiz.db"):
        self.badgeId = badgeId
        self.token = token
        self.name = "example"
        self.value = "badge"
        self.name_color = "grey"
        self.value_color = "blue"
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
        query = """CREATE TABLE IF NOT EXISTS badges (
                     ID TEXT PRIMARY KEY NOT NULL,
                     DATE TEXT NOT NULL,
                     TOKEN TEXT NOT NULL CHECK(TOKEN > ' '),
                     NAME TEXT,
                     VALUE TEXT,
                     NCOLOR TEXT,
                     VCOLOR TEXT)"""
        self.executeSQL(query)

    def checkDupId(self):
        if self.readMessage(self.badgeId):
            self.badgeId = None
            return True
        return False

    def generateBadge(self):
        while (not self.badgeId):
            hash_value = str(uuid.uuid4())
            self.badgeId = hash_value[:8]
            self.token = hash_value[-12:]
            self.checkDupId()

        self.saveBadge()

    def saveBadge(self):
        query = "INSERT INTO badges (ID, DATE, TOKEN) VALUES (?, ?, ?)"
        args = ('%s' % self.badgeId,
                time.strftime('%Y-%m-%d'),
                '%s' % self.token)
        self.executeSQL(query, args)

    def updateBadge(self):
        query = """UPDATE badges
                   SET NAME = ?, VALUE = ?, NCOLOR = ?, VCOLOR = ?
                   WHERE ID = ? AND TOKEN = ?"""
        args = ("%s" % self.name,
                "%s" % self.value,
                "%s" % self.name_color,
                "%s" % self.value_color,
                '%s' % self.badgeId,
                '%s' % self.token)
        self.executeSQL(query, args)

    def getBadge(self):
        query = "SELECT name, value, ncolor, vcolor FROM badges WHERE id = ?"
        result = self.executeSQL(query, (self.badgeId,))
        try:
            logging.info(result)
            self.name = result[0]
            self.value = result[1]
            self.ncolor = result[2]
            self.vcolor = result[3]
        except Exception:
            return False
        else:
            return True

    def validateToken(self):
        query = "SELECT * FROM badges WHERE ID = ? AND TOKEN = ?"
        return self.executeSQL(query, (self.badgeId, self.token,))

    def readMessage(self, pk_id):
        query = "SELECT * FROM badges WHERE ID = ?"
        return self.executeSQL(query, (pk_id,))

    def readAllMessages(self):
        query = "SELECT * FROM badges"
        return self.executeSQL(query, fetchall=True)

    def deleteMessage(self):
        query = "DELETE FROM badges WHERE ID = ? AND TOKEN = ?"
        return self.executeSQL(query, (self.badgeId, self.token,))

    def countMessage(self):
        query = "SELECT count(*) FROM badges"
        return self.executeSQL(query)

    def deleteOldMessages(self):
        query = "DELETE FROM badges WHERE date <= date('now', '-90 day')"
        return self.executeSQL(query)
