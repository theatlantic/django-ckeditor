#!/usr/bin/env bash

# Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
# For licensing, see LICENSE.html or http://ckeditor.com/license

function abspath {
    if [[ -d "$1" ]]
    then
        pushd "$1" >/dev/null
        pwd -P
	popd >/dev/null
    elif [[ -e $1 ]]
    then
        pushd $(dirname $1) >/dev/null
        echo $(pwd -P)/$(basename $1) | perl -pne 's/\/\//\//g;'
        popd >/dev/null
    else
        echo $1 does not exist! >&2
        return 127
    fi
}

VERSION="3.6.3"

DIR=$(abspath $(dirname $0))

LANGTOOL="$DIR/langtool.sh"

pushd $DIR

if [ -d "release" ]; then
    if [ ! -d "releases" ]; then
        mkdir "releases"
    fi
    MOD_TIME=$(perl -MFile::stat -e 'use POSIX qw(strftime); print strftime("%Y-%m-%d_%H%M", localtime stat("release")->mtime);')
    mv release "releases/release-${VERSION}_${MOD_TIME}"
fi

CURRENT_VERSION=$($DIR/current_version.pl)

java -jar ckreleaser/ckreleaser.jar ckreleaser.release ../.. release "${VERSION}" "ckeditor_${VERSION}" --run-before-release=$LANGTOOL
popd

if [ -d "$DIR/release/release" ]; then

  pushd "$DIR/release/release"
  OUTDIR=$(abspath "$DIR/../../")

  # Remove BOM and CRLF
  find . -name 'ckeditor*.js' -depth 1 | xargs -I{} perl -pi -e 's/^\xEF\xBB\xBF//;' "{}"
  find . -name '*.css' | xargs -I{} perl -pi -e 's/^\xEF\xBB\xBF//;' "{}"
  find . -name '*ckeditor*.js' -depth 1 | xargs -I{} ~/bin/fixjsunicode "{}"
  find -E "plugins/a11yhelp/lang"    -type f -not -regex '.*\/(en|he)\.js' -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/devtools/lang"    -type f -not -regex '.*\/(en)\.js'    -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/placeholder/lang" -type f -not -regex '.*\/(en|he)\.js' -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/specialchar/lang" -type f -not -regex '.*\/(en)\.js'    -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/uicolor/lang"     -type f -not -regex '.*\/(en|he)\.js' -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/atlanticpagebreak"     -type f -regex '.*\.js'          -print0 | xargs -0 -I{} perl -pi -e 's/\r\n/\n/;' "{}"
  find -E "plugins/codemirror"       -type f -regex '.*\.js'               -print0 | xargs -0 -I{} perl -pi -e 's/^\xEF\xBB\xBF//;' "{}"

  find "plugins/atlanticpagebreak" -type f -name 'plugin.js'               -print0 | xargs -0 -I{} $DIR/remove_copyright.pl "{}"

  perl -pi -e 's/(Copyright \(c\) 2003\-201)2/${1}1/g;' skins/django/dialog.css skins/django/skin.js skins/django/templates.css
  perl -pi -e 's/(Copyright \(c\) 2003\-201)3/${1}2/g;' lang/_translationstatus.txt
  perl -pi -e 's/^\xEF\xBB\xBF//g;' plugins/specialchar/lang/en.js lang/mk.js lang/ug.js
  perl -pi -e 's/\r\n/\n/g;' lang/mk.js lang/ug.js
  perl -pi -e 's/^\xEF\xBB\xBF//g;' plugins/smiley/plugin.js plugins/specialchar/lang/en.js skins/bootstrap/skin.js

  perl -pi -e "s/(timestamp\s?:\s?)'[A-Z0-9]{4}'/\$1'${CURRENT_VERSION}'/g;" ckeditor.js ckeditor_basic.js _source/core/ckeditor_base.js
  perl -pi -e "s/TIMESTAMP = '[A-Z0-9]{4}'/TIMESTAMP = '${CURRENT_VERSION}'/g;" $OUTDIR/../../../settings.py

  cp $OUTDIR/plugins/aside/plugin.js plugins/aside/plugin.js

  cp -R "plugins/" $OUTDIR/plugins
  cp -R "lang/" $OUTDIR/lang
  cp -R "skins/" $OUTDIR/skins
  cp -R "themes/" $OUTDIR/themes
  cp -R "images/" $OUTDIR/images
  cp -R "adapters/" $OUTDIR/adapters
  cp ckeditor*.js $OUTDIR

  popd

fi
