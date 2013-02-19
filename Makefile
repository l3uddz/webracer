# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

all: test

test:
	nosetests -a '!client,!facade'
	nosetests -a 'client'
	nosetests -a 'facade=httplib'
	WEBRACER_HTTP_CLIENT=pycurl nosetests -a 'client'

clean:
	-rm -rf $(BUILDDIR)/* ./**/*.pyc

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# XXX this does not report undocumented class methods
doccov:
	$(SPHINXBUILD) -b coverage $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Coverage report is in $(BUILDDIR)/python.txt."
