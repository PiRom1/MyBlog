
document.addEventListener('DOMContentLoaded', function () {
    
    
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const totalSpeakers = parseInt(document.getElementById('yoda').getAttribute('nb_sounds'));
    console.log('nb sounds : ', parseInt(totalSpeakers)); 

        
   
    function playSound(i) {
        console.log('1');
        var sound = document.getElementById('sound_'+i);
        const url = document.getElementById('id_'+i).getAttribute('url');
        console.log(url);
        var source = document.getElementById('source_'+i);

        var sound_id = document.getElementById('id_'+i).getAttribute('sound_id');
        
        fetch("/increment_sound/?sound="+sound_id, {
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


        source.src = url;

        console.log(source.src);
        
    
        // Recharger et jouer le nouveau fichier audio
        sound.load();
        sound.play();
        

    
    };
    
    // Ajoute des écouteurs d'événements pour chaque bouton
    for (let i = 1; i <= totalSpeakers; i++) {
        const speaker = document.getElementById('id_'+i);
        console.log(i);
        speaker.addEventListener('click', function() {
            playSound(i);
        });
    }
   
});


