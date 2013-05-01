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
                var $element = $(element);
                var elementConfig = $.extend({}, config || {});
                if (!config) {
                    var configName = $element.attr('data-config-name');
                    elementConfig = $.parseJSON($element.attr('data-config')) || {};
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
            //
            // if (!config) {
            //     return $this.filter('textarea, div, p').each(function(i, element) {
            //
            //         oldFn.apply()
            //         $element.ckeditor(config);
            //     });
            // }
        };
    }

    $(document).ready(function() {
        $('.django-ckeditor-textarea').ckeditor();
        // $('.django-ckeditor-textarea').each(function(i, textarea) {
        //     var $textarea = $(textarea);
        //     var configName = $textarea.attr('data-config-name');
        //     var config = $.parseJSON($textarea.attr('data-config')) || {};
        //     var baseConfig = {};
        //     if (typeof DJCKEDITOR == 'object' && typeof DJCKEDITOR.configs == 'object') {
        //         baseConfig = $.extend({}, baseConfig,
        //             DJCKEDITOR.configs[configName] || {});
        //     }
        //     config = $.extend({}, baseConfig, config);
        //     $textarea.ckeditor(config);
        // });
    });

})();
