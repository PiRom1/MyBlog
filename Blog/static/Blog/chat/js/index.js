document.addEventListener('DOMContentLoaded', function () {
    var loadMoreBtn = document.getElementById('load-more');
    var session = document.querySelector('.container').id;

    loadMoreBtn.addEventListener('click', function () {
        console.log('Load more button clicked');
        var page = parseInt(loadMoreBtn.getAttribute('data-next-page'), 10);
        console.log(page);

        // Requête AJAX pour obtenir plus de messages
        url = `/${session}/?page=${page}`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
            }
        })
        .then(response => response.json())
        .then(data => {
            var messagesContainer = document.querySelector('.messages');
            messagesContainer.innerHTML = '';
            // Ajouter les nouveaux messages au début
            messagesContainer.insertAdjacentHTML('afterbegin', data.messages_html);

            // Met à jour l'offset
            loadMoreBtn.setAttribute('data-next-page', page + 1);
            console.log(loadMoreBtn);
        });
    });
});