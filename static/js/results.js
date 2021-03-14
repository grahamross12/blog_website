// $(document).ready(function(){
//     $(".save-button").submit(function() {
//         e.preventDefault();
//         document.write('hello');
//         $.ajax({

//             type: 'POST',
//             url: '/save',
//         })
//         return false;
//     });
// });

function saveArticle(title, elem) {
    $.ajax({
            type: 'POST',
            url: '/save',
            data: {'title': title}
        })
    elem.find(">:first-child").toggleClass('saved');
    return
}
