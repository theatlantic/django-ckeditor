/*
Copyright (c) 2003-2011, Frederico Caldeira Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

importClass( java.lang.Integer );
importClass( java.lang.System );

var CKRELEASER =
{
	isCompiled : false,
	verbose : 0,
	os : System.getProperty( "os.name" ).substring( 0, 3 ).toLowerCase(),
	path : "",
	revisionNumber : 0,

	timestamp : 0,

	load : function( className )
	{
		if ( CKRELEASER.isCompiled )
		{
			loadClass( className );
		}
		else
		{
			var path = className;

			if ( path.indexOf( "ckpackager." ) === 0 )
				path = path.replace( /^ckpackager\./, '_source/ckpackager/' );
			else if ( path.indexOf( "tools." ) === 0 )
				path = path.replace( /^tools\./, '_dev/_thirdparty/' );
			else
				path = path.replace( /^ckreleaser\./, "_source/" );

			path = path.replace( /\./g, '/' ) + '.js';

			load( CKRELEASER.path + path );
		}
	}
};
