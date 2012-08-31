# IS-Academia to ICS

###/!\ Deprecated. IS-Academia now has an Export to iCalendar button.

Fetch data from IS-Academia and convert it in .ics for importation in calendar.

## Usage:
DownloadCalendar.py -u USERNAME -p PASSWORD \[-d STARTDATE\] \[-w NUMWEEKS\]  

-u USERNAME	:	GASPAR username  
-p PASSWORD	:	GASPAR password  
-d STARTDATE :	Download calendar from this date, format: dd.mm.yyyy (default: 20.09.2012)  
-w NUMWEEKS	:	Number of weeks to download (default: 14)  

##Todo:

* Verify months abbreviations. 
* Issue with event ID's that are not unique / XML that says duration is 2 hours even if it's only 1.
