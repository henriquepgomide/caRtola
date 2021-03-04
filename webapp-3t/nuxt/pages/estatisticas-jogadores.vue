<template>
  <div id="estatisticas-time">
    <v-container>
      <div class="d-flex justify-center">
        <h1>Estatísticas dos Jogadores</h1>
      </div>
    </v-container>
    <v-card>
      <v-card-title>
        Jogadores
        <v-spacer></v-spacer>
        <v-text-field
          v-model="ngames"
          label="Mínimo de Partidas"
          type="number"
          class="mx-10"
        ></v-text-field>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Pesquisa"
        ></v-text-field>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="playerstats"
        :search="search"
        sort-by="score_mean"
        sort-desc="true"
      >
        <template v-slot:item.player_team="{ item }">
          <img :src="addTeamLogo(parseInt(item.player_team))" width="30" />
        </template>
        <template v-slot:item.player_position="{ item }">
          {{ item.player_position.toUpperCase() }}
        </template>
        <template v-slot:item.score_mean="{ item }">
          {{ Math.round(item.score_mean * 10) / 10 }}
        </template>
        <template v-slot:item.score_no_cleansheets_mean="{ item }">
          {{ Math.round(item.score_no_cleansheets_mean * 10) / 10 }}
        </template>
        <template v-slot:item.score_mean_away="{ item }">
          {{ Math.round(item.score_mean_away * 10) / 10 }}
        </template>
        <template v-slot:item.score_mean_home="{ item }">
          {{ Math.round(item.score_mean_home * 10) / 10 }}
        </template>
        <template v-slot:item.diff_home_away_s="{ item }">
          {{ Math.round(item.diff_home_away_s * 10) / 10 }}
        </template>
        <template v-slot:item.shots_x_mean="{ item }">
          {{ Math.round(item.shots_x_mean * 10) / 10 }}
        </template>
        <template v-slot:item.G_mean="{ item }">
          {{ Math.round(item.G_mean * 10) / 10 }}
        </template>
        <template v-slot:item.A_mean="{ item }">
          {{ Math.round(item.A_mean * 10) / 10 }}
        </template>
        <template v-slot:item.DS_mean="{ item }">
          {{ Math.round(item.DS_mean * 10) / 10 }}
        </template>
        <template v-slot:item.fouls_mean="{ item }">
          {{ Math.round(item.fouls_mean * 10) / 10 }}
        </template>
      </v-data-table>
    </v-card>
    <v-container>
      <h4 id="legenda" class="header">Legenda</h4>
      <p>
        Como funcionam nossas estatísticas. Os valores da média em casa, fora e
        geral você já está familiarizado. Média sem saldo de Gols pode te ajudar
        a escolher os melhores defensores. Verifique também nossa página de
        <a :href="estatisticas - times">previsão de SG dos confrontos</a>. Temos
        também a coluna 'Diff Casa Fora', onde você pode identificar jogadores
        que têm desempenho melhor em casa do que jogando fora. Se o desempenho
        for significativamente maior em casa, o valor será maior que +1; se for
        significativamente maior jogando fora de casa, o valor será menor que
        -1. Por fim, a outra métrica que desenvolvemos foi xChutes. xChutes
        combina todos os chutes que vão em direção ao gol e nos dão uma ideia do
        potencial de gols de um determinado atleta.
      </p>
    </v-container>
  </div>
</template>

<script>
import playerstats from '../static/statistics/player_data.json'

export default {
  data() {
    return {
      playerstats,
      search: '',
      ngames: 5,
      headers: [
        { text: 'Time', value: 'player_team' },
        { text: 'Nome', value: 'player_nickname' },
        { text: 'Pos', value: 'player_position' },
        {
          text: 'Jogos',
          value: 'n_games',
          filter: (value) => {
            if (!this.ngames) return true

            return value >= parseInt(this.ngames)
          },
        },
        { text: 'Preço', value: 'price_cartoletas' },
        { text: 'Média', value: 'score_mean' },
        { text: 'Média Casa', value: 'score_mean_home' },
        { text: 'Média Fora', value: 'score_mean_away' },
        { text: 'Média sem SG', value: 'score_no_cleansheets_mean' },
        { text: 'Diff Casa/Fora', value: 'diff_home_away_s' },
        { text: 'xChutes', value: 'shots_x_mean' },
        { text: 'Gols', value: 'G_mean' },
        { text: 'Assistências', value: 'A_mean' },
        { text: 'Desarmes', value: 'DS_mean' },
        { text: 'Faltas Cometidas', value: 'fouls_mean' },
      ],
    }
  },
  methods: {
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
