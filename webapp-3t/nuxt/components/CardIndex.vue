<template>
  <div id="card-index">
    <v-card class="mx-auto" :disabled="disabled">
      <v-img
        max-width="300"
        lazy-src="cards/placeholder.webp"
        :src="linkToImage"
      ></v-img>
      <v-card-title>
        {{ title }}
      </v-card-title>
      <v-card-subtitle>
        {{ subtitle }}
      </v-card-subtitle>
      <v-card-actions>
        <v-btn color="deep-orange" text :to="url">
          Ver
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
export default {
  props: {
    disabled: Boolean,
    title: String,
    subtitle: String,
    url: String,
    linkToImage: String,
  },
  data: () => ({}),
}
</script>

<style scoped>
#card-index {
  margin-right: 1rem;
  margin-top: 1rem;
}
</style>
