<template>
  <div id="estatisticas-time">
    <v-container>
      <div class="d-flex justify-center">
        <h1>Previsão de Saldo de Gols</h1>
      </div>
    </v-container>
    <v-container>
      <div>
        <p>
          Saiba as chances de sair gol em cada partida do campeonato Brasileiro.
          Mágica? Não, estatística. Nós criamos nossas estatísticas com base na
          história dos confrontos entre os times, tudo feito com base num artigo
          científico publicado na revista <i>Royal Statistical Society</i>. Quer
          ver como fazemos, olhe este post que publicamos
          <a
            href="https://medium.com/@hpgomide/como-montamos-defesas-no-cartolafc-com-estatística-e-modelagem-de-dados-6f5d58ac1034"
            >no Medium</a
          >. Saiba como usar, vendo a <a href="#legenda">legenda.</a>
        </p>
      </div>
    </v-container>
    <v-card>
      <v-card-title>
        <v-spacer></v-spacer>
      </v-card-title>
      <v-data-table :headers="headers" :items="predictions" :search="search">
        <template v-slot:item.away_team_name="{ item }">
          <img :src="addTeamLogo(item.away_team_name)" width="30" />
        </template>
        <template v-slot:item.home_team_name="{ item }">
          <img :src="addTeamLogo(item.home_team_name)" width="30" />
        </template>
      </v-data-table>
    </v-card>
    <v-container>
      <h4 id="legenda" class="header">Legenda</h4>
      <p>
        Como funciona nosso modelo? Vamos lá. Defesa, Ataque e Geral são índices
        criados com base na metodologia de trabalho que bateu casas de apostas
        no Reino Unido. Quanto maior o número, melhor. Chance de gol está ligada
        a probabilidade do time fazer ao menos um gol na partida. Como sabemos
        isso, fazemos 100.000 simulações dos confrontos com base no desempenho
        histórico dos times.
      </p>
    </v-container>
  </div>
</template>

<script>
import predictions from '../static/statistics/team_predictions.json'

export default {
  data() {
    return {
      predictions,
      headers: [
        { text: 'Força Defesa', value: 'home_defense' },
        { text: 'Força Ataque', value: 'home_attack' },
        { text: 'Força Geral', value: 'home_strength' },
        { text: 'Mando', value: 'home_team_name' },
        {
          text: '% Chance de fazer pelo menos 1 gol',
          value: 'home_scoring_odds',
        },
        {
          text: '% Chance de fazer pelo menos 1 gol',
          value: 'away_scoring_odds',
        },
        { text: 'Fora', value: 'away_team_name' },
        { text: 'Força Geral', value: 'away_strength' },
        { text: 'Força Defesa', value: 'away_defense' },
        { text: 'Força Ataque', value: 'away_attack' },
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
          return id
      }
    },
  },
}
</script>
