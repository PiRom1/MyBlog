

document.addEventListener('DOMContentLoaded', function () {
    // Sélectionne le textarea
    
    const form = document.getElementById('message_form');
    var message_form = document.getElementById('message_html');
    const message = document.getElementById('message_content');

    const submit_button = document.getElementById('submit');

    
    console.log('envoi !');


    function send_message(e) {
    
        if (message.innerHTML.trim() === '') {
            alert('Veuillez entrer un message.');
            return; // Ne rien faire si le message est vide
        }

        console.log("texte du message : ", message.textContent, message.innerHTML);
        var message_text = message.innerHTML;
        message_text = message_text.replace(/&lt;/g, '<');
        message_text = message_text.replace(/&gt;/g, '>');
        console.log(message_text);
        // Remplit le champ caché avec le contenu HTML
        message_form.value = message_text;

        console.log('Envoi !', message_form.value, message_text,  message.innerHTML);

        // Soumet le formulaire
        form.submit();
    
    };

    // Ajoute un écouteur d'événements pour capturer "Ctrl + Enter"
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            console.log('salut');
            e.preventDefault();
            send_message();
        }
    });

    submit_button.addEventListener('click', send_message);
});
