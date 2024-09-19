const app_product = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            categories: [], // Liste der Hauptkategorien
            activeCategoryId: null, // Aktive Kategorie-ID
            activeSubCategoryId: null // Aktive Unterkategorie-ID
        };
    },
    methods: {
        async syncProductToSw6(event) {
            try {
                this.$showToast('success', 'Sync SW6 gestartet!')
                const productId = event.target.dataset.bridgeProductId;
                // Call the API endpoint
                const response = await fetch(`/api/product/sync_to_sw6/${productId}`);
                const result = await response.json();
                this.$showToast(result.status, result.message);
            } catch (error) {
                console.log(error);
                // handle the error as appropriate for your application
            } finally {
                // Remove spinner class from button
                event.target.classList.remove('spinner-grow');
            }
        },
        async deleteProductInBridge(event) {
            // Benutzerabfrage, ob das Produkt wirklich gelöscht werden soll
            const confirmation = confirm("Sind Sie sicher, dass Sie dieses Produkt löschen möchten?");

            // Falls der Benutzer nicht bestätigt, wird die Operation abgebrochen
            if (!confirmation) {
                return;
            }

            try {
                this.$showToast('success', 'Löschvorgang gestartet!');
                const productId = event.target.dataset.bridgeProductId;
                // Ruf den API-Endpunkt auf
                const response = await fetch(`/api/product/delete_in_bridge/${productId}`, {
                    method: 'DELETE'
                });
                const result = await response.json();
                console.log(result);
                this.$showToast(result.status, result.message);
            } catch (error) {
                console.log(error);
                // Behandle den Fehler entsprechend Ihrer Anwendung
            } finally {
                // Entferne die Spinner-Klasse von der Schaltfläche
                event.target.classList.remove('spinner-grow');
            }
        },
        async syncProductToERP(event) {
            try {
                this.$showToast('success', 'Sync ERP gestartet!')
                const productId = event.target.dataset.bridgeProductId;
                // Call the API endpoint
                const response = await fetch(`/api/product/sync_to_erp/${productId}`);
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
        },
        async syncProductMarketplaceStatus(event) {
            let marketplaceId = event.target.dataset.marketplaceId;
            let productId = event.target.dataset.productId;
            let isActive = event.target.dataset.isActive === "True";
            let new_state = !isActive;
            try {
                event.target.disabled = true;
                this.$showToast('success', `Der Status des Produkts wird geändert! -> ${new_state}`);
                response = await fetch(`/api/product/sync_product_marketplace_status/${productId}/${marketplaceId}/${new_state}`);
                const result = await response.json();
                console.log(result);
                this.$showToast(result.status, result.message);

            } catch (error) {
                console.log(error);
                // handle the error as appropriate for your application
            } finally {
                // Remove spinner class from button
                event.target.dataset.isActive = new_state;
                event.target.classList.remove('spinner-grow');
                event.target.disabled = false;
            }
        },
        async syncStatusProduct(event) {
            let productId = event.target.dataset.productId;
            let isActive = event.target.dataset.isActive === "True";
            let new_state = !isActive;
            try {
                event.target.disabled = true;
                this.$showToast('success', `Der Status des Produkts ${productId} wird geändert. -> ${new_state}`);
                const response = await fetch(`/api/product/sync_status/${productId}/${new_state}`)
                const result = await response.json();
                console.log(result);
                this.$showToast(result.status, result.message);
            } catch (error) {

            } finally {
                event.target.dataset.isActive = new_state;
                event.target.disabled = false;
            }
        },
        async updateProductInBridge(event) {
            try {
                this.$showToast('success', 'Product wird von ERP geladen');
                const productId = event.target.dataset.bridgeProductId;

                // API-Endpunkt aufrufen
                const response = await fetch(`/api/product/update_in_bridge/${productId}`, {
                    method: 'PUT'
                });

                const result = await response.json();
                console.log(result);
                this.$showToast(result.status, result.message);
            } catch (error) {
                console.log(error);
                // Behandle den Fehler entsprechend Ihrer Anwendung
                this.$showToast('error', 'Ein Fehler ist beim Update des Produkts aufgetreten');
            }
        },
        async fetchCategoryChildren(category) {
            this.activeCategoryId = category.id;
            this.activeSubCategoryId = null;
            if (!category.children || category.children.length === 0) {
                try {
                    const response = await fetch(`/api/categories/${category.id}/children`);
                    if (response.ok) {
                        const data = await response.json();
                        const index = this.categories.findIndex(cat => cat.id === category.id);
                        if (index !== -1) {
                            this.categories[index].children = data.categories;
                        }
                    } else {
                        console.error('Fehler beim Abrufen der Unterkategorien');
                    }
                } catch (error) {
                    console.error('Fehler:', error);
                }
            }
        },
        async fetchCategoryProducts(parentCategory, subCategory) {
            this.activeSubCategoryId = subCategory.id;
            if (!subCategory.products || subCategory.products.length === 0) {
                try {
                    const response = await fetch(`/api/subcategories/${subCategory.id}/products`);
                    if (response.ok) {
                        const data = await response.json();
                        const parentIndex = this.categories.findIndex(cat => cat.id === parentCategory.id);
                        if (parentIndex !== -1) {
                            const childIndex = this.categories[parentIndex].children.findIndex(child => child.id === subCategory.id);
                            if (childIndex !== -1) {
                                this.categories[parentIndex].children[childIndex].products = data.products;
                            }
                        }
                    } else {
                        console.error('Fehler beim Abrufen der Produkte');
                    }
                } catch (error) {
                    console.error('Fehler:', error);
                }
            }
        },
    },
    mounted() {
        fetch('/api/categories/root')
            .then(response => response.json())
            .then(data => {
                if (data.result === 'success') {
                    this.categories = data.categories;
                    console.log(this.categories);
                } else {
                    console.error('Fehler beim Abrufen der Root-Kategorien:', data.message);
                }
            })
            .catch(error => {
                console.error('Fehler:', error);
            });
    }
})