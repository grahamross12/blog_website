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
    let title_elems = $('.post-container').find('.article-title');
    let button_elems = $('.post-container').find('.plus');
    console.log(button_elems[1])
    for (var i = 0; i < saved_titles.length; i++) {
        for (let j = 0; j < title_elems.length; j++) {
            if (saved_titles[i] === title_elems[j].text) {
                console.log(j);
            }
        }
    }
}