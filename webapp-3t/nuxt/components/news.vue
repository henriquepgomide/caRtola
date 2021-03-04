<template>
  <div>
    <v-card class="d-flex justify-space-between">
      <v-card class="pa-3" flat tile>
        <!--<a class="font-weight-black" :href="url">{{ title }}</a> |-->
        {{ description }}
      </v-card>
      <v-card class="pa-2" flat tile>
        {{ formatDate(datePosted) }}
        <v-chip v-if="newPost" label dark>Novo</v-chip>
      </v-card>
    </v-card>
  </div>
</template>
<script>
export default {
  props: {
    title: String,
    description: String,
    url: String,
    datePosted: String,
  },
  data() {
    return {
      newPost: false,
    }
  },
  methods: {
    formatDate() {
      return `${this.datePosted.split('-')[2].substring(0, 2)}/${
        this.datePosted.split('-')[1]
      }/${this.datePosted.split('-')[0]}`
    },
    returnChip() {
      const diffTime = Math.abs(new Date() - new Date(this.datePosted))
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      this.newPost = diffDays < 4
    },
  },
}
</script>
