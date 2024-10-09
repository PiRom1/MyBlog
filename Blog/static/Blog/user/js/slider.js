

document.addEventListener('DOMContentLoaded', function () {
   
    const sliderInput = document.getElementById('slider');
    const sliderValue = document.getElementById('slider_value');
    const graph = document.getElementById('graph');
    let timeout; // Variable pour stocker le timer de debouncing

    getSlider = function() {

        clearTimeout(timeout);


        timeout = setTimeout(() => {
            let value = sliderInput.value; // Récupérer la valeur de l'input
            sliderValue.textContent = value; // Mettre à jour le texte du span
            console.log(sliderValue.textContent); // Afficher la valeur dans la console

            fetch(`/update_plot/?value=${value}`, {
                method: 'GET',
            })
            .then(response => response.json())
            .then(data => {
                // console.log(data);
                console.log(data.plot);
                
                graph.src = 'data:image/png;base64,'+data['plot'];
                console.log(graph.src);
                
                
                
            })
            .catch(error => console.error('Error:', error));
    }, 300);
    

};
    

    sliderInput.addEventListener('input', getSlider);
    
});
