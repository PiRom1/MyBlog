

document.addEventListener('DOMContentLoaded', function () {
    
    
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const totalCheckBox = parseInt(document.getElementById('yoda').getAttribute('nb_sounds'));
    console.log('nb sounds : ', parseInt(totalCheckBox)); 

        
   
    function updateCheckBox(sound) {
        console.log("sound : ", sound);
        fetch("/update_soundbox/?sound="+sound, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,  // Obtenez le token CSRF
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('Mise à jour réussie:', data);
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
    };
    

    
    // Ajoute des écouteurs d'événements pour chaque bouton
    for (let i = 1; i <= totalCheckBox; i++) {
        const speaker = document.getElementById('input_'+i);
        const sound = document.getElementById('id_'+i).getAttribute('sound_id');
        speaker.addEventListener('change', function() {updateCheckBox(sound)})
        console.log(speaker.checked);
        
    }
   
});


