#!/usr/bin/env python

DESCRIPTION = '''\
  Vacation service for Postfix ver0.2 Copyright(C) 2013 M.Andrews
		released under the BSD License.
		Create: 2013/01/10
		Update: 2013/01/10

'''
USAGE = '''\
 usage: python vacation.py sender@domain.tld recipient@domain.tld
'''

import socket, threading, sys, time, re, syslog, os, MySQLdb, smtplib, string

# MySQL configuration
DB_HOST                  = "a.b.c.d"
DB_USER                  = "user"
DB_PASSWORD              = "password"
DB_DB                    = "vacation"

# SMTP
RELAY_HOST		 = "relay.domain.tld"

# Verbose logging
VERBOSE 		 = 0

SENDER			 = sys.argv[1]
RAW_RECIPIENT_LIST       = sys.argv[2].split('@')
RECIPIENT		 = RAW_RECIPIENT_LIST[0] + "@" + RAW_RECIPIENT_LIST[1]

def mysql_conn(host, user, password, db, query):
	"""Connect to MySQL server, execute query, return results"""
	try:
	        db = MySQLdb.connect(host, user, password, db)
	        cursor = db.cursor()
	        cursor.execute(query)
		db.commit()
	        results = cursor.fetchall()
	        return results
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_INFO, "fatal: SQL queried failed. %s" %e)		

def write_file(filename, writetype, string):
        f = open(filename, writetype)
        f.write(string)
        f.close()

def send_message(to, mesg_from, subject, text):
	body = string.join((
	        "From: %s" % mesg_from,
	        "To: %s" % to,
	        "Subject: %s" % subject ,
	        "",
	        text
	        ), "\r\n")
	server = smtplib.SMTP(RELAY_HOST)
	server.sendmail(mesg_from, [to], body)
	server.quit()

def vacation_thread(sender, recipient):
	"""Called by vacation_core(), execute program logic"""
	try:
		## Check if a reply has been sent for this user today
	        query = "SELECT 'yes' FROM outofoffice_log WHERE sender = " + "'" + sender + "'" + " AND recipient = " + "'" + recipient + "'" + " AND created >= CURDATE()"
        	results = mysql_conn(DB_HOST, DB_USER, DB_PASSWORD, DB_DB, query)
        	for row in results:
                	sent = row[0]
	
		try:
                	sent
		except NameError:
			sent = 'na'

		if sent == 'na':
			## Get variables for processing
		        query = "SELECT subject, bodytext, ooofrom FROM outofoffice WHERE username = " + "'" + recipient + "'"
        		results = mysql_conn(DB_HOST, DB_USER, DB_PASSWORD, DB_DB, query)
	        	for row in results:
        	        	subject = row[0]
        	        	bodytext = row[1]
        	        	ooofrom = row[2]
				try:
					send_message(sender, ooofrom, subject, bodytext)
					syslog.syslog(syslog.LOG_INFO, "info: sent to=<" + str(sender) + "> local-recipient=<" + str(recipient) + "> reply-to=<" + str(ooofrom) + "> relay=[" + RELAY_HOST + "]" )
				except Exception,e:
					syslog.syslog(syslog.LOG_INFO, "fatal: could not send reply message")

			try:
			        query = "INSERT INTO outofoffice_log VALUES(" + "'" + recipient + "', " + "'" + sender + "', " + "NOW())"
        			results = mysql_conn(DB_HOST, DB_USER, DB_PASSWORD, DB_DB, query)
			except:
				syslog.syslog(syslog.LOG_INFO, "fatal: insert SQL query failed")
		else:
			if VERBOSE == 1:
				syslog.syslog(syslog.LOG_INFO, "info: message already sent to=<" + str(sender) + "> local-recipient=<" + str(recipient) + ">" )
	except:
		syslog.syslog(syslog.LOG_INFO, "fatal: Service failed ")

def vacation_core():
	"""Called by vacation() Establish syslog, establish socket, open threads"""
	syslog.openlog("vacation", syslog.LOG_PID, syslog.LOG_MAIL)
	try:
		threading.Thread(target=vacation_thread, args=(SENDER, RECIPIENT)).start()
	except:
		syslog.syslog(syslog.LOG_INFO, "fatal: unable to start policy service thread")

if __name__ == "__main__":
	vacation_core()
