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
            orders: []
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
            const orderStatesElements = document.querySelectorAll('.order-states');

            for (const element of orderStatesElements) {
                const orderApiId = element.dataset.orderApiId;

                const orderState = element.querySelector('.order-state').dataset.orderState;
                const orderStateMachineId = element.querySelector('.order-state').dataset.orderStateMachineId;
                const paymentState = element.querySelector('.payment-state').dataset.paymentState;
                const paymentStateMachineId = element.querySelector('.payment-state').dataset.paymentStateMachineId;
                const shippingState = element.querySelector('.shipping-state').dataset.shippingState;
                const shippingStateMachineId = element.querySelector('.shipping-state').dataset.shippingStateMachineId;

                const promises = []; // Array to store Promises

                // Instead of awaiting each operation, add them to the promises array
                if (orderState) {
                    promises.push(this.fetchStateMachineTransitions(orderState, orderStateMachineId, element, 'order'));
                }
                if (paymentState) {
                    promises.push(this.fetchStateMachineTransitions(paymentState, paymentStateMachineId, element, 'payment'));
                }
                if (shippingState) {
                    promises.push(this.fetchStateMachineTransitions(shippingState, shippingStateMachineId, element, 'shipping'));
                }

                // Now wait for all promises to complete.
                // This will run all the promises in parallel and wait for all of them to complete
                await Promise.allSettled(promises);
            }
        },

        /**
         * Asynchronously fetches the transitions of a specific state machine, based on a state name and state machine Id,
         * and updates select options using the resulting data.
         *
         * The function will avoid making an API call if no state name is provided,
         * and will log any encountered errors during its execution.
         * If the fetched data has its status as success,
         * the function then updates select options on the front end.
         *
         * @param {string} stateName - The name of the state whose transitions are to be fetched.
         * @param {string} stateMachineId - The Id of the state machine whose transitions are to be fetched.
         * @param {HTMLElement} parentElement - The parent element containing the to be updated select component.
         * @param {string} category - The category of the select field to be updated.
         * @return {void}
         */
        async fetchStateMachineTransitions(stateName, stateMachineId, parentElement, category) {
            if (!stateName) return; // Avoid API call if no stateName provided

            try {
                const response = await fetch(`/api/orders/sw6/get_to_state_machine_transition_by_name/${stateName}/${stateMachineId}`);

                if (!response.ok) {
                    this.$showToast('error', `Status für ${parentElement} konnte nicht gesetzt werden`);
                    // Throwing an error in case of non-success HTTP status
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.status === 'success') {
                    console.log(`Successfully fetched state details`, data.message);

                    // Updating the select field based on the category in case of success
                    this.updateSelectOptions(parentElement, category, data.data);
                } else {
                    console.error(`Error fetching state details:`, data.message); // Log error message in case of unsuccessful fetch
                }
            } catch (error) {
                console.error(`Error in request for state:`, error); // Log error message in case of exception
            }
        },

        /**
         * Function to update the options of a select element with provided options.
         *
         * @param {HTMLElement} parentElement - The parent HTML element hosting the select element.
         * @param {string} category - The category to which the select element belongs.
         * @param {Array} options - An array of option objects, each containing 'actionName' and 'toStateMachineState' properties.
         * @returns {void}
         */
        updateSelectOptions(parentElement, category, options) {
            const select = parentElement.querySelector(`.${category}-state select`);
            // Set first option as default and clear existing options using options[0].fromStateMachineState.name
            select.innerHTML = '<option value="" selected disabled>' + options[0].fromStateMachineState.name + '</option>';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                // Assume your options have a 'value' property
                optionElement.value = option.actionName;
                // And a 'text' property
                optionElement.textContent = option.toStateMachineState.name;
                // Append the created option element to the select
                select.appendChild(optionElement);
            });
            // Fetch the spinner element
            const spinner = parentElement.querySelector('.spinner-grow');
            // If spinner exists, remove it from the DOM
            if (spinner) {
                spinner.remove();
            }
            // Enable the select field
            select.disabled = false;
        },

        /**
         * Responds to a UI event by changing the state of an order.
         * Logs the order ID, action, and category, shows a confirmation toast,
         * and triggers the order state change.
         *
         * @param {Event} event - The event triggered on the UI.
         * @param {number} sw6OrderId - The order's ID in the SW6 system.
         * @param {number} bridgeOrderId - The order's ID in the bridge system.
         * @param {string} category - The order's category (could be 'order', 'payment', or 'shipping').
         * @return {void}
         */
        async onSelectChangeState(event, sw6OrderId, bridgeOrderId, category) {
            const actionName = event.target.value; // The chosen action.


            // Log formatted order details.
            console.log(`Order ID: ${sw6OrderId}, Action: ${actionName}, Category: ${category}`);

            // Show a confirmation toast.
            this.$showToast('success', `Status <strong>"${category}"</strong> wird auf <strong>"${actionName}"</strong> geändert`);

            // Perform the state change.
            event.target.disabled = true;
            await this.changeOrderState(sw6OrderId, bridgeOrderId, actionName, category);
            event.target.disabled = false;
        },

        /**
         * Changes the state of an order by sending a GET request to the proper API endpoint.
         *
         * @param {number} sw6OrderId - The order's ID in the SW6 system.
         * @param {number} bridgeOrderId - The order's ID in the bridge system.
         * @param {string} actionName - The action name to set.
         * @param {string} category - The order's category (could be 'order', 'payment', or 'shipping').
         * @return {void}
         */
        async changeOrderState(sw6OrderId, bridgeOrderId, actionName, category) {
            console.log(`Changing state of ${category} for order ${sw6OrderId} to ${actionName}`);
            let endpoint;
            switch(category) {
                case 'order':
                    endpoint = `/api/orders/sw6/order/${sw6OrderId}/state/${actionName}`;
                    break;
                case 'payment':
                    endpoint = `/api/orders/sw6/order_transaction/${sw6OrderId}/state/${actionName}`;
                    break;
                case 'shipping':
                    endpoint = `/api/orders/sw6/order_delivery/${sw6OrderId}/state/${actionName}`;
                    break;
                default:
                    console.log(`Unknown category: ${category}`);
                    return;
            }

            try {
                const response = await fetch(endpoint, { method: 'PATCH' });
                if(response.ok) {
                    const data = await response.json();
                    console.log(data.message);
                    this.$showToast('success', `Status <strong>"${category}"</strong> for order ${sw6OrderId} changed to <strong>"${actionName}"</strong>`);
                    await this.syncOrderToBridge(sw6OrderId);

                } else {
                    console.log(`Error with HTTP request: ${response.statusText}`);
                    this.$showToast('error', `Failed to change status of <strong>"${category}"</strong> for order ${sw6OrderId}`);
                }
            } catch(error) {
                console.error(`Fetch error: ${error}`);
                this.$showToast('error', `Fetch error: ${error}`);
            }
        },
        /**
         * Syncs an order to the bridge system by sending a PUT request to the proper API endpoint.
         *
         * @param {number} sw6OrderId - The order's ID in the SW6 system.
         * @return {void}
         */
        async syncOrderToBridge(sw6OrderId) {
            console.log(`Syncing SW6 Order ${sw6OrderId} to the bridge system.`);
            let endpoint = `/api/orders/sw6/sync_one_to_bridge/${sw6OrderId}`;

            try {
                const response = await fetch(endpoint, { method: 'PATCH' });
                if(response.ok) {
                    const data = await response.json();
                    console.log(data.message);
                    this.$showToast('success', data.message);
                } else {
                    const data = await response.json();
                    console.log(`Error with HTTP request: ${response.statusText}`);
                    this.$showToast('error', data.message);
                }
            } catch(error) {
                console.error(`Fetch error: ${error}`);
                this.$showToast('error', `Fetch error: ${error}`);
            }
        },

        async create_order_in_erp_by_bridge_order_id(order_id) {
            // Call the Flask API endpoint
            try {
                const response = await fetch(
                    `/api/orders/erp/create_order/${order_id}`,
                    { method: "POST" }
                );

                // Get the result from the response to acquire the message
                const result = await response.json();

                if (!response.ok) {
                    // Show error toast with message from the server
                    this.$showToast('error', result.message);
                    throw new Error(result.message);
                }

                // Show success toast with message from the server
                this.$showToast('success', result.message);
            } catch (error) {
                console.error("There was a problem with the fetch operation:", error);
                // If the error is not from the server, show a generic error message
                if (!error.message.includes('No order found') || !error.message.includes('Bestellung')) {
                    this.$showToast('error', `Fehler: ${error.message}`);
                }
            }
        }



    },
    mounted() {
        this.fetchOrderStateName()  // This is need to get all the states
    }
})