function saveArticle(title, url, image_url, description, elem, user_id) {
	if (!user_id) {
		let host = window.location.hostname
    	window.location.href =  "/login";
    	return
    }
    elem.find(">:first-child").toggleClass('saved');
        $.ajax({
            type: 'POST',
            url: '/saving',
            data: {'title': title,
                   'url': url,
                   'image_url': image_url,
                   'description': description}
        });
    return
}


function check_results(saved_titles) {
    let elems = $('.post-container');
    let title_elems = elems.find('.article-title');
    if (saved_titles == null || title_elems == null) {
        return;
    }
    for (var i = 0; i < saved_titles.length; i++) {
        for (let j = 0; j < title_elems.length; j++) {
            if (saved_titles[i] === title_elems[j].text) {
                elems.eq(j).find('.plus').addClass('saved');
            }
        }
    }
    return
}


function check_results_homepage(saved_titles) {
    let elems = $('.post-container-small-all');
    let title_elems = elems.find('.article-title-text');
    console.log(title_elems[1].innerText)
    
    if (saved_titles == null || title_elems == null) {
        return;
    }
    for (var i = 0; i < saved_titles.length; i++) {
        
        for (let j = 0; j < title_elems.length; j++) {
            if (saved_titles[i] === title_elems[j].innerText) {
                elems.eq(j).find('.plus').addClass('saved');
            }
        }
    }
    return
}

// function load_more_results(query, page) {
//     $.ajax({
//         type: 'GET',
//         url: '/results',
//         data: {'query': query,
//                'page': page}
//         success: function(response) {
//         $("#place_for_suggestions").html(response);
//       },
//     });
    

//     return false;
// }