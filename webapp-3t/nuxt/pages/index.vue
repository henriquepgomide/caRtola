<template>
  <div>
    <v-container class="pr-16 pl-16">
      <v-row class="justify-center">
        <card-index
          title="Estatísticas Jogadores"
          subtitle="Use os dados a seu favor"
          link-to-image="cards/estatisticas-cartola.webp"
          url="estatisticas-jogadores"
        />
        <card-index
          title="Previsão de SG"
          subtitle="Veja as chances de saldo de gols"
          link-to-image="cards/estatisticas-cartola.webp"
          url="estatisticas-times"
        />
        <card-index
          title="Comparação de Jogadores 3T"
          subtitle="Use nosso sistema único de estatísticas"
          link-to-image="cards/estatisticas-cartola.webp"
          :disabled="true"
        />
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { butter } from '~/plugins/buttercms'
import CardIndex from '~/components/CardIndex.vue'

export default {
  components: {
    CardIndex,
  },
  data() {
    return {
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
          page: 1,
          page_size: 5,
        })
        .then((res) => {
          this.posts = res.data.data
        })
    },
  },
  head() {
    return {
      title: 'Home',
      meta: [
        {
          hid: 'title',
          name: 'title',
          content: 'Home',
        },
        {
          hid: 'description',
          name: 'description',
          content: process.env.npm_package_description,
        },
        { hid: 'twitter:card', name: 'twitter:card', content: 'Cartola PFC' },
        { hid: 'twitter:site', name: 'twitter:site', content: '@pfc_cartola' },
        {
          hid: 'twitter:creator',
          name: 'twitter:creator',
          content: '@pfc_cartola',
        },
        {
          hid: 'twitter:title',
          name: 'twitter:title',
          content: this.title,
        },
        {
          hid: 'twitter:description',
          name: 'twitter:description',
          content:
            'Comunidade de Cartola FC, o fantasy mais querido do Brasil. Ranking dos Youtubers e estatísticas para você mitar no Cartola FC',
        },
        {
          hid: 'og:image',
          property: 'og:image',
          content: 'cartola-pfc-logotipo-2020.png',
        },
        { hid: 'og:site_name', name: 'og:site_name', content: 'Cartola PFC' },
        { hid: 'og:type', name: 'og:type', content: 'website' },
        {
          hid: 'og:url',
          name: 'og:url',
          content: 'https://www.cartolapfc.com.br',
        },
        { hid: 'og:title', name: 'og:title', content: 'Cartola PFC' },
        {
          hid: 'og:description',
          name: 'og:description',
          content:
            'Comunidade de Cartola FC, o fantasy mais querido do Brasil. Ranking dos Youtubers e estatísticas para você mitar no Cartola FC',
        },
      ],
    }
  },
}
</script>
