
// Afficher le formulaire lorsque le mot est cliqué
$('#ouvrirFormulaire').click(function() {
    // console.log('test');
    // $('#formContainer').toggle();  // Afficher/cacher le formulaire

    let elements = [document.getElementById('formContainer'), document.getElementById('fieldsContainer')];

    elements.forEach(function(element) {
        if (element.style.display === 'none') {
            element.style.display = 'block';
        }
        else {
            element.style.display = 'none';
        }
    });
});

// // Gestionnaire de soumission de formulaire via AJAX
// $('#monFormulaire').on('submit', function(event) {
//     event.preventDefault();  // Empêcher le rechargement de la page
//     console.log('oui')
//     $.ajax({
//         type: 'POST',
//         url: '{% url "UserView" %}',  // Assure-toi d'avoir le bon nom de la vue
//         data: $(this).serialize(),  // Envoyer les données du formulaire
//         success: function(response) {
//             $('#message').html('<p>' + response.message + '</p>');
//             $('#monFormulaire')[0].reset();  // Réinitialiser le formulaire
//         },
//         error: function(xhr) {
//             $('#message').html('<p>Une erreur s\'est produite : ' + xhr.responseJSON.errors + '</p>');
//         }
//     });
// });

