(function() {

    var $;

    // This is defined in templates/ckeditor/configs.js
    if (typeof CKEDITOR == 'object' && typeof CKEDITOR.jQuery == 'object') {
        $ = CKEDITOR.jQuery;
    } else {
        $ = (typeof grp == 'object' && grp.jQuery)
              ? grp.jQuery
              : (typeof django == 'object' && django.jQuery) ? django.jQuery : window.jQuery;
    }

    if (!$) {
        return;
    }

    if (typeof $.fn.ckeditor == 'function') {
        var oldFn = $.fn.ckeditor;
        $.fn.ckeditor = function(callback, config) {
            if (!CKEDITOR.env.isCompatible) {
                return this;
            }
            if (!$.isFunction(callback)) {
                var tmp;
                tmp = config; config = callback; callback = tmp;
            }

            var $this = this;

            return $this.filter('textarea, div, p').each(function(i, element) {
                var $element = $(element),
                    editor = $element.data('ckeditorInstance'),
                    instanceLock = $element.data('_ckeditorInstanceLock');

                if (editor && !instanceLock && callback) {
                    callback.apply(editor, [this]);
                    return this;
                }
                var elementConfig = $.extend({}, config || {});
                if (!config) {
                    var configName = $element.attr('data-config-name');
                    try {
                        elementConfig = $.parseJSON($element.attr('data-config') || '{}') || {};
                    } catch(e) {}
                    var baseConfig = {};
                    if (typeof DJCKEDITOR == 'object' && typeof DJCKEDITOR.configs == 'object') {
                        baseConfig = $.extend({}, baseConfig,
                            DJCKEDITOR.configs[configName] || {});
                    }
                    elementConfig = $.extend({}, baseConfig, elementConfig);

                }
                if ($.isFunction(callback)) {
                    oldFn.call($element, callback, elementConfig);
                } else {
                    oldFn.call($element, elementConfig);
                }

            });
        };
    }

    $(document).ready(function() {
        $('.django-ckeditor-textarea').ckeditor();
    });

})();
