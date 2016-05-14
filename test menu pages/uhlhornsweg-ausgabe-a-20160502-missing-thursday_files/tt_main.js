/***
 ***** TorTags *****
 ***/

function ttShowSearchBox() {
    $('tth').set('class', 'tt-hide');
    $('tt-search').set('class', 'tt-show');
}

function ttShowAlltags(el) {
    var hlink = el + '_all';
    $(el).set('class', 'tt_show_tags');
    $(hlink).set('class', 'tt_hidden_tags');
}