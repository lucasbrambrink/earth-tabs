// Get Options

chrome.topSites.get(top_sites);

var random_sub = [];

function restore_options() {

    chrome.storage.sync.get({
        show_title: true,
        show_sites: false,
        subreddits: true
    }, function (items) {


        if (items.show_title == false) {
            $('.info').css('display', 'none');
        }
        if (items.show_sites == true) {
            $('.top_sites').css('display', 'inherit');
        }

        subreddit = items.subreddits;
        x = 0;
        for (var index in subreddit) {

            if (subreddit[index] == 1) {
                //    console.log(index);
                random_sub[x] = index;
                x++;
            }

        }

        subreddit = random_sub[Math.floor(Math.random() * random_sub.length)];
        if (subreddit == null) {
            subreddit = 'earthporn';
        }

        new_photo(subreddit);

    });

}

// Attempt to get a photo from local storage


var photo = localStorage.getItem('photo');
if (photo == null) {

    // If a photo doesn't exist, retrieve one from server and set it as localStorage item
    new_photo();

    var photo = localStorage.getItem('photo');

}

// Parse the image data
the_image = JSON.parse(photo);

$('.background').css("background-image", "url('" + the_image.url + "')");

$('.title').attr("href", "http://reddit.com" + the_image.permalink);
$('.title').html(the_image.title);
$('.author').html("By " + the_image.author);
$('.ups').html(the_image.ups);
$('.info').css('opacity', '0.6');


// cache photo as previous
var lastPhoto = localStorage.getItem('lastPhoto');
if (lastPhoto == null) {
    $('.last-title').remove();
} else {
    $('.last-title').attr('href', "http://reddit.com" + lastPhoto);
}
localStorage.setItem('lastPhoto', the_image.permalink);

function new_photo(subreddit) {

    $.getJSON("http://tab.pics/api/" + subreddit, function (data) {
        data.data_uri = null;
        var dataToStore = JSON.stringify(data);
        localStorage.removeItem('photo');
        localStorage.setItem('photo', dataToStore);

    }).fail(function () {
        trackError('Image Request Failed');
    });

}

function top_sites(data) {

    $.each(data, function (index, value) {

        $('.top_sites').append("<div class='site_container'><div class='site'><a href='" + value.url + "'>" + value.title.substring(0, 25) + "..<div class='url'>" + value.url + "</div></div></a></div>");
        index++;
        if (index == 5)
            return false;
    });

}


document.addEventListener('DOMContentLoaded', restore_options);
