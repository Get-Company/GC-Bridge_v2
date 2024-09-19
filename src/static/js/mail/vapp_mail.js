const vapp_mail = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            progress: -1,
            search: '',
            results: [],
            selectedItems: [],
            selectedProducts: [], // Array to hold selected products
            selectedTemplate: '',
            responseDataHtml: '',
        };
    },
    methods: {
        fetchResults(search) {
            /**
             * Sends a GET request to the server for product search results.
             * It also handles the received data by calling the `this.handleData(data)` method and logs any encountered errors.
             *
             * @param {string} search - The string to search for amongst the products. Triggers the API call only when it's length is above 3 characters.
             * @return {Promise<any>} - It returns a Promise. In this case, this is the Promise returned by the `fetch()` method.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * app.fetchResults("test");
             */
            if (search.length >= 3) {
                fetch('/api/product/search?q=' + search)
                    .then(response => response.json())
                    .then(data => {
                        this.handleData(data);
                    })
                    .catch(error => console.error('Error:', error));
            }
        },
        handleData(data) {
            /**
             * Method to handle the data received from a fetch request.
             * It assigns the input data to the `results` field of the Vue instance.
             *
             * @param {Array<Object>} data - array of product data to be stored in `results`.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * const data = [{ 'name': 'Product1', 'price': '200'}, { 'name': 'Product2', 'price': '150' }];
             * app.handleData(data);
             */
            this.results = data;
        },
        addToProducts() {
            /**
             * Method to add selected items to the list of selected products, while ensuring there are no duplicates.
             *
             * @note The selectedItems are reset to an empty array after the operation.
             * @note At the end of the method, it also makes a call to `this.renderTemplate()` to update the state based on the updated products list.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * // and products exist with the names 'Product1' and 'Product2', and erp_nr '100' and '200' respectively
             * app.selectedItems = [{name: 'Product1', erp_nr: '100'}, {name: 'Product2', erp_nr: '200'}];
             * app.addToProducts(); // adds 'Product1' and 'Product2' to selectedProducts
             *
             * // Trying to add 'Product1' again, along with 'Product3'
             * app.selectedItems = [{name: 'Product1', erp_nr: '100'}, {name: 'Product3', erp_nr: '300'}];
             * app.addToProducts(); // adds only 'Product3' to selectedProducts, as 'Product1' is already in selectedProducts
             */
            if (this.selectedItems.length > 0) {
                for (let selectedItem of this.selectedItems) {
                    // Create a new instance of the object
                    let item = Object.assign({}, selectedItem);

                    // Check if the item is already in the array
                    let itemIndex = this.selectedProducts.findIndex(
                        sP => sP.name === item.name && sP.erp_nr === item.erp_nr
                    );
                    if (itemIndex === -1) {
                        this.selectedProducts.push(item);
                    }
                }

                this.selectedItems = []; // Reset selectedItems
            }
        },
        removeFromProducts(index) {
            /**
             * Method to remove an item from selected products at the given index.
             *
             * @param {number} index - The index at which the item is to be removed from the selected products.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * // and app.selectedProducts = [{ 'name': 'Product1' }, { 'name': 'Product2' }];
             * app.removeFromProducts(0); // removes 'Product1' from selectedProducts
             */
            this.selectedProducts.splice(index, 1); // Remove item from the array
        },
        async renderTemplate() {
            /**
             * Async method to render an email template, based on the currently selected template and products.
             * It sends a POST request to the server with the selected details, gets the response, and handles it accordingly.
             *
             * @note The rendered HTML (if present in the response) is added to the `#email` element on the page and in `this.responseDataHtml`.
             * @note Calls ['this.updateUrl()'] at the method's end to update URL parameters based on the changed state.
             * @note If the conditions for sending the POST request (that at least one template and product are selected) aren't met, error toast messages are shown.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * app.selectedTemplate = 'newsletter';
             * app.selectedProducts = [{ 'name': 'Product1', 'price': '200'}, { 'name': 'Product2', 'price': '150' }];
             * app.renderTemplate(); // Sends a POST request and handles the response
             */
            if (this.selectedTemplate && this.selectedProducts.length > 0) {
                // Create the payload
                const data = {
                    selectedTemplate: this.selectedTemplate,
                    products: this.selectedProducts
                };

                try {
                    // Send the POST request
                    const response = await fetch('/api/mail/render_template', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                    });

                    if (!response.ok) throw new Error(`HTTP status ${response.status}`);

                    const responseData = await response.json();  // << Rename this variable

                    console.log('Success:', responseData);

                    // Create a toast message based on the status
                    if (responseData.status_code === 200) {
                        this.$showToast('success', 'Email template created successfully.');
                    } else {
                        this.$showToast('error', responseData.message);
                        console.log(responseData);
                    }

                    // If the response contains HTML, append it to the #email element
                    if ('html' in responseData) {
                        let emailDiv = document.querySelector('#email');
                        emailDiv.innerHTML = responseData.html;
                        this.responseDataHtml = responseData.html;
                    }
                } catch (error) {
                    console.error('Error:', error);
                    this.$showToast('error', error.toString());
                }
            } else {
                // Show a toast message if conditions are not met
                if (!this.selectedTemplate) {
                    this.$showToast('error', 'Bitte ein template wählen');
                }
                if (this.selectedProducts.length === 0) {
                    this.$showToast('error', 'Bitte mindestens 1 Pordukt auswählen');
                }
            }
            this.updateUrl()
        },
        updateUrl() {
            /**
             * Method to update the URL's query parameters based on current state of selectedTemplate and selectedProducts.
             * It modifies the window's history using the pushState method, so the page is not refreshed from this modification.
             *
             * @note The updated selectedProducts array is being transformed into a base64 string via `btoa(JSON.stringify(this.selectedProducts))` for preserving the array structure in the URL.
             *
             * @example
             *
             * // Assuming an instance of the Vue app is stored in `app`
             * app.updateUrl(); // updates URL with the current `this.selectedTemplate` and `this.selectedProducts`
             *
             * // Example of URL Parameters Update:
             *
             * // Current state:
             * // this.selectedTemplate = "template1";
             * // this.selectedProducts = [{ "name": "product1", "price": "100" }, { "name": "product2", "price": "200" }];
             *
             * // After calling `app.updateUrl()`:
             * // The URL could look like this: 'http://example.com?selectedTemplate=template1&selectedProducts=W3sibmFtZSI6InByb2R1Y3QxIiwicHJpY2UiOiIxMDAifSx7Im5hbWUiOiJwcm9kdWN0MiIsInByaWNlIjoiMjAwIn1d'
             *
             * // Decoding Process:
             * // The base64 string 'W3sibmFtZSI6InByb2R1Y3QxIiwicHJpY2UiOiIxMDAifSx7Im5hbWUiOiJwcm9kdWN0MiIsInByaWNlIjoiMjAwIn1d' can be decoded using `atob()`.
             * // And then parse the decoded JSON string back into a JavaScript object using `JSON.parse()`.
             * let encodedProducts = 'W3sibmFtZSI6InByb2R1Y3QxIiwicHJpY2UiOiIxMDAifSx7Im5hbWUiOiJwcm9kdWN0MiIsInByaWNlIjoiMjAwIn1d';
             * let decodedProducts = JSON.parse(atob(encodedProducts));
             *
             * console.log(decodedProducts); // Prints: [{ "name": "product1", "price": "100" }, { "name": "product2", "price": "200" }]
             */
            const url = new URL(window.location.href);
            url.searchParams.set('selectedTemplate', this.selectedTemplate);
            url.searchParams.set('selectedProducts', btoa(JSON.stringify(this.selectedProducts)));
            window.history.pushState({}, '', url);
        },
    },
    created() {
        const url = new URL(window.location.href);
        if (url.searchParams.has('selectedTemplate')) {
            this.selectedTemplate = url.searchParams.get('selectedTemplate');
        }
        if (url.searchParams.has('selectedProducts')) {
            this.selectedProducts = JSON.parse(atob(url.searchParams.get('selectedProducts')));
        }
    }
});