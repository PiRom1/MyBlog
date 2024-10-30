
document.addEventListener('DOMContentLoaded', function () {
    
    const filter = document.getElementById('filter');
    const sounds = document.querySelectorAll('.data');

    console.log(sounds);


    function transform_text(text) {
        text = text.toLowerCase().replace(/ /g,'').replace(/_/g,' ').replace(/-/g,' ').replace(/'/g,' ');

        return(text);
    }




    function filtering() {

        sounds.forEach(sound => {

            var tags = transform_text(sound.getAttribute('tags'));
            var name = transform_text(sound.getAttribute('name'));
            
            console.log('tags ; ', tags, 'name : ', name);

            if (tags.includes(transform_text(filter.value)) || name.includes(transform_text(filter.value)) ) {
                sound.style.display= 'block';
                console.log('présent');
            }
            else {
                sound.style.display = 'none';
                console.log('absent');
            }


        });
   
        
    }


    filter.addEventListener('input', filtering);
        
});


