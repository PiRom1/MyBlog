document.addEventListener('DOMContentLoaded', function () {

    const comment_text = document.querySelector('label[for="id_comment"]');
    comment_text.innerHTML = '';
    console.log(comment_text);


    form = document.getElementById('form');

    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            form.submit();
        }
    })


})