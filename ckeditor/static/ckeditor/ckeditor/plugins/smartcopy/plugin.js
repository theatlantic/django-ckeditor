/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

(function(a){var b={allowedCopyTags:['A','ABBR','ACRONYM','BLOCKQUOTE','BR','DIV','HR','I','IFRAME','IMG','LI','OL','P','Q','S','STRIKE','SUB','SUP','TABLE','TR','TD','TH','UL'],removeAttrs:[]};CKEDITOR.plugins.add('smartcopy',{init:function(c){var d,e;if(c.config.smartCopyAllowedTags!==undefined)d=c.config.smartCopyAllowedTags.map(function(g){return g.toUpperCase();});else d=b.allowedCopyTags;if(c.config.smartCopyRemoveAttrs!==undefined)e=c.config.smartCopyRemoveAttrs;else e=b.smartCopyRemoveAttrs;var f=false;if(e&&a.inArray('style',e))f=true;c.on('paste',function(g){var h=g.data.html;g.stop();var i=document.createElement('div');i.innerHTML=h;window.$wrapper=a(i);$wrapper.find('*').each(function(j,k){$el=a(k);if(k.nodeType===Node.ELEMENT_NODE&&a.inArray(k.nodeName,d)===-1){if(k.innerHTML)$el.contents().unwrap();else k.parentNode.removeChild(k);}else if(e)for(var j in e)$el.removeAttr(e[j]);});g.editor.insertHtml($wrapper.html());});}});})(django.jQuery);
