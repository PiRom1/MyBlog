document.addEventListener('DOMContentLoaded', function() {

    function fade_audio(audio, mode, duration = 1000) {
        let stepTime = 50; // ms entre chaque baisse de volume
        let steps = duration / stepTime;
        let currentStep = 0;

        let fade = setInterval(() => {
            currentStep++;
            if (mode === 'fadeout') {
                audio.volume = Math.max(1 - currentStep / steps, 0);
            }
            if (mode === 'fadein') {
                audio.play();
                audio.volume = Math.max(currentStep / steps, 0);
            }

            if (currentStep >= steps) {
                clearInterval(fade);
                if (mode === "fadeout") {
                    audio.pause();
                }
            }
        }, stepTime);
}


    
    // Background Audio

    var audio = new Audio("/static/music/dinocrypt/dungeon.mp3");


    const speaker = document.getElementById("speaker");

    const muted_speaker_class = "fi fi-ss-volume-slash";
    const speaker_class = "fi fi-rs-volume";

    speaker.classList = speaker_class;
    speaker.classList = muted_speaker_class;
    let fadeout_time = 2 // nb of seconds to fadeout / fadein
    

    speaker.addEventListener('click', function() {
        console.log(speaker);
        const speaker_value = speaker.getAttribute("value");

        if (speaker_value === 'false') { // Set to True
            speaker.setAttribute('value', 'true');
            speaker.classList = speaker_class;
            fade_audio(audio, 'fadein', fadeout_time * 1000);

        }
        else { // Set to False
            speaker.setAttribute('value', 'false');
            speaker.classList = muted_speaker_class;
            fade_audio(audio, 'fadeout', fadeout_time * 1000);           
        }
    })


})