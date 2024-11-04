

document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const tkt_button = document.getElementById('tkt-btn');
    var popup = document.getElementById('tkt-popup');

    // Afficher popup texte

    // Get new text
    console.log('hey !');
    tkt_button.addEventListener('click', function() {

        const url = '/tkt';

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin',
            })        
        .then(response => response.json())
        .then(data => {
            console.log(data);
            popup.innerHTML = data['text'];
            popup.style.display = 'block';
            })
        })

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.tkt-popup')) {
            popup.style.display = 'none';
        }
    });




})