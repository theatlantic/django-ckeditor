function getState( editor, path )
{
	var firstBlock = path.block || path.blockLimit;

	if ( !firstBlock || firstBlock.getName() == 'body' )
		return CKEDITOR.TRISTATE_OFF;

	// See if the first block has a asideRight parent.
	if ( firstBlock.getAscendant( 'asideRight', true ) )
		return CKEDITOR.TRISTATE_ON;

	return CKEDITOR.TRISTATE_OFF;
}

function onSelectionChange( evt )
{
	var editor = evt.editor,
	command = editor.getCommand( 'asideRight' );
	command.state = getState( editor, evt.data.path );
	command.fire( 'state' );
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


var commandObject =
{
	exec : function( editor )
	{
		var state = editor.getCommand( 'asideRight' ).state,
			selection = editor.getSelection(),
			range = selection && selection.getRanges( true )[0];

		if ( !range )
			return;

		var bookmarks = selection.createBookmarks();

		// Kludge for #1592: if the bookmark nodes are in the beginning of
		// asideRight, then move them to the nearest block element in the
		// asideRight.
		if ( CKEDITOR.env.ie )
		{
			var bookmarkStart = bookmarks[0].startNode,
				bookmarkEnd = bookmarks[0].endNode,
				cursor;

			if ( bookmarkStart && bookmarkStart.getParent().getName() == 'asideRight' )
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
					&& bookmarkEnd.getParent().getName() == 'asideRight' )
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

			// If any of the selected blocks is a asideRight, remove it to prevent
			// nested asideRights.
			while ( tmp.length > 0 )
			{
				block = tmp.shift();
				if ( block.getName() == 'asideRight' )
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

			// Now we have all the blocks to be included in a new asideRight node.
			var bqBlock = editor.document.createElement( 'aside' );

			bqBlock.setAttribute('style', 'float:right');
			
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
					if ( block.getParent().getName() == 'asideRight' )
					{
						bqParent = block.getParent();
						bqChild = block;
						break;
					}
					block = block.getParent();
				}

				// Remember the blocks that were recorded down in the moveOutNodes array
				// to prevent duplicates.
				if ( bqParent && bqChild && !bqChild.getCustomData( 'asideRight_moveout' ) )
				{
					moveOutNodes.push( bqChild );
					CKEDITOR.dom.element.setMarker( database, bqChild, 'asideRight_moveout', true );
				}
			}

			CKEDITOR.dom.element.clearAllMarkers( database );

			var movedNodes = [],
				processedasideRightBlocks = [];

			database = {};
			while ( moveOutNodes.length > 0 )
			{
				var node = moveOutNodes.shift();
				bqBlock = node.getParent();

				// If the node is located at the beginning or the end, just take it out
				// without splitting. Otherwise, split the asideRight node and move the
				// paragraph in between the two asideRight nodes.
				if ( !node.getPrevious() )
					node.remove().insertBefore( bqBlock );
				else if ( !node.getNext() )
					node.remove().insertAfter( bqBlock );
				else
				{
					node.breakParent( node.getParent() );
					processedasideRightBlocks.push( node.getNext() );
				}

				// Remember the asideRight node so we can clear it later (if it becomes empty).
				if ( !bqBlock.getCustomData( 'asideRight_processed' ) )
				{
					processedasideRightBlocks.push( bqBlock );
					CKEDITOR.dom.element.setMarker( database, bqBlock, 'asideRight_processed', true );
				}

				movedNodes.push( node );
			}

			CKEDITOR.dom.element.clearAllMarkers( database );

			// Clear asideRight nodes that have become empty.
			for ( i = processedasideRightBlocks.length - 1 ; i >= 0 ; i-- )
			{
				bqBlock = processedasideRightBlocks[i];
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
};


CKEDITOR.plugins.add('asideRight',
{
    init: function(editor)
    {
        var pluginName = 'asideRight';
        
        editor.addCommand(pluginName, commandObject);
        editor.ui.addButton('Aside Right',{
			label: 'Aside Right',
			command: pluginName
		});

		//CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/asideRight.js');
        
        editor.on( 'selectionChange', onSelectionChange );
    },
    requires : [ 'domiterator' ]
});
