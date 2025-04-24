document.addEventListener('DOMContentLoaded', function() {    
    // Get the CSRF token for POST requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Add event listeners to all dino option cards
    function addSelectionListeners() {
        document.querySelectorAll('.dino-option').forEach(card => {
            card.addEventListener('click', function() {
                const dinoId = this.dataset.dinoId;
                selectDino(dinoId);
            });
        });
    }
    
    // Function to handle dino selection
    function selectDino(dinoId) {        
        // Disable all cards to prevent double-clicking
        document.querySelectorAll('.dino-option').forEach(card => {
            card.classList.add('disabled');
            card.style.pointerEvents = 'none';
        });
        
        // Make API call to select the dino and get the next options
        fetch('/dinowars/pvm/select-run-dino/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                dino_id: dinoId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.redirect) {
                    // Run creation completed, redirect to PvM page
                    window.location.href = data.redirect;
                    return;
                }
                
                // Update our tracking variables
                selectionStep = data.selection_step;
                
                // Update the UI to show selected dinos and new options
                updateSelectedDinosDisplay(data.selected_dinos);
                updateDinoOptions(data.random_dinos);
                updateSelectionStepTitle(selectionStep);
            } else {
                console.error('Error:', data.error);
                alert('An error occurred: ' + data.error);
                
                // Re-enable cards in case of error
                document.querySelectorAll('.dino-option').forEach(card => {
                    card.classList.remove('disabled');
                    card.style.pointerEvents = 'auto';
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your selection: ' + error);
            
            // Re-enable cards in case of error
            document.querySelectorAll('.dino-option').forEach(card => {
                card.classList.remove('disabled');
                card.style.pointerEvents = 'auto';
            });
        });
    }
    
    // Function to update the selected dinos display
    function updateSelectedDinosDisplay(selectedDinos) {
        const container = document.getElementById('selected-dinos-container');
        container.innerHTML = '';
        
        selectedDinos.forEach(dino => {
            const dinoElement = document.createElement('div');
            dinoElement.className = 'selected-dino';
            dinoElement.innerHTML = `
                <h3 class="dino-name">${dino.name}</h3>
                <div class="dino-stats">
                    <p><i class="fi fi-ss-heart"></i> ${dino.hp || 'N/A'}</p>
                    <p><i class="fi fi-ss-sword-alt"></i> ${dino.atk || 'N/A'}</p>
                    <p><i class="fi fi-ss-shield"></i> ${dino.defense || 'N/A'}</p>
                    <p><i class="fi fi-ss-bolt"></i> ${dino.spd || 'N/A'}</p>
                    <p><i class="fi fi-ss-location-crosshairs"></i> ${dino.crit || 'N/A'}</p>
                    <p><i class="fi fi-ss-burst"></i> ${dino.crit_dmg || 'N/A'}</p>
                </div>
                <p class="dino-attack">${dino.attack || 'N/A'}</p>
            `;
            container.appendChild(dinoElement);
        });
    }
    
    // Function to update the available dino options
    function updateDinoOptions(dinos) {
        const optionsContainer = document.getElementById('dino-options');
        optionsContainer.innerHTML = '';
        
        dinos.forEach(dino => {
            const dinoElement = document.createElement('div');
            dinoElement.className = 'dino-option';
            dinoElement.dataset.dinoId = dino.id;
            dinoElement.innerHTML = `
                <h3 class="dino-name">${dino.name}</h3>
                <div class="dino-stats">
                    <p><i class="fi fi-ss-heart"></i> ${dino.base_hp || dino.hp || 'N/A'}</p>
                    <p><i class="fi fi-ss-sword-alt"></i> ${dino.base_atk || dino.atk || 'N/A'}</p>
                    <p><i class="fi fi-ss-shield"></i> ${dino.base_def || dino.defense || 'N/A'}</p>
                    <p><i class="fi fi-ss-bolt"></i> ${dino.base_spd || dino.spd || 'N/A'}</p>
                    <p><i class="fi fi-ss-location-crosshairs"></i> ${dino.base_crit || dino.crit || 'N/A'}</p>
                    <p><i class="fi fi-ss-burst"></i> ${dino.base_crit_dmg || dino.crit_dmg || 'N/A'}</p>
                </div>
                <p class="dino-attack">${dino.attack || 'N/A'}</p>
            `;
            optionsContainer.appendChild(dinoElement);
        });
        
        // Re-add event listeners to the new cards
        addSelectionListeners();
    }
    
    // Function to update the selection step title
    function updateSelectionStepTitle(step) {
        const title = document.getElementById('selection-step-title');
        const circles = document.getElementById('step-circles');
        if (title) {
            if (step === 2) {
                title.textContent = "Select Your Second Dino";
                circles.children[0].classList.add('active');
                circles.children[1].classList.add('active');
                circles.children[2].classList.remove('active');
            } else if (step === 3) {
                title.textContent = "Select Your Third Dino";
                circles.children[0].classList.add('active');
                circles.children[1].classList.add('active');
                circles.children[2].classList.add('active');
            } else {
                title.textContent = "Select Your First Dino";
                circles.children[0].classList.add('active');
                circles.children[1].classList.remove('active');
                circles.children[2].classList.remove('active');
            }
        }
    }
    
    // Initialize the page
    addSelectionListeners();
});
