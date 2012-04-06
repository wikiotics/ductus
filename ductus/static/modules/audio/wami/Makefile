# Makefile to build Wami-recorder

# path the to mxmlc flex compiler (version 4.6 works, previous versions don't)
MXMLC		= /usr/local/flex_sdk4.6/bin/mxmlc
# swf file to save to
SWF_FILE	= Wami.swf
DUCTUS_ROOT	= 
INSTALL_PATH 	= $(DUCTUS_ROOT)/ductus/static/modules/audio/

all:
	$(MXMLC) -compiler.source-path=src -static-link-runtime-shared-libraries=true -output $(SWF_FILE) src/edu/mit/csail/wami/client/Wami.mxml

install:
	cp $(SWF_FILE) $(INSTALL_PATH)

test:
	echo $(INSTALL_PATH)
