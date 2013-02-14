dbcation
========

Database backed vacation script for postfix

Requirements
=================================================================
postfix  
python  
python MySQLdb (yum install MySQL-python / apt-get install python-mysqldb)  
MySQL server


Postfix configuration
=================================================================
main.cf
-----------------------------------------------------------------

transport_maps = hash:/etc/postfix/transport  
virtual_alias_maps = mysql:/etc/postfix/vacation.cf  


master.cf
-----------------------------------------------------------------
 
vacation   unix  -       n       n       -       -       pipe  
flags=FR user=localuser argv=/usr/bin/python /etc/postfix/vacation.py ${sender} ${recipient}
 

transport
-----------------------------------------------------------------

autoreply.domain.tld  vacation:


vacation.cf
-----------------------------------------------------------------

hosts = a.b.c.d, w.x.y.z  
user = abcd  
password = wxyz  
dbname = passwd  
query = SELECT CONCAT('%s',"@autoreply.domain.tld"), '%s' FROM outofoffice WHERE username = '%s' AND NOW() BETWEEN startdate AND enddate


MySQL configuration
=================================================================
Import sql configuration
-----------------------------------------------------------------

mysql vacation < vacation.sql


Notes
=================================================================
Virtual hosting
-----------------------------------------------------------------

Postfix has the ability to alias mail from a virtual address to a local address, so this script allows you to send  
vacation replies with an alternate replyto address.  The column username defines the email address which matches the  
recipient address.  The column ooofrom is used as the replyto address in the vacation reply email to the sender.  If you  
plan on accepting messages for the same address that will be included in the replyto simply insert the same address  
into the username and ooofrom columns.


