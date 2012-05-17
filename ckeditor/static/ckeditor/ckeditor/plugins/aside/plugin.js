(function(){

function getState( editor, path )
{
	var firstBlock = path.block || path.blockLimit;

	if ( !firstBlock || firstBlock.getName() == 'body' )
		return CKEDITOR.TRISTATE_OFF;

	// See if the first block has a aside parent.
	if ( firstBlock.getAscendant( 'aside', true ) )
		return CKEDITOR.TRISTATE_ON;

	return CKEDITOR.TRISTATE_OFF;
}



function noBlockLeft( bqBlock )
{
	for ( var i = 0, length = bqBlock.getChildCount(), child ; i < length && ( child = bqBlock.getChild( i ) ) ; i++ )
	{
		if ( child.type == CKEDITOR.NODE_ELEMENT && child.isBlockBoundary() )
			return false;
	}
	return true;
}


function commandObject(editor, side){

		var state = editor.getCommand( 'aside' ).state,
			selection = editor.getSelection(),
			range = selection && selection.getRanges( true )[0];

		if ( !range )
			return;

		var bookmarks = selection.createBookmarks();

		// Kludge for #1592: if the bookmark nodes are in the beginning of
		// aside, then move them to the nearest block element in the
		// aside.
		if ( CKEDITOR.env.ie )
		{
			var bookmarkStart = bookmarks[0].startNode,
				bookmarkEnd = bookmarks[0].endNode,
				cursor;

			if ( bookmarkStart && bookmarkStart.getParent().getName() == 'aside' )
			{
				cursor = bookmarkStart;
				while ( ( cursor = cursor.getNext() ) )
				{
					if ( cursor.type == CKEDITOR.NODE_ELEMENT &&
							cursor.isBlockBoundary() )
					{
						bookmarkStart.move( cursor, true );
						break;
					}
				}
			}

			if ( bookmarkEnd
					&& bookmarkEnd.getParent().getName() == 'aside' )
			{
				cursor = bookmarkEnd;
				while ( ( cursor = cursor.getPrevious() ) )
				{
					if ( cursor.type == CKEDITOR.NODE_ELEMENT &&
							cursor.isBlockBoundary() )
					{
						bookmarkEnd.move( cursor );
						break;
					}
				}
			}
		}

		var iterator = range.createIterator(),
			block;
		iterator.enlargeBr = editor.config.enterMode != CKEDITOR.ENTER_BR;

		if ( state == CKEDITOR.TRISTATE_OFF )
		{
			var paragraphs = [];
			while ( ( block = iterator.getNextParagraph() ) )
				paragraphs.push( block );

			// If no paragraphs, create one from the current selection position.
			if ( paragraphs.length < 1 )
			{
				var para = editor.document.createElement( editor.config.enterMode == CKEDITOR.ENTER_P ? 'p' : 'div' ),
					firstBookmark = bookmarks.shift();
				range.insertNode( para );
				para.append( new CKEDITOR.dom.text( '\ufeff', editor.document ) );
				range.moveToBookmark( firstBookmark );
				range.selectNodeContents( para );
				range.collapse( true );
				firstBookmark = range.createBookmark();
				paragraphs.push( para );
				bookmarks.unshift( firstBookmark );
			}

			// Make sure all paragraphs have the same parent.
			var commonParent = paragraphs[0].getParent(),
				tmp = [];
			for ( var i = 0 ; i < paragraphs.length ; i++ )
			{
				block = paragraphs[i];
				commonParent = commonParent.getCommonAncestor( block.getParent() );
			}

			// The common parent must not be the following tags: table, tbody, tr, ol, ul.
			var denyTags = { table : 1, tbody : 1, tr : 1, ol : 1, ul : 1 };
			while ( denyTags[ commonParent.getName() ] )
				commonParent = commonParent.getParent();

			// Reconstruct the block list to be processed such that all resulting blocks
			// satisfy parentNode.equals( commonParent ).
			var lastBlock = null;
			while ( paragraphs.length > 0 )
			{
				block = paragraphs.shift();
				while ( !block.getParent().equals( commonParent ) )
					block = block.getParent();
				if ( !block.equals( lastBlock ) )
					tmp.push( block );
				lastBlock = block;
			}

			// If any of the selected blocks is a aside, remove it to prevent
			// nested asides.
			while ( tmp.length > 0 )
			{
				block = tmp.shift();
				if ( block.getName() == 'aside' )
				{
					var docFrag = new CKEDITOR.dom.documentFragment( editor.document );
					while ( block.getFirst() )
					{
						docFrag.append( block.getFirst().remove() );
						paragraphs.push( docFrag.getLast() );
					}

					docFrag.replace( block );
				}
				else
					paragraphs.push( block );
			}

			// Now we have all the blocks to be included in a new aside node.
			var bqBlock = editor.document.createElement( 'aside' );
			
			
			if (side == "right") bqBlock.setAttribute('class', 'aside-right');
			
			bqBlock.insertBefore( paragraphs[0] );
			while ( paragraphs.length > 0 )
			{
				block = paragraphs.shift();
				bqBlock.append( block );
			}
		}
		else if ( state == CKEDITOR.TRISTATE_ON )
		{
			var moveOutNodes = [],
				database = {};

			while ( ( block = iterator.getNextParagraph() ) )
			{
				var bqParent = null,
					bqChild = null;
				while ( block.getParent() )
				{
					if ( block.getParent().getName() == 'aside' )
					{
						bqParent = block.getParent();
						bqChild = block;
						break;
					}
					block = block.getParent();
				}

				// Remember the blocks that were recorded down in the moveOutNodes array
				// to prevent duplicates.
				if ( bqParent && bqChild && !bqChild.getCustomData( 'aside_moveout' ) )
				{
					moveOutNodes.push( bqChild );
					CKEDITOR.dom.element.setMarker( database, bqChild, 'aside_moveout', true );
				}
			}

			CKEDITOR.dom.element.clearAllMarkers( database );

			var movedNodes = [],
				processedasideBlocks = [];

			database = {};
			while ( moveOutNodes.length > 0 )
			{
				var node = moveOutNodes.shift();
				bqBlock = node.getParent();

				// If the node is located at the beginning or the end, just take it out
				// without splitting. Otherwise, split the aside node and move the
				// paragraph in between the two aside nodes.
				if ( !node.getPrevious() )
					node.remove().insertBefore( bqBlock );
				else if ( !node.getNext() )
					node.remove().insertAfter( bqBlock );
				else
				{
					node.breakParent( node.getParent() );
					processedasideBlocks.push( node.getNext() );
				}

				// Remember the aside node so we can clear it later (if it becomes empty).
				if ( !bqBlock.getCustomData( 'aside_processed' ) )
				{
					processedasideBlocks.push( bqBlock );
					CKEDITOR.dom.element.setMarker( database, bqBlock, 'aside_processed', true );
				}

				movedNodes.push( node );
			}

			CKEDITOR.dom.element.clearAllMarkers( database );

			// Clear aside nodes that have become empty.
			for ( i = processedasideBlocks.length - 1 ; i >= 0 ; i-- )
			{
				bqBlock = processedasideBlocks[i];
				if ( noBlockLeft( bqBlock ) )
					bqBlock.remove();
			}

			if ( editor.config.enterMode == CKEDITOR.ENTER_BR )
			{
				var firstTime = true;
				while ( movedNodes.length )
				{
					node = movedNodes.shift();

					if ( node.getName() == 'div' )
					{
						docFrag = new CKEDITOR.dom.documentFragment( editor.document );
						var needBeginBr = firstTime && node.getPrevious() &&
								!( node.getPrevious().type == CKEDITOR.NODE_ELEMENT && node.getPrevious().isBlockBoundary() );
						if ( needBeginBr )
							docFrag.append( editor.document.createElement( 'br' ) );

						var needEndBr = node.getNext() &&
							!( node.getNext().type == CKEDITOR.NODE_ELEMENT && node.getNext().isBlockBoundary() );
						while ( node.getFirst() )
							node.getFirst().remove().appendTo( docFrag );

						if ( needEndBr )
							docFrag.append( editor.document.createElement( 'br' ) );

						docFrag.replace( node );
						firstTime = false;
					}
				}
			}
		}

		selection.selectBookmarks( bookmarks );
		editor.focus();

}

CKEDITOR.plugins.add('aside',
{
    init: function(editor)
    {
        var pluginName = 'aside';
        
        editor.addCommand(pluginName, {
			exec : function(editor){
				commandObject(editor, "left")
			}
		});
        editor.ui.addButton('AsideLeft',{
			label: 'AsideLeft',
			command: pluginName,
			icon: this.path + 'images/left.gif'
		});
		
		editor.addCommand('asideRight', {
			exec : function(editor){
				commandObject(editor, "right")
			}
		});
        editor.ui.addButton('AsideRight',{
			label: 'AsideRight',
			command: 'asideRight',
			icon: this.path + 'images/right.gif'
		});
        
        editor.on( 'selectionChange', function onSelectionChange( evt ) {
			var editor = evt.editor,
			command = editor.getCommand( 'aside' );
			command.state = getState( editor, evt.data.path );
			command.fire( 'state' );
		});
    },
    requires : [ 'domiterator' ]
});

})();