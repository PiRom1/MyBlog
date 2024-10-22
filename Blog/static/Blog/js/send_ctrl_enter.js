

document.addEventListener('DOMContentLoaded', function () {
    // Sélectionne le textarea
    var textarea = document.querySelector('textarea[name="message"]');
    
    // Ajoute un écouteur d'événements pour capturer "Ctrl + Enter"
    textarea.addEventListener('keydown', function (e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault(); // Empêche le saut de ligne par défaut
            document.getElementById('message_form').submit(); // Soumet le formulaire
        }
    })
});
