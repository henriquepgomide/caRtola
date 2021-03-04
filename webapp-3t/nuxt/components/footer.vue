<template>
  <v-footer color="primary" padless>
    <v-row justify="center" no-gutters>
      <v-btn
        v-for="link in links"
        :key="link"
        color="white"
        text
        rounded
        class="my-2"
      >
        {{ link }}
      </v-btn>
      <v-col class="primary-darken2 py-4 text-center white--text" cols="12">
        <strong>&copy; Gato Mestre</strong> - Este é um produto da Globo.
        {{ new Date().getFullYear() }}
      </v-col>
    </v-row>
  </v-footer>
</template>

<script>
export default {
  data: () => ({
    links: null,
    // links: ['Home', 'Blog', 'Política do Site', 'Termos de uso', 'Sobre'],
  }),
}
</script>
