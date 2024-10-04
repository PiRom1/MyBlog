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
        .then(response => {
            console.log(response);
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


function getCSRFToken() {
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return csrfToken;
}



function incrementCounter() {
    
    fetch('/increment/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // Récupération du token CSRF
        },
        body: JSON.stringify({})
    }).then(response => response.json())
      .then(data => console.log(data));
}