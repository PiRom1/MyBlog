document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Variables
    var plus = document.getElementById('plus');
    const first_pari = document.getElementById('first_pari');
    let nb_issues = 2;
    const submit_button = document.getElementById('submit');
    let error;

    // Forms
    const pari_name = document.getElementById('pari_name');
    const pari_description = document.getElementById('pari_description');
    const pari_duration = document.getElementById('pari_duration');


    function create_issue() {
        let newDiv = document.createElement('div');
        newDiv.innerHTML = `Issue ${nb_issues} : <input class="pari_issue" type="text" name="Issue"><br>`;
        
        plus.parentNode.insertBefore(newDiv, plus);
        newDiv.querySelector('input').focus();
    }    

    function afficher_erreur(erreur) {
        if (error) {
            error.innerHTML = '';
        }
        error = document.createElement('div');
        error.style.color = 'tomato';
        error.innerHTML = `Attention ! ${erreur}`;
        
        plus.parentNode.appendChild(error, plus);
    } 
    
    plus.addEventListener('click', function() {
        nb_issues += 1;
        create_issue();
    })


    submit_button.addEventListener('click', function() {
        const pari_issues = document.querySelectorAll('.pari_issue');


        var issues = Array.from(pari_issues).map(f => f.value);
        
        fetch('/paris/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken // Assurez-vous d'ajouter le token CSRF ici
            },
            body: JSON.stringify({'name': pari_name.value,
                'description' : pari_description.value,
                'duration' : pari_duration.value,
                'issues' : issues}) // Envoyer l'ID de l'item
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success === true) {
                window.location.href = '/paris';
            }
            else {
                afficher_erreur(data.error);
            }
        });

    })
    


});