PROJECT     := $(notdir ${PWD})
FONT_NAME   := websymbols


################################################################################
## ! DO NOT EDIT BELOW THIS LINE, UNLESS YOU REALLY KNOW WHAT ARE YOU DOING ! ##
################################################################################


TMP_PATH    := /tmp/${PROJECT}-$(shell date +%s)
REMOTE_NAME ?= origin
REMOTE_REPO ?= $(shell git config --get remote.${REMOTE_NAME}.url)


# Add local versions of ttf2eot nd ttfautohint to the PATH
#PATH := $(PATH):./support/font-builder/support/ttf2eot
#PATH := $(PATH):./support/font-builder/support/ttfautohint/frontend
#PATH := $(PATH):./support/font-builder/bin
PWD  := $(shell pwd)
BIN  := ./node_modules/.bin


dist: font html

dump:
	rm -r ./src/svg/
	mkdir ./src/svg/
	#font-dump.js --hcrop --vcenter -c config.yml -f -i ./src/original/websymbols-fixed.svg -o ./src/svg/ -d diff.yml
	${BIN}/svg-font-dump -c `pwd`/config.yml -f -i ./src/original/websymbols-fixed.svg -o ./src/svg/ -d diff.yml
	${BIN}/svgo --config `pwd`/dump.svgo.yml -f ./src/svg


font:
	@if test ! `which ttfautohint` ; then \
		echo "ttfautohint not found. run:" >&2 ; \
		echo "  make support" >&2 ; \
		exit 128 ; \
		fi

	${BIN}/svg-font-create -c config.yml -i ./src/svg -o "./font/$(FONT_NAME).svg"
	fontforge -c 'font = fontforge.open("./font/$(FONT_NAME).svg"); font.generate("./font/$(FONT_NAME).ttf")'
	#fontbuild.py -c ./config.yml -t ./src/font_template.sfd -i ./src/svg -o ./font/$(FONT_NAME).ttf
	#font_remap.py -c ./config.yml -i ./src/original/websymbols-regular-webfont.ttf -o ./font/$(FONT_NAME).ttf
	#font_transform.py -c ./config.yml -i ./font/$(FONT_NAME).ttf -o ./font/$(FONT_NAME)-transformed.ttf
	#mv ./font/$(FONT_NAME)-transformed.ttf ./font/$(FONT_NAME).ttf
	ttfautohint --latin-fallback --hinting-limit=200 --hinting-range-max=50 --symbol ./font/$(FONT_NAME).ttf ./font/$(FONT_NAME)-hinted.ttf
	mv ./font/$(FONT_NAME)-hinted.ttf ./font/$(FONT_NAME).ttf
	#fontconvert.py -i ./font/$(FONT_NAME).ttf -o ./font
	${BIN}/ttf2eot "./font/$(FONT_NAME).ttf" "./font/$(FONT_NAME).eot"
	${BIN}/ttf2woff "./font/$(FONT_NAME).ttf" "./font/$(FONT_NAME).woff"


npm-deps:
	@if test ! `which npm` ; then \
		echo "Node.JS and NPM are required for html demo generation." >&2 ; \
		echo "This is non-fatal error and you'll still be able to build font," >&2 ; \
		echo "however, to build demo with >> make html << you need:" >&2 ; \
		echo "  - Install Node.JS and NPM" >&2 ; \
		echo "  - Run this task once again" >&2 ; \
		else \
		npm install -g jade js-yaml.bin ; \
		fi


support:
	git submodule init support/font-builder
	git submodule update support/font-builder
	which ttf2eot ttfautohint > /dev/null || (cd support/font-builder && $(MAKE))
	which js-yaml jade > /dev/null || $(MAKE) npm-deps


html:
	@${BIN}/jade -O '$(shell node_modules/.bin/js-yaml -j config.yml)' ./src/demo/demo.jade -o ./font

gh-pages:
	@if test -z ${REMOTE_REPO} ; then \
		echo 'Remote repo URL not found' >&2 ; \
		exit 128 ; \
		fi
	cp -r ./font ${TMP_PATH} && \
		touch ${TMP_PATH}/.nojekyll
	cd ${TMP_PATH} && \
		git init && \
		git add . && \
		git commit -q -m 'refreshed gh-pages'
	cd ${TMP_PATH} && \
		git remote add remote ${REMOTE_REPO} && \
		git push --force remote +master:gh-pages 
	rm -rf ${TMP_PATH}


dev-deps:
	@if test 0 -ne `id -u` ; then \
		echo "root priveledges are required" >&2 ; \
		exit 128 ; \
		fi
	apt-get -qq install \
		fontforge python python-fontforge libfreetype6-dev \
		python-yaml python-pip \
		build-essential \
		autoconf automake libtool
	pip -q install pystache argparse


clean:
	git clean -f -x


.SILENT: dev-deps
.PHONY: font support
