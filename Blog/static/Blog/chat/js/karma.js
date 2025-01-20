// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    
    // Get every messages
    const messages = document.querySelectorAll('.text');
    

    var i = 0;
    // Loop on messages
    messages.forEach((message) => {
        karma = message.getAttribute('karma');
        console.log("karma : ", karma);
        console.log(message);
        message.addEventListener('click', function() {
            console.log('karma du message : ', karma);
          });

    });
})