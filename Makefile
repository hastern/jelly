# creation makefile
# author: Hanno Sternberg
# 

NAME 	= jelly

PY	=python
SETUP	=$(PY) setup.py
DOC	=epydoc

SRC_EGG	=$(shell $(SETUP) --fullname)-py2.7.egg

.PHONY: build egg dist clean doc license description info run

default: all

all: build dist egg

build:
	$(SETUP) build

egg: 
	$(SETUP) bdist_egg
	
dist:
	$(SETUP) sdist

run:
	@$(PY) -m custard
	
doc:
	$(DOC) --config=epydocfile
	
license:
	@$(SETUP) --license
	
description:
	@$(SETUP) --long-description
	
info: license description
	
clean:
	$(SETUP) clean
	rm -rf build dist $(NAME).egg-info doc
	
	


