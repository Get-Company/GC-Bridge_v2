const app_orders = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            progress: -1, // Init value for the progress bar
        };
    },
    methods: {
        /**
         * Asynchronously retrieves and syncs open order IDs from an API endpoint.
         * Initial progress is set to 0 and progresses as each order ID is successfully synced.
         * Finally, it displays a toast message indicating the number of orders were processed.
         * If an error occurs during the process, a toast error message is displayed and progress is set to -1.
         * After displaying the toast message, the page reloads after a delay of 2 seconds, regardless of success or error.
         */
        async api_orders_sw6_get_open_ids() {
            // Initializing progress to 0
            this.progress = 0;

            try {
                // Fetching open order IDs from the api endpoint
                const response = await fetch('/api/orders/sw6/get_open_order_ids');

                // Handling fetch failure cases
                if (!response.ok) {
                    throw new Error('Fehler beim Abrufen der Bestellungen');
                }

                // Parsing response to json
                const result = await response.json();

                console.log(result);

                // Displaying a toast message for the given status and message
                this.$showToast(result.status, result.message);

                // Updating progress to 5
                this.progress= 5;

                // Syncing each order to the bridge and updating progress
                for (const [index,orderId] of result.order_ids.data.entries()) {
                    await this.api_orders_sw6_sync_one_to_bridge(orderId);
                    this.progress = ((index+1) / (result.order_ids.total)) * 100;
                }
                // Displaying a success toast message indicating the number of orders processed
                this.$showToast('success', result.message);

                // Setting progress to -1 after completion of all orders
                this.progress = -1;
            } catch (error) {
                // Setting progress to -1 and logging error to console when an error occurs
                this.progress = -1;
                console.error(error);

                // Displaying a toast error message
                this.$showToast('error', '<p>Ein Fehler ist aufgetreten:</p>' + error);
            }

           

            // Reloading the page after a delay of 2 seconds
            setTimeout(() => {
                console.log("Reload after fetching orders in 2 sec...");
                window.location = "/orders";
            }, 2000);  // 2000ms delay for timeout
        },

        /**
         * Asynchronously sends a specific order to a bridge by using its 'sw6_order_id'.
         * If the order is successfully sent, it shows a success toast with the response message.
         * If an error occurs during this process, it logs the error and subsequently shows an error toast message.
         *
         * @async
         * @param {string} sw6_order_id - An order's identifier in the SW6 system.
         *
         * @throws {Error} Will throw an error if the response from the fetch function isn't okay.
         */
        async api_orders_sw6_sync_one_to_bridge(sw6_order_id) {
            try {
                // Replaces <sw6_order_id> with the actual order ID
                const response = await fetch(`/api/orders/sw6/sync_one_to_bridge/${sw6_order_id}`, {method: 'PATCH'});
                if (!response.ok) {
                    throw new Error('Fehler beim Synchronisieren der Bestellung');
                }
                const result = await response.json();
                // Use 'result' here to display a success message or perform other actions
                this.$showToast('success', result.message);
            } catch (error) {
                // Logs any error encountered during the process
                console.error(error);
                // Shows an error toast with the order ID that encountered the error during synchronization
                this.$showToast('error', `Fehler beim Synchronisieren der Bestellung ${sw6_order_id}.`);
            }
        },

    }

})