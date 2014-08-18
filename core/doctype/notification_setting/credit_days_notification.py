import webnotes
from webnotes.utils import cstr
from webnotes.utils.email_lib import sendmail
from webnotes.utils import now, get_datetime, cint, validate_email_add, cstr
from datetime import datetime, timedelta


def check_period():
	if datetime.now() >= get_datetime(webnotes.conn.get_value("Notification Setting", None, "execution_time")):
		generate_message()
		set_next_execution_time()

def set_next_execution_time():
	next_execution_time = get_datetime(webnotes.conn.get_value("Notification Setting", None, "execution_time")) + timedelta(hours=cint(webnotes.conn.get_value("Notification Setting", None, "interval")))
	webnotes.conn.set_value("Notification Setting","Notification Setting","execution_time",next_execution_time)

def get_customer_wise_credit_details():
	return webnotes.conn.sql(""" select name, net_total_export, outstanding_amount, customer, posting_date, 
		group_concat(email,' ') as email, value, credit, last_date, percent_time_left from
			(select si.name, net_total_export, outstanding_amount, si.customer,si.posting_date, c.email_id as email, sing.value,
		                cust.credit_days as credit ,
		                DATE_ADD(si.posting_date, INTERVAL cust.credit_days DAY) as last_date,
		                (DATEDIFF(DATE_ADD(si.posting_date, INTERVAL cust.credit_days DAY),curdate())/cust.credit_days)*100 as percent_time_left,
		                DATEDIFF(CURDATE(),si.posting_date) 
			from `tabSales Invoice` si , `tabContact` c , `tabCustomer` cust, `tabSingles` sing
			where c.customer = si.customer
			and ifnull(cust.enable_notification,0) = 1 
			and cust.name = si.customer 
			and field = 'percentage_time_left' 
			and doctype = 'Notification Setting'
			and cust.credit_days is not null
			and si.outstanding_amount > 0
			and si.docstatus = 1
			) test
		where percent_time_left <= value
		group by  name, net_total_export, outstanding_amount, customer,posting_date,value, credit,
		last_date, percent_time_left""",as_dict=1)

def generate_message():
	cust_credit_details = generate_cust_credit_details()
	for customer in cust_credit_details:
		msg = get_msg_format(customer)
		row = ""
		for invoice in cust_credit_details[customer]:
			row += """ <tr><td align='left'>%(name)s</td><td align='right'>%(net_total_export)s</td>
					<td align='right'>%(outstanding_amount)s</td>
				</tr>"""%cust_credit_details[customer][invoice]
		msg = msg + row + """</table><br><br> Credit Controller,<br> Sapphire Virtual Networks Limited
			</body>
		</html>"""
		send_mail(msg, cust_credit_details[customer][invoice].get('email'))

def generate_cust_credit_details():
	cust_credit_details = {}
	customer_wise_credit_details = get_customer_wise_credit_details()
	for credit_details in customer_wise_credit_details:
		cust_credit_details.setdefault(credit_details.get("customer"),{})
		cust_credit_details[credit_details.get("customer")][credit_details.get("name")] = credit_details

	return cust_credit_details

def get_msg_format(customer):
	return """ Hello %(customer)s, <br><br><br><br>
		This is an intemation for pending payments : 
			<html>
				<body>
					<br>
						<table border=1 style="border-collapse:collapse">
							<tr>
								<th>Invoice</th>
								<th>Total Amount</th>
								<th>Outstanding Amount</th>
							<tr>
		"""%{'customer':customer}

def send_mail(msg, customer_email):
	cust_emails = validate_customer_mail(customer_email.split(','))
	email_ids = get_emails(cust_emails)
	for i in range(0,cint(webnotes.conn.get_value('Notification Setting', None, 'frequency'))):
		sendmail(email_ids, subject="Payment Reminder", msg = msg)

def validate_customer_mail(cust_emails):
	emails = []
	for email in cust_emails:
		if validate_email_add(email):
			emails.append(email)
	return emails

def get_emails(email_list):
	return get_accounts_role_emails(email_list)

def get_accounts_role_emails(email_list):
	for profile in webnotes.conn.sql(""" select distinct p.name  from tabProfile p, tabUserRole ur 
		where ur.role in ("Accounts Manager","Accounts User") 
			and ur.parent = p.name; """,as_list=1):
		email_list.append(profile[0])

	return email_list
	
#and c.email_id  REGEXP '^[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$'
