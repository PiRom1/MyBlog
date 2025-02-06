
// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    var enjoy = document.getElementById('enjoy_link');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


    enjoy.addEventListener('click', function() {

        fetch('/increment_enjoy/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({})
        }).then(response => response.json())
        .then(data => console.log(data));
    });

});
    