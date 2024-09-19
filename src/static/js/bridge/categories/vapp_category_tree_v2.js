// vapp_category_tree_v2.js
const CategoryNode = {
    name: 'CategoryNode',
    props: ['node'],
    data() {
        return {
            products: [],
            showProducts: false
        };
    },
    methods: {
        async loadProducts(categoryId) {
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
                        this.products = data.products;
                    } else {
                        console.error('Fehler:', data.message);
                    }
                } else {
                    console.error('Fehler beim Abrufen der Produkte');
                }
            } catch (error) {
                console.error('Fehler:', error);
            }
        },
        toggleProducts() {
            console.log('Klick auf Caret');
            if (this.showProducts) {
                this.showProducts = false;
            } else {
                this.loadProducts(this.node.data.id)
                    .then(() => {
                        this.showProducts = true;
                    });
            }
        },
        async updateSortField(product) {
            try {
                const response = await fetch('/api/product/update_sort', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        product_id: product.id,
                        sort: product.sort,
                    }),
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.status === 'success') {
                        // Optional: Erfolgsmeldung anzeigen
                        this.$showToast('success', 'Sortierwert erfolgreich aktualisiert');
                    } else {
                        console.error('Fehler:', data.message);
                        this.$showToast('error', 'Fehler beim Aktualisieren des Sortierwerts: ' + data.message);
                    }
                } else {
                    console.error('Fehler beim Aktualisieren des Sortierwerts');
                    this.$showToast('error', 'Fehler beim Aktualisieren des Sortierwerts');
                }
            } catch (error) {
                console.error('Fehler:', error);
                this.$showToast('error', 'Fehler beim Aktualisieren des Sortierwerts: ' + error.message);
            }
        },
    },
    template: `
      <li>
        <span>{{ node.data.title }}: {{ node.data.id }}</span>
        &nbsp;
        <a @click.prevent="toggleProducts" href="#" class="btn btn-dark" role="button">
          i
        </a>
        <ul v-if="node.nodes.length">
          <category-node v-for="child in node.nodes" :key="child.data.id" :node="child"></category-node>
        </ul>
        <ul v-if="showProducts">
          <li v-for="product in products" :key="product.id">
            {{ product.name }} ({{ product.erp_nr }}): {{ product.id }}
            <!-- Neues Sort-Eingabefeld -->
            <input type="number" v-model.number="product.sort" @change="updateSortField(product)"/>
          </li>
        </ul>
      </li>
    `,
    components: {
        'category-node': null  // Wird später zugewiesen
    }
};

CategoryNode.components['category-node'] = CategoryNode;

const CategoryTree = {
    template: `
      <div>
        <ul>
          <category-node v-for="node in tree" :key="node.data.id" :node="node"></category-node>
        </ul>
      </div>
    `,
    data() {
        return {
            tree: [],  // Hier wird der CategoryTree gespeichert
        };
    },
    components: {
        'category-node': CategoryNode
    },
    methods: {
        async fetchCategoryTree() {
            try {
                const response = await fetch('/api/categories/get_category_tree', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    this.tree = data;
                } else {
                    console.error('Fehler beim Abrufen der Kategorien');
                }
            } catch (error) {
                console.error('Fehler:', error);
            }
        }
    },
    created() {
        this.fetchCategoryTree(); // Lade die Kategorien beim Erstellen der Komponente
    }
};

const app_bridge_category_tree = Vue.createApp(CategoryTree);