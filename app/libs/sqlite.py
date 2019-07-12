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

    def __init__(self, database="/app/db/notiz.db"):
        self.hashval = None
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
                   messages(ID TEXT PRIMARY KEY NOT NULL,
                            DATE TEXT NOT NULL,
                            DATA TEXT NOT NULL CHECK(DATA > ' '))"""
        self.executeSQL(query)

    def checkDupId(self):
        if self.readMessage(self.hashval):
            self.hashval = None
            return True
        return False

    def generateId(self):
        while (not self.hashval):
            self.hashval = str(uuid.uuid4())[:8]
            self.checkDupId()
        logging.info("Generated ID is %s" % self.hashval)
        return self.hashval

    def saveMessage(self, message):
        query = "INSERT INTO messages (ID, DATE, DATA) VALUES (?, ?, ?)"
        args = ('%s' % self.hashval,
                time.strftime('%Y-%m-%d'),
                '%s' % str(message))
        self.executeSQL(query, args)

    def readMessage(self, pk_id):
        query = "SELECT * FROM messages WHERE ID = ?"
        return self.executeSQL(query, (pk_id,))

    def readAllMessages(self):
        query = "SELECT * FROM messages"
        return self.executeSQL(query, fetchall=True)

    def deleteMessage(self, pk_id):
        query = "DELETE FROM messages WHERE ID= ?"
        return self.executeSQL(query, (pk_id,))

    def countMessage(self):
        query = "SELECT count(*) FROM messages"
        return self.executeSQL(query)

    def deleteOldMessages(self):
        query = "DELETE FROM messages WHERE date <= date('now', '-90 day')"
        return self.executeSQL(query)
