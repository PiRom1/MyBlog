// Ajout d'un écouteur d'événement au clic sur l'image
document.addEventListener('DOMContentLoaded', function () {
    
    
    // Get every messages
    const messages = document.querySelectorAll('.text');
    const boxes = document.querySelectorAll('.message-content');
    const names = document.querySelectorAll('.name a');
    const user_avatars = document.querySelectorAll('.user-avatar img');
    const font_tab = []
    const rgb_tab = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08'];

    console.log("boxes : ", boxes);

    var i = 0;
    // Loop on messages
    messages.forEach((message) => {
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
            }

            // border color
            else if (key === "border_color") {
                
                box.style.setProperty('border-style', 'solid', 'important')
                box.style.setProperty('border-width', '2px', 'important')
                box.style.setProperty('border-color', skins[key], 'important')
            }

            // background color
            else if (key === "background_color") {
                
                box.style.setProperty('background', skins[key], 'important')
            }

            // name color
            else if (key === "name_rgb") {
                name.style.setProperty('color', skins[key], 'important');
                }

            // avatar color
            else if (key === "avatar_color") {
                user_avatar.style.setProperty('border-style', 'solid', 'important');
                user_avatar.style.setProperty('border-width', '3px', 'important');
                user_avatar.style.setProperty('border-radius', '50%', 'important');
                user_avatar.style.setProperty('border-color', skins[key], 'important');
                }

            // font
            else if (key === "font") {
                message.childNodes[1].style.setProperty('font-family', skins[key], 'important');
                if (font_tab.includes(skins[key]) === false) {
                    font_tab.push(skins[key]);
                }
            }

            // Rainbow border
            else if (key === "border_rgb") {
                const rgbDiv = document.createElement('div');
                rgbDiv.className = 'rainbow';
                messageContent = message.parentNode;
                messageContent.parentNode.insertBefore(rgbDiv, messageContent);
                rgbDiv.appendChild(messageContent);
                if(skins[key] !== 'rainbow') {defineRGBAnimation(skins[key], rgbDiv, rgb_tab);}
                const rgbCss = document.getElementById('rainbow-css');
                if (rgbCss === null) {
                    const css = document.createElement('link');
                    css.id = 'rainbow-css';
                    css.rel = 'stylesheet';
                    css.href = '/static/Blog/chat/css/rainbow.css';
                    document.head.appendChild(css);
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

function defineRGBAnimation(pattern, div, rgb_tab){
    if (pattern === '#000'){
        div.style.setProperty('--Background', 
            'linear-gradient(5deg,#000,#333,#666,#999,#ccc,#fff,#ccc,#999,#666,#333,#000,#333,#666);')
    }
    else{
        var index = rgb_tab.indexOf(pattern) + rgb_tab.length;
        var anim_str = 'linear-gradient(5deg';
        [0,1,0,-1,0,1,0,-1,0,1,0,-1,0,1,0].forEach((i) => {
            anim_str += ',' + rgb_tab[(index + i) % rgb_tab.length];
        });
        anim_str += ');';
        console.log("anim_str : ", anim_str);
        console.log("div : ", div);
        div.setAttribute("style", "--Background: " + anim_str + "--Position: 100% 0%;");
        div.style.setProperty();
        console.log("div : ", div);
    }
}