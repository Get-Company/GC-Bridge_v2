const app_orders = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            progress: -1, // Init value for the progress bar
        };
    },
    methods: {
        async api_orders_sw6_get_open_ids() {
            this.progress = 0;
            try {
                const response = await fetch('/api/orders/sw6/get_open_order_ids');
                if (!response.ok) {
                    throw new Error('Fehler beim Abrufen der Bestellungen');
                }
                const result = await response.json();
                this.$showToast(result.status, result.message);
                this.progress= 5;


                for (const [index,orderId] of result.order_ids.data.entries()) {
                    await this.api_orders_sw6_sync_one_to_bridge(orderId);
                    this.progress = ((index+1) / (result.order_ids.total)) * 100;
                }
                this.progress = -1;

            } catch (error) {
                this.progress = -1;
                console.error(error);
                this.$showToast('error', '<p>Ein Fehler ist aufgetreten:</p>' + error);
            }
            this.$showToast('success', `${result.order_ids.total} Bestellungen wurden angelegt.`);
        },
        async api_orders_sw6_sync_one_to_bridge(sw6_order_id) {
            try {
                // Ersetzen Sie <sw6_order_id> durch die tatsächliche Order-ID
                const response = await fetch(`/api/orders/sw6/sync_one_to_bridge/${sw6_order_id}`);

                if (!response.ok) {
                    throw new Error('Fehler beim Synchronisieren der Bestellung');
                }

                const result = await response.json();

                // Sie können hier result verwenden, um eine Erfolgsmeldung anzuzeigen oder weitere Aktionen durchzuführen
                this.$showToast('success', result.message);
            } catch (error) {
                console.error(error);
                this.$showToast('error', `Fehler beim Synchronisieren der Bestellung ${sw6_order_id}.`);
            }
        }
    }

})