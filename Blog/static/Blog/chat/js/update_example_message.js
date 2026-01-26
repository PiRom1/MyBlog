

function update_example_message(document, message, box, name, avatar, skins) {
  

    // Text color
    box.querySelectorAll('p').forEach((text) => {
        text.style.setProperty('color', 'black', 'important');    
    });

    // Border color
    box.style.setProperty("border", "none");
   
    // Background color
    box.style.setProperty('background', 'rgb(255, 187, 153)', 'important');

    // Name color
    name.style.setProperty('color', 'black');

    // Avatar color
    avatar.style.setProperty("border", "none");

    // Font 
    box.querySelectorAll('p').forEach((text) => {
        text.style.setProperty("font-family", "'Open Sans', sans-serif");
        text.style.setProperty('font-size', '1.2em', 'important');
    })

    // Border Image
    let example_borderImage = document.getElementById("example-borderImage");
    if (example_borderImage) {
        messageContent = message.parentNode.parentNode;
        messageContent?.replaceWith(...messageContent.childNodes);
    }

    // Border RGB

    name.style.removeProperty('animation');
    name.style.removeProperty('--TC');
    name.classList.remove('rainbow-text');
    
    let example_RgbBorder = document.getElementById("example-RgbBorder");
    let example_RgbName = document.getElementById("example-name");
    if (example_RgbBorder) {
        messageContent = message.parentNode.parentNode;
        messageContent?.replaceWith(...messageContent.childNodes);
        // name.style.removeProperty('border');
    }
    



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
            
            avatar = avatar_color(avatar, skins[key]);
            }

        // font
        else if (key === "font") {
            box = font_message(box, skins[key]);
        
        }

        // border image
        else if (key === "border_image") {
            
            document = border_image(document, message, skins[key], example = 'example-');
        }

        // Rainbow border
        else if (key === "border_rgb") {
            
            document = border_rgb(document, message, skins[key], example = 'example-');
        }
        
        // Rainbow name
        else if (key === "name_rgb") {
            
            [document, name, user_avatar] = name_rgb(document, name, avatar, skins[key]);
        }
    });

    return document, message, box, name, avatar 
}