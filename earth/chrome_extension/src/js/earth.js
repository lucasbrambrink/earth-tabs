/*
Created by Lucas Brambrink, 2017;
*/

var API_URL = 'https://earth-images.world/api/v0/earth';
// var API_URL = 'http://127.0.0.1:8000/api/v0/earth';


/* Utils */
var setImage = function (image_data) {
    var imageDiv = document.getElementById('initial-load-image');
    var video = document.getElementById('video');
    if (image_data.is_video) {
        var video_source = document.getElementById('video-source');
        video_source.src = image_data.video_url;
        setTimeout(function () {
            video.play();
        }, 100);
        imageDiv.style.display = 'none';
        video.style.display = 'block';
        if (image_data.special_css) {
            var styles = image_data.special_css.split(';').filter(function(value) {
                return value.length;
            });
            var style, attribute, css_value;
            for(var i = 0; i < styles.length; i++) {
                style = styles[i];
                attribute = style.split(':')[0];
                css_value = style.split(':')[1];
                video.style[attribute] = css_value;
            }
        }
        // localStorage.removeItem('cachedImage');
    } else {
        imageDiv.style.backgroundImage = "url('" + image_data.preferred_image_url + "')";
        if (image_data.contain_image) {
            imageDiv.style.backgroundSize = 'contain';
        }
        imageDiv.style.display = 'block';
        video.style.display = 'none';
    }
};
var getRandomToken = function () {
    var randomPool = new Uint8Array(32);
    crypto.getRandomValues(randomPool);
    var hex = '';
    for (var i = 0; i < randomPool.length; ++i) {
        hex += randomPool[i].toString(16);
    }
    return hex;
};

/* Load Image */
var image = {};
var cachedImage = localStorage.getItem('cachedImage');
if (cachedImage) {
    image = JSON.parse(cachedImage);
    setImage(image);
}

var refreshedWithVideo = window.location.href.indexOf('refreshed') > -1;

/* Load settings */
var settings = {};
(function (settings, load_image) {
    chrome.storage.sync.get(['token', 'settings_uid'], function(items) {
        var token = items.token;
        if (!token) {
            token = getRandomToken();
            chrome.storage.sync.set({token: token});
        }
        settings.token = token;

        var loadImageCallback = function(uid) {
            if (window.vmSettings) {
                window.vmSettings.getSettings();
            }
            if (load_image) {
               window.vmSettings.getNewImage();
            }
        };

        var uid = items.settings_uid;
        if (uid) {
            settings.uid = uid;
            loadImageCallback(settings.uid);
        }
        else {
            $.ajax({
                url: API_URL + '/settings/new/',
                method: 'POST',
                headers: {'token': settings.token}
            }).success(function(resp) {
                chrome.storage.sync.set({"settings_uid": resp.url_identifier});
                settings.uid = resp.url_identifier;
                loadImageCallback(settings.uid);
            });
        }
    });
})(settings, true);

/* Analytics */
var _gaq = _gaq || [];

