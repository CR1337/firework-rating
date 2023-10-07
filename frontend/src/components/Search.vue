<style>
    .bordered {
        border: 1px solid black;
        padding: 10px;
        margin: 10px;
    }
</style>

<template>
    Save: <input type="text" v-model="searchName"><button @click="saveSearch()">💾</button>
    <template v-if="searches.length > 0">
        Load: <select v-model="selectedSearch">
            <option v-for="search in searches" :value="search">{{ search }}</option>
        </select>
        <button @click="loadSearch()">📂</button>
        <button @click="deleteSearch()">🗑️</button>
    </template>
    <div class="bordered"><Filter type="group" inverted="false" :filters="[]" uuid="root" @data-changed="filterDataChanged"></Filter></div><br>
    <a href="/">Main Page</a><br>
    <button @click="new_search()">🆕 New Search</button>
    <button @click="perform_search()">🔍 Find</button>
    <button @click="toggleColumnSelection()">↘️</button>
    <br><br>
    <template v-if="showColumnSelection">
        <template v-for="(_, column, index) of showColumns">
            <label><input type="checkbox" v-model="showColumns[column]">{{ column }}</label>&nbsp;&nbsp;&nbsp;
            <template  v-if="(index + 1) % 3 == 0"><br><br></template>
        </template>
        <br><br>
    </template>
    Found {{ products.length }} products.
    <table>
        <thead>
        <tr>
            <th v-if="showColumns.id" class="table-cell">ID</th>
            <th v-if="showColumns.is_new" class="table-cell">New</th>
            <th v-if="showColumns.availability" class="table-cell">Available</th>
            <th v-if="showColumns.shop" class="table-cell">Shop</th>
            <th v-if="showColumns.article_number" class="table-cell">Article Number</th>
            <th v-if="showColumns.name" class="table-cell sortable" @click="sort('name')">Name</th>
            <th v-if="showColumns.package_size" class="table-cell sortable" @click="sort('package_size')">Package Size</th>
            <th v-if="showColumns.price" class="table-cell sortable" @click="sort('price')">Price</th>
            <th v-if="showColumns.yt_link" class="table-cell">YT Link</th>
            <th v-if="showColumns.shot_count" class="table-cell sortable" @click="sort('shot_count')">Shots</th>
            <th v-if="showColumns.duration" class="table-cell sortable" @click="sort('duration')">Duration</th>
            <th v-if="showColumns.nem" class="table-cell sortable" @click="sort('nem')">NEM</th>
            <th v-if="showColumns.weight" class="table-cell sortable" @click="sort('weight')">Weight</th>
            <th v-if="showColumns.min_caliber" class="table-cell sortable" @click="sort('min_caliber')">Min Caliber</th>
            <th v-if="showColumns.max_caliber" class="table-cell sortable" @click="sort('max_caliber')">Max Caliber</th>
            <th v-if="showColumns.min_height" class="table-cell sortable" @click="sort('min_height')">Min Height</th>
            <th v-if="showColumns.max_height" class="table-cell sortable" @click="sort('max_height')">Max Height</th>
            <th v-if="showColumns.nem_per_second" class="table-cell sortable" @click="sort('nem_per_second')">NEM/s</th>
            <th v-if="showColumns.nem_per_shot" class="table-cell sortable" @click="sort('nem_per_shot')">NEM/Shot</th>
            <th v-if="showColumns.price_per_second" class="table-cell sortable" @click="sort('price_per_second')">€/s</th>
            <th v-if="showColumns.price_per_shot" class="table-cell sortable" @click="sort('price_per_shot')">€/Shot</th>
            <th v-if="showColumns.price_per_nem" class="table-cell sortable" @click="sort('price_per_nem')">€/NEM</th>
            <th v-if="showColumns.shots_per_second" class="table-cell sortable" @click="sort('shots_per_second')">Shots/s</th>
            <th v-if="showColumns.rating" class="table-cell sortable" @click="sort('rating')">Rating</th>
            <th v-if="showColumns.rated" class="table-cell sortable" @click="sort('rated')">Rated</th>
            <th v-if="showColumns.tags" class="table-cell sortable" @click="sort('tags')">Tags</th>
            <th v-if="showColumns.colors" class="table-cell sortable" @click="sort('colors')">Colors</th>
            <th v-if="showColumns.fan" class="table-cell">Fan</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="product in sortedProducts">
            <td v-if="showColumns.id" class="table-cell" align="right">{{ product.id_ }}</td>
            <td v-if="showColumns.is_new" class="table-cell" align="right">{{ product.is_new }}</td>
            <td v-if="showColumns.availability" class="table-cell" align="right">{{ product.availability }}</td>
            <td v-if="showColumns.shop" class="table-cell" align="left"><a :href="product.url" target="_blank">Shop</a></td>
            <td v-if="showColumns.article_number" class="table-cell" align="right">{{ product.article_number }}</td>
            <td v-if="showColumns.name" class="table-cell" align="right"><a :href="'product/' + product.id_" target="_blank">{{ product.short_name }}</a></td>
            <td v-if="showColumns.package_size" class="table-cell" align="right">{{ product.package_size }}</td>
            <td v-if="showColumns.price" class="table-cell" align="right">{{ (product.price == null) ? '-' : product.price / 100 }} €</td>
            <td v-if="showColumns.yt_link && product.youtube_handle == null" class="table-cell" align="right"><a :href="'https://youtube.com/results?search_query=' + product.name" target="_blank">Search</a></td>
            <td v-else-if="showColumns.yt_link" class="table-cell" align="right"><a :href="product.youtube_handle" target="_blank">YT</a></td>
            <td v-if="showColumns.shot_count" class="table-cell" align="right">{{ (product.shot_count == null) ? '-' : product.shot_count }}</td>
            <td v-if="showColumns.duration" class="table-cell" align="right">{{ (product.duration == null) ? '-' : product.duration }}</td>
            <td v-if="showColumns.nem" class="table-cell" align="right">{{ (product.nem == null) ? '-' : product.nem / 1000 }} kg</td>
            <td v-if="showColumns.weight" class="table-cell" align="right">{{ (product.weight == null) ? '-' : product.weight / 1000 }} kg</td>
            <td v-if="showColumns.min_caliber" class="table-cell" align="right">{{ (product.min_caliber == null) ? '-' : product.min_caliber }} mm</td>
            <td v-if="showColumns.max_caliber" class="table-cell" align="right">{{ (product.max_caliber == null) ? '-' : product.max_caliber }} mm</td>
            <td v-if="showColumns.min_height" class="table-cell" align="right">{{ (product.min_height == null) ? '-' : product.min_height }} m</td>
            <td v-if="showColumns.max_height" class="table-cell" align="right">{{ (product.max_height == null) ? '-' : product.max_height }} m</td>
            <td v-if="showColumns.nem_per_second" class="table-cell" align="right">{{ (product.nem_per_second == null) ? '-' : product.nem_per_second }} kg/s</td>
            <td v-if="showColumns.nem_per_shot" class="table-cell" align="right">{{ (product.nem_per_shot == null) ? '-' : product.nem_per_shot }} kg</td>
            <td v-if="showColumns.price_per_second" class="table-cell" align="right">{{ (product.price_per_second == null) ? '-' : product.price_per_second }} €/s</td>
            <td v-if="showColumns.price_per_shot" class="table-cell" align="right">{{ (product.price_per_shot == null) ? '-' : product.price_per_shot }} €</td>
            <td v-if="showColumns.price_per_nem" class="table-cell" align="right">{{ (product.price_per_nem == null) ? '-' : product.price_per_nem }} €/kg</td>
            <td v-if="showColumns.shots_per_second" class="table-cell" align="right">{{ (product.shots_per_second == null) ? '-' : product.shots_per_second }} Hz</td>
            <td v-if="showColumns.rating" class="table-cell" align="right">{{ (product.rating == null) ? '-' : product.rating }}</td>
            <td v-if="showColumns.rated" class="table-cell" align="right">{{ product.rated }}</td>
            <td v-if="showColumns.tags" class="table-cell" align="right">{{ tagsString(product) }}</td>
            <td v-if="showColumns.colors" class="table-cell" align="right">{{ colorsString(product) }}</td>
            <td v-if="showColumns.fan" class="table-cell" align="right">{{ product.fan }}</td>

        </tr>
        </tbody>
    </table>
