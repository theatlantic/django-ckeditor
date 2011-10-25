( function(){
	
	var exampleDialog = function(editor){
		return {
			"title" : "Aside",
			"minWidth" : 500,
			"minHeight" : 500,
			"buttons" : [ CKEDITOR.dialog.okButton, CKEDITOR.dialog.cancelButton ],
			"onOk": function() {
					var textareaObj = this.getContentElement( 'tab1', 'textareaId' );
					alert( "You have entered: " + textareaObj.getValue() );
			},

			"contents": [
				{
					id : 'tab1',
					label : 'Label',
					title : 'Title',
					expand : true,
					padding : 0,
					elements :
					[
						{
							type : 'html',
							html : '<p>This is some sample HTML content.</p>'
						},
						{
							type : 'textarea',
							id : 'textareaId',
							rows : 4,
							cols : 40
						}
					]
				}
			]
					
		}
	}
	
	CKEDITOR.dialog.add('insertHTML', function(editor) {
		return exampleDialog(editor);
	});
		
})();