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
flags=FR user=airadmin argv=/usr/bin/python /etc/postfix/vacation.py ${sender} ${recipient}
 

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
mysql vacation < vacation.sql