</template>

<script>
import axios from 'axios';
import Filter from '@/components/Filter.vue';

export default {
    name: 'Product',
    components: {
        Filter
    },
    data() {
        return {
            filterData: null,
            products: [],
            currentSortKey: 'name',
            currentSortOrder: 'asc',
            showColumnSelection: false,
            showColumns: {
                id: false,
                shop: true, //url
                name: true, //short_name
                article_number: false,
                price: true,
                yt_link: true, //yt_link
                weight: false,
                min_caliber: false,
                max_caliber: false,
                min_height: false,
                max_height: false,
                shot_count: true,
                duration: true,
                fan: false,
                nem: true,
                availability: false,
                is_new: false,
                rating: false,
                rated: false,
                tags: true,
                colors: true,
                nem_per_second: true,
                nem_per_shot: true,
                shots_per_second: true,
                price_per_shot: true,
                price_per_second: true,
                price_per_nem: true,
                package_size: false
            },
            searchName: "",
            searches: []
        };
    },
    mounted() {
        this.loadAvailableSearches();
        this.new_search();
    },
    methods: {
        new_search() {
            this.filterData.inverted = false;
            this.filterData.filters = [];
            this.filterData.filters.push({
                uuid: crypto.randomUUID(),
                type: "boolean",
                inverted: false,
                columnName: "availability",
                showNull: false,
                operator: "and"
            });
            this.filterData.filters.push({
                uuid: crypto.randomUUID(),
                type: "boolean",
                inverted: false,
                columnName: "rating",
                showNull: false,
                operator: "and"
            });
            this.emitter.emit('newFilterData', this.filterData);
        },
        filterDataChanged(data) {
            this.filterData = data;
            console.log(this.filterData);
        },
        perform_search() {
            const path = "http://localhost:5000/find-products";
            axios.post(
                path,
                this.filterData,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            ).then((res) => {
                this.products = res.data.products;
            })
            .catch((error) => {
                console.error(error);
            });
        },
        sort(key) {
            if (key == this.currentSortKey) {
                this.currentSortOrder = this.currentSortOrder === 'asc' ? 'desc' : 'asc';
            }
            this.currentSortKey = key;
        },
        tagsString(product) {
            return product.tags.join(", ");
        },
        colorsString(product) {
            return product.colors.join(", ");
        },
        toggleColumnSelection() {
            this.showColumnSelection = !this.showColumnSelection;
        },
        saveSearch() {
            if (this.searchName == "") {
                alert("Please enter a name for the search.");
                return;
            }
            const path = "http://localhost:5000/searches";
            axios.post(
                path,
                {
                    search_name: this.searchName,
                    search: this.filterData
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            ).then((res) => {
                if (!this.searches.includes(this.searchName))
                    this.searches.push(this.searchName);
            }).catch((error) => {
                console.error(error);
            });
        },
        loadSearch() {
            const path = "http://localhost:5000/searches/" + this.selectedSearch;
            axios.get(
                path,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            )
                .then((res) => {
                    this.filterData = res.data.search;
                    this.emitter.emit('newFilterData', this.filterData);
                    this.searchName = this.selectedSearch;
                    this.perform_search();
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        deleteSearch() {
            const path = "http://localhost:5000/searches/" + this.selectedSearch;
            axios.delete(
                path,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            )
                .then((res) => {
                    this.searches = this.searches.filter((search) => search != this.selectedSearch);
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        loadAvailableSearches() {
            const path = "http://localhost:5000/searches";
            axios.get(
                path,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            )
                .then((res) => {
                    this.searches = res.data.searches;
                })
                .catch((error) => {
                    console.error(error);
                });
        }
    },
    computed: {
        sortedProducts() {
            return this.products.sort((a,b) => {
                let modifier = 1;
                if(this.currentSortOrder === 'desc') modifier = -1;
                if (this.currentSortKey == "colors" || this.currentSortKey == "tags") {
                    if(a[this.currentSortKey].length < b[this.currentSortKey].length) return -1 * modifier;
                    if(a[this.currentSortKey].length > b[this.currentSortKey].length) return 1 * modifier;
                    return 0;
                }
                if(a[this.currentSortKey] < b[this.currentSortKey]) return -1 * modifier;
                if(a[this.currentSortKey] > b[this.currentSortKey]) return 1 * modifier;
                return 0;
            });
        }
    },
    created() {
        document.title = "Overview";
        this.$nextTick(() => {
            this.perform_search();
        })
    }
};
</script>

