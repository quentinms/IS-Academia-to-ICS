#!/usr/bin/env python
#-*- coding: utf-8 -*-

import cookielib, urllib, urllib2
import argparse
from time import strptime
from xml.dom.minidom import parseString
import re

#POST https://isa.epfl.ch/imoniteur_ISAP/!logins.tryToConnect
#Host: isa.epfl.ch
#ww_x_username=XXXXXXX&ww_x_password=XXXXXXX&ww_x_urlAppelant=
#
#Date format: dd.mm.YYYY
#
#Source: http://wikipython.flibuste.net/CodesReseau#G.2BAOk-rer_les_cookies


def loginAndDownloadXML(username, password, date,nbWeeks):
	  
	  # Cookies
	cookiejar = cookielib.CookieJar()
	urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
	  
	 # Send POST Request
	values = {'ww_x_username':username, 'ww_x_password':password,'ww_x_urlAppelant': '' }
	data = urllib.urlencode(values)
	request = urllib2.Request("https://isa.epfl.ch/imoniteur_ISAP/!logins.tryToConnect", data)
	url = urlOpener.open(request)  # Notre cookiejar reçoit automatiquement les cookies
	page = url.read()
	 
	 # Check if we're logged in
	if not 'ISA-CNXKEY' in [cookie.name for cookie in cookiejar]:
		raise ValueError, "Issue while connecting with login=%s, password=%s" % (username,password)
	 
	 #Download XMl
	url = urlOpener.open("https://isa.epfl.ch/imoniteur_ISAP/!PORTAL14S.portalCell?ww_k_cell=1210054559&ww_x_date=%s&ww_n_semaines=%s" % (date,nbWeeks))
	page = url.read()
	
	#Save result in file
	f = open('calendar.xml', 'w')
	f.write(page)
	f.close()

#http://www.travisglines.com/web-coding/python-xml-parser-tutorial
def parseXML():
	
	#Get the data
	f = open('calendar.xml','r')
	data = f.read()
	f.close()
	
	#Parse it nicely
	dom = parseString(data)
	
	#Get the lectures
	events = dom.getElementsByTagName('seance')
	
	if (events.length != 0):
		content=""
		#Extract info for each lecture
		for event in events:
			
			#Event ID
			#Important: EID are not unique. >.<
			eId = event.toxml()
			eId = re.sub("<seance id=\"","",eId)
			eId = re.sub("\">.*</seance>","",eId, 0 ,re.DOTALL)
			
			libelle = event.getElementsByTagName('libelle')[0]
			libs = libelle.getElementsByTagName('lib')
			
			#Course Name
			courseName = libs[0].toxml()
			courseName = re.sub("<lib>","",courseName)
			courseName = re.sub("</lib>","",courseName)
			
			#Room
			room = libs[1].toxml()
			room = re.sub("\[/URL\]</lib>","",room)
			room = re.sub("<lib>\[.*\]","",room)
				
			#Date and Time
			#<d_seance>17-OCT-12</d_seance>
			#<n_heuredebut>16</n_heuredebut>
			#<n_heurefin>17</n_heurefin>
			
			day = event.getElementsByTagName('d_seance')[0].toxml()
			day = re.sub("<d_seance>","",day)
			day = re.sub("</d_seance>","",day)
			
			startH = event.getElementsByTagName('n_heuredebut')[0].toxml()
			startH = re.sub("</n_heuredebut>","",startH)
			startH = re.sub("<n_heuredebut>","",startH)
			
			endH = event.getElementsByTagName('n_heurefin')[0].toxml()
			endH = re.sub("</n_heurefin>","",endH)
			endH = re.sub("<n_heurefin>","",endH)
			
			#Event Type
			#<type>LIP_PROJET</type>
			eType = event.getElementsByTagName('type')[0].toxml()
			eType = re.sub("<type>LIP_","",eType)
			eType = re.sub("</type>","",eType)
		
			#Teacher
			#<infobulle><lib>Madoeuf Stéphane</lib></infobulle>
			
			teacher = event.getElementsByTagName('infobulle')[0].getElementsByTagName('lib')[0].toxml()
			teacher = re.sub("<lib>","",teacher)
			teacher = re.sub("</lib>","",teacher)
			
			#print "Debug: "+eId+" | "+courseName+" | "+room+" | "+day+" | "+startH+"-"+endH+" | "+eType+" | "+teacher
			content+=createICS(eId,courseName,room,day,startH,endH,eType,teacher)+"\n"
		
		header = """BEGIN:VCALENDAR
PRODID:QMS-ISACADEMIA-TO-ICS
VERSION:2.0
METHOD:PUBLISH
			"""	
			
		footer = """END:VCALENDAR"""
		
		ics = header+content+footer
		
		#Save file
		f = open('epfl.ics', 'w')
		f.write(ics.encode("utf-8"))
		f.close()
	else :
		print "No events! Please choose an other period."
		
def createICS(eId,courseName,room,day,startH,endH,eType,teacher):
	
	formattedDate = formatDate(day)
	if(len(startH) < 2):
		startH = "0"+startH
	if(len(endH) < 2):
		endH = "0"+endH

	start = formattedDate+"T"+startH+"0000"
	end = formattedDate+"T"+endH+"0000"
		
	content = """
BEGIN:VEVENT
UID:%s
LOCATION:%s
SUMMARY:%s
DTSTART:%s
DTEND:%s
CLASS:PUBLIC
TRANSP:TRANSPARENT
END:VEVENT
	""" % (startH+"_"+eId,room,courseName+" ("+eType+")",start,end)
	
	return content
	
	
#From 17-OCT-12 to 20121017
def formatDate(day):
	infos=day.split("-")
	
	day=infos[0]
	
	#TODO: Verify month abbrev.
	month = {'JAN':'01','FEV':'02','MAR':'03','AVR':'04', 'MAI':'05','JUN':'06','JUI':'07', 'AOU':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'
	}[infos[1]]
	
	year="20"+infos[2]
	
	formattedDate = year+month+day
	
	return formattedDate

def inputDateFormat(string):
	try:
		strptime(string,"%d.%m.%Y")
	except ValueError as err:
	   	msg = "%s is not a valid date (%s)" % (string,err)
	   	raise argparse.ArgumentTypeError(msg)
	   		
	return string

#Main
parser = argparse.ArgumentParser(description='Downloads calendar data from IS-Academia and export it in a .ics file')
parser.add_argument('-u', action="store", dest='username', help = 'GASPAR username', required = True)
parser.add_argument('-p', action="store", dest='password', help='GASPAR password', required = True)
parser.add_argument('-d', action="store", dest='startDate',type=inputDateFormat, default='17.09.2012', help = 'Download calendar from this date, format: dd.mm.yyyy (default: %(default)s)')
parser.add_argument('-w', action="store", dest='numWeeks',type=int, default=14, help = 'Number of weeks to download (default: %(default)s)')

args = parser.parse_args()
username = args.username
password = args.password
startDate = args.startDate
numWeeks = args.numWeeks

loginAndDownloadXML(username, password, startDate, numWeeks)
parseXML()
