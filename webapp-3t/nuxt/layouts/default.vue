<template>
  <v-app dark>
    <v-navigation-drawer v-model="drawer" app>
      <v-list-item>
        <v-img
          src="gato-mestre-logotipo.svg"
          max-width="220"
          max-height="220"
          aspect-ration="1"
          alt="Gato Mestre 2021"
          class="hidden-sm-and-down"
        />
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">
            Gato Mestre
          </v-list-item-title>
          <v-list-item-subtitle>
            O Lugar do Cartoleiro Pro
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
      <v-list>
        <v-list-item
          v-for="(item, i) in items"
          :key="i"
          :to="item.to"
          router
          exact
        >
          <v-list-item-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title v-text="item.title" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Gato Mestre</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container class="full-height" fluid>
        <nuxt />
      </v-container>
    </v-main>
    <Footer />
  </v-app>
</template>

<script>
import Footer from '~/components/footer'

export default {
  components: {
    Footer,
  },
  data() {
    return {
      drawer: null,
      items: [
        {
          icon: 'mdi-apps',
          title: 'Principal',
          to: '/',
        },
        {
          icon: 'mdi-table-of-contents',
          title: 'Estatísticas Jogadores',
          to: '/estatisticas-jogadores',
        },
        {
          icon: 'mdi-chart-donut',
          title: 'Previsão de SG',
          to: '/estatisticas-times',
        },
        {
          icon: 'mdi-chart-donut',
          title: 'Comparação Jogadores - 3T',
          to: '/comparacao-jogadores',
        },
        {
          icon: 'mdi-code-tags',
          title: 'Dados',
          to: '/dados',
        },
      ],
      title: 'Time Gato Mestre',
    }
  },
}
</script>
