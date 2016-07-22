#!/usr/bin/python

import sqlite3 as sqlite
import argparse, sys
import datetime
import json
import fileinput
from subprocess import check_output, CalledProcessError

DATABASE = "/root/db/fbdaq.db"
WIFI_RESULT = check_output(["wifiState.sh"])
ENDPOINT = ""
DATABASE_TIMEOUT = 15

#   The order of incoming variables is as follows:
#       script name, deviceID, dateTime, temp0, temp1, 
#           temp2, temp3, waterVolume, project, ENDPOINT

#   Parsing, unpacking, and storing arguments of script into list
parser = argparse.ArgumentParser()
parser.add_argument('elemList', nargs='*')
args = parser.parse_args()
argList = args.elemList

#   API ENDPOINT
if not argList:
    print("NOTHING")
    sys.exit()
else:
    ENDPOINT = argList.pop()
   
#   Test ENDPOINT
#ENDPOINT = "https://dv8ecs8jrd.execute-api.us-east-1.amazonaws.com/prod/testlogger"

##  Function to create JSON object from data attributes in list or
##      Sqlite3 Row object.
##  INPUT: Can take either a list or a tuple
##  OUTPUT: JSON Object
def makeJsonObj(listOfArgs, sqlRowKeys=None):
    ROW_HEADERS = ['deviceID', 'dateTime', 'temp0', 'temp1', 'temp2', 
        'temp3', 'waterGal', 'project']

    assert not isinstance(listOfArgs, basestring)
    dataDict = {}

    if isinstance(listOfArgs, sqlite.Row):
        dataDict = dict(zip(sqlRowKeys, listOfArgs))
    else:
        dataDict = dict(zip(ROW_HEADERS, listOfArgs))
   
##  Scrubbing variables for proper data typing
    dataDict['dateTime'] = long(dataDict['dateTime'])
    dataDict['temp0'] = float(dataDict['temp0'])
    dataDict['temp1'] = float(dataDict['temp1'])
    dataDict['temp2'] = float(dataDict['temp2'])
    dataDict['temp3'] = float(dataDict['temp3'])
   
    jsonObj = json.dumps(dataDict, indent=4, separators=(',',': '))
    return jsonObj
    

##  Given a parsed list of arguments, constructs a JSON object
##      to send via a curl wrapper to AWS.
##  INPUT: List of arguments, which strictly abides to the order
##      stated above
##  OUTPUT: "\"ACTIVE\"" message is printed to STDOUT, which the
##      Atmega reads to be a successful request
def sendReceivedData(inputDataList):
    jsonObj = makeJsonObj(inputDataList)
    curlResult = curlCheckOutputErrorHandlerWrapper(jsonObj, ENDPOINT, False)
    print(curlResult)
    if ("STORING" in curlResult):
    	storeReceivedData(inputDataList)
    	sys.exit()

##  Implement error handling wrapper helper function for curl
##  INPUT: JSON object containing structure of required attributes, 
##      and a String of the HTTPS AWS API Gateway endpoint
##  OUTPUT: Returns either an "ACTIVE" or "STORING" string
def curlCheckOutputErrorHandlerWrapper(jsonObject, httpsEndpoint, batchSendBool):
    curlResult = "NOTHING"
    try:
    	curlResult = check_output(["curlh", jsonObject, ENDPOINT])
    except CalledProcessError:
    	curlResult = "STORING"
    	if batchSendBool:
    	    curlResult = "FAILED"
    return curlResult

##  Given a timeout, sends via curl each row in the table
##      to AWS.
##  INPUT: void
##  OUTPUT: void
def processDatabaseRecords():
    con = sqlite.connect(DATABASE) 
    con.row_factory = sqlite.Row
    con.text_factory = str
    cur = con.cursor()
    
##  Creating timeout feature for sending data out from database.
    startTime = datetime.datetime.now()
    timeDiff = (datetime.datetime.now() - startTime).total_seconds()
    while (timeDiff < DATABASE_TIMEOUT):
        cur.execute('''SELECT * FROM tempData ORDER BY dateTime ASC''')
        row = cur.fetchone()
        if (row is None):
            break

##      Provides the column name and record values, order is kept
##          such that position refers to the proper field name.
        tempJsonObj = makeJsonObj(row, row.keys())

        curlResult = curlCheckOutputErrorHandlerWrapper(tempJsonObj, ENDPOINT, True)
        
        if ("FAILED" in curlResult):
            sys.exit()
        
##      If the result from curl consists of the string "ACTIVE",
##          delete the row from the table. 
        if ("ACTIVE" in curlResult):
            cur.execute("DELETE FROM tempData WHERE dateTime=?;",(row['dateTime'],))
            con.commit()

        timeDiff = (datetime.datetime.now() - startTime).total_seconds()

##  Stores received data into the Sqlite3 database. 
##  INTPUT: List of arguments, which strictly abides to the order
##      stated above
##  OUTPUT: A string "STORING" sent to STDOUT for an Atmega update
def storeReceivedData(inputDataList):
##  If no connection or connection is suboptimal, store and try again later.
    con = sqlite.connect(DATABASE)
    cur = con.cursor()
    cur.execute('''INSERT INTO tempData (deviceID, dateTime, temp0, temp1, temp2, temp3, waterGal, project) VALUES(?,?,?,?,?,?,?,?)''',tuple(argList))
    con.commit()
    con.close()

##  Begin script ... 
if ("ok" in WIFI_RESULT):

##  Processing received data.
    sendReceivedData(argList)

##  Process any records within database
    processDatabaseRecords()

else:

##  Store received data
    storeReceivedData(argList)
