SHELL = /bin/bash

this_dir       := '$(shell pwd)'
python_version := 3.4
python         := $(this_dir)/python/bin/python$(python_version)
easy_install   := $(python) $(this_dir)/python/bin/easy_install-$(python_version)
pip            := $(python) $(this_dir)/python/bin/pip$(python_version)
setuptools     := https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
site_packages  := $(this_dir)/python/lib/python$(python_version)/site-packages
tap            := mkdir -p .make; touch

export PIP_DOWNLOAD_CACHE = .cache

python: .make/dependencies requirements.txt
	- pyvenv-$(python_version) python
	mkdir -p python/local
	- ln -s ../bin python/local/bin
	rm -f $(site_packages)/setuptools*.{egg,pth} # setuptools bug
	cd /tmp; curl -C - '-#' $(setuptools) | $(python)
	$(easy_install) pip
	$(pip) install -r requirements.txt

.make/dependencies:
	# Python $(python_version)
	python$(python_version) -h >/dev/null
	$(tap) $@
