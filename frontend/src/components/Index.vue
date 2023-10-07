<template>
    <button @click="rating()">Rating</button>
    <button @click="search()">Search</button>
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
                .then(res => {
                    let nextProduct = res.data;
                    window.location.replace("/product/" + nextProduct.id_);
                })
                .catch(error => {
                    if (error.response.status == 404) {
                      alert("No more products to rate!");
                    } else {
                      console.error(error);
                    }
                });
      },
      search() {
        window.location.replace("/search");
      }
  },
  created() {
    document.title = "Fireworks Rating";
  }
}
</script>