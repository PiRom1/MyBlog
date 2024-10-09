

document.addEventListener('DOMContentLoaded', function () {
   
    const sliderInput = document.getElementById('slider');
    const sliderValue = document.getElementById('slider_value');
    const graph = document.getElementById('graph');
    const viewed_user = graph.getAttribute('viewed_user');
    console.log(viewed_user);
    let timeout; // Variable pour stocker le timer de debouncing

    getSlider = function() {

        clearTimeout(timeout);


        timeout = setTimeout(() => {
            let value = sliderInput.value; // Récupérer la valeur de l'input
            sliderValue.textContent = value; // Mettre à jour le texte du span
            console.log(sliderValue.textContent); // Afficher la valeur dans la console

            fetch(`/update_plot/?value=${value}&user=${viewed_user}`, {
                method: 'GET',
            })
            .then(response => response.json())
            .then(data => {
                                
                graph.src = 'data:image/png;base64,'+data['plot'];
               
            })
            .catch(error => console.error('Error:', error));
    }, 150);
    

};
    

    sliderInput.addEventListener('input', getSlider);
    
});
