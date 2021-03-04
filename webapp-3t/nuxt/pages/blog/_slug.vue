<template>
  <div id="blog-post">
    <v-container>
      <h1>{{ post.data.title }}</h1>
    </v-container>
    <v-container>
      <h4>
        {{ post.data.author.first_name }} {{ post.data.author.last_name }}
      </h4>
    </v-container>
    <v-container>
      <div v-html="post.data.body" />
    </v-container>

    <router-link
      v-if="post.meta.previous_post"
      :to="/blog/ + post.meta.previous_post.slug"
      class="button"
    >
      {{ post.meta.previous_post.title }}
    </router-link>
    <router-link
      v-if="post.meta.next_post"
      :to="/blog/ + post.meta.next_post.slug"
      class="button"
    >
      {{ post.meta.next_post.title }}
    </router-link>
  </div>
</template>
<script>
import { butter } from '~/plugins/buttercms'

export default {
  name: 'BlogPost',
  data() {
    return {
      post: {
        data: {
          author: {},
        },
        meta: {},
      },
    }
  },
  watch: {
    $route(to, from) {
      this.getPost()
    },
  },
  created() {
    this.getPost()
  },
  methods: {
    getPost() {
      butter.post
        .retrieve(this.$route.params.slug)
        .then((res) => {
          console.log(res.data)
          this.post = res.data
        })
        .catch((res) => {
          console.log(res)
        })
    },
  },
}
</script>
