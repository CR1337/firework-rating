<style>
    .boxplot {
        width: 100%;
    }
    .first-row {
        margin-bottom: 8px;
        margin-top: 8px;
    }
    .second-row {
        margin-bottom: 8px;
        margin-top: 8px;
    }
    .yt-player {
        width: 500px;
        height: 280px;
    }
    .rate-button {
        margin-left: 4px;
        margin-right: 4px;
        height: 280px;
        width: 20%;
    }
    .save-button {
        width: 75%;
        height: 150px;
    }
    .like-button{
        accent-color: lightgreen;
    }
    .dislike-button{
        accent-color: red;
    }
    .unrated-button{
        accent-color: black;
    }
    input[type=checkbox]{
        width: 64px;
        height: 64px;
    }
    label{
        font-size:12pt;
    }
    .stat-cell {
        height: 98px;
        border-color: gray;
        border-style: solid;
    }
    h3 {
        text-align: center;
    }
    .new-tag {
        color: red;
    }

    .loading-screen {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        width: 100vw;
        background-color: #f4f4f4;
    }
</style>

<template>
    <div class="container" v-if="product">
        <h3>
            <template id="new-tag" v-if="product.is_new">[NEW]</template>
            <a :href="product.url" target="_blank">{{ product.name }}</a>
            <b>[{{ product.package_size }}]<template v-if="!saved">*</template></b>
        </h3>
        <div class="row first-row">
            <div class="col-sm-6">
                <a v-if="product.youtube_handle == null" :href="'https://youtube.com/results?search_query=' + product.name" target="_blank">Youtube Search</a>
                <!-- <iframe class="yt-player" :width="videoWidth" :height="videoHeight" v-else :src="'https://www.youtube.com/embed/' + product.youtube_handle" frameborder="0" allowfullscreen></iframe> -->
                <a v-else :href="'https://youtube.com/watch?v=' + product.youtube_handle + '&vq=hd2160'" target="_blank">Youtube Video</a>
            </div>
            <div class="col-sm-4">
                <label for="disliked-radio">Dislike</label>
                <input class="rate-button dislike-button"  type="radio" id="unliked-radio" v-model="rating" value="disliked" v-on:change="rated()" />
                <label for="unrated-radio">Unrated</label>
                <input class="rate-button unrated-button" type="radio" id="unrated-radio" v-model="rating" value="unrated" v-on:change="rated()" />
                <label for="liked-radio">Like</label>
                <input class="rate-button like-button" type="radio" id="liked-radio" v-model="rating" value="liked" v-on:change="rated()" />
            </div>
            <div class="col-sm-2">
                <button class="save-button" type="button" @click="save_button()">Save</button>
                <br>
                <button class="save-button" type="button" @click="next()">Save &<br>Next unrated</button>
            </div>
        </div>
        <div class="row second-row">
            <div class="col-sm-2">
                <input type="checkbox" id="availability" v-model="product.availability" @click="saved=false" />
                <label for="availability">Available</label>
            </div>
            <div class="col-sm-2">
                <input type="checkbox" id="fan" v-model="product.fan" @click="saved=false" />
                <label for="fan">Fan</label>
            </div>
            <div class="col-sm-8">
                <smart-tagz
                    autosuggest
                    :allow-duplicates="false"
                    input-placeholder="Add tag..."
                    :default-tags="product.tags"
                    :sources="allTags"
                    ref="tagz"
                    :on-changed="updateTags"
                />
            </div>
        </div>
        <div class="row third-row">
            <div class="col-sm-6 stat-cell">
                Price:
                <template v-if="product.price != null">
                    <b>{{ product.price / 100 }} €</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price.svg'" />
                </template>
                <template v-else>
                    - €
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                NEM/s:
                <template v-if="product.nem_per_second != null">
                    <b>{{ product.nem_per_second }} kg/s</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem_per_second.svg'" />
                </template>
                <template v-else>
                    - kg/s
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 stat-cell">
                Shots:
                <template v-if="product.shot_count != null">
                    <b>{{ product.shot_count }}</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_shot_count.svg'" />
                </template>
                <template v-else>
                    -
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                NEM/Shot:
                <template v-if="product.nem_per_shot != null">
                    <b>{{ product.nem_per_shot }} kg</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem_per_shot.svg'" />
                </template>
                <template v-else>
                    - kg
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 stat-cell">
                Duration:
                <template v-if="product.duration != null">
                    <b>{{ product.duration }} s</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_duration.svg'" />
                </template>
                <template v-else>
                    - s
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                €/s:
                <template v-if="product.price_per_second != null">
                    <b>{{ product.price_per_second }} €/s</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_second.svg'" />
                </template>
                <template v-else>
                    - €/s
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 stat-cell">
                NEM:
                <template v-if="product.nem != null">
                    <b>{{ product.nem / 1000 }} kg</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_nem.svg'" />
                </template>
                <template v-else>
                    - kg
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                €/Shot:
                <template v-if="product.price_per_shot != null">
                    <b>{{ product.price_per_shot }} €</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_shot.svg'" />
                </template>
                <template v-else>
                    - €
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 stat-cell">
                Min. Height:
                <template v-if="product.min_height != null">
                    <b>{{ product.min_height }} m</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_min_height.svg'" />
                </template>
                <template v-else>
                    - m
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                €/NEM:
                <template v-if="product.price_per_nem != null">
                    <b>{{ product.price_per_nem }} €/kg</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_price_per_nem.svg'" />
                </template>
                <template v-else>
                    - €/kg
                </template>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 stat-cell">
                Miax. Height:
                <template v-if="product.max_height != null">
                    <b>{{ product.max_height }} m</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_max_height.svg'" />
                </template>
                <template v-else>
                    - m
                </template>
            </div>
            <div class="col-sm-6 stat-cell">
                Shots/s:
                <template v-if="product.shots_per_second != null">
                    <b>{{ product.shots_per_second }} Hz</b>
                    <br><img class="boxplot" :src="'http://localhost:5000/static/product_plots/' + product.id_ + '_shots_per_second.svg'" />
                </template>
                <template v-else>
                    - Hz
                </template>
            </div>
        </div>
    </div>
    <div v-else>
        <div class="loading-screen">
            <h2 style="color: #333;">Loading Product...</h2>
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="width: 100px; height: 100px; background: #f4f4f4; display: block; shape-rendering: auto;" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                <path d="M10 50A40 40 0 0 0 90 50A40 42 0 0 1 10 50" fill="#0d6efd" stroke="none">
                    <animateTransform attributeName="transform" type="rotate" dur="1.5384615384615383s" repeatCount="indefinite" keyTimes="0;1" values="0 50 51;360 50 51"></animateTransform>
                </path>
            </svg>
        </div>
    </div>
    <br>
    <button @click="showAllTags()">Tags</button>&nbsp;&nbsp;&nbsp;
    <a href="/">Main Page</a>&nbsp;&nbsp;&nbsp;<a href="/overview">Overview</a>


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
            rating: 'unrated',
            saved: true
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
                    document.title = this.product.short_name;
                    if (this.product.youtube_handle == null) {
                        this.youtube_search_handle = this.get_youtube_search_handle();
                    }
                    if (this.product.rated) {
                        if (this.product.rating) {
                            this.rating = 'liked';
                        } else {
                            this.rating = 'disliked';
                        }
                    }
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
                    break;
                case 'disliked':
                    this.product.rated = true;
                    this.product.rating = false;
                    break;
                default:
                    this.product.rated = false;
                    this.product.rating = false;
                    break;
            }
            this.saved = false;
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
            }).then((res) => {
                console.log(res);
            })
            .catch((error) => {
                console.error(error);
            });
            this.saved = true;
        },
        save_button() {
            this.save();
            alert("Saved!");
        },
        next() {
            this.save();
            const path = "http://localhost:5000/product/next-unrated?excluded=" + this.product.id_;
            axios.get(path)
                .then((res) => {
                    let nextProduct = res.data;
                    window.location.replace("/product/" + nextProduct.id_);
                })
                .catch((error) => {
                    console.error(error);
                });
        },
        updateTags() {
            let tagsObject = this.$refs.tagz.tagsData;
            this.product.tags = [];
            for (const i of tagsObject) {
                this.product.tags.push(i.value);
            }
            this.saved = false;
        },
        showAllTags() {
            alert(this.allTags.join("\n"))
        }
    },
    created() {
        this.initialize();
    }
};
</script>
