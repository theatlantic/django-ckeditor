(function($){

	var defaults = {
		allowedCopyTags: ['A', 'ABBR', 'ACRONYM', 'BLOCKQUOTE', 'BR', 'DIV', 'HR', 'I', 'IFRAME', 'IMG', 
			'LI', 'OL', 'P', 'Q', 'S', 'STRIKE', 'SUB', 'SUP', 'TABLE', 'TR', 'TD', 'TH', 'UL'],
		removeAttrs: []
	}

	CKEDITOR.plugins.add('smartcopy',
	{
	    init: function(editor)
	    {
	    	// Determine what tags and attributes are allowed 
	    	var allowedCopyTags, removeAttrs;
	    	if ( editor.config.smartCopyAllowedTags !== undefined ) {
	    		allowedCopyTags = editor.config.smartCopyAllowedTags.map(function(x) { 
	    			return x.toUpperCase(); 
	    		});
	    	} else {
	    		allowedCopyTags = defaults.allowedCopyTags;
	    	}
	    	if (editor.config.smartCopyRemoveAttrs !== undefined) {
	    		removeAttrs = editor.config.smartCopyRemoveAttrs;
	    	} else {
	    		removeAttrs = defaults.smartCopyRemoveAttrs;
	    	}

	    	var removeStyles = false;
	    	if (removeAttrs && $.inArray('style', removeAttrs)) {
	    		removeStyles = true;
	    	}

			editor.on('paste', function (evt) {
				var copiedHtml = evt.data.html;
			    evt.stop(); // we don't let editor to paste data, only for current event

			    // 
			    var wrapper = document.createElement('div');
				wrapper.innerHTML = copiedHtml;
				window.$wrapper = $(wrapper);

				// Remove disallowed tags
				$wrapper.find('*').each(function(i, el) {
					$el = $(el);
					// Is the current element in our list of allowed tags
					 if (el.nodeType === Node.ELEMENT_NODE && $.inArray(el.nodeName, allowedCopyTags) === -1) {
					 	if (el.innerHTML) {
					 		// If the node contains text, remove its surrounding tag
					 		$el.contents().unwrap(); 
					 	} else {
					 		// If the node doesn't contain text, remove it
					 		el.parentNode.removeChild(el);
					 	}
					 } else {

					 	// Remove any disallowed attributes
					 	if (removeAttrs) {
						 	for (var i in removeAttrs) {
						 		$el.removeAttr(removeAttrs[i]);
						 	}
						 }

					 	// // If we aren't removing all styles, then remove font styles
					 	// if (!removeStyles && el.style !== undefined) {
					 	// 	el.style.removeProperty('font');
					 	// 	el.style.removeProperty('color');
					 	// }
					 }
				});

			    // insert the data to paste it
			    evt.editor.insertHtml($wrapper.html());
			});
	    },
	});
})(django.jQuery);