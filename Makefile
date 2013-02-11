all: test

test:
	nosetests -a '!client,!facade'
	nosetests -a 'client'
	nosetests -a 'facade=httplib'
	WEBRACER_HTTP_CLIENT=pycurl nosetests -a 'client'
