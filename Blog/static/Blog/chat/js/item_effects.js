// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    
    
    // Get every messages
    const messages = document.querySelectorAll('.text');
    const boxes = document.querySelectorAll('.message-content');
    const names = document.querySelectorAll('.name a');
    const user_avatars = document.querySelectorAll('.user-avatar img');
    const font_tab = []

    console.log("boxes : ", boxes);

    var i = 0;
    // Loop on messages
    messages.forEach((message) => {
        console.log("message : ", message);
        // Get skins
        skins = message.getAttribute('skins');
        skins = skins.replace(/'/g, '"');
        skins = JSON.parse(skins);
        console.log("skins : ", skins);

        const box = boxes[i];
        const name = names[i];
        const user_avatar = user_avatars[i];

        // Loop on skins
        Object.keys(skins).forEach(function(key) {
            
            // text color
            if (key === "text_color") {
                message.style.setProperty('color', skins[key], 'important')
                console.log(skins[key]);
            }

            // border color
            else if (key === "border_color") {
                
                box.style.setProperty('border-style', 'solid', 'important')
                box.style.setProperty('border-width', '2px', 'important')
                box.style.setProperty('border-color', skins[key], 'important')
                console.log(skins[key]);
            }

            // background color
            else if (key === "background_color") {
                
                box.style.setProperty('background', skins[key], 'important')
                console.log(skins[key]);
            }

            // name color
            else if (key === "name_color") {
                console.log(name);
                name.style.setProperty('color', skins[key], 'important');
                }

            // avatar color
            else if (key === "avatar_color") {
                console.log(name);
                user_avatar.style.setProperty('border-style', 'solid', 'important');
                user_avatar.style.setProperty('border-width', '3px', 'important');
                user_avatar.style.setProperty('border-radius', '50%', 'important');
                user_avatar.style.setProperty('border-color', skins[key], 'important');
                }

            // font
            else if (key === "font") {
                message.childNodes[1].style.setProperty('font-family', skins[key], 'important');
                console.log('to push :',skins[key]);
                if (font_tab.includes(skins[key]) === false) {
                    font_tab.push(skins[key]);
                }
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

