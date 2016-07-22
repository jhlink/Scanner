import numpy as mp
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys
import xlrd
import time

def setter():
	x=0
	list = []
	start_time = time.time()
	main(x,list,start_time)


def main(x,list,start_time):
	
	
	

	while( time.time()-start_time<3600):
		x =x+1
		BarCode  = raw_input("")
		BarCode  = str(BarCode)
		list.append(BarCode)
		a = set(list)
	
	f =open('f1.txt','w')
	for x in a:
    		f.write(x+'\n')
	f.close()
	fromaddr = "FirstBuildInventory@gmail.com"
	toaddr = "james@firstbuild.com, tim@firstbuild.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "SUBJECT OF THE MAIL"
	 
	body = "SEE ATTACH"
	filename = "f1.txt"
	f = file(filename)
	attachment = MIMEText(f.read())
	attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
	msg.attach(attachment)
	 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "firstbuild")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
while(1):
	setter()

