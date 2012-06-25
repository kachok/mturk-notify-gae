import fix_path

from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.api.taskqueue import *

from google.appengine.ext.webapp.util import run_wsgi_app

import logging
import datetime

import json

import settings


import urllib
from google.appengine.api import urlfetch

class MonotransSubmitHandler(webapp.RequestHandler):
  def post(self):

	payload=self.request.get("payload")
			
	logging.debug('payload = ' + str(payload))
	
	self.response.headers['Content-Type'] = 'text/plain'
	self.response.out.write(str(payload))
	
	payload=json.loads(payload)

	logging.debug('payload = ' + str(payload))

	data=json.loads(payload["data"])

	logging.debug('data = ' + str(data))
	
	baseurl=settings.settings["monotrans_url"]
	
	
	for i in range(1,6):

		res2=data["page_"+str(i)]["smth"]

	
		res2=res2.encode('utf-8')
		logging.debug('res2 = ' + str(res2))

		#res2 = urllib.quote_plus(res2)
	
		endpoint=data["page_"+str(i)]["method"]

		logging.debug('endpoint = ' + str(endpoint))
		url=baseurl+endpoint
	
		"""
		headers={'Content-Type': 'application/json; charset=utf-8'}
		headers = dict((k.encode('ascii') if isinstance(k, unicode) else k,
		                     v.encode('ascii') if isinstance(v, unicode) else v)
		                    for k,v in headers.items())
		url=url.encode('ascii')
		req = urllib2.Request(url, res2, headers)
		ff = urllib2.urlopen(req)
		response = ff.read()

		logging.debug('response = ' + str(response))

		ff.close()	
		"""

		url=url.encode('ascii')
		headers={'Content-Type': 'application/json; charset=utf-8'}
		headers = dict((k.encode('ascii') if isinstance(k, unicode) else k,
		                     v.encode('ascii') if isinstance(v, unicode) else v)
		                    for k,v in headers.items())
		
		result = urlfetch.fetch(url=url,
		                        payload=res2,
		                        method=urlfetch.POST,
		                        headers=headers, deadline=59)


application = webapp.WSGIApplication([
                                      ('/monotranssubmit', MonotransSubmitHandler),
                                      ], debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
