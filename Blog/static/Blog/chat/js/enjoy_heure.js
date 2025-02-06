
document.addEventListener('DOMContentLoaded', function () {
    const enjoy_popup = document.getElementById('enjoy-heure');
    const enjoy = document.getElementById('enjoy');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


    document.addEventListener('click', function(e){
        if (!e.target.closest('.enjoy-heure')) {
            enjoy_popup.style.display = 'none';
        }
    })

    enjoy.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        fetch('/ask_heure_enjoy', {
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
            enjoy_popup.style.display = 'block';
            enjoy_popup.innerHTML = data.message;
        })
    })

    
       





})