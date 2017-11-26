/*
Created by Lucas Brambrink, 2017;
*/

// var API_URL = 'https://earth-pics.tk/api/v0/earth';
var API_URL = 'http://127.0.0.1:8000/api/v0/earth';
// var getNewImage = function() {
//     $.getJSON(API_URL + '/get')
//         .success(function(resp) {
//             newImage = resp;
//             $('body').css("background-image", "url('" + newImage.preferred_image_url + "')");
//         }).fail(function () {
//             console.log('Image Request Failed');
//         });
// };

// Attempt to get a photo from local storage
var cachedImage = localStorage.getItem('cachedImage');
if (cachedImage !== null && cachedImage !== undefined && cachedImage !== 'undefined') {
    setImage(JSON.parse(cachedImage));
}

// var lastImage  = localStorage.getItem('lastImage');
// if (lastImage !== null) {
//     var links = lastImage.split('|');
//     $('body').css("background-image", "url('" + links[1] + "')");
// } else {
//     getNewImage();
// }

/* Load settings */
var settings = {};
loadOrCreateSettings(settings, true);

/* Analytics */
var _gaq = _gaq || [];

/* Vue.js */
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
                vmSettings.queueSettingsUpdate();
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
                    case 'wiki':
                        return 'try ...president';
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
                return {
                    type: this.type,
                    source: this.source,
                    filter_class: this.filter_class,
                    arguments: this.serializeArguments()
                };
            },
            serializeArguments: function() {
                var mapped_fields = this.fields.length === 1
                    ? ['value']
                    : ['value_type', 'value_operand', 'value'];
                var field;
                var serialized = [];
                for (var i = 0; i < this.fields.length; i++) {
                    field = this.fields[i];
                    serialized.push(field + '=' + this[mapped_fields[i]])
                }
                return serialized.join('&');
            },
            updateFields: function(component) {
                var mapped_fields = this.fields.length === 1
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
            allow_wiki: false,
            contain_reddit: false,
            contain_apod: false,
            contain_wiki: false,
            ratio_reddit: 1,
            ratio_apod: 1,
            ratio_wiki: 1,
            save_copy: "Save",
            saving: false,
            history_items: [],
            show_history: false,
            serialized_state: '',
            is_queued: false,
            queued_image: false,
            border_css: '',
            show_settings: false,
            filters: {
                all: {
                    query: Filter('query', 'global', 'all'),
                    resolution: Filter('resolution', 'global', 'all')
                },
                reddit: {
                    query: Filter('query', 'specific', 'reddit'),
                    score: Filter('score', 'specific', 'reddit'),
                    resolution: Filter('resolution', 'specific', 'reddit')
                },
                apod: {
                    query: Filter('query', 'specific', 'apod'),
                    resolution: Filter('resolution', 'specific', 'apod')
                },
                wiki: {
                    query: Filter('query', 'specific', 'wiki'),
                }
            },
        },
        computed: {
            relative_frequency: function () {
                return [
                    this.ratio_reddit,
                    this.ratio_apod,
                    this.ratio_wiki
                ].join(',');
            },
            frequency: function () {
                return this.active_ratios.join(':');
            },
            hide_ratios: function () {
                return this.not_enough_for_ratio ||
                    this.active_ratios.every(function(r) { return r === 1});
            },
            not_enough_for_ratio: function () {
                return this.active_ratios.length < 2;
            },
            active_ratios: function() {
                var active = [];
                if (this.allow_reddit) {
                    active.push(this.ratio_reddit)
                }
                if (this.allow_apod) {
                    active.push(this.ratio_apod)
                }
                if (this.allow_wiki) {
                    active.push(this.ratio_wiki)
                }
                return active;
            }
        },
        methods: {
            settingsCallback: function(resp) {
                allowed_sources = resp.allowed_sources.split(',');
                var source;
                for(var i = 0; i < allowed_sources.length; i++) {
                    source = allowed_sources[i];
                    vmSettings['allow_' + source] = true;
                }
                var contain_data_sources = resp.contain_data_sources.split(',');
                for(i = 0; i < contain_data_sources.length; i++) {
                    source = contain_data_sources[i];
                    vmSettings['contain_' + source] = true;
                }
                var relative_frequency = resp.relative_frequency.split(',');
                var sources = ['reddit', 'apod', 'wiki'];
                for(i = 0; i < relative_frequency.length; i++) {
                    source = sources[i];
                    var freq = parseInt(relative_frequency[i]);
                    if (isNaN(freq)) freq = 1;
                    vmSettings['ratio_' + source] = freq;
                }
                var filter;
                for (i = 0; i < resp.filters.length; i++) {
                    filter = resp.filters[i];
                    source = filter['type'] === 'global' ? 'all' : filter.source;
                    var object = vmSettings.filters[source][filter.filter_class];
                    object.loadArguments(filter.arguments);
                    object.updateFields(this.getComponent(object));
                }
            },
            getSettings: function () {
                $.ajax({
                    url: API_URL + '/settings/' + settings.uid,
                    method: 'GET',
                    headers: {'token': settings.token}
                }).success(this.settingsCallback)
            },
            getComponent: function(filter) {
                var child;
                for (var i = 0; i < this.$children.length; i++) {
                    child = this.$children[i];
                    if (child.filter_class === filter.filter_class && child.source === filter.source) {
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
                    this.filters.wiki,
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
                return serialized_filters;
            },
            submitSettings: function () {
                // _gaq.push(['_trackEvent', 'submit settings', 'clicked']);
                values = {
                    allow_reddit: this.allow_reddit,
                    allow_apod: this.allow_apod,
                    allow_wiki: this.allow_wiki,
                    contain_reddit: this.contain_reddit,
                    contain_apod: this.contain_apod,
                    contain_wiki: this.contain_wiki,
                    filters: this.serializerFilters(),
                    token: settings.token,
                    relative_frequency: this.relative_frequency
                };
                var url = API_URL + '/settings/save/' + settings.uid;
                var that = this;
                var state = JSON.stringify(values);
                var submitSettingsCallback = function(resp, textStatus, xhr) {
                    that.save_copy = 'Saved!';
                    that.border_css = 'saved';
                    that.saving = true;
                    if (xhr.status === 206) {
                        that.border_css = 'restrictive';
                    }
                    setTimeout(function () {
                        that.border_css = '';
                        that.saving = false;
                    }, 1000);
                    localStorage.clear();
                };

                // prevent excessive API calls if state has not changed.
                if (this.serialized_state === state) {
                    submitSettingsCallback(null, null, {});
                } else {
                    this.serialized_state = state;
                    $.ajax({
                        url: url,
                        data: JSON.stringify(values),
                        contentType: 'application/json',
                        type: 'PUT',
                        headers: {'token': settings.token},
                        dataType: 'json'
                    }).success(submitSettingsCallback);
                }
            },
            queueSettingsUpdate: function() {
                console.log('queued!');
                if (this.is_queued) {
                    return;
                } else {
                    this.is_queued = true;
                }
                this.border_css = 'saved';
                _gaq.push(['_trackEvent', 'submit settings', 'clicked']);
                setTimeout(function(that) {
                    return function () {
                        that.submitSettings();
                        that.is_queued = false;
                    }
                }(this), 2000);
            },
            getHistoryCallback: function(that, resp) {
                return function (resp) {
                    that.history_items = resp;
                }
            },
            getHistory: function () {
                this.show_history = true;
                _gaq.push(['_trackEvent', 'show history', 'clicked']);
                if (this.history_items.length === 0) {
                    $.ajax({
                        url: API_URL + '/settings/history/' + settings.uid,
                        headers: {'token': settings.token}
                    }).success(this.getHistoryCallback(this));
                }
            },
            addAsQueryParams: function(url, values) {
                queries = [];
                Object.keys(values).forEach(function(key, index) {
                    queries.push(key + '=' + values[key]);
                });
                return url + '?' + queries.join('&');
            },
            refreshImage: function () {
                if (this.queued_image) {
                    return;
                } else {
                    this.queued_image = true;
                }
                setTimeout(function(that) {
                    return function () {
                        localStorage.removeItem('cachedImage');
                        getNewImage(settings.uid);
                        that.queued_image = false;
                    }
                }(this), 500);
            }
        }
    });
    window.vmSettings = vmSettings;
})();