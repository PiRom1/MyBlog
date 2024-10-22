

// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    var items = document.getElementById('items');
    
    var textColor = items.getAttribute('text-color');
    var borderColor = items.getAttribute('border-color');

    console.log("text color : ", textColor);
    console.log("border color : ", borderColor);

    // Text color
    const messageTexts = document.querySelectorAll('.text');
        
    messageTexts.forEach((text) => {
        text.style.setProperty("color", textColor, 'important');  // Change la couleur ici
    });


    // Border color
    const messageTexts = document.querySelectorAll('.text');
        
    messageTexts.forEach((text) => {
        text.style.setProperty("color", textColor, 'important');  // Change la couleur ici
    });

});

