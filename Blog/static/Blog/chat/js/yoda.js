

// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    var yoda = document.getElementById('yoda');
    var enjoy = document.getElementById('enjoy');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function incrementCounter(link) {
        
        fetch('/'+link +'/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({})
        }).then(response => response.json())
        .then(data => console.log(data));
    }


    function playYodaSound() {
    
        var audioPlayer = document.getElementById('audio-player');
        var audioSource = document.getElementById('audio-source');
        var yoda_sounds = document.getElementById("yoda_sounds").innerHTML;
        
    
        yoda_sounds = yoda_sounds.replace(/'/g, '"');
        yoda_sounds = JSON.parse(yoda_sounds);
    
        var randomNumber = Math.floor(Math.random() * yoda_sounds.length);
        var sound = yoda_sounds[randomNumber];
        console.log("Sound : ", sound);
    
        audioSource.src = sound;
        console.log(audioSource.src);

        fetch('/increment_sound/?sound='+sound, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({})
        }).then(response => response.json())
        .then(data => console.log(data));
    

    
        // Recharger et jouer le nouveau fichier audio
        audioPlayer.load();
        audioPlayer.play();
    
    };
    
    
    
    
    enjoy.addEventListener('click', function() {incrementCounter('increment_enjoy')});
    yoda.addEventListener('click', function() {incrementCounter('increment_yoda')});
    yoda.addEventListener('click', playYodaSound);
});

