# this is endpoint for MTurk Notification API (will receive notes from MTurk when tasks are submitted)
# and will fetch data from MTurk and submit it into Monotrans queue
import fix_path

from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.api.taskqueue import *

from google.appengine.ext.webapp.util import run_wsgi_app

from boto.mturk.notification import * 

import logging

import json

import boto
import settings

class Handler(webapp.RequestHandler):
  def get(self):
	"""
	GET /mt/notifications.cgi?method=Notify
	  &Signature=vH6ZbE0NhkF/hfNyxz2OgmzXYKs=
	  &Timestamp=2006-05-23T23:22:30Z
	  &Version=2006-05-05
	  &Event.1.EventType=AssignmentAccepted
	  &Event.1.EventTime=2006-04-21T18:55:23Z
	  &Event.1.HITTypeId=KDSFO4455LKDAF3
	  &Event.1.HITId=KDSFO4455LKDAF3
	  &Event.1.AssignmentId=KDSFO4455LKDAF3KDSFO4455LKDAF3
	  &Event.2.EventType=AssignmentReturned
	  &Event.2.EventTime=2006-04-21T18:55:23Z
	  &Event.2.HITTypeId=KDSFO4455LKDAF3
	  &Event.2.HITId=KDSFO4455LKDAF3KDSFO4455LKDAF3
	  &Event.2.AssignmentId=KDSFO4455LKDAF3KDSFO4455LKDAF3 HTTP/1.1
	Content-Type: text/xml
	Accept: application/soap+xml, application/dime, multipart/related, text/*
	SOAPAction: http://soap.amazon.com
	User-Agent: Jakarta Commons-HttpClient/2.0final
	Host: example.com:80	
	"""

	d={}
	
	args=self.request.arguments()
	for arg in args:
		d[arg]=self.request.get(arg,"")
			
	nm = boto.mturk.notification.NotificationMessage(d) 
	verifies=nm.verify(settings.settings["aws_secret_access_key"]) 

	#nm.events - array of Events
	
	self.response.headers['Content-Type'] = 'text/plain'
	self.response.out.write(str(verifies))
	
	queue=Queue(name="mturkassignments")
	for ev in nm.events:
		#TODO: add them to Queue/create Tasks
		data={}
		
		data['EventType']=ev.event_type
		data['EventTime']=ev.event_time_str
		data['HITTypeId']=ev.hit_type
		data['HITId']=ev.hit_id
		try:
			data['AssignmentId']=ev.assignment_id
		except:
			pass
		
		data=json.dumps(data)
		logging.debug('event = ' + str(data))
		
		task=Task(url='/mturkassignments', params={"payload":data})
		queue.add(task)

		self.response.out.write(str(data))
		


application = webapp.WSGIApplication([
                                      ('/handler', Handler),
                                      ], debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
