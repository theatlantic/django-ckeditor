/*
Copyright (c) 2003-2012, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @fileOverview jQuery adapter provides easy use of basic CKEditor functions
 *   and access to internal API. It also integrates some aspects of CKEditor with
 *   jQuery framework.
 *
 * Every TEXTAREA, DIV and P elements can be converted to working editor.
 *
 * Plugin exposes some of editor's event to jQuery event system. All of those are namespaces inside
 * ".ckeditor" namespace and can be binded/listened on supported textarea, div and p nodes.
 *
 * Available jQuery events:
 * - instanceReady.ckeditor( editor, rootNode )
 *   Triggered when new instance is ready.
 * - destroy.ckeditor( editor )
 *   Triggered when instance is destroyed.
 * - getData.ckeditor( editor, eventData )
 *   Triggered when getData event is fired inside editor. It can change returned data using eventData reference.
 * - setData.ckeditor( editor )
 *   Triggered when getData event is fired inside editor.
 *
 * @example
 * <script src="jquery.js"></script>
 * <script src="ckeditor.js"></script>
 * <script src="adapters/jquery/adapter.js"></script>
 */

(function()
{
	/**
	 * Allows CKEditor to override jQuery.fn.val(), making it possible to use the val()
	 * function on textareas, as usual, having it synchronized with CKEditor.<br>
	 * <br>
	 * This configuration option is global and executed during the jQuery Adapter loading.
	 * It can't be customized across editor instances.
	 * @type Boolean
	 * @example
	 * &lt;script&gt;
	 * CKEDITOR.config.jqueryOverrideVal = true;
	 * &lt;/script&gt;
	 * &lt;!-- Important: The JQuery adapter is loaded *after* setting jqueryOverrideVal --&gt;
	 * &lt;script src="/ckeditor/adapters/jquery.js"&gt;&lt;/script&gt;
	 * @example
	 * // ... then later in the code ...
	 *
	 * $( 'textarea' ).ckeditor();
	 * // ...
	 * $( 'textarea' ).val( 'New content' );
	 */
	CKEDITOR.config.jqueryOverrideVal = (typeof CKEDITOR.config.jqueryOverrideVal == 'undefined') ? true : CKEDITOR.config.jqueryOverrideVal;

	var arrayReduce = Array.prototype.reduce;

	if (!arrayReduce) {
		arrayReduce = function(accumulator) {
			if (this === null || this === undefined) {
				throw new TypeError("Object is null or undefined");
			}
			var i = 0, l = this.length >> 0, curr;

			if (typeof accumulator !== "function") {
				// ES5 : "If IsCallable(callbackfn) is false, throw a TypeError exception."
				throw new TypeError("First argument is not callable");
			}

			if (arguments.length < 2) {
				if (l === 0) {
					throw new TypeError("Array length is 0 and no second argument");
				}
				curr = this[0];
				i = 1; // start accumulating at the second element
			} else {
				curr = arguments[1];
			}
			while (i < l) {
				if (i in this) {
					curr = accumulator.call(undefined, curr, this[i], i, this);
				}
				++i;
			}

			return curr;
		};
	}

	var normalizeVersion = function(version){
		var normalized = [];
		var splits = version.split('.');
		for (var i = 0; i < splits.length; i++) {
			normalized.push(parseInt(splits[i], 10));
		}
		return normalized;
	};

	var versionCompare = function(version1, version2) {
		if ('undefined' === typeof version1) {
			throw new Error("$.versioncompare needs at least one parameter.");
		}
		version2 = version2 || $.fn.jquery;
		if (version1 == version2) {return 0;};

		var v1 = normalizeVersion(version1);
		var v2 = normalizeVersion(version2);
		var len = Math.max(v1.length, v2.length);
		for (var i = 0; i < len; i++) {
			v1[i] = v1[i] || 0;
			v2[i] = v2[i] || 0;
			if (v1[i] == v2[i]) continue;
			return (v1[i] > v2[i]) ? 1 : -1;
		}
		return 0;
	};

	var getBestJQuery = function() {
		var jqueries = [];
		if (typeof window.django != 'undefined' && typeof django.jQuery != 'undefined') {
			jqueries.push(['django.jQuery', django.jQuery]);
		}
		if (typeof window.jQuery != 'undefined') {
			jqueries.push(['jQuery', window.jQuery]);
		}
		if (typeof window.grp != 'undefined' && typeof grp.jQuery != 'undefined') {
			jqueries.push(['grp.jQuery', grp.jQuery]);
		}
		return arrayReduce.call(jqueries, function(prevValue, currValue, index, array) {
			return (versionCompare(currValue[1].fn.jquery, prevValue[1].fn.jquery) >= 0) ? currValue : prevValue;
		});
	};

	if (typeof(CKEDITOR.jQuery) == 'undefined') {
		if (typeof(CKEDITOR.versionCompare) != 'function') {
			CKEDITOR.versionCompare = versionCompare;
		}
		var bestJQuery = getBestJQuery();
		if (versionCompare(bestJQuery[1].fn.jquery, '1.4.2') <= 0) {
			var scripts = document.getElementsByTagName("script"),
				currentScript = scripts[scripts.length-1],
				currentSrc = currentScript.src,
				rootUrl = currentSrc.replace(/\/[^\/]+$/, ''),
				newSrc = rootUrl + '/jquery-1.7.2.js';
			document.write('<scr' + 'ipt type="text/javascript" src="' + newSrc + '"></sc' + 'ript>');
		} else {
			CKEDITOR.jQueryObj = bestJQuery[0];
			CKEDITOR.jQuery = bestJQuery[1].noConflict();
		}
	}


	if ( typeof CKEDITOR.jQuery == 'undefined' )
		return;

	(function($) {

	// jQuery object methods.
	$.extend( $.fn,
	/** @lends jQuery.fn */
	{
		/**
		 * Return existing CKEditor instance for first matched element.
		 * Allows to easily use internal API. Doesn't return jQuery object.
		 *
		 * Raised exception if editor doesn't exist or isn't ready yet.
		 *
		 * @name jQuery.ckeditorGet
		 * @return CKEDITOR.editor
		 * @see CKEDITOR.editor
		 */
		ckeditorGet: function()
		{
			var instance = this.eq( 0 ).data( 'ckeditorInstance' );
			if ( !instance )
				throw "CKEditor not yet initialized, use ckeditor() with callback.";
			return instance;
		},
		/**
		 * Triggers creation of CKEditor in all matched elements (reduced to DIV, P and TEXTAREAs).
		 * Binds callback to instanceReady event of all instances. If editor is already created, than
		 * callback is fired right away.
		 *
		 * Mixed parameter order allowed.
		 *
		 * @param callback Function to be run on editor instance. Passed parameters: [ textarea ].
		 * Callback is fiered in "this" scope being ckeditor instance and having source textarea as first param.
		 *
		 * @param config Configuration options for new instance(s) if not already created.
		 * See URL
		 *
		 * @example
		 * $( 'textarea' ).ckeditor( function( textarea ) {
		 *   $( textarea ).val( this.getData() )
		 * } );
		 *
		 * @name jQuery.fn.ckeditor
		 * @return jQuery.fn
		 */
		ckeditor: function( callback, config )
		{
			if ( !CKEDITOR.env.isCompatible )
				return this;

			if ( !$.isFunction( callback ))
			{
				var tmp = config;
				config = callback;
				callback = tmp;
			}

			this.filter( 'textarea, div, p' ).each( function()
			{
				var $element = $( this ),
					editor = $element.data( 'ckeditorInstance' ),
					instanceLock = $element.data( '_ckeditorInstanceLock' ),
					element = this;

				if ( editor && !instanceLock )
				{
					if ( callback )
						callback.apply( editor, [ this ] );
				}
				else if ( !instanceLock )
				{
					// CREATE NEW INSTANCE

					// Handle config.autoUpdateElement inside this plugin if desired.
					if ( config.autoUpdateElement
						|| ( typeof config.autoUpdateElement == 'undefined' && CKEDITOR.config.autoUpdateElement ) )
					{
						config.autoUpdateElementJquery = true;
					}

					// Always disable config.autoUpdateElement.
					config.autoUpdateElement = false;
					$element.data( '_ckeditorInstanceLock', true );

					// Set instance reference in element's data.
					editor = CKEDITOR.replace( element, config );
					$element.data( 'ckeditorInstance', editor );

					// Register callback.
					editor.on( 'instanceReady', function( event )
					{
						var editor = event.editor;
						setTimeout( function()
						{
							// Delay bit more if editor is still not ready.
							if ( !editor.element )
							{
								setTimeout( arguments.callee, 100 );
								return;
							}

							// Remove this listener.
							event.removeListener( 'instanceReady', this.callee );

							// Forward setData on dataReady.
							editor.on( 'dataReady', function()
							{
								$element.trigger( 'setData' + '.ckeditor', [ editor ] );
							});

							// Forward getData.
							editor.on( 'getData', function( event ) {
								$element.trigger( 'getData' + '.ckeditor', [ editor, event.data ] );
							}, 999 );

							// Forward destroy event.
							editor.on( 'destroy', function()
							{
								$element.trigger( 'destroy.ckeditor', [ editor ] );
							});

							var $form = $element.parents( 'form' );

							// Integrate with form submit.
							if ( editor.config.autoUpdateElementJquery && $element.is( 'textarea' ) && $form.length )
							{
								var onSubmit = function() { editor.updateElement(); };

								// Bind to submit event.
								$form.bind( 'submit.ckeditor', onSubmit );

								// Bind to form-pre-serialize from jQuery Forms plugin.
								$form.bind( 'form-pre-serialize.ckeditor', onSubmit );

								// Unbind when editor destroyed.
								$element.bind( 'destroy.ckeditor', function()
								{
									$form.unbind( 'submit.ckeditor', onSubmit );
									$form.unbind( 'form-pre-serialize.ckeditor', onSubmit );
								});
							}

							// Garbage collect on destroy.
							editor.on( 'destroy', function()
							{
								$element.data( 'ckeditorInstance', null );
							});

							// Remove lock.
							$element.data( '_ckeditorInstanceLock', null );

							// Fire instanceReady event.
							$element.trigger( 'instanceReady.ckeditor', [ editor ] );

							// Run given (first) code.
							if ( callback )
								callback.apply( editor, [ element ] );
						}, 0 );
					}, null, null, 9999);
				}
				else
				{
					// Editor is already during creation process, bind our code to the event.
					CKEDITOR.on( 'instanceReady', function( event )
					{
						var editor = event.editor;
						setTimeout( function()
						{
							// Delay bit more if editor is still not ready.
							if ( !editor.element )
							{
								setTimeout( arguments.callee, 100 );
								return;
							}

							if ( editor.element.$ == element )
							{
								// Run given code.
								if ( callback )
									callback.apply( editor, [ element ] );
							}
						}, 0 );
					}, null, null, 9999);
				}
			});
			return this;
		}
	});

	// New val() method for objects.
	if ( CKEDITOR.config.jqueryOverrideVal )
	{
			$.valHooks[ 'textarea' ] = {
				get: function( elem ) {
					var $this = $( elem ),
						editor = $this.data( 'ckeditorInstance' );

					if ( editor ) return editor.getData();
				},
				set: function( elem, value ) {
					var $this = $( elem ),
						editor = $this.data( 'ckeditorInstance' );

					if ( editor ) editor.setData( value );
				}
			};
	}
})(CKEDITOR.jQuery);

})();
