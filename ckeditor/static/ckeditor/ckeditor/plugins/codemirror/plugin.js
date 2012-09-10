/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.plugins.add('codemirror',{requires:['sourcearea'],init:function(a){var b=this.path,b=CKEDITOR.getUrl('plugins/codemirror');b=b.substr(0,b.indexOf('?'))+'/';CKEDITOR.scriptLoader.load(b+'js/codemirror.min.js');a.on('mode',function(){if(a.mode=='source'){var c=a.textarea,d=c.getParent(),e=d.$.clientHeight+'px',f=CodeMirror.fromTextArea(a.textarea.$,{stylesheet:b+'css/colors.css',path:b+'js/',mode:'htmlmixed',passDelay:300,passTime:35,continuousScanning:1000,undoDepth:1,height:a.config.height||e,textWrapping:false,lineNumbers:false,enterMode:'flat'});a.on('beforeCommandExec',function(g){g.removeListener();a.textarea.setValue(f.getCode());a.fire('dataReady');});CKEDITOR.plugins.mirrorSnapshotCmd={exec:function(g){if(g.mode=='source'){g.textarea.setValue(f.getCode());g.fire('dataReady');}}};a.addCommand('mirrorSnapshot',CKEDITOR.plugins.mirrorSnapshotCmd);}});a.on('instanceReady',function(c){c.removeListener();if(a.mode=='wysiwyg'){var d=a.getData().indexOf('<?php');if(d!==-1)a.execCommand('source');}});}});
