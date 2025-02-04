document.addEventListener('DOMContentLoaded', async function () {

    const data_div = document.getElementById('data');
    let data = data_div.getAttribute('data');
    data = data.replace(/'/g, '"');
    data = JSON.parse(data);
    console.log(data);


    const plot = document.getElementById('plot');

    const layout = {
        title: {
            text: 'Scores du jeu Tracker',
            font: { color: 'ivory', size: 24 } // Couleur orange, taille 24px
        },
        xaxis: { 
            title: {
                text: 'Scores', 
                font: { color: 'white' } // Couleur du titre de l'axe X
            },
            color: 'white'
        },
        yaxis: { 
            title: {
                text: 'Index', 
                font: { color: 'white' } // Couleur du titre de l'axe X
            },
            color: 'white'
        },
        paper_bgcolor: 'rgba(245, 210, 175, 0.2)', 
        plot_bgcolor: 'rgba(255, 255, 255, 0)' 
    };



    Plotly.newPlot(plot, data, layout);

});