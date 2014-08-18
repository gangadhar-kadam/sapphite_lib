# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd.
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl

@webnotes.whitelist()
def interval(interval):
	webnotes.conn.set_value("Notification Setting", "Notification Setting", "execution_time", 
		(datetime.now()+timedelta(hours=cint(interval))).strftime('%Y-%m-%d %H:%M:%S'))
