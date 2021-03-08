<template>
  <div id="estatisticas-time">
    <div class="d-flex justify-center">
      <h1>Comparação Jogadores</h1>
      {{ computeMean(playerScouts.points) }}
      {{ computeQuantile(playerScouts.points, playerOne.score_mean) }}
    </div>
    <v-container>
      <v-containter>
        <v-row>
          <v-col cols="12" sm="6" md="6">
            <v-autocomplete
              v-model="playerOne"
              :items="items"
              item-text="PlayerName"
              label="Procure um jogador"
              return-object
              @change="findPlayer"
            ></v-autocomplete>
            <v-card class="mx-auto my-12" max-width="400">
              <v-img
                class="align-end"
                :src="'players/' + playerOne.player_id + '.webp'"
              >
                <v-rating
                  :value="4.0"
                  color="orange"
                  medium
                  half-increments
                  readonly
                ></v-rating>
              </v-img>
              <v-card-title>
                {{ fixPlayerName(playerOne.player_slug) }}
              </v-card-title>
              <v-card-subtitle>
                {{ playerOne.player_position.toUpperCase() }}
              </v-card-subtitle>
              <v-simple-table>
                <tbody>
                  <tr>
                    <td>Preço</td>
                    <td>{{ roundStats(playerOne.price_cartoletas) }}</td>
                  </tr>
                  <tr>
                    <td>Média</td>
                    <td>{{ roundStats(playerOne.score_mean) }}</td>
                  </tr>
                  <tr>
                    <td>Jogos na temporada</td>
                    <td>{{ roundStats(playerOne.n_games) }}</td>
                  </tr>
                  <tr>
                    <td>Última pontuação</td>
                    <td>{{ roundStats(playerOne.last_points) }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="6">
            <v-autocomplete
              v-model="playerTwo"
              :items="items"
              item-text="PlayerName"
              label="Procure um jogador"
              return-object
              @change="findPlayer"
            ></v-autocomplete>
            <v-card class="mx-auto my-12" max-width="400">
              <v-img
                class="align-end"
                :src="'players/' + playerTwo.player_id + '.webp'"
              >
                <v-rating
                  :value="4.0"
                  color="orange"
                  medium
                  half-increments
                  readonly
                ></v-rating>
              </v-img>
              <v-card-title>
                {{ fixPlayerName(playerTwo.player_slug) }}
              </v-card-title>
              <v-card-subtitle>
                {{ playerTwo.player_position.toUpperCase() }}
              </v-card-subtitle>
              <v-simple-table>
                <thead>
                  <th></th>
                  <th></th>
                </thead>
                <tbody>
                  <tr>
                    <td>Preço</td>
                    <td>
                      {{ roundStats(playerTwo.price_cartoletas) }}
                    </td>
                  </tr>
                  <tr>
                    <td>Média</td>
                    <td>{{ roundStats(playerTwo.score_mean) }}</td>
                  </tr>
                  <tr>
                    <td>Jogos na temporada</td>
                    <td>{{ roundStats(playerTwo.n_games) }}</td>
                  </tr>
                  <tr>
                    <td>Última pontuação</td>
                    <td>{{ roundStats(playerTwo.last_points) }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-col>
        </v-row>
      </v-containter>
    </v-container>
    <v-container>
      <radar-chart :chart-data="data" :options="options" />
    </v-container>
    <v-container>
      <v-col cols="12" sm="6" md="6">
        <v-autocomplete
          v-model="playerOne"
          :items="items"
          item-text="PlayerName"
          label="Procure um jogador"
          return-object
          @change="findPlayer"
        ></v-autocomplete>
        {{ searchBarA }}
      </v-col>
    </v-container>
  </div>
</template>

<script>
import * as ss from 'simple-statistics'
import playerstats from '../static/statistics/player_data.json'
import RadarChart from '../components/RadarChart.vue'

export default {
  components: {
    'radar-chart': RadarChart,
  },
  data() {
    return {
      playerstats,
      playerOne: playerstats[0],
      playerTwo: playerstats[10],
      searchBarA: '',
      playerScouts: null,
      playerSlug: null,
      filteredResult: null,
      data: {
        labels: [
          'Pontos Cartola',
          'Pontos Cartola sem SG',
          'Gols',
          'Assistências',
          'Chutes a Gol',
          'Roubadas',
          'Faltas',
          'Impedimento',
          'Passes incompletos',
        ],
        datasets: [
          {
            backgroundColor: 'rgba(255,109,0,.3)',
            borderColor: 'rgba(255,109,0,.7)',
            pointRadius: 3,
            data: [10, 80, 90, 75, 90, 10, 40, 90, 10],
            label: 'Rafael',
          },
          {
            backgroundColor: 'rgba(0,77,64,.3)',
            borderColor: 'rgba(0,77,64,.7)',
            pointRadius: 3,
            data: [90, 80, 90, 75, 90, 10, 40, 90, 10],
            label: 'Freddy',
          },
        ],
      },
      options: {
        legend: {
          position: 'top',
          labels: {
            fontSize: 20,
            padding: 20,
          },
        },
        scale: {
          ticks: {
            stepSize: 20,
          },
          pointLabels: {
            fontSize: 20,
          },
        },
      },
    }
  },
  computed: {
    items() {
      return this.playerstats.map((entry) => {
        const PlayerName =
          entry.player_nickname +
          ' (' +
          this.fixTeamName(entry.player_team) +
          ')'
        return Object.assign({}, entry, { PlayerName })
      })
    },
  },
  created() {
    this.playerScouts = {
      points: this.playerstats.map((item) => item.score_mean),
      pointsCleanSheet: this.playerstats.map(
        (item) => item.score_no_cleansheets_mean
      ),
      pointsHome: this.playerstats.map((item) => item.score_mean_home),
      pointsAway: this.playerstats.map((item) => item.score_mean_away),
      goals: this.playerstats.map((item) => item.G_mean),
      assists: this.playerstats.map((item) => item.A_mean),
      shots: this.playerstats.map((item) => item.shots_x_mean),
      offsides: this.playerstats.map((item) => item.I_mean),
      fouls: this.playerstats.map((item) => item.fouls_mean),
      incPasses: this.playerstats.map((item) => item.PI_mean),
      greatSaves: this.playerstats.map((item) => item.DD_mean),
    }
  },
  methods: {
    fixPlayerName(name) {
      const string = name.replace('-', ' ')
      return string.replace(/\b\w/g, (l) => l.toUpperCase())
    },
    findPlayer() {
      const query = this.playerstats.filter(
        (name) => name.player_nickname === this.searchBarA
      )
      console.log(query)
      this.filteredResult = query
    },
    computeMean(myArray) {
      return ss.mean(myArray)
    },
    computeQuantile(playersStats, playerStat) {
      return ss.quantileRank(playersStats, playerStat)
    },
    roundStats(stat) {
      return Math.round(stat * 100) / 100
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
    fixTeamName(id) {
      switch (id) {
        case '327':
          return 'América-MG'
        case '200':
          return 'Atlético-RN'
        case '373':
          return 'Atlético-GO'
        case '282':
          return 'Atlético-MG'
        case '293':
          return 'Atlético-PR'
        case '314':
          return 'Avaí'
        case '265':
          return 'Bahia'
        case '263':
          return 'Botafogo'
        case '280':
          return 'Bragantino Red Bull'
        case '204':
          return 'Ceará-SC'
        case '354':
          return 'Ceará-SC'
        case '315':
          return 'Chapecoense'
        case '205':
          return 'Náutico'
        case '264':
          return 'Corinthians'
        case '294':
          return 'Coritiba'
        case '206':
          return 'Criciuma'
        case '283':
          return 'Cruzeiro'
        case '316':
          return 'Figueirense'
        case '262':
          return 'Flamengo'
        case '266':
          return 'Fluminense'
        case '209':
          return 'Fortaleza'
        case '210':
          return 'Goiás'
        case '290':
          return 'Goiás'
        case '284':
          return 'Grêmio'
        case '211':
          return 'Grêmio Barueri'
        case '212':
          return 'Grêmio Prudente'
        case '213':
          return 'Guarani'
        case '285':
          return 'Internacional'
        case '214':
          return 'Ipatinga'
        case '215':
          return 'Joinville'
        case '216':
          return 'Juventude'
        case '218':
          return 'Paysandu'
        case '275':
          return 'Palmeiras'
        case '217':
          return 'Paraná'
        case '303':
          return 'Ponte Preta'
        case '219':
          return 'Portuguesa'
        case '344':
          return 'Santa Cruz'
        case '220':
          return 'Santo André'
        case '277':
          return 'Santos'
        case '221':
          return 'São Caetano'
        case '276':
          return 'São Paulo'
        case '292':
          return 'Sport'
        case '267':
          return 'Vasco'
        case '287':
          return 'Vitória'
        default:
          return 'Sem time'
      }
    },
  },
}
</script>
