/****** Settings *****

1. without any settings specified, will operate on default values
2. if settings are visited, ask API to provide new UID
3. on save, POST to backend using UID to link to settings object
    - auth/security not *really* necessary but might be a nice-to-have
4. earth.js will fetch UID (from chrome.storage) and use to make API image request


*/
// var API_URL = 'https://earth-pics.tk/api/v0/earth';
var API_URL = 'http://127.0.0.1:8000/api/v0/earth';
var getNewImage = function() {
    $.getJSON(API_URL + '/get')
        .success(function(resp) {
            newImage = resp;
            $('body').css("background-image", "url('" + newImage.preferred_image_url + "')");
        }).fail(function () {
            console.log('Image Request Failed');
        });
};

var lastImage  = localStorage.getItem('lastImage');
if (lastImage !== null) {
    var links = lastImage.split('|');
    $('body').css("background-image", "url('" + links[1] + "')");
} else {
    getNewImage();
}


var settings = {};
chrome.storage.sync.get("settings_uid", function(item) {
    if (item === null || item === undefined) {
        $.getJSON(API_URL + '/settings/new')
            .success(function(resp) {
                chrome.storage.sync.set({"settings_uid": resp.url_identifier});
                settings['uid'] = resp.url_identifier;
            });
    }
    else {
        settings['uid'] = item.settings_uid;
    }
});



