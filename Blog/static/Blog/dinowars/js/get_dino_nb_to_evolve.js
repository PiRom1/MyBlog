document.addEventListener('DOMContentLoaded', function () {
    let popup;
    const dino_cards = document.querySelectorAll('.dino-card');
  
    dino_cards.forEach(dino_card => {
      dino_card.addEventListener('contextmenu', function (e) {
        e.preventDefault();
  
        fetch(`/dinowars/get_dino_nb_to_evolve/${dino_card.getAttribute('data-dino-id')}`, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              // Supprime l'ancienne popup s'il y en a une
              if (popup) {
                popup.remove();
              }



              // Création de la popup
              popup = document.createElement('div');
              popup.textContent = data.message;
              popup.style.position = 'absolute';
              popup.style.padding = '10px';
              popup.style.backgroundColor = '#fddbc5';
              popup.style.boxShadow = 'rgba(0, 0, 0, 0.5) 0px 5px 15px';
              popup.style.fontSize = '16px';
              popup.style.fontWeight = 'bold';
              popup.style.borderRadius = '4px';
              popup.style.color = 'ivory';
              popup.style.border = '1px solid #ccc';
              popup.style.zIndex = '1000';
              popup.style.width = '200px'; // Taille fixe pour calculer plus facilement
              document.body.appendChild(popup);
  
              // Position initiale
              let left = e.pageX;
              let top = e.pageY;
  
              // Vérification de l'espace disponible
              const popupRect = popup.getBoundingClientRect();
              const viewportWidth = window.innerWidth;
              const viewportHeight = window.innerHeight;
  
              // Si ça dépasse à droite
              if (left + popupRect.width > viewportWidth) {
                left = viewportWidth - popupRect.width - 10; // 10px de marge
              }
              // Si ça dépasse en bas
              if (top + popupRect.height > viewportHeight) {
                top = viewportHeight - popupRect.height - 10;
              }
  
              // Appliquer les nouvelles coordonnées
              popup.style.left = `${left}px`;
              popup.style.top = `${top}px`;
  
              // Afficher la popup
              popup.style.display = 'block';
            }
          });
      });
    });
  
    // Supprimer la popup au clic ailleurs
    document.addEventListener('click', function () {
      if (popup) {
        popup.remove();
      }
    });
  });
  