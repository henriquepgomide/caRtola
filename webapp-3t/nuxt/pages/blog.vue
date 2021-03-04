<template>
  <div id="blog-home">
    <v-container>
      <v-row class="justify-center">
        <h1>Notícias</h1>
      </v-row>
    </v-container>

    <v-container class="pr-10 pl-10">
      <div v-for="(post, index) in posts" :key="post.slug + '_' + index">
        <news
          :title="post.title"
          :description="post.meta_description"
          :date-posted="post.published"
          :url="'/blog/' + post.slug"
        />
      </div>
    </v-container>

    <v-container>
      <div class="text-xs-center">
        <v-pagination v-model="page_number" :length="6"></v-pagination>
      </div>
    </v-container>
  </div>
</template>
<script>
import { butter } from '~/plugins/buttercms'
import News from '~/components/news.vue'

export default {
  name: 'BlogHome',
  components: {
    News,
  },
  data() {
    return {
      page_number: 1,
      posts: [],
    }
  },
  created() {
    this.getPosts()
  },
  methods: {
    getPosts() {
      butter.post
        .list({
          page: this.page_number,
          page_size: 10,
        })
        .then((res) => {
          this.posts = res.data.data
        })
    },
    goPage(num) {
      if (this.page_number > 0) {
        this.page_number += num
        this.getPosts()
      } else {
        this.page_number = 1
        this.getPosts()
      }
    },
  },
}
</script>
