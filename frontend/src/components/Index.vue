<template>
    <button @click="rating()">Rating</button>
    <button @click="overview()">Overview</button>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Index',
  data() { return {} },
  methods: {
      rating() {
        const path = "http://localhost:5000/product/next-unrated";
            axios.get(path)
                .then((res) => {
                    let nextProduct = res.data;
                    window.location.replace("/product/" + nextProduct.id_);
                })
                .catch((error) => {
                    console.error(error);
                });
      },
      overview() {
        window.location.replace("/overview");
      }
  }
}
</script>