/* Vue.js */
(function() {

    var imageItem = Vue.component('earth-image', {
        template: '#image',
        props: ["image_url", "image_id", "permalink", "title", "author",
            "contain_image", "is_administrator", "favorited", "maps_url",
            "align", "is_video", "video_url", "reverse_inactive",
            "cached_image_url"],
        computed: {
            styleObject: function() {
                var background_size = this.contain_image ? "contain" : "cover";
                return {
                    backgroundImage: 'url(' + this.image_url + ')',
                    backgroundSize: background_size

                }
            },
        },
        methods: {
            toggleHistory: function () {
                vmSettings.toggleHistory();
            },
            toggleFavorites: function () {
                vmSettings.toggleFavorites();
            },
            toggleSettings: function () {
                vmSettings.show_main_index = vmSettings.show_main_index != 1 ? 1 : 0;
            },
            favoriteThisImage: function () {
                this.favorited = true;
                vmSettings.favoriteThisImage();
            },
            go_to_map: function () {
                window.open(
                    this.maps_url
                );
            },
            set_image_status: function (set_inactive) {
                var that = this;
                var method = set_inactive ? 'DELETE' : 'PUT';
                $.ajax({
                    url: API_URL + '/get/' + settings.uid + '/' + this.image_id,
                    method: method,
                    headers: {'token': settings.token}
                }).success(function() {
                    that.reverse_inactive = set_inactive;
                });
            }
        }
    });

    var historyItem = Vue.component('history', {
        template: '#history',
        props: ["index", "image_url", "permalink", "title", "image_id", "saved"],
        methods : {
            save: function () {
                this.saved = true;
                vmSettings.favoriteImage(this.image_id);
            }
        }
    });
    var favoriteItem = Vue.component('favorite', {
        template: '#favorites',
        props: ["index", "image_url", "permalink", "title", "image_id"],
        methods: {
            delete: function () {
                vmSettings.deleteFavoriteImage(this.image_id);
            },
            set_image: function () {
                vmSettings.refreshImageWithId(this.image_id);
            }
        }
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
                        return 'filter by keyword... try yosemite';
                    case 'apod':
                        return 'filter by keyword... try galaxy';
                    case 'wiki':
                        return 'filter by keyword... try president';
                    default:
                        return 'filter by keyword... try nepal';
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
            image_data: [image],
            cached_image_url: '',
            history: [],
            settings: [],
            filterNav: 0,
            setting_uid: null,
            only_favorites: false,
            only_favorites_own: false,
            allow_reddit: false,
            allow_apod: false,
            allow_wiki: false,
            allow_video: false,
            allow_wallpapers: false,
            allow_imaginarylandscapes: false,
            contain_reddit: false,
            contain_apod: false,
            contain_wiki: false,
            ratio_reddit: 1,
            ratio_apod: 1,
            ratio_wiki: 1,
            ratio_video: 1,
            ratio_wallpapers: 1,
            ratio_imaginarylandscapes: 1,
            save_copy: "Save",
            saving: false,
            loaded_history: false,
            history_items: [],
            loaded_favorites: false,
            favorite_items: [],
            needs_history_refresh: false,
            show_main_index: refreshedWithVideo ? 1 : 0,
            serialized_state: '',
            is_queued: false,
            queued_image: false,
            align: 0,
            border_css: '',
            align_info_box: 'right',
            filters: {
                all: {
                    query: Filter('query', 'global', 'all'),
                    // resolution: Filter('resolution', 'global', 'all')
                },
                reddit: {
                    query: Filter('query', 'specific', 'reddit'),
                    // score: Filter('score', 'specific', 'reddit'),
                    // resolution: Filter('resolution', 'specific', 'reddit')
                },
                apod: {
                    query: Filter('query', 'specific', 'apod'),
                    // resolution: Filter('resolution', 'specific', 'apod')
                },
                wiki: {
                    query: Filter('query', 'specific', 'wiki'),
                }
            },
        },
        // mounted: function () {
        //     this.image_data = [cachedImage];
        //     // var cachedImage = localStorage.getItem('cachedImage');
        //     // if (cachedImage !== null && cachedImage !== undefined && cachedImage !== 'undefined') {
        //     //     this.image_data = [JSON.parse(cachedImage)];
        //     // }
        // },
        computed: {
            relative_frequency: function () {
                return [
                    this.ratio_reddit,
                    this.ratio_apod,
                    this.ratio_wiki,
                    this.ratio_video,
                    this.ratio_imaginarylandscapes,
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
                if (this.allow_video) {
                    active.push(this.ratio_video)
                }
                if (this.allow_wallpapers) {
                    active.push(this.ratio_wallpapers)
                }
                if (this.allow_imaginarylandscapes) {
                    active.push(this.ratio_imaginarylandscapes)
                }
                return active;
            }
        },
        methods: {
            settingsCallback: function (that) {
                return function(resp) {
                    allowed_sources = resp.allowed_sources.split(',');
                    var source;
                    for(var i = 0; i < allowed_sources.length; i++) {
                        source = allowed_sources[i];
                        that['allow_' + source] = true;
                    }
                    var contain_data_sources = resp.contain_data_sources.split(',');
                    for(i = 0; i < contain_data_sources.length; i++) {
                        source = contain_data_sources[i];
                        that['contain_' + source] = true;
                    }
                    var relative_frequency = resp.relative_frequency.split(',');
                    var sources = ['reddit', 'apod', 'wiki', 'video', 'wallpapers'];
                    for(i = 0; i < relative_frequency.length; i++) {
                        source = sources[i];
                        var freq = parseInt(relative_frequency[i]);
                        if (isNaN(freq)) freq = 1;
                        that['ratio_' + source] = freq;
                    }
                    that.only_favorites = resp.only_favorites;
                    that.only_favorites_own = resp.only_favorites_own;
                    var filter;
                    for (i = 0; i < resp.filters.length; i++) {
                        filter = resp.filters[i];
                        source = filter['type'] === 'global' ? 'all' : filter.source;
                        var object = that.filters[source][filter.filter_class];
                        object.loadArguments(filter.arguments);
                        object.updateFields(that.getComponent(object));
                    }
                    if (isNaN(resp.align)) resp.align = 0;
                    that.align = resp.align;
                }
            },
            getSettings: function () {
                $.ajax({
                    url: API_URL + '/settings/' + settings.uid,
                    method: 'GET',
                    headers: {'token': settings.token}
                }).success(this.settingsCallback(this))
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
                    allow_video: this.allow_video,
                    allow_wallpapers: this.allow_wallpapers,
                    allow_imaginarylandscapes: this.allow_imaginarylandscapes,
                    contain_reddit: this.contain_reddit,
                    contain_apod: this.contain_apod,
                    contain_wiki: this.contain_wiki,
                    contain_video: false,
                    filters: this.serializerFilters(),
                    token: settings.token,
                    relative_frequency: this.relative_frequency,
                    align: this.align,
                    only_favorites: this.only_favorites,
                    only_favorites_own: this.only_favorites_own
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
                    that.loaded_history = true;
                    that.needs_history_refresh = false;
                }
            },
            getHistory: function () {
                this.show_main_index = 2;
                _gaq.push(['_trackEvent', 'show history', 'clicked']);
                if (!this.loaded_history || this.needs_history_refresh) {
                    $.ajax({
                        url: API_URL + '/settings/history/' + settings.uid,
                        headers: {'token': settings.token}
                    }).success(this.getHistoryCallback(this));
                }
            },
            getFavoriteCallback: function(that, resp) {
                return function (resp) {
                    that.favorite_items = resp;
                    that.loaded_favorites = true;
                }
            },
            loadFavorites: function () {
                $.ajax({
                    url: API_URL + '/favorite/' + settings.uid,
                    headers: {'token': settings.token}
                }).success(this.getFavoriteCallback(this));
            },
            getFavorites: function () {
                this.show_main_index = 3;
                _gaq.push(['_trackEvent', 'show favorites', 'clicked']);
                if (!this.loaded_favorites) {
                    this.loadFavorites();
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
                this.needs_history_refresh = true;
                if (this.queued_image) {
                    return;
                } else {
                    this.queued_image = true;
                }
                setTimeout(function(that) {
                    return function () {
                        localStorage.removeItem('cachedImage');
                        that.getNewImage(true);
                        that.queued_image = false;
                    }
                }(this), 300);
            },
            toggleHistory: function () {
                this.show_main_index = this.show_main_index === 2 ? 0 : 2;
                if (this.show_main_index === 2) {
                    this.getHistory();
                }
            },
            toggleFavorites: function () {
                this.show_main_index = this.show_main_index === 3 ? 0 : 3;
                console.log('here')
                if (this.show_main_index === 3) {
                    console.log('there')
                    this.getFavorites();
                }
            },
            getNewImage: function (is_refresh) {
                var url = API_URL + '/get';
                if (settings.uid) {
                    url += '/' + settings.uid;
                }
                url += '?width=' + window.innerWidth + '&height=' + window.innerHeight;
                var successCallback = (function(that) {
                    return function (resp) {
                        cachedImage = localStorage.getItem('cachedImage');
                        localStorage.removeItem('cachedImage');
                        localStorage.setItem('cachedImage', JSON.stringify(resp));
                        if (cachedImage === null) {
                            that.image_data = [resp];
                            setImage(resp);
                            if (!resp.is_video) {
                                that.getNewImage();
                            }
                        } else {
                            if (!resp.is_video) {
                                that.cached_image_url = resp.preferred_image_url;
                            }
                        }
                        if (is_refresh && resp.is_video) {
                            var extension = refreshedWithVideo ? '' : '?refreshed=1';
                            window.location.href = window.location.href + extension;
                        }
                    }
                })(this);
                $.getJSON(url)
                    .success(successCallback).fail(function () {
                        console.log('Image Request Failed');
                });
            },
            favoriteImage: function (image_id) {
                var that = this;
                $.ajax({
                    url: API_URL + '/favorite/' + settings.uid + '/' + image_id,
                    method: 'POST',
                    headers: {'token': settings.token}
                }).success(function() {
                    that.loadFavorites();
                });
            },
            favoriteThisImage: function () {
                _gaq.push(['_trackEvent', 'favorite item', 'clicked']);
                var image = this.image_data[0];
                this.favoriteImage(image.id);
            },
            deleteFavoriteImage: function(image_id) {
                _gaq.push(['_trackEvent', 'favorite item deleted', 'clicked']);
                var that = this;
                $.ajax({
                    url: API_URL + '/favorite/' + settings.uid + '/' + image_id,
                    method: 'DELETE',
                    headers: {'token': settings.token}
                }).success(function() {
                    that.loadFavorites();
                });
            },
            setAlign: function(num) {
                this.align = num;
                this.queueSettingsUpdate();
            },
            refreshImageWithId: function(image_id) {
                var that = this;
                $.ajax({
                    url: API_URL + '/get/' + settings.uid + '/' + image_id,
                    method: 'GET',
                    headers: {'token': settings.token}
                }).success(function(resp) {
                    that.image_data = [resp];
                    setImage(resp);
                });
            },
            favoritesChange: function(event) {
                var selected_own = event.target.name === 'only_favorites_own';
                var selected_general = event.target.name === 'only_favorites';
                if (selected_own && this.only_favorites) {
                    this.only_favorites = false
                }
                if (selected_general && this.only_favorites_own) {
                    this.only_favorites_own = false;
                }
                this.queueSettingsUpdate();
            },

        }
    });
    window.vmSettings = vmSettings;
})();