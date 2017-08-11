/**
 * Created by lucasbrambrink on 8/5/17.
 */


function setImage(imageData) {
    $('.image').css("background-image", "url('" + imageData.preferred_image_url + "')");
    if (imageData.contain_image) {
        $('.image').css("background-size", "contain");
    }
    $('.title')
        .attr("href", imageData.permalink)
        .html(imageData.title);
    $('.author').html("-- " + imageData.author);
    $('.ups').html(imageData.ups);
    setLastSeenImage(imageData);
}

var getNewSettings = function () {
    $.getJSON(API_URL + '/settings/new/')
        .success(function(resp) {
            chrome.storage.sync.set({"settings_uid": resp.url_identifier});
            settings['uid'] = resp.url_identifier;
            console.log('success!', resp);
        })
        .fail(function (resp) {
            console.log(resp);
        });
};
