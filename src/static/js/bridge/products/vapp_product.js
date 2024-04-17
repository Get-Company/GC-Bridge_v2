const app_product = Vue.createApp({
    delimiters: ['${', '}'],
    methods: {
        async syncProductToSw6(event) {
            try {
                this.$showToast('success', 'Sync gestartet!')
                const productId = event.target.dataset.bridgeProductId;
                // Call the API endpoint
                const response = await fetch(`/api/product/sync_to_sw6/${productId}`);
                const result = await response.json();
                console.log(result)
                this.$showToast(result.status, result.message);
            } catch (error) {
                console.log(error);
                // handle the error as appropriate for your application
            } finally {
                // Remove spinner class from button
                event.target.classList.remove('spinner-grow');
            }
        }
    }
})