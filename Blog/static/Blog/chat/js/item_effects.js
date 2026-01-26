
document.addEventListener('DOMContentLoaded', function () {
    
    // Get every messages
    const messages = document.querySelectorAll('.text');
    const boxes = document.querySelectorAll('.message-content');
    const names = document.querySelectorAll('.name a');
    const user_avatars = document.querySelectorAll('.user-avatar img');
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
        skins = message.getAttribute('skins');
        if (skins === '') {
            skins = "{}";
        }
        if (message.id === "example-text") {
            return;
        } // Pas de skin pour le message d'exemple
        skins = skins.replace(/'/g, '"');
        skins = JSON.parse(skins);

        let box = boxes[i];
        let name = names[i];
        let user_avatar = user_avatars[i];



        // Loop on skins
        Object.keys(skins).forEach(function(key) {
            
            // text color
            if (key === "text_color") {
                
                box = text_color(box, skins[key]);
            }

            // border color
            else if (key === "border_color") {
                
                box = border_color(box, skins[key]);
            }

            // background color
            else if (key === "background_color") {
                
                box = background_color(box, skins[key]);
            }

            // name color
            else if (key === "name_color") {
                name = name_color(name, skins[key]);
                }

            // avatar color
            else if (key === "avatar_color") {
               
                user_avatar = avatar_color(user_avatar, skins[key]);
                }

            // font
            else if (key === "font") {
                box = font_message(box, skins[key]);
               
                if (font_tab.includes(skins[key]) === false) {
                    font_tab.push(skins[key]);
                }
            }

            // border image
            else if (key === "border_image") {
               
                document = border_image(document, message, skins[key]);
            }

            // Rainbow border
            else if (key === "border_rgb") {
               
                document = border_rgb(document, message, skins[key]);
            }
            
            // Rainbow name
            else if (key === "name_rgb") {
                
                document, name, user_avatar = name_rgb(document, name, user_avatar, skins[key]);
            }
        });
        i = i+1;
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

