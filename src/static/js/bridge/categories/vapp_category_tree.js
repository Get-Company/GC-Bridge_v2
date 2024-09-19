const app_bridge_category_tree = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            tree: [],
            tree_index: 0

        };
    },
    methods: {
        async fetchCategoryTree() {
            try {
                const response = await fetch('/api/categories/get_category_tree');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                } else {
                    this.tree = await response.json();
                    this.createNewSortable()
                }
            } catch (error) {
                console.log('Error fetching category tree', error);
            } finally {
                document.getElementById('info').style.display = 'none';
            }
        },


        async sendData(requestData) {
            const response = await fetch('/api/category/set_assoc_sort', {  // Update URL if needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            if (response.ok) {
                this.$showToast('success', 'Daten erfolgreich aktualisiert');  // Update message if needed
                return response
            } else {
                this.$showToast('error', 'Es ist ein Fehler bei der Aktualisierung aufgetreten');  // Update message if needed
            }
        },

        getNodeData(node) {
            const span = node.querySelector('span');
            return {
                id: span.dataset.id,
                after_category_id: span.dataset.after_category_id,
                parent_category_id: span.dataset.parent_category_id,
                type_of: span.dataset.type,
                title: span.dataset.title,
                category_id: span.dataset.category_id,
                sort: span.dataset.sort,
            };
        },

        saveNodeData(node, data) {
            const span = node.querySelector('span');
            span.dataset.id = data.id;
            span.dataset.after_category_id = data.after_category_id;
            span.dataset.parent_category_id = data.parent_category_id;
            span.dataset.type_of = data.type_of;
            span.dataset.title = data.title;
            span.dataset.category_id = data.category_id;
            span.dataset.sort = data.sort;
            if (data.type_of === 'category') {
                span.innerText = `"${data.title}: ${data.id}`;
            } else if (data.type_of === 'product') {
                span.innerText = `"${data.title}: ${data.id}`;
            }
        },

        findNextTreeNode(searchId, rootNode) {
            let spanElement = rootNode.querySelector('span[data-id="' + searchId + '"]');

            if (spanElement !== null) {
                let currentNode = spanElement.parentNode.parentNode; // get the parent node

                if (currentNode.nextElementSibling !== null) {
                    return currentNode.nextElementSibling; // return the next sibling node if it exists
                }
            }

            console.log(`No next sibling node found after span with data-id=${searchId}`);
            return null; // no next sibling node found after the span with the required data-id
        },

        createNewSortable() {
            this.tree = new SortableTree({
                nodes: this.tree,
                element: this.$el.querySelector('#tree'),
                stateId: 'tree-basic',
                initCollapseLevel: 1,
                confirm: async (movedNode, targetParentNode) => {
                    return confirm("Wirklich verschieben?");
                },
                renderLabel: ({
                                  nodes,
                                  id,
                                  after_category_id,
                                  parent_category_id,
                                  type_of,
                                  title,
                                  category_id,
                                  sort
                              }) => {
                    let spanTemplate = '';

                    if (type_of === 'category') {
                        spanTemplate = `
                        <span 
                        data-id="${id}"
                        data-after_category_id="${after_category_id}"
                        data-parent_category_id="${parent_category_id}"
                        data-type="${type_of}" 
                        data-title="${title}" >
                            ${title}: ${id}
                            <i class="fas fa-info-circle" @click="getProductsOfCategory(${id})"></i>
                        </span>
                        <ul v-if="activeCategoryId === ${id}">
                            ${nodes && nodes.map(product => `
                                <li key="${product.id}">
                                    ${product.name} (${product.erp_nr}): ${product.id}
                                </li>
                            `).join('')}
                        </ul>
                    `;
                    } else if (type_of === 'product') {
                        spanTemplate = `
                        <span 
                        data-id="${id}"
                        data-type="${type_of}" 
                        data-title="${title}"
                        data-category_id="${category_id}"
                        data-sort="${sort}">
                            ${title}: ${id}
                        </span>
                    `;
                    }
                    return spanTemplate;
                },

                onChange: async ({nodes, movedNode, srcParentNode, targetParentNode}) => {
                    const movedNodeData = this.getNodeData(movedNode);
                    const srcNodeData = this.getNodeData(srcParentNode);
                    const targetNodeData = this.getNodeData(targetParentNode);
                    const targetNextNode = this.findNextTreeNode(movedNodeData.id, targetParentNode);
                    const targetNextNodeData = this.getNodeData(targetNextNode);

                    const message = `Verschieben <b>"${movedNodeData.title}"</b> von <b>"${srcNodeData.title}"</b> nach <b>"${targetNodeData.title}"</b> gestartet!"`;
                    this.$showToast('success', message);

                    // Object mit allen Daten, bereit zum Versand
                    const requestData = {
                        moved: movedNodeData,
                        source: srcNodeData,
                        target: targetNodeData,
                        targetNextNode: targetNextNodeData
                    };

                    const response = await this.sendData(requestData)
                        .catch(error => {
                            console.error('Error:', error);
                            this.$showToast('error', 'Es ist ein Fehler bei der Übertragung aufgetreten');
                        });
                },
            });
        },
        async getProductsOfCategory(categoryId) {
            this.activeCategoryId = categoryId; // Setze die Kategorie als aktiv
            try {
                const response = await fetch(`/api/products/get_by_category/${categoryId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();

                    if (data.status === 'success') {
                        this.$showToast('success', 'Produkte erfolgreich abgerufen');
                        // Füge die Produkte zu der entsprechenden Kategorie hinzu
                        const category = this.tree.find(node => node.id === categoryId);
                        if (category) {
                            this.$set(category, 'products', data.products); // setze die Produkte-Knoten dynamisch
                        }
                        this.createNewSortable(); // Refresh the SortableTree
                    } else {
                        this.$showToast('error', data.message);
                    }
                } else {
                    this.$showToast('error', 'Es ist ein Fehler beim Abrufen der Produkte aufgetreten');
                }
            } catch (error) {
                console.error('Error:', error);
                this.$showToast('error', 'Es ist ein Fehler bei der Übertragung aufgetreten');
            }
        },
    },
    mounted() {
        this.fetchCategoryTree();
    }

});