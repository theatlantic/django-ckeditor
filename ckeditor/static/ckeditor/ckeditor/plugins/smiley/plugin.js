/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.plugins.add('smiley',{requires:['dialog'],init:function(a){a.config.smiley_path=a.config.smiley_path||this.path+'images/';a.addCommand('smiley',new CKEDITOR.dialogCommand('smiley'));a.ui.addButton('Smiley',{label:a.lang.smiley.toolbar,command:'smiley'});CKEDITOR.dialog.add('smiley',this.path+'dialogs/smiley.js');}});CKEDITOR.config.smiley_images=['smiley.png','sad.png','wink.png','teeth.png','grin.png','tongue.png','surprised.png','evilgrin.png','waii.png','lightbulb.png','thumbs_up.png','thumbs_down.png','heart.png','envelope.png'];CKEDITOR.config.smiley_descriptions=['smiley','sad','wink','teeth','grin','cheeky','surprise','evil','waii','lightbulb','thumbs up','thumbs down','heart','mail'];
