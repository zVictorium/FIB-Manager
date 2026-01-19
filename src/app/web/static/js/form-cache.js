/**
 * Form Cache - Saves and restores form values using localStorage
 * This allows users to persist their form selections between sessions
 */

const FormCache = {
    STORAGE_KEY_PREFIX: 'fib_manager_',

    /**
     * Save form values to localStorage
     * @param {string} formId - Unique identifier for the form
     * @param {HTMLFormElement} form - The form element
     */
    save(formId, form) {
        const formData = {};
        const elements = form.elements;

        for (let i = 0; i < elements.length; i++) {
            const element = elements[i];
            if (!element.name) continue;

            if (element.type === 'checkbox') {
                formData[element.name] = element.checked;
            } else if (element.type === 'radio') {
                if (element.checked) {
                    formData[element.name] = element.value;
                }
            } else if (element.tagName === 'SELECT') {
                formData[element.name] = element.value;
            } else if (element.type !== 'submit' && element.type !== 'reset' && element.type !== 'button') {
                formData[element.name] = element.value;
            }
        }

        try {
            localStorage.setItem(this.STORAGE_KEY_PREFIX + formId, JSON.stringify(formData));
        } catch (e) {
            console.warn('FormCache: Unable to save to localStorage', e);
        }
    },

    /**
     * Restore form values from localStorage
     * @param {string} formId - Unique identifier for the form
     * @param {HTMLFormElement} form - The form element
     * @param {Object} options - Options for restoration
     * @param {Array} options.exclude - Field names to exclude from restoration
     */
    restore(formId, form, options = {}) {
        const exclude = options.exclude || [];

        try {
            const stored = localStorage.getItem(this.STORAGE_KEY_PREFIX + formId);
            if (!stored) return;

            const formData = JSON.parse(stored);
            const elements = form.elements;

            for (let i = 0; i < elements.length; i++) {
                const element = elements[i];
                if (!element.name || exclude.includes(element.name)) continue;
                if (!(element.name in formData)) continue;

                const value = formData[element.name];

                if (element.type === 'checkbox') {
                    element.checked = value;
                } else if (element.type === 'radio') {
                    element.checked = (element.value === value);
                } else if (element.tagName === 'SELECT') {
                    element.value = value;
                } else if (element.type !== 'submit' && element.type !== 'reset' && element.type !== 'button') {
                    element.value = value;
                }
            }
        } catch (e) {
            console.warn('FormCache: Unable to restore from localStorage', e);
        }
    },

    /**
     * Clear cached form data
     * @param {string} formId - Unique identifier for the form (optional, clears all if not provided)
     */
    clear(formId) {
        try {
            if (formId) {
                localStorage.removeItem(this.STORAGE_KEY_PREFIX + formId);
            } else {
                // Clear all form cache entries
                Object.keys(localStorage)
                    .filter(key => key.startsWith(this.STORAGE_KEY_PREFIX))
                    .forEach(key => localStorage.removeItem(key));
            }
        } catch (e) {
            console.warn('FormCache: Unable to clear localStorage', e);
        }
    },

    /**
     * Initialize form caching for a form
     * @param {string} formId - Unique identifier for the form
     * @param {HTMLFormElement} form - The form element
     * @param {Object} options - Options
     */
    init(formId, form, options = {}) {
        if (!form) return;

        // Restore saved values on page load
        this.restore(formId, form, options);

        // Save values on form input changes
        form.addEventListener('input', () => this.save(formId, form));
        form.addEventListener('change', () => this.save(formId, form));

        // Handle reset button - clear cache and reset form
        form.addEventListener('reset', () => {
            this.clear(formId);
            // Use setTimeout to allow the form to reset first
            setTimeout(() => {
                // Trigger any change events if needed
            }, 0);
        });
    }
};

// Auto-initialize forms with data-form-cache attribute
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form[data-form-cache]').forEach(form => {
        const formId = form.getAttribute('data-form-cache');
        const excludeAttr = form.getAttribute('data-form-cache-exclude');
        const exclude = excludeAttr ? excludeAttr.split(',').map(s => s.trim()) : [];
        
        FormCache.init(formId, form, { exclude });
    });
});
