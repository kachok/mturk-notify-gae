import fix_path

from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.api.taskqueue import *

from google.appengine.ext.webapp.util import run_wsgi_app

from boto.mturk.notification import * 

import logging
import datetime

import json

import boto
import settings

from boto.mturk.connection import MTurkConnection

class MTurkAssignmentHandler(webapp.RequestHandler):
  def post(self):

	payload=self.request.get("payload")
			
	logging.debug('payload = ' + str(payload))
	
	self.response.headers['Content-Type'] = 'text/plain'
	self.response.out.write(str(payload))
	
	queue=Queue(name="monotranssubmit")

	conn=MTurkConnection(aws_access_key_id=settings.settings["aws_access_key_id"],
		                      aws_secret_access_key=settings.settings["aws_secret_access_key"],
		                      host=settings.settings["service_url"].replace("https://",""))
		
	payload=json.loads(payload)
	
	assignments=conn.get_assignments(hit_id=payload["HITId"])

	for assgnmnt in assignments:

		logging.debug('assgnmnt = ' + str(assgnmnt))
		
		#print assgnmnt
		mturk_worker_id=assgnmnt.WorkerId
		mturk_assignment_id=assgnmnt.AssignmentId
		submit_time=assgnmnt.SubmitTime
		accept_time=assgnmnt.AcceptTime
		#autoapproval_time=assgnmnt.AutoApprovalTime
		#mturk_status=assgnmnt.AssignmentStatus
		#approval_time=None
		#rejection_time=None
		
		utc = datetime.datetime.strptime(submit_time, '%Y-%m-%dT%H:%M:%SZ')
		submit_time=utc

		utc = datetime.datetime.strptime(accept_time, '%Y-%m-%dT%H:%M:%SZ')
		accept_time=utc

		
		
		print mturk_worker_id
		print accept_time, submit_time, submit_time-accept_time
		
		results={}
		for i in assgnmnt.answers[0]:
			#print i
			results[i.qid]=i.fields[0]
			pass

		result=json.dumps(results)
		logging.debug('result = ' + str(result))
		
		
		if "data" in results:
			#print results["data"]
			data=json.loads(results["data"])

		try:
			conn.approve_assignment(mturk_assignment_id, "Thank you for working on my HITs, have a good day!")

			#TODO: submit data to Monotrans queue
			task=Task(url='/monotranssubmit', params={"payload":result})
			queue.add(task)
		except:
			#print "already approved"

			#TODO: remove next two lines - this is just for DEBUG
			task=Task(url='/monotranssubmit', params={"payload":result})
			queue.add(task)

			pass

		


application = webapp.WSGIApplication([
                                      ('/mturkassignments', MTurkAssignmentHandler),
                                      ], debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
