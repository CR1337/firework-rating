<template>
    <a :href="product.url" target="_blank"><h1>{{ product.name }}</h1></a>
    <br>
    <div class="container">
        <div class="row">
            <div class="col-sm-6">
                <a v-if="product.youtube_handle == null" :href="'https://youtube.com/results?search_query=' + product.name" target="_blank">Youtube Search</a>
                <iframe v-else :src="'https://www.youtube.com/embed/' + product.youtube_handle" frameborder="0" allowfullscreen></iframe>
            </div>
            <div class="col-sm-4">
                <label for="liked-radio">Like</label>
                <input type="radio" id="liked-radio" v-model="rating" value="liked" />
                <label for="disliked-radio">Dislike</label>
                <input type="radio" id="unliked-radio" v-model="rating" value="disliked" />
                <label for="unrated-radio">Unrated</label>
                <input type="radio" id="unrated-radio" v-model="rating" value="unrated" />
            </div>
            <div class="col-sm-2">
                <button type="button" @click="save()">Save</button>
                <button type="button" @click="next()">Next unrated</button>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-2">
                <input type="checkbox" id="availability" v-model="product.availability" />
                <label for="availability">Available</label>
            </div>
            <div class="col-sm-2">
                <input type="checkbox" id="fan" v-model="product.fan" />
                <label for="fan">Fan</label>
            </div>
            <div class="col-sm-8">
                <smart-tagz
                    autosuggest
                    :allow-duplicates="false"
                    input-placeholder="Add tag..."
                    :default-tags="product.tags"
                    :sources="allTags"
                    :v-model="product.tags"
                />
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                Price:
                <template v-if="product.price != null">
                    {{ product.price / 100 }} €
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price.svg'" />
                </template>
                <template v-else>
                    - €
                </template>
            </div>
            <div class="col-sm-6">
                NEM/s:
                <template v-if="product.nem_per_second != null">
                    {{ product.nem_per_second }} kg/s
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem_per_second.svg'" />
                </template>
                <template v-else>
                    - kg/s
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                Shots:
                <template v-if="product.shot_count != null">
                    {{ product.shot_count }}
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_shot_count.svg'" />
                </template>
                <template v-else>
                    -
                </template>
            </div>
            <div class="col-sm-6">
                NEM/Shot:
                <template v-if="product.nem_per_shot != null">
                    {{ product.nem_per_shot }} kg
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem_per_shot.svg'" />
                </template>
                <template v-else>
                    - kg
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                Duration:
                <template v-if="product.duration != null">
                    {{ product.duration }} s
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_duration.svg'" />
                </template>
                <template v-else>
                    - s
                </template>
            </div>
            <div class="col-sm-6">
                €/s:
                <template v-if="product.price_per_second != null">
                    {{ product.price_per_second }} €/s
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_second.svg'" />
                </template>
                <template v-else>
                    - €/s
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                NEM:
                <template v-if="product.nem != null">
                    {{ product.nem }} kg
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem.svg'" />
                </template>
                <template v-else>
                    - kg
                </template>
            </div>
            <div class="col-sm-6">
                €/Shot:
                <template v-if="product.price_per_shot != null">
                    {{ product.price_per_shot }} €
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_shot.svg'" />
                </template>
                <template v-else>
                    - €
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                Min. Height:
                <template v-if="product.min_height != null">
                    {{ product.min_height }} m
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_min_height.svg'" />
                </template>
                <template v-else>
                    - m
                </template>
            </div>
            <div class="col-sm-6">
                €/NEM:
                <template v-if="product.price_per_nem != null">
                    {{ product.price_per_nem }} €/kg
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_nem.svg'" />
                </template>
                <template v-else>
                    - €/kg
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6">
                Miax. Height:
                <template v-if="product.max_height != null">
                    {{ product.max_height }} m
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_max_height.svg'" />
                </template>
                <template v-else>
                    - m
                </template>
            </div>
            <div class="col-sm-6">
                Shots/s:
                <template v-if="product.shots_per_second != null">
                    {{ product.shots_per_second }} Hz
                    <img :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_shots_per_second.svg'" />
                </template>
                <template v-else>
                    - Hz
                </template>
            </div>
        </div>
    </div>
    <br>
    <a href="/">Main Page</a><a href="/overview">Overview</a>


</template>

<script>
import axios from 'axios';
import { SmartTagz } from "smart-tagz";
import "smart-tagz/dist/smart-tagz.css";

export default {
    name: 'Product',
    data() {
        return {
            product: null,
            allTags: [],
            rating: 'unrated'
        };
    },
    components: {
        SmartTagz
    },
    methods: {
        initialize() {
            this.getAllTags();
            this.getProduct();
        },
        getAllTags() {
            const path = "http://localhost:5000/tags";
            axios.get(path)
                .then((res) => {
                    this.allTags = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        getProduct() {
            const id = this.$route.params.id;
            const path = "http://localhost:5000/product/" + id;
            axios.get(path)
                .then((res) => {
                    this.product = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        rated() {
            switch (this.rating) {
                case 'liked':
                    this.product.rated = true;
                    this.product.rating = true;
                case 'disliked':
                    this.product.rated = true;
                    this.product.rating = false;
                default:
                    this.product.rated = false;
                    this.product.rating = false;
            }
        },
        save() {
            fetch("http://localhost:5000/product/" + this.product.id_, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    availability: this.product.availability,
                    fan: this.product.fan,
                    tags: this.product.tags,
                    rated: this.product.rated,
                    rating: this.product.rating
                })
            })
                .catch((error) => {
                    console.error(error);
                });
        },
        next() {
            const path = "http://localhost:5000/product/next-unrated?excluded=" + this.product.id_;
            axios.get(path)
                .then((res) => {
                    this.save();
                    let nextProduct = res.data;
                    window.location.replace("/product/" + nextProduct.id_);
                })
                .catch((error) => {
                    console.error(error);
                });
        }
    },
    created() {
        this.initialize();
    }
};
</script>