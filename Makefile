all: test

test:
	nosetests -a '!client,!facade'
	nosetests -a 'client'
	nosetests -a 'facade=httplib'
