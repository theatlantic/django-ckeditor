/**
 * @fileOverview The "codemirror" plugin. It's indented to enhance the
 *  "sourcearea" editing mode, which displays the xhtml source code with
 *  syntax highlight and line numbers.
 * @see http://marijn.haverbeke.nl/codemirror/ for CodeMirror editor which this
 *  plugin is using.
 */

CKEDITOR.plugins.add('codemirror', {
    requires: ['sourcearea'],
    /**
     * This's a command-less plugin, auto loaded as soon as switch to 'source' mode
     * and 'textarea' plugin is activeated.
     * @param {Object} editor
     */

    init: function(editor) {
        var thisPath = this.path;
        var thisPath = [
			'_source/', // @Packager.RemoveLine
			'plugins/codemirror'
		].join('');
		var thisUrl = CKEDITOR.getUrl(thisPath);
		if (thisUrl.indexOf('?') > 0) {
		    thisUrl = thisUrl.substr(0, thisUrl.indexOf('?'));
		}
        CKEDITOR.scriptLoader.load( CKEDITOR.getUrl(thisPath + '/js/codemirror.min.js'));
        var cssFile = CKEDITOR.getUrl(thisPath + '/css/colors.css');
        editor.element.getDocument().appendStyleSheet(cssFile);
        editor.on('mode', function() {
            if (editor.mode == 'source') {
                var sourceAreaElement = editor.textarea,
                    holderElement = sourceAreaElement.getParent();
                var holderHeight = holderElement.$.clientHeight + 'px';
                /* http://codemirror.net/manual.html */
                var codemirrorInit = CodeMirror.fromTextArea(
                editor.textarea.$, {
                    stylesheet: cssFile,
                    path: thisUrl + '/js/',
                    mode: 'htmlmixed',
                    passDelay: 300,
                    passTime: 35,
                    continuousScanning: 1000,
                    theme: "mac-classic",
                    indentUnit: 4,
                    indentWithTabs: true,
                    /* Numbers lower than this suck megabytes of memory very quickly out of firefox */
                    undoDepth: 1,
                    height: editor.config.height || holderHeight,
                    /* Adapt to holder height */
                    textWrapping: false,
                    lineNumbers: false,
                    enterMode: 'flat',
                    wordWrap: true,
                    extraKeys: {
        				"'>'": function(cm) { cm.closeTag(cm, '>'); },
        				"'/'": function(cm) { cm.closeTag(cm, '/'); }
        			}
                });
                // Commit source data back into 'source' mode.
                editor.on('beforeCommandExec', function(e) {
                    // Listen to this event once.
                    e.removeListener();
                    editor.textarea.setValue(codemirrorInit.getValue());
                    editor.fire('dataReady');

/*editor._.modes[ editor.mode ].loadData(
                                    codemirror.getCode() );*/
                });

                CKEDITOR.plugins.mirrorSnapshotCmd = {
                    exec: function(editor) {
                        if (editor.mode == 'source') {
                            editor.textarea.setValue(codemirrorInit.getValue());
                            editor.fire('dataReady');
                        }
                    }
                };
                editor.addCommand('mirrorSnapshot', CKEDITOR.plugins.mirrorSnapshotCmd); /* editor.execCommand('mirrorSnapshot'); */
            }
        });
        editor.on('instanceReady', function(e) {
            e.removeListener();
            if (editor.mode == 'wysiwyg') {
                var thisData = editor.getData().indexOf('<?php');
                if (thisData !== -1) {
                    editor.execCommand('source');
                }
            }
        });
    }

});
