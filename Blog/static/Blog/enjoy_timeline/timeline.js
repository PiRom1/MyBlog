document.addEventListener('DOMContentLoaded', function () {


    // Get data
    const squares = document.querySelectorAll('.square');
    const hour_panel = document.getElementById('hour-panel');
    const data = document.getElementById("data");

    const timestamps_data = JSON.parse(data.getAttribute("data"));
    const default_stamp_color = JSON.parse(data.getAttribute("default_stamp_color"));
    const default_note_color = JSON.parse(data.getAttribute("default_note_color"));

    console.log("timestamps data : ", timestamps_data);

    let color_type = "stamps_color";


    function colorize_squares() {

        squares.forEach(square => {
            console.log(square);

            var hour = square.getAttribute('hour');
            var minute = square.getAttribute('minute');

            let key = `${hour}_${minute}`;
            let square_color;


            if (!(key in timestamps_data)) {
                console.log("key ", key," not in data")
                if (color_type === "stamps_color") {
                    square_color = default_stamp_color;
                }
                else {
                    square_color = default_note_color;
                }
                
            }
            else {
                square_color = timestamps_data[key][color_type];
            }

            console.log(square_color, typeof(square_color));
            const rgbColor = `rgb(${square_color[0]}, ${square_color[1]}, ${square_color[2]})`;

            square.style.backgroundColor  = rgbColor;
        })
    }


    
    // Loop à travers les éléments
    squares.forEach((square, index) => {
        var hour = square.getAttribute('hour');
        var minute = square.getAttribute('minute');

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


    // Colorization of squares

    const notes_color = document.getElementById("notes_color");
    const stamps_color = document.getElementById("stamps_color");

    stamps_color.style.fontWeight = 'bold';

    notes_color.addEventListener('click', function() {
        notes_color.style.fontWeight = 'bold';
        stamps_color.style.fontWeight = '';
        color_type = "notes_color";
        colorize_squares();
    })


    stamps_color.addEventListener('click', function() {
        notes_color.style.fontWeight = '';
        stamps_color.style.fontWeight = 'bold';
        color_type = "stamps_color";
        colorize_squares();
    })

    colorize_squares();



    // Add timestamp
    const add_stamp = document.getElementById("add_stamp");

    add_stamp.style.textDecoration = 'underline';
    add_stamp.style.cursor = 'pointer';

    add_stamp.addEventListener('click', function() {
        let date = new Date();
        console.log(date);
        window.location.href = `${date.getHours()}/${date.getMinutes()}`;

    })




})