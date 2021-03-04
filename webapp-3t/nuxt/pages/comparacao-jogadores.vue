<template>
  <div id="estatisticas-time">
    <v-container>
      <div class="d-flex justify-center">
        <h1>Comparação Jogadores</h1>
      </div>
    </v-container>
    {{ playerstats[1] }}
    <v-card cols="12">
      <v-img :src="'players/' + playerstats[1].player_id + '.webp'"></v-img>
      <v-card-title>
        <v-img
          :src="addTeamLogo(parseInt(playerstats[1].player_team))"
          max-width="40"
        ></v-img>
        {{ playerstats[1].player_slug.toUpperCase() }}</v-card-title
      >
      <v-simple-table>
        <thead>
          <th>Estatística</th>
          <th>Valor</th>
        </thead>
        <tbody>
          <tr>
            <td>Preço</td>
            <td>Média</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-card>
    <v-container>
      <v-col cols="12" sm="6" md="6">
        <v-autocomplete
          v-model="searchBoxA"
          :items="playerstats"
          item-text="player_nickname"
          @change="filterPlayerA"
        ></v-autocomplete>
        <div v-if="!!filteredResult">
          <v-card>
            <v-img
              :src="'players/' + filteredResult[0].player_id + '.png'"
            ></v-img>
            <v-card-title>
              <v-img
                :src="addTeamLogo(parseInt(filteredResult[0].player_team))"
                max-width="40"
              ></v-img>
              {{ filteredResult[0].player_slug.toUpperCase() }}</v-card-title
            >
          </v-card>
        </div>
      </v-col>
    </v-container>
  </div>
</template>

<script>
import * as ss from 'simple-statistics'
import playerstats from '../static/statistics/player_data.json'

export default {
  data() {
    return {
      playerstats,
      searchBoxA: '',
      searchBoxB: '',
      filteredResult: null,
      listOfValues: [1, 2, 3, 4, 5],
    }
  },
  methods: {
    computeMean(myArray) {
      return ss.mean(myArray)
    },
    filterPlayerA() {
      const query = this.playerstats.filter(
        (name) => name.player_nickname === this.searchBoxA
      )
      this.filteredResult = query
    },
    addTeamLogo(id) {
      switch (id) {
        case 282:
          return 'https://s.glbimg.com/es/sde/f/equipes/2017/11/23/Atletico-Mineiro-escudo45px.png'
        case 262:
          return 'https://s.glbimg.com/es/sde/f/equipes/2018/04/09/Flamengo-45.png'
        case 293:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2018/12/13/escudo45.png'
        case 314:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2018/09/04/escudo-avai-45x45.png'
        case 265:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/bahia_45x45.png'
        case 263:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png'
        case 354:
          return 'https://s.glbimg.com/es/sde/f/equipes/2018/05/11/ceara-45x45.png'
        case 341:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/09/18/CSA_45.png'
        case 315:
          return 'https://s.glbimg.com/es/sde/f/equipes/2015/08/03/Escudo-Chape-145.png'
        case 264:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/corinthians_45x45.png'
        case 283:
          return 'https://s.glbimg.com/es/sde/f/equipes/2015/04/29/cruzeiro_45.png'
        case 266:
          return 'https://s.glbimg.com/es/sde/f/equipes/2015/07/21/fluminense_45x45.png'
        case 284:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/gremio_45x45.png'
        case 285:
          return 'https://s.glbimg.com/es/sde/f/equipes/2016/05/03/inter45.png'
        case 275:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/palmeiras_45x45.png'
        case 277:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/santos_45x45.png'
        case 276:
          return 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/sao_paulo_45x45.png'
        case 267:
          return 'https://s.glbimg.com/es/sde/f/equipes/2016/07/29/Vasco-45.png'
        case 356:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2018/06/10/fortaleza-ec-45px.png'
        case 290:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2019/05/01/Goias_45px.png'
        case 280:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2020/01/01/45.png'
        case 292:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2015/07/21/sport45.png'
        case 294:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2017/03/29/coritiba45.png'
        case 373:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2020/07/02/atletico-go-2020-45.png'
        default:
          return 'https://s.glbimg.com/es/sde/f/organizacoes/2020/01/01/45.png'
      }
    },
  },
}
</script>
