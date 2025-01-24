document.addEventListener('DOMContentLoaded', function () {


    const squares = document.querySelectorAll('.square');
    const hour_panel = document.getElementById('hour-panel');
    let nb = document.getElementById("nb").getAttribute("nb");
    nb = nb.replace(/'/g, '"');
    nb = JSON.parse(nb);

    let colors = document.getElementById("colors").getAttribute("colors");
    colors = colors.replace(/'/g, '"');
    colors = JSON.parse(colors);

        
        // Loop à travers les éléments
        squares.forEach((square, index) => {
            var hour = square.getAttribute('hour');
            var minute = square.getAttribute('minute');

            const square_nb = nb[`${hour}_${minute}`];
            const square_color = colors[`${hour}_${minute}`];
           

            const rgbColor = `rgb(${square_color.join(',')})`;

            square.style.backgroundColor  = rgbColor;

            

            square.addEventListener('mousemove', function(e) {

                hour_panel.innerHTML = `${hour}h${minute}`;
                hour_panel.style.display = 'block';
                hour_panel.style.position = 'absolute';
                hour_panel.style.left = (e.pageX - hour_panel.clientWidth) + 'px';
                hour_panel.style.top = e.pageY - hour_panel.clientHeight + 'px';
                

            })

            square.addEventListener('mouseout', function() {
                hour_panel.style.display = 'none';
            })

            square.addEventListener('click', function() {
                window.location.href=`/enjoy_timeline/${hour}/${minute}`;
            })


        });


})