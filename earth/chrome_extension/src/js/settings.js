/****** Settings *****

1. without any settings specified, will operate on default values
2. if settings are visited, ask API to provide new UID
3. on save, POST to backend using UID to link to settings object
    - auth/security not *really* necessary but might be a nice-to-have
4. earth.js will fetch UID (from chrome.storage) and use to make API image request


*/
var API_URL = 'https://earth-pics.tk/api/v0/earth';
var getNewImage = function() {
    $.getJSON(API_URL + '/get')
        .success(function(resp) {
            newImage = resp;
            $('body').css("background-image", "url('" + newImage.preferred_image_url + "')");
        }).fail(function () {
            console.log('Image Request Failed');
        });
};

var loadSettings = function() {
  $.getJSON(API_URL + '/settings/' + settings.uid).success(function (resp) {
        $('#query').val(resp.query_keywords_title);
        $('#vote_type').val(resp.score_type);
        $('#threshold').val(resp.score_threshold_operand);
        $('#threshold_value').val(resp.score_threshold);
        $('#resolution_type').val(resp.resolution_type);
        $('#resolution_threshold').val(resp.resolution_threshold_operand);
        $('#resolution_threshold_value').val(resp.resolution_threshold);

        allowed_sources = resp.allowed_sources.split(',');
        var source;
        for(var i; i < allowed_sources.length; i++) {
            source = allowed_sources[i];
            $('#allow_' + source).prop('checked');
        }
    });
};
getNewImage();


var addAsQueryParams = function(url, values) {
    queries = [];
    Object.keys(values).forEach(function(key, index) {
        queries.push(key + '=' + values[key]);
    });
    return url + '?' + queries.join('&');
};

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
    loadSettings();
});


$('form').on('submit', function (e) {
    e.preventDefault();
    var values = {
        query_keywords_title: $('#query').val(),
        score_type: $('#vote_type').val(),
        score_threshold_operand: $('#threshold').val(),
        score_threshold: $('#threshold_value').val(),
        resolution_type: $('#resolution_type').val(),
        resolution_threshold_operand: $('#resolution_threshold').val(),
        resolution_threshold: $('#resolution_threshold_value').val(),
        allow_reddit: $('#allow_reddit').prop('checked'),
        allow_apod: $('#allow_apod').prop('checked')
    };
    var url = addAsQueryParams(API_URL + '/settings/save/' + settings.uid, values);
    console.log(url);
    $.get(url).success(function(resp) {
        $('input[type=submit]').val('Saved!').addClass('saved');
        setTimeout(function() {
            $('input[type=submit]').val('Save').removeClass('saved');
        }, 1000);
        localStorage.clear();
    });
});
