"""
py 3.9
To add a set of course IDs to the automatic archive list
this script makes a simple call to the content API for a csv list of course IDs.
The result is an entry in the course_registry table for that course PK1.

  registry_key = last access by un-enrolled admin
  registry_value = 2021-06-21 11:37:27.448

developed by jeff.kelley@blackboard.com  June 2021

BLACKBOARD MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE, OR NON-INFRINGEMENT. BLACKBOARD SHALL NOT BE LIABLE FOR ANY
DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR
DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

logic..
Authenticate to get token
Itterate through the list of cousres:
 - Call the content API

TODO:

"""

import requests
import json
import datetime
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import sys
import csv
import argparse
import configparser


#########
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logfile.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

#### 
#parse and ready the arguments from the command line 
parser = argparse.ArgumentParser(description='Properties, Input file and Output file')
parser.add_argument("PROPERTIES_FILE", help="The properties file")
parser.add_argument("INPUT_FILE", help="List of Learn Course IDs")

args = parser.parse_args()
propFile = args.PROPERTIES_FILE
inFile = args.INPUT_FILE

# read the properties file into "config" container
config = configparser.ConfigParser()
config.read(propFile)

# setting and validating variables from properties file
KEY = config.get('properties', 'KEY')
SECRET = config.get('properties', 'SECRET')
MYHOST = 'https://' + config.get('properties', 'HOST')
RESULTLIMIT = config.get('properties', 'RESULTLIMIT')

#########################
class doAuthenticate:
  #reads the constants HOST, KEY, SECRET to get token and related attributes
  def __init__(self):
    
    AUTHDATA = {
      'grant_type': 'client_credentials'
    }

    r = requests.post(MYHOST + '/learn/api/public/v1/oauth2/token', data=AUTHDATA, auth=(KEY, SECRET))
    if r.status_code == 200:  #success
      parsed_json = json.loads(r.text)  #read the response into dictionary
      self.token = parsed_json['access_token'] 
      self.expiresIn = parsed_json['expires_in']
      m, s = divmod(self.expiresIn, 60)  #convert token lifespan into m minutes and s seconds
      self.expiresAt = datetime.datetime.now() + datetime.timedelta(seconds = s, minutes = m) 
      self.authStr = 'Bearer ' + self.token
      print('[' + str(datetime.datetime.now()) + ']|Token ' + self.token + ' Expires in ' + str(m) + ' minutes and '+ str(s) + ' seconds. (' + str(self.expiresAt) + ')' )
    else:  #failed to authenticate
      print ('Failed to authenticate: ' + r)
      sys.exit()

##################
class nearlyExpired:
  #pauses and reauthenticates if expriation within x seconds
  def __init__(self,sessionExpireTime):
      bufferSeconds = 120
      self.expired = False
      self.time_left = (sessionExpireTime - datetime.datetime.now()).total_seconds()
      #self.time_left = 30  #use for testing
      if self.time_left < bufferSeconds:
            print ('[' + str(datetime.datetime.now()) + ']|PLEASE WAIT  Token almost expired retrieving new token in ' + str(bufferSeconds) + 'seconds.')
            time.sleep(bufferSeconds + 1)
            self.expired = True


#########################
class callContentsApi:
  #input a course_id
  def __init__(self, course_Id):
    self.thisId = course_Id
    #print ('Get request for content API for ' + self.thisId)
    ROOTCOURSEURL = MYHOST + '/learn/api/public/v1/courses/courseId:' + self.thisId
    GETCONTENT = ROOTCOURSEURL + '/contents?limit=' + str(RESULTLIMIT)
    getContents = requests.get(GETCONTENT, headers={'Authorization':thisAuth.authStr})
    if getContents.status_code != 200:
      print ('Error getting contents for course: ' + self.thisId)
      print ('Status: ' + str(getContents.status_code))
    else:
      print ('Success reading contents for : ' + self.thisId)


#################################
## START THE SCRIPT ###

sys.stdout = Logger()
batchStart = datetime.datetime.now()
batchId = batchStart.strftime("%Y%m%d-%H%M")
print ('[' + str(batchStart) + ']|Starting Batch ID = ' + batchId)

thisAuth = doAuthenticate()


#file readiness
inputFile = open(inFile)



## itterate over the ids in the input file
for line in inputFile:
    if nearlyExpired(thisAuth.expiresAt).expired:
        thisAuth = doAuthenticate()
    
    thisId = line.rstrip()
    #print ('[' + str(datetime.datetime.now()) + ']|'+ thisId + '|Start this course')

    callContentsApi(thisId)

# lets close up shop
inputFile.close()
print ('[' + str(datetime.datetime.now()) + ']|Closing batch ')
