
function defineRGBAnimation(pattern, div, rgb_tab){
    if (pattern === '#000'){
        div.setAttribute("style",
            "--Background: linear-gradient(5deg,#333,#000,#333,#666,#999,#ccc,#fff,#ccc,#999,#666,#333,#000,#333);" +
            "--Animation: steam 8s linear infinite;");
    }
    else{
        var index = rgb_tab.indexOf(pattern) + rgb_tab.length;
        var anim_str = 'linear-gradient(5deg';
        [0,-1,0,1,0,-1,0,1,0,-1,0,1,0,-1,0].forEach((i) => {
            anim_str += ',' + rgb_tab[(index + i) % rgb_tab.length];
        });
        anim_str += ');';
        div.setAttribute("style", "--Background: " + anim_str + "--Position: 100% 0%;");
    }
}

function defineRGBAnimationName(pattern, nameDiv, avatarDiv, rgb_tab){
    if (pattern === '#000'){
        ['#000','#333','#666','#999','#ccc','#fff','#fff','#ccc','#999','#666','#333','#000'].forEach((color, index) => {
            nameDiv.style.setProperty('--TC' + (index+1), color);
            avatarDiv.style.setProperty('--BC' + (index+1), color);
        });
    }
    else {
        var rgbIndex = rgb_tab.indexOf(pattern) + rgb_tab.length;
        [0,1,0,-1,0,1,0,-1,0,1,0,-1].forEach((i, idx) => {
            nameDiv.style.setProperty('--TC' + (idx+1), rgb_tab[(rgbIndex + i) % rgb_tab.length]);
            avatarDiv.style.setProperty('--BC' + (idx+1), rgb_tab[(rgbIndex + i) % rgb_tab.length]);
            nameDiv.style.setProperty("animation", "rainbow-text 16s linear infinite");
            avatarDiv.style.setProperty("animation", "rainbow-border 16s linear infinite");
        });
    }
}



function text_color(box, pattern) {
    console.log(box.innerHTML);
    box.querySelectorAll('p').forEach((text) => {
        text.style.setProperty('color', pattern, 'important');    
    });
    return box;
}


function border_color(box, pattern) {
    box.style.setProperty('border-style', 'solid', 'important');
    box.style.setProperty('border-width', '2px', 'important');
    box.style.setProperty('border-color', pattern, 'important');
    return box;
}


function background_color(box, pattern) {
    box.style.setProperty('background', pattern, 'important');
    return box;


}


function name_color(name, pattern) {
    name.style.setProperty('color', pattern, 'important');
    return name;
}



function avatar_color(avatar, pattern) {
    avatar.style.setProperty('border-style', 'solid', 'important');
    avatar.style.setProperty('border-width', '3px', 'important');
    avatar.style.setProperty('border-radius', '50%', 'important');
    avatar.style.setProperty('border-color', pattern, 'important');
    return avatar;
}

function font_message(box, pattern) {
    box.querySelectorAll('p').forEach((text) => {
        text.style.setProperty('font-family', pattern, 'important');
        text.style.setProperty('font-size', '1.2em', 'important');
    })
    return box;
}

function border_image(document, message, pattern, example = '') {
    console.log("border image created");
    const borderDiv = document.createElement('div');
    borderDiv.id = `${example}borderImage`;
    borderDiv.className = 'message-border-image';
    messageContent = message.parentNode;
    messageContent.parentNode.insertBefore(borderDiv, messageContent);
    borderDiv.appendChild(messageContent);
    borderDiv.style.setProperty('flex', '1');
    borderDiv.style.setProperty('border-image-slice', '31 16 30 15 fill');
    borderDiv.style.setProperty('border-image-outset', '0px');
    borderDiv.style.setProperty('border-image-repeat', 'round');
    borderDiv.style.setProperty('border-style', 'solid');
    borderDiv.style.setProperty('border-width', '30px 15px');
    borderDiv.style.setProperty('border-image-source', `url(${pattern})`, 'important');

    return document;
}



function border_rgb(document, message, pattern, example = '') {
    const rgb_tab = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08'];

    const rgbDiv = document.createElement('div');
    rgbDiv.className = 'rainbow';
    rgbDiv.id = `${example}RgbBorder`;
    messageContent = message.parentNode;
    messageContent.parentNode.insertBefore(rgbDiv, messageContent);
    rgbDiv.appendChild(messageContent);
    if(pattern !== 'rainbow') {defineRGBAnimation(pattern, rgbDiv, rgb_tab);}
    const rgbCss = document.getElementById('rainbow-css');
    if (rgbCss === null) {
        const css = document.createElement('link');
        css.id = 'rainbow-css';
        css.rel = 'stylesheet';
        css.href = '/static/Blog/chat/css/rainbow.css';
        document.head.appendChild(css);
    }
}



function name_rgb(document, name, user_avatar, pattern, example = '') {
    const rgb_tab = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08'];

    name.classList.add('rainbow-text');
    user_avatar.style.border = "3px solid"; 
    user_avatar.style.animation = "rainbow-border 8s linear infinite";
    // name.id = `${example}RgbName`;
    user_avatar.classList.add('rainbow-border');
    
    if(pattern !== 'rainbow') {defineRGBAnimationName(pattern, name, user_avatar, rgb_tab);}
    const rgbCss = document.getElementById('rainbow-css');
    if (rgbCss === null) {
        const css = document.createElement('link');
        css.id = 'rainbow-css';
        css.rel = 'stylesheet';
        css.href = '/static/Blog/chat/css/rainbow.css';
        document.head.appendChild(css);
    }
   

    return document, name, user_avatar;
}



