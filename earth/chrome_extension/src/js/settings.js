/****** Settings *****

1. without any settings specified, will operate on default values
2. if settings are visited, ask API to provide new UID
3. on save, POST to backend using UID to link to settings object
    - auth/security not *really* necessary but might be a nice-to-have
4. earth.js will fetch UID (from chrome.storage) and use to make API image request


*/
var API_URL = 'https://earth-pics.tk/api/v0/earth/get';
function getNewImage() {
    $.getJSON(API_URL)
        .success(function(resp) {
            newImage = resp;
            $('body').css("background-image", "url('" + newImage.preferred_image_url + "')");
        }).fail(function () {
            console.log('Image Request Failed');
        });
}
getNewImage();


chrome.storage.sync.get("settings_uid", function(item) {
    if (item === null) {
        $.getJSON('https://earth-pics.tk/api/v0/earth/settings/new', function(item) {
            chrome.storage.sync.set({"settings_uid": item.url_identifier});
        });
    }
});


