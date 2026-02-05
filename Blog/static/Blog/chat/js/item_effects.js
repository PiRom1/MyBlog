
document.addEventListener('DOMContentLoaded', function () {
    
    // Get every messages
    const messages = document.querySelectorAll('.message');
    const font_tab = []
    const rgb_tab = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08'];
    var favorite_fonts = document.getElementById('items').getAttribute('fonts');
    favorite_fonts = favorite_fonts.replace(/'/g,'"');
    favorite_fonts = JSON.parse(favorite_fonts);

    favorite_fonts.forEach((font) => {
        font_tab.push(font);
    })


    // Change bg image
    var bg_image = document.getElementById('items').getAttribute('background');

    if (bg_image != '') {
        document.body.style.backgroundImage = `url(${bg_image})`;
    }



    var i = 0;
    // Loop on messages
    messages.forEach((message) => {

        // Get skins
        skins = message.querySelector(".text").getAttribute('skins');
        if (skins === '') {
            skins = "{}";
        }
        if (message.id === "example-text") {
            return;
        } // Pas de skin pour le message d'exemple
        if (skins) {
            skins = skins.replace(/'/g, '"');
            skins = JSON.parse(skins);
            let message_font = set_skins_to_message(message, skins);
            if (font_tab.includes(message_font) === false) {
                        font_tab.push(message_font);
                    }
        }

        
    });


    var font = document.createElement('link');
    font.rel = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?' 
    for (var f in font_tab) {
        font.href += 'family=' + font_tab[f].replace(/ /g, '+') + '&';
    }
    font.href += 'display=swap';
    document.head.appendChild(font);
});

