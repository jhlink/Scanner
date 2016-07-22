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
	
	scannerList = [] 									#raw input list from scanner including repeating entries
	start_time = time.time() 							#start time for the function
	main(scannerList,start_time)

def main(list,start_time):
	while( time.time()-start_time<5):  				#send a file every 3600seconds (1hr) if something changes
		BarCode  = raw_input("")
		BarCode  = str(BarCode)							#Gets input from scanner converts to String
		list.append(BarCode)
		ScanSet = set(list) 							#Converts list to Set with no repeating codes
	
	f =open('f1.txt','w') 								#write to file named f1.txt
	for x in ScanSet:
    		f.write(x+'\n')
	f.close()


	fromaddr = "FirstBuildInventory@gmail.com"			#Setting the email Fields
	toaddr = "james@firstbuild.com, tim@firstbuild.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "SUBJECT OF THE MAIL"
	 
	body = "SEE ATTACH"								
	filename = "f1.txt"									#Attach Text File
	f = file(filename)
	attachment = MIMEText(f.read())
	attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
	msg.attach(attachment)
	 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "firstbuild")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)				#Send Mail
	server.quit()


while(1):												#infinite loop to have the code always running
setter()

