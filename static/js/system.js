// Author: Ryuta Aoki

/**
 * Focuses the first required element if isRequired is true, otherwise focuses the submit button.
 * @param {boolean} isRequired - Indicates whether to focus the first required element or not.
 */
function focusFirstRequiredElement(isRequired) {
    if (isRequired) {
        // Focus the first required field
        var firstRequiredField = document.querySelector("[required]");
        if (firstRequiredField) {
            firstRequiredField.focus();
        }
    } else {
        // Focus the next submit button
        var submitButton = document.querySelector('button[type="submit"]');
        submitButton.focus();
    }
}

/**
 * Disables the submit button.
 */
function disableSubmitButton() {
    // Find and disable the submit button
    var submitButton = document.querySelector('button[type="submit"]');
    submitButton.disabled = true;
}

/**
 * Captures keydown events for digits 0 to 5 and handles rating button selection.
 * @param {Event} event - The keydown event.
 * @param {string} buttonClass - The CSS class for the rating buttons.
 * @param {string} inputId - The ID of the hidden input to store the rating value.
 */
function handleRatingKeydown(event, buttonClass, inputId) {
    var ratingButtons = document.querySelectorAll(buttonClass);
    var submitButton = document.querySelector('button[type="submit"]');
    var inputElement = document.getElementById(inputId);

    if (event.key >= 0 && event.key <= 5) {
        // Handle numeric key press
        var selectedButton = document.querySelector(buttonClass + '[data-value="' + event.key + '"]');
        if (selectedButton) {
            // Deselect all buttons and select the pressed one
            ratingButtons.forEach(function (btn) {
                btn.classList.remove('selected');
            });
            selectedButton.classList.add('selected');
            inputElement.value = event.key;
            submitButton.focus();
        }
    } else if (event.key === 'Tab' && inputElement.value !== '') {
        // Handle Tab key press if input is not empty
        event.preventDefault();
        submitButton.focus();
    }
}

/**
 * Captures keydown events for '0' (No) and '1' (Yes) and handles selection.
 * @param {Event} event - The keydown event.
 * @param {string} buttonClass - The CSS class for the rating buttons.
 * @param {string} inputId - The ID of the hidden input to store the selection value.
 */
function handleYesNoKeydown(event, buttonClass, inputId) {
    var ratingButtons = document.querySelectorAll(buttonClass);
    var submitButton = document.querySelector('button[type="submit"]');
    var inputElement = document.getElementById(inputId);
    
    if (event.key === '0' || event.key === '1') {
        // Handle '0' or '1' key press
        var selectedButton = document.querySelector(buttonClass + '[data-value="' + (event.key === '0' ? 'いいえ' : 'はい') + '"]');
        if (selectedButton) {
            // Deselect all buttons and select the pressed one
            ratingButtons.forEach(function (btn) {
                btn.classList.remove('selected');
            });
            selectedButton.classList.add('selected');
            inputElement.value = event.key === '0' ? 'いいえ' : 'はい';
            submitButton.focus();
        }
    } else if (event.key === 'Tab' && inputElement.value !== '') {
        // Handle Tab key press if input is not empty
        event.preventDefault();
        submitButton.focus();
    }
}

/**
 * Checks if all required elements are filled and shows an error message if not.
 * @param {Event} event - The form submit event.
 * @param {string} errorMessage - The error message to display if a required field is empty.
 */
function validateRequiredFields(event, errorMessage) {
    event.preventDefault(); 
    clearFormErrors();
    var isValid = true;

    // Check required fields
    var requiredFields = form.querySelectorAll("[required]");
    requiredFields.forEach(function (field) {
        if (!field.value) {
            isValid = false;
            displayFormError(field, errorMessage, field.parentNode);
        }
    });

    // Check required radio buttons
    var radioGroups = {};
    requiredFields.forEach(function (field) {
        if (field.type === 'radio') {
            if (!radioGroups[field.name]) {
                radioGroups[field.name] = [];
            }
            radioGroups[field.name].push(field);
        }
    });

    for (var groupName in radioGroups) {
        var radios = radioGroups[groupName];
        var isChecked = radios.some(function (radio) {
            return radio.checked;
        });

        if (!isChecked) {
            isValid = false;
            displayFormError(radios[0], errorMessage, radios[0].parentNode.parentNode);
        }
    }

    if (isValid) {
        form.submit();
    }
}

