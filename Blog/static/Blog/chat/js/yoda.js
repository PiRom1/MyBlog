function playYodaSound() {
    
    var audioPlayer = document.getElementById('audio-player');
    var audioSource = document.getElementById('audio-source');
    var yoda_sounds = document.getElementById("yoda_sounds").innerHTML;
    var static_url = document.getElementById("yoda_sounds").getAttribute("url");

    yoda_sounds = yoda_sounds.replace(/'/g, '"');
    yoda_sounds = JSON.parse(yoda_sounds);

    var randomNumber = Math.floor(Math.random() * yoda_sounds.length);
    var sound = yoda_sounds[randomNumber];
    console.log("Sound : ", sound);

    audioSource.src = static_url + sound;


    // Recharger et jouer le nouveau fichier audio
    audioPlayer.load();
    audioPlayer.play();

};

// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    var yoda = document.getElementById('yoda');
    yoda.addEventListener('click', playYodaSound);
});

