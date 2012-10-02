(function($) {

/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @file Horizontal Page Break
 */

// Register a plugin named "pagebreak".
CKEDITOR.plugins.add( 'atlanticpagebreak',
{
	init : function( editor )
	{
		// Register the command.
		editor.addCommand( 'atlanticpagebreak', CKEDITOR.plugins.pagebreakCmd );

		// Register the toolbar button.
		editor.ui.addButton( 'AtlanticPageBreak',
			{
				label : 'Insert pagebreak',
				command : 'atlanticpagebreak',
				icon: this.path + 'images/pagebreak.gif'
			});

		// Opera needs help to select the page-break.
		CKEDITOR.env.opera && editor.on( 'contentDom', function()
		{
			editor.document.on( 'click', function( evt )
			{
				var target = evt.data.getTarget();
				if ( target.is( 'div' ) && target.hasClass( 'pagebreak')  )
					editor.getSelection().selectElement( target );
			});
		});
	},

	afterInit : function( editor )
	{
		var label = editor.lang.pagebreakAlt;

		// Register a filter to displaying placeholders after mode change.
		var dataProcessor = editor.dataProcessor,
			dataFilter = dataProcessor && dataProcessor.dataFilter,
			htmlFilter = dataProcessor && dataProcessor.htmlFilter;

		if ( htmlFilter )
		{
			htmlFilter.addRules(
			{
				attributes : {
					'class' : function( value, element )
					{
						if ( value == 'pagebreak' ) {
							var span = CKEDITOR.htmlParser.fragment.fromHtml( '&nbsp;' );
							element.children.length = 0;
							element.add( span );
							var attrs = element.attributes;
							delete attrs[ 'aria-label' ];
							delete attrs.contenteditable;
							delete attrs.title;
							delete attrs.style;

							return value;
						}
					}
				}
			}, 5 );
		}

		if ( dataFilter )
		{
			dataFilter.addRules(
				{
					elements :
					{
						div : function( element )
						{
							var attributes = element.attributes;

							if ( attributes.class == 'pagebreak' )
							{
								attributes.contenteditable = "false";
								attributes[ 'data-cke-display-name' ] = "pagebreak";
								attributes[ 'aria-label' ] = label;
								attributes[ 'title' ] = label;
								attributes[ 'style' ] = "clear:both;border-top:dotted 1px #D8D8D8;border-bottom:dotted 1px #D8D8D8;";

								element.children.length = 0;
							}
						}
					}
				});
		}
	},

	requires : [ 'fakeobjects' ]
});

CKEDITOR.plugins.pagebreakCmd =
{
	exec : function( editor )
	{
		var label = editor.lang.pagebreakAlt;

		// Create read-only element that represents a print break.
		var pagebreak = CKEDITOR.dom.element.createFromHtml(
			'<div ' +
			'contenteditable="false" ' +
			'title="'+ label + '" ' +
			'aria-label="'+ label + '" ' +
			'data-cke-display-name="pagebreak" ' +
			'style="clear:both;border-top:dotted 1px #D8D8D8;border-bottom:dotted 1px #D8D8D8;" ' +
			'class="pagebreak">&nbsp;' +
			'</div>', editor.document );

		var ranges = editor.getSelection().getRanges( true );

		editor.fire( 'saveSnapshot' );

		for ( var range, i = ranges.length - 1 ; i >= 0; i-- )
		{
			range = ranges[ i ];

			if ( i < ranges.length -1 )
				pagebreak = pagebreak.clone( true );

			range.splitBlock( 'p' );
			range.insertNode( pagebreak );
			if ( i == ranges.length - 1 )
			{
				var next = pagebreak.getNext();
				range.moveToPosition( pagebreak, CKEDITOR.POSITION_AFTER_END );

				// If there's nothing or a non-editable block followed by, establish a new paragraph
				// to make sure cursor is not trapped.
				if ( !next || next.type == CKEDITOR.NODE_ELEMENT && !next.isEditable() )
					range.fixBlock( true, editor.config.enterMode == CKEDITOR.ENTER_DIV ? 'div' : 'p'  );

				range.select();
			}
		}

		editor.fire( 'saveSnapshot' );
	}
};
})(django.jQuery);