/**
 * Displays an error message for a specific field.
 * @param {HTMLElement} field - The form field with an error.
 * @param {string} message - The error message to display.
 * @param {HTMLElement} insertNode - The node to insert the error message into.
 */
function displayFormError(field, message, insertNode) {
    var error = document.createElement('div');
    error.className = 'form_error_message';
    error.textContent = message;
    insertNode.appendChild(error);
}

/**
 * Clears all error messages from the form.
 */
function clearFormErrors() {
    var errors = document.querySelectorAll('.form_error_message');
    errors.forEach(function (error) {
        error.remove();
    });
}

/**
 * Automatically plays audio elements and optionally submits a form when the audio ends.
 * @param {string} formId - The ID of the form to submit when audio ends.
 * @param {boolean} autoSubmit - Indicates whether to submit the form when audio ends.
 */
function autoPlayAudio(formId, autoSubmit) {
    var audios = document.querySelectorAll('audio');
    var form = document.getElementById(formId);

    audios.forEach(function(audio) {
        // Try to play the audio
        audio.play().catch(function(error) {
            console.log("Auto-play was prevented: ", error);
        });

        // Submit the form when the audio ends if autoSubmit is true
        audio.addEventListener('ended', function() {
            if (autoSubmit) {
                form.submit();
            }
        });
    });
}

/**
 * Sets a timer to submit a form after a specified amount of time.
 * @param {string} formId - The ID of the form to submit.
 * @param {number} milliseconds - The time in milliseconds to wait before submitting the form.
 */
function submitFormAfterTimeout(formId, milliseconds) {
    var form = document.getElementById(formId);
    setTimeout(function() {
        form.submit();
    }, milliseconds);
}

/**
 * Activates rating buttons and ensures a value is selected before submitting the form.
 * @param {string} formId - The ID of the form.
 * @param {string} buttonClass - The CSS class for the rating buttons.
 * @param {string} inputId - The ID of the hidden input to store the selected rating value.
 */
function handleRatingButtonClick(formId, buttonClass, inputId) {
    var form = document.getElementById(formId);
    var ratingButtons = document.querySelectorAll(buttonClass);
    var hiddenInput = document.getElementById(inputId);
    var nextButton = form.querySelector('button[type="submit"]');

    ratingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Deselect all buttons and select the clicked one
            ratingButtons.forEach(function(btn) {
                btn.classList.remove('selected');
            });
            button.classList.add('selected');
            hiddenInput.value = button.getAttribute('data-value');
            nextButton.focus();
        });
    });

    form.addEventListener('submit', function(event) {
        // Show an error if no rating is selected
        if (hiddenInput.value === '') {
            event.preventDefault();
            displayFormError(hiddenInput, "この項目は必須です。", hiddenInput.parentNode);
        }
    });
}

/**
 * Disables the browser's back feature and shows an alert with an error message.
 * @param {string} errorMessage - The error message to display when the back button is pressed.
 */
function disableBrowserBackButton(errorMessage) {
    // Prevent the back button
    history.replaceState(null, null, null);
    history.pushState(null, null, null);

    window.addEventListener('popstate', function(e) {
        console.log(errorMessage);
        history.pushState(null, null, null);
        alert(errorMessage);
    });
}

/**
 * Enables session storage for the page, tracking if the page has been reloaded.
 * @param {string} pageName - The name of the page to track in session storage.
 */
function trackPageReload(pageName) {
    window.addEventListener('beforeunload', function() {
        // Set reloaded flag in session storage
        sessionStorage.setItem(`${pageName}_reloaded`, 'true');
    });
    
    if (!sessionStorage.getItem(`${pageName}_loaded_once`)) {
        // Set loaded once flag and remove reloaded flag
        sessionStorage.setItem(`${pageName}_loaded_once`, 'true');
        sessionStorage.removeItem(`${pageName}_reloaded`);
    }
}
