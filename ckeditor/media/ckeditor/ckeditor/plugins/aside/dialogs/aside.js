( function(){
	
	var exampleDialog = function(editor){
		return {
			title : "Aside,
			minWidth : /*number of pixels*/,
			minHeight : /*number of pixels*/,
			buttons: /*array of button definitions*/,
			onOk: /*function*/ ,
			onLoad: /*function*/,
			onShow: /*function*/,
			onHide: /*function*/,
			onCancel: /*function*/,
			resizable: /* none,width,height or both  */,
			contents: /*content definition, basically the UI of the dialog*/
		}
	}
	
	CKEDITOR.dialog.add('insertHTML', function(editor) {
		return exampleDialog(editor);
	});
		
})();