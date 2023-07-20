<template>
    <table>
        <tr>
            <th>Shop Page</th>
            <th @click="sort('name')">Name</th>
            <th @click="sort('price')">Price</th>
            <th>Youtube Link</th>
            <th @click="sort('shout_count')">Shot Count</th>
            <th @click="sort('duration')">Duration</th>
            <th @click="sort('nem')">NEM</th>
            <th @click="sort('rating')">Rating</th>
            <th @click="sort('rated')">Rated</th>
            <th>Tags</th>
        </tr>
        <tr v-for="product in sortedProducts">
            <td align="left"><a :href="product.url" target="_blank">Pyroland</a></td>
            <td align="right"><a :href="'product/' + product.id_" target="_blank">{{ product.name }}</a></td>
            <td align="right">{{ (product.price == null) ? '-' : product.price / 100 }} €</td>
            <td align="right" v-if="product.youtube_handle == null"><a href="https://youtube.com/results?search_query={{ product.name }}" target="_blank">Search</a></td>
            <td align="lef" v-else><a :href="product.youtube_handle" target="_blank">Youtube</a></td>
            <td align="right">{{ product.shot_count }}</td>
            <td align="right">{{ product.duration }}</td>
            <td align="right">{{ (product.nem == null) ? '-' : product.nem / 1000 }} kg</td>
            <td align="right">{{ (product.rating == null) ? '-' : product.rating }}</td>
            <td align="right">{{ product.rated }}</td>
            <td align="right">{{ product.tags }}</td>
        </tr>
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
        this.getProducts();
    }
}
</script>