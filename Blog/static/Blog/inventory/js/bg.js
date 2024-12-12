


// JavaScript pour gérer les événements de clic
document.addEventListener('DOMContentLoaded', function () {

    const form = document.getElementById('bg_form');
    console.log(form);

    form.addEventListener('change', function(event){
        
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            document.body.style.backgroundImage = `url(${e.target.result})`; // Met à jour le background
        };

        reader.readAsDataURL(file); // Lit le fichier comme URL de données


    })

});