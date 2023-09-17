<style>
table {
    width: 100%;
    border: 1px solid black;
}
.table-cell {
    border: 1px solid black;
}
.sortable {
    text-decoration: underline;
    color: red;
    cursor: pointer;
}
</style>

<template>
    <a href="/">Main Page</a>
    <table>
        <thead>
        <tr>
            <th class="table-cell">Shop</th>
            <th class="table-cell sortable" @click="sort('package_size')">Name</th>
            <th class="table-cell sortable" @click="sort('price')">Price</th>
            <th class="table-cell">YT Link</th>
            <th class="table-cell sortable" @click="sort('shot_count')">Shots</th>
            <th class="table-cell sortable" @click="sort('duration')">Duration</th>
            <th class="table-cell sortable" @click="sort('nem')">NEM</th>
            <th class="table-cell sortable" @click="sort('nem_per_second')">NEM/s</th>
            <th class="table-cell sortable" @click="sort('nem_per_shot')">NEM/Shot</th>
            <th class="table-cell sortable" @click="sort('price_per_second')">€/s</th>
            <th class="table-cell sortable" @click="sort('price_per_shot')">€/Shot</th>
            <th class="table-cell sortable" @click="sort('price_per_nem')">€/NEM</th>
            <th class="table-cell sortable" @click="sort('shots_per_second')">Shots/s</th>
            <th class="table-cell sortable" @click="sort('rating')">Rating</th>
            <th class="table-cell sortable" @click="sort('rated')">Rated</th>
            <th class="table-cell">Tags</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="product in sortedProducts">
            <td class="table-cell" align="left"><a :href="product.url" target="_blank">Shop</a></td>
            <td class="table-cell" align="right"><a :href="'product/' + product.id_" target="_blank">{{ product.short_name }}</a>[{{ product.package_size }}]</td>
            <td class="table-cell" align="right">{{ (product.price == null) ? '-' : product.price / 100 }} €</td>
            <td class="table-cell" align="right" v-if="product.youtube_handle == null"><a :href="'https://youtube.com/results?search_query=' + product.name" target="_blank">Search</a></td>
            <td class="table-cell" align="right" v-else><a :href="product.youtube_handle" target="_blank">YT</a></td>
            <td class="table-cell" align="right">{{ (product.shot_count == null) ? '-' : product.shot_count }}</td>
            <td class="table-cell" align="right">{{ (product.duration == null) ? '-' : product.duration }}</td>
            <td class="table-cell" align="right">{{ (product.nem == null) ? '-' : product.nem / 1000 }} kg</td>
            <td class="table-cell" align="right">{{ (product.nem_per_second == null) ? '-' : product.nem_per_second }} kg/s</td>
            <td class="table-cell" align="right">{{ (product.nem_per_shot == null) ? '-' : product.nem_per_shot }} kg</td>
            <td class="table-cell" align="right">{{ (product.price_per_second == null) ? '-' : product.price_per_second }} €/s</td>
            <td class="table-cell" align="right">{{ (product.price_per_shot == null) ? '-' : product.price_per_shot }} €</td>
            <td class="table-cell" align="right">{{ (product.price_per_nem == null) ? '-' : product.price_per_nem }} €/kg</td>
            <td class="table-cell" align="right">{{ (product.shots_per_second == null) ? '-' : product.shots_per_second }} Hz</td>
            <td class="table-cell" align="right">{{ (product.rating == null) ? '-' : product.rating }}</td>
            <td class="table-cell" align="right">{{ product.rated }}</td>
            <td class="table-cell" align="right">{{ tagsString(product) }}</td>
        </tr>
        </tbody>
    </table>
</template>

<script>
import axios from 'axios';

export default {
    name: 'Overview',
    data() {
        return {
            products: [],
            currentSortKey: 'name',
            currentSortDir: 'asc'
        }
    },
    methods: {
        getProducts() {
            const path = "http://localhost:5000/products";
            axios.get(path)
                .then((res) => {
                    console.log(res.data);
                    this.products = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        sort(key) {
            if (key == this.currentSortKey) {
                this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc';
            }
            this.currentSortKey = key;
        },
        tagsString(product) {
            return product.tags.join(", ");
        }
    },
    computed: {
        sortedProducts() {
            return this.products.sort((a,b) => {
                let modifier = 1;
                if(this.currentSortDir === 'desc') modifier = -1;
                if(a[this.currentSortKey] < b[this.currentSortKey]) return -1 * modifier;
                if(a[this.currentSortKey] > b[this.currentSortKey]) return 1 * modifier;
                return 0;
            });
        }
    },
    created() {
        document.title = "Overview";
        this.getProducts();
    }
}
</script>