(function() {

    var historyItem = Vue.component('history', {
        template: '#history',
        props: ["index", "image_url", "permalink", "title"]
    });

    var filter = Vue.component('filter', {
        template: '#filter',
        props: ["source", "filter_class", "type", "index", "value", "value_type", "value_operand", "active"],
        methods: {
            updateValue: function(field, value) {
                this[field] = value;
                vmSettings.filters[this.source][this.filter_class][field] = value;
                if (!!this.value) {
                    this.active = true;
                }
            },
            clear: function() {
                this.updateValue('value', '');
                this.updateValue('value_operand', '');
                this.updateValue('value_type', '');
                this.active = false;
            }
        },
        computed: {
            suggestion: function () {
                switch(this.source) {
                    case 'reddit':
                        return 'try ...yosemite';
                    case 'apod':
                        return 'try ...galaxy';
                    default:
                        return 'try ...nepal'
                }
            }
        }
    });

    var Filter = function(filter_class, filter_type, source) {
        var filter = {
            type: filter_type,
            filter_class: filter_class,
            source: source,
            loadArguments: function(arguments) {
                var key_values = arguments.split('&');
                var key_value;
                for (var i = 0; i < key_values.length; i++) {
                    key_value = key_values[i].split('=');
                    this[key_value[0]] = key_value[1];
                }
            },
            serialize: function() {
                data = [
                    'type=' + this.type,
                    'source=' + this.source,
                    'filter_class=' + this.filter_class,
                    'arguments=' + this.serializeArguments()
                ];
                return data.join(',')
            },
            serializeArguments: function() {
                var mapped_fields = this.fields.length == 1
                    ? ['value']
                    : ['value_type', 'value_operand', 'value'];
                var field;
                var arguments = [];
                for (var i = 0; i < this.fields.length; i++) {
                    field = this.fields[i];
                    arguments.push(
                        field + '*' + this[mapped_fields[i]]
                    );
                }
                return arguments.join('$');
            },
            updateFields: function(component) {
                var mapped_fields = this.fields.length == 1
                    ? ['value']
                    : ['value_type', 'value_operand', 'value'];
                for (var i = 0; i < mapped_fields.length; i++) {
                    mapped_field = mapped_fields[i];
                    field = this.fields[i];
                    component.updateValue(mapped_field, this[field]);
                }
            }
        };
        switch (filter_class) {
            case 'query':
                filter.index = 0;
                filter.fields = ['key_words'];
                // console.log('test');
                break;
            case 'score':
                filter.index = 1;
                filter.fields = [
                    'score_type',
                    'score_threshold_operand',
                    'score_value'];
                break;
            case 'resolution':
                filter.index = 2;
                filter.fields = [
                    'resolution_type',
                    'resolution_threshold_operand',
                    'resolution_value'];
                break;
        }
        return filter;
    };

    var vmSettings = new Vue({
        el: '#vm-settings',
        mixins: [],
        data: {
            history: [],
            settings: [],
            filterNav: 0,
            setting_uid: null,
            allow_reddit: false,
            allow_apod: false,
            save_copy: "Save",
            saving: false,
            history_items: [],
            show_history: false,
            filters: {
                all: {
                    query: Filter('query', 'global', 'all')
                },
                reddit: {
                    query: Filter('query', 'specific', 'reddit'),
                    score: Filter('score', 'specific', 'reddit'),
                    resolution: Filter('resolution', 'specific', 'reddit')
                },
                apod: {
                    query: Filter('query', 'specific', 'apod'),
                    resolution: Filter('resolution', 'specific', 'apod')
                }
            },
        },
        created: function() {
            setTimeout(this.getSettings, 100);
        },
        methods: {
            settingsCallback: function(resp) {
                console.log(resp);
                allowed_sources = resp.allowed_sources.split(',');
                var source;
                for(var i = 0; i < allowed_sources.length; i++) {
                    source = allowed_sources[i];
                    vmSettings['allow_' + source] = true;
                }
                var filter;
                for (i = 0; i < resp.filters.length; i++) {
                    filter = resp.filters[i];
                    source = filter['type'] == 'global' ? 'all' : filter.source;
                    var object = vmSettings.filters[source][filter.filter_class];
                    object.loadArguments(filter.arguments);
                    object.updateFields(this.getComponent(object));
                }

            },
            getSettings: function () {
                $.getJSON(API_URL + '/settings/' + settings.uid)
                    .success(this.settingsCallback)
            },
            getComponent: function(filter) {
                var child;
                for (var i = 0; i < this.$children.length; i++) {
                    child = this.$children[i];
                    if (child.filter_class == filter.filter_class && child.source == filter.source) {
                        return child;
                    }
                }
                return null;
            },
            serializerFilters: function () {
                var all_filters = [
                    this.filters.all,
                    this.filters.reddit,
                    this.filters.apod,
                ];
                var serialized_filters = [];
                var filter;
                for(var i = 0; i < all_filters.length; i++) {
                    filter = all_filters[i];
                    Object.keys(filter).forEach(function (key, index) {
                        if (!!filter[key].value) {
                            serialized_filters.push(
                                filter[key].serialize()
                            );
                        }
                    });
                }
                return serialized_filters.join('|');
            },
            submitSettings: function () {
                values = {
                    allow_reddit: this.allow_reddit,
                    allow_apod: this.allow_apod,
                    filters: this.serializerFilters()
                };
                var url = this.addAsQueryParams(API_URL + '/settings/save/' + settings.uid, values);
                console.log(url);
                var that = this;
                $.get(url).success(function(resp, textStatus, xhr) {
                    that.save_copy = 'Saved!';
                    that.saving = true;
                    if (xhr.status === 206) {
                        that.save_copy = '(Too Restrictive!)'
                    }
                    console.log(resp);
                    setTimeout(function () {
                        that.save_copy = 'Save';
                        that.saving = false;
                    }, 1000);
                    localStorage.clear();
                });
            },
            getHistoryCallback: function(that, resp) {
                return function (resp) {
                    that.history_items = resp;
                }
            },
            getHistory: function () {
                this.show_history = true;
                if (this.history_items.length === 0) {
                    $.getJSON(API_URL + '/settings/history/' + settings.uid)
                     .success(this.getHistoryCallback(this));
                }
            },
            addAsQueryParams: function(url, values) {
                queries = [];
                Object.keys(values).forEach(function(key, index) {
                    queries.push(key + '=' + values[key]);
                });
                return url + '?' + queries.join('&');
            }
        }
    });
    window.vmSettings = vmSettings;
})();