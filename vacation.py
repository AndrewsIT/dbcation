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

# History
# =================================================================
# v0.1 Created
# v0.2 Fixed reply-to, updated logging
# -----------------------------------------------------------------
#
#
# Postfix configuration
# =================================================================
#  main.cf
# -----------------------------------------------------------------
#
# transport_maps = hash:/etc/postfix/transport
# virtual_alias_maps = mysql:/etc/postfix/vacation.cf
#
#  master.cf
# -----------------------------------------------------------------
# 
# vacation   unix  -       n       n       -       -       pipe
#  flags=FR user=airadmin argv=/usr/bin/python /etc/postfix/vacation.py ${sender} ${recipient}
# 
#  transport
# -----------------------------------------------------------------
#
# autoreply.domain.tld	vacation:
#
#  vacation.cf
# -----------------------------------------------------------------
#
# hosts = a.b.c.d, w.x.y.z
# user = abcd
# password = wxyz
# dbname = passwd
# query = SELECT CONCAT('%s',"@autoreply.domain.tld"), '%s' FROM outofoffice WHERE username = '%s' AND NOW() BETWEEN startdate AND enddate
#
#

import socket, threading, sys, time, re, syslog, os, MySQLdb, smtplib, string

# MySQL configuration
DB_HOST                  = "a.b.c.d"
DB_USER                  = "user"
DB_PASSWORD              = "password"
DB_DB                    = "db"

SENDER			 = sys.argv[1]
RAW_RECIPIENT_LIST       = sys.argv[2].split('@')
RECIPIENT		 = RAW_RECIPIENT_LIST[0] + "@" + RAW_RECIPIENT_LIST[1]

RELAY_HOST		 = "relay.domain.tld"

VERBOSE 		 = 0

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
					#if VERBOSE == 1:
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

		#syslog.syslog(syslog.LOG_INFO, "info: sent to=<" + str(sender) + "> local-recipient=<" + str(recipient) + "> reply-to=<" + str(ooofrom) + ">" )			
	except:
		syslog.syslog(syslog.LOG_INFO, "fatal: Service failed ")

def vacation_core():
	"""Called by vacation() Establish syslog, establish socket, open threads"""
	syslog.openlog("vacation", syslog.LOG_PID, syslog.LOG_MAIL)
	#syslog.syslog(syslog.LOG_INFO, "info: start %s" % re.findall("[^\n]+", DESCRIPTION)[0].strip())
	try:
		threading.Thread(target=vacation_thread, args=(SENDER, RECIPIENT)).start()
	except:
		syslog.syslog(syslog.LOG_INFO, "fatal: unable to start policy service thread")

if __name__ == "__main__":
	vacation_core()