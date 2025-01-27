// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    
    // Get every messages
    const messages = document.querySelectorAll('.message-content');
    
    console.log(messages);
    var i = 0;
    // Loop on messages
    messages.forEach((message) => {
        karma = message.getAttribute('karma');
        console.log("karma : ", karma);
        console.log(message);
        message.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            const karma = message.getAttribute('karma').split('>')[0];
            console.log('karma du message : ', message.getAttribute('karma'));
            const texte = document.createElement("span");
            texte.textContent = karma;
            texte.style.position = "absolute";
            texte.style.left = `${e.pageX}px`;
            texte.style.top = `${e.pageY}px`;
            texte.style.background = "rgba(237, 213, 168, 0.75)";
            texte.style.padding = "5px";
            texte.style.border = "1px solid black";
            texte.style.borderRadius = "5px";
            document.body.appendChild(texte);
            setTimeout(() => texte.remove(), 500);
          });

    });


})