/**
 * ToastPlugin for Vue 3
 * This plugin allows displaying Bootstrap toast notifications within a Vue application.
 * It supports dynamic creation of toast elements based on a predefined template,
 * applying a status-specific style, and automatically removing the toast after it's hidden.
 */
const ToastPlugin = {
    install(app, options) {
        /**
         * Registers a global method $showToast to display toast notifications.
         * @param {string} status - The status type of the toast ('success' or 'error').
         * @param {string} message - The message to be displayed inside the toast.
         */
        app.config.globalProperties.$showToast = function(status, message) {
            // Find the original toast element to clone.
            const originalToastEl = document.getElementById('liveToast');
            // Clone the original toast element for a new unique toast instance.
            const clonedToastEl = originalToastEl.cloneNode(true); // Deep clone
            // Assign a unique ID to the cloned element based on the current timestamp.
            clonedToastEl.id = `toast-${Date.now()}`;

            // Locate the .toast-body within the cloned element to update the message.
            const toastBody = clonedToastEl.querySelector('.toast-body');
            toastBody.innerHTML = message; // Update the toast message.

            // Reset any previous status classes and add the new status class.
            clonedToastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning'); // Reset classes
            switch(status) {
                case 'success':
                    clonedToastEl.classList.add('bg-success');
                    break;
                case 'error':
                    clonedToastEl.classList.add('bg-danger');
                    break;
                case 404:
                    clonedToastEl.classList.add('bg-danger');
                case 500:
                    clonedToastEl.classList.add('bg-danger');
                // Additional cases can be added as needed.
            }

            // Append the cloned, updated toast element to the toast container.
            document.querySelector('.toast-container').appendChild(clonedToastEl);

            // Initialize and show the toast using Bootstrap's Toast component.
            const toast = new bootstrap.Toast(clonedToastEl, {
                // delay: 10000,
                autohide: false
            });
            toast.show();

            // Since the delay function of the toast is not working, we simply creat our own:
            setTimeout(() => {
                toast.hide()
            }, 10000);

            // Add an event listener to remove the toast element from the DOM after it's hidden.
            clonedToastEl.addEventListener('hidden.bs.toast', () => {
                clonedToastEl.remove();
            });
        }
    }
}
