var subreddits_saved = {};

function save_options() {
    var show_title = document.getElementById('show_title').checked;
    var show_sites = document.getElementById('show_sites').checked;
    var subreddits = document.getElementsByClassName('subreddit');

    for (i = 0; i < subreddits.length; i++) {
        the_subreddit = subreddits[i].getAttribute('value');
        if (subreddits[i].checked) {
            //true
            subreddits_saved[the_subreddit] = 1;
        } else {
            subreddits_saved[the_subreddit] = 0;
        }
    }

    chrome.storage.sync.set({
        show_title: show_title,
        show_sites: show_sites,
        subreddits: subreddits_saved
    }, function () {

        // Update status to let user know options were saved.
        var status = document.getElementById('status');
        status.textContent = 'Options saved.';
        setTimeout(function () {
            status.textContent = '';
        }, 750);
    });
}

var saved_list = {};
function restore_options() {

    chrome.storage.sync.get({
        show_title: true,
        show_sites: false,
        subreddits: true
    }, function (items) {
        document.getElementById('show_title').checked = items.show_title;
        document.getElementById('show_sites').checked = items.show_sites;
        subreddit = items.subreddits;
        for (var index in subreddit) {
            document.getElementById('subreddit[' + index + ']').checked = subreddit[index];
        }
    });
}

document.getElementById('save').addEventListener('click',save_options);
chrome.topSites.get(top_sites);

function list_subreddits(subreddits)
{
    $.each(subreddits, function (index, value)
    {
        if(value==1) {
            $('.subreddits').append('<br/><label><input class="subreddit" type="checkbox" value="'+value+'" id="subreddit['+value+']" checked="checked"/>'+value+'</label>');
        } else {
            $('.subreddits').append('<br/><label><input class="subreddit" type="checkbox" value="'+value+'" id="subreddit['+value+']" />'+value+'</label>');
        }
    });

    restore_options();
}

var sub_list;

function get_subreddits() {
    $.getJSON("http://tab.pics/api/subreddits", function (sub_list) {
        list_subreddits(sub_list)
    }).fail(function () {
        trackError('Cant get options from server');
    });
}

get_subreddits();

function top_sites(data) {
    $.each(data, function (index, value) {
    });
	
}
