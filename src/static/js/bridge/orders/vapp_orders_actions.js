const app_orders_actions = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            customer_id: null,
            new_customer_nr: null,
            current_customer_nr: null,
            bridge_customer_id: null,
            orderStates: [],
            paymentStates: [],
            shippingStates: [],
            orders: [],
        }
    },
    methods: {
        /**
         * This method is used to change customer number in both sw6 and bridge for a given customer.
         * It first sets the class member variables for customer_id, current_customer_nr and bridge_customer_id and cancels the form submit.
         * Then it fetches the new customer number and checks if its valid.
         * If it's valid then it makes asynchronous calls to update the customer number in sw6 and bridge API endpoints.
         * It shows different success or error messages based on the update status and redirects the user to /orders page if successful.
         *
         * @param event {Event} - The form submit event. It's default action will be prevented to handle form submission through Javascript.
         * @param customer_id {Number} - The ID of the customer whose number needs to be changed.
         * @param current_customer_nr {Number} - The current number of the customer.
         * @param bridge_customer_id {Number} - The ID of the associated bridge customer.
         */
        async api_customer_change_customer_nr(event, customer_id, current_customer_nr, bridge_customer_id) {
            try {
                // Set class member variables
                this.customer_id = customer_id;
                this.current_customer_nr = current_customer_nr;
                this.bridge_customer_id = bridge_customer_id;

                // Prevent default form submit action
                event.preventDefault();

                // Access specific form input element
                const form = event.target;

                // Use new classes for input elements identification
                const newCustomerNrInput = form.querySelector('.new-customer-nr');

                // Get new customer number
                const new_customer_nr = newCustomerNrInput.value;

                // Check if new customer number is provided
                if (!new_customer_nr) {
                    this.$showToast('error', "New customer number is not provided");
                    return;
                }
                this.new_customer_nr = new_customer_nr;

                // Call APIs to update customer number in sw6 and bridge systems
                const changed_in_sw6 = await this.api_customer_change_customer_nr_in_sw6();
                const changed_in_bridge = await this.api_customer_change_customer_nr_in_bridge();

                // If customer numbers updated successfully in both systems
                if (changed_in_sw6 && changed_in_bridge) {
                    // Show success message with old and new customer numbers and current customer id
                    this.$showToast('success', `
                                <div class="row">
                                    <div class="col">
                                        <strong>Old:</strong><br/>
                                        ${current_customer_nr}<br/>
                                    </div>
                                    <div class="col">
                                        <span class="display-6"><strong> -> </strong></span>
                                    </div>
                                    <div class="col">
                                        <strong>New:</strong><br/>
                                        ${new_customer_nr}
                                    </div>
                                </div>
                                <hr />
                                <div class="row">
                                    <div class="col">
                                        <strong>Customer ID:</strong><br/>
                                        ${customer_id}<br/>
                                    </div>
                                </div>
                            `);
                    // Redirect to orders page after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/orders'
                    }, 2000);
                } else {
                    // Show error message if failed to update customer numbers
                    this.$showToast('error', 'Changing the customer number failed. Aborted');
                    return false;
                }
            } catch (error) {
                // Show error message in case of exception
                this.$showToast('error', '<p>The following error occurred: </p><pre>'+error+'</pre>')
            }
        },

        /**
         * Asynchronously changes a customer's number in sw6.
         * It makes a PUT request to the /api/sw6/customers/update_erp_nr' endpoint with the customerId and newCustomerNumber.
         *
         * This function will:
         * 1) Construct a request JSON object with the current instance's customerId and newCustomerNumber.
         * 2) Send an asynchronous HTTP PUT request to the API endpoint.
         * 3) Handle the API response; showing a toast notification containing the status and response message.
         * 4) Return true or false based on the update operation's success status.
         *
         * @throws {Error} Throws an error when the API response status is not OK.
         * @return {Boolean} Returns true if the status of responseData is 'success', otherwise returns false.
         */
        async api_customer_change_customer_nr_in_sw6(){
            // Prepare the request data
            const requestData = {
                customer_id: this.customer_id,
                new_customer_nr: this.new_customer_nr
            }

            try {
                // send PUT request to the API endpoint
                const response = await fetch('/api/sw6/customers/update_erp_nr', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                // Throw error if response status is not ok
                if (!response.ok) {
                    throw new Error(`API-Fehler: ${response.status} ${response.statusText}`);
                }

                // Parse the JSON response
                const responseData = await response.json();

                // Display a toast notification with the response status and message
                this.$showToast(responseData['status'], responseData['message']);

                // Return true or false based on response status
                if (responseData['status'] === 'success') {
                    return true;
                }
                else {
                    return false;
                }

            } catch (error) { // Catch block to handle any potential errors
                console.error('Fehler beim Senden der Anfrage:', error);
                this.$showToast('error', '<p>Ein Fehler ist aufgetreten:</p><pre>'+error+'</pre>');
                return false;
            }
        },

        /**
         * This asynchronous function is part of a Vue.js component that is responsible for
         * sending a PUT request to update a Customer Number in the "Bridge" system. The function
         * prepares the request data, sends the request, and handles the response by showing
         * toast notifications, throwing errors when needed and logging the response data.
         *
         * @function
         * @async
         */
        async api_customer_change_customer_nr_in_bridge() {
            // Prepare request data
            const requestData = {
                customer_id: this.customer_id,
                new_customer_nr: this.new_customer_nr,
                bridge_customer_id:this.bridge_customer_id,
            }

            try {
                // Send a PUT request to the specified URL
                const response = await fetch('/api/bridge/customers/update_erp_nr', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                // Throw an error if the response is not successful
                if (!response.ok) {
                    throw new Error(`API-Fehler: ${response.status} ${response.statusText}`);
                }

                // Parse the response data
                const responseData = await response.json();

                // Show a toast notification with the status and message
                this.$showToast(responseData['status'], responseData['message']);

                // Log the response data
                console.log(responseData);

                // If the status is "success", return true, otherwise return false
                if (responseData['status'] === 'success') {
                    return true;
                }
                else {
                    return false;
                }

            } catch (error) {
                // Log the error
                console.error('Fehler beim Senden der Anfrage:', error);

                // Show a toast notification with the error message
                this.$showToast('error', '<p>Ein Fehler ist aufgetreten:</p><pre>'+error+'</pre>');

                // Return false since there was an error
                return false;
            }
        },

        /**
         * Asynchronously fetches the current state of each order, payment, and shipping, and updates the UI accordingly.
         *
         * Function traverses through each element with the class '.order-states', extracting order, payment, and shipping state details.
         * For each situation, it calls fetchStateMachineTransitions method with necessary details if a state exists.
         */
        async fetchOrderStateName() {
            // Fetch all elements with the class '.order-states'
            const orderStatesElements = document.querySelectorAll('.order-states');

            for (const element of orderStatesElements) {
                // Fetch order API id from data attribute
                const orderApiId = element.dataset.orderApiId;

                // Fetch state details from each child element
                const orderState = element.querySelector('.order-state').dataset.orderState;
                const orderStateMachineId = element.querySelector('.order-state').dataset.orderStateMachineId;
                const paymentState = element.querySelector('.payment-state').dataset.paymentState;
                const paymentStateMachineId = element.querySelector('.payment-state').dataset.paymentStateMachineId;
                const shippingState = element.querySelector('.shipping-state').dataset.shippingState;
                const shippingStateMachineId = element.querySelector('.shipping-state').dataset.shippingStateMachineId;

                // Make asynchronous calls for each state
                if (orderState) {
                    await this.fetchStateMachineTransitions(orderState, orderStateMachineId, element, 'order');
                }
                if (paymentState) {
                    await this.fetchStateMachineTransitions(paymentState, paymentStateMachineId, element, 'payment');
                }
                if (shippingState) {
                    await this.fetchStateMachineTransitions(shippingState, shippingStateMachineId, element, 'shipping');
                }
            }
        },

        async fetchStateMachineTransitions(stateName, stateMachineId, parentElement, category) {
            if (!stateName) return; // Vermeide API-Aufruf, falls kein Zustandsname gesetzt ist

            try {
                const response = await fetch(`/api/orders/sw6/get_to_state_machine_transition_by_name/${stateName}/${stateMachineId}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                if (data.status === 'success') {
                    console.log(`Erfolg state details`, data.message);
                    console.log(data.data)
                    // Hier aktualisierst du das Select-Feld basierend auf der Kategorie
                    this.updateSelectOptions(parentElement, category, data.data);
                } else {
                    console.error(`Fehler beim Abrufen der state details:`, data.message);
                }
            } catch (error) {
                console.error(`Fehler bei der Anfrage für state:`, error);
            }
        },

        /**
         * Updates the options of a select element based on the given data.
         *
         * @param {HTMLElement} parentElement - The parent element containing the select element.
         * @param {string} category - The category of the select element.
         * @param {Array} options - An array of objects representing the options.
         *                          Each object should have properties 'actionName' and 'toStateMachineState'.
         * @return {void}
         */
        updateSelectOptions(parentElement, category, options) {
            const select = parentElement.querySelector(`.${category}-state select`);
            select.innerHTML = '<option value="" selected disabled>' + options[0].fromStateMachineState.name + '</option>'; // Setze eine leere Option und leere bestehende Optionen
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.actionName; // Angenommen, deine Optionen haben eine 'value' Eigenschaft
                optionElement.textContent = option.toStateMachineState.name; // und eine 'text' Eigenschaft
                select.appendChild(optionElement);
            });

            // Entferne den Spinner
            const spinner = parentElement.querySelector('.spinner-grow');
            if (spinner) {
                spinner.remove(); // Entferne den Spinner aus dem DOM
            }

            // Aktiviere das Select-Feld wieder
            select.disabled = false;
        },

        /**
         * Changes the state of an order based on the selected action.
         *
         * @param {Event} event - The event object that triggered the change.
         * @param {number} sw6OrderId - The ID of the order in the SW6 system.
         * @param {number} bridgeOrderId - The ID of the order in the bridge system.
         * @param {string} category - The category of the order.
         * @return {void}
         */
        onSelectChangeState(event, sw6OrderId, bridgeOrderId, category) {
            const actionName = event.target.value; // Wert des ausgewählten <option>
            console.log(`Order ID: ${orderId}, Action: ${actionName}, Category: ${category}`);
            // Implementiere hier die Logik, um den Zustand zu ändern
            this.changeOrderState(orderId, actionName, category);
        },

        /**
         * Asynchronously changes the state of an order based on the action and category given.
         *
         * @param {string} orderId - The ID of the order.
         * @param {string} actionName - The name of the action to be carried out on the order.
         * @param {string} category - The category of the order.
         */
        async changeOrderState(orderId, actionName, category) {
            // Running asynchronous operation to change state such as an API request
            console.log(`Changing state of ${category} for order ${orderId} to ${actionName}`);

            // Implement your asynchronous API call here
        },

    },
    mounted() {
        this.fetchOrderStateName()  // This is need to get all the states
    }
})