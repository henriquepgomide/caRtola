[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/caRtola-R/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link) | README in [English](https://github.com/henriquepgomide/caRtola/blob/master/README.en.md)

*Novidade #1* - Modelo preditivo em python agora disponível
*Novidade #2* - Acesse o protótipo da dashboard (caRtola - STATS)[https://henriquepgomide.shinyapps.io/cartola-stats/]. 

# Introdução

Este repositório tem como objetivo disponibilizar os dados e modelos preditivos do Cartola FC. Os scripts estão escritos em R e Python.

* Para acessar os dados, use qualquer programa. Está tudo disponível em arquivos separados por vírgulas. Até o Excel abre :)
* Para executar os scripts contidos:
  * R -  você precisará instalar o [R](https://www.r-project.org/) e eu fortemente recomendo a instalação da [IDE RStudio](https://www.rstudio.com/products/rstudio/download/)
  * Python - siga as instruções no diretório lib/python. 


## Estrutura do repositório

<!-- language: lang-none -->
```
├── dashboard
│   └── cartola-stats
├── db
│   ├── 2014
│   ├── 2015
│   ├── 2016
│   ├── 2017
│   └── worldTeamData
├── lib
│   ├── python
│   └── R
└── tutorials
    └── R
``` 


**Dashboard**

* Aplicativo Shiny para escolher seu jogador. Disponível no link (caRtola - STATS)[https://henriquepgomide.shinyapps.io/cartola-stats/]. Você pode executá-lo pelo computador. 


**db**

* Os dados das estatísticas dos jogadores do Cartola estão separados por ano.
  * Crédito das edições 2014 e 2015: (https://github.com/thevtm/CartolaFCDados)
  * Crédito da edição de 2016: Arnaldo Gualberto

* Os dados dos times são extraídos do site da CBF.


**lib**

Você encontra scripts em R e python para coletar e analisar os dados do cartola

Na pasta R:

  * caRtola_fetch.R - coleta os dados da API do Cartola
  * team_data_scraper.R* - coleta dados do site da CBF 
  * data_wrangling - agrega os dados dos scouts do cartola, cria variáveis para uso em modelos preditivos agregando outras fontes.
  * rdata_2_sql.R - transforma os dados do objeto cartola em arquivo sql.

**tutorials**

Você encontra tutoriais para iniciantes sobre o cartola.

  *  Vale a pena usar a média para escolher jogadores?
  *  Modelos preditivos são melhores que a média?



# Autores

Henrique Gomide
 * henriquepgomide@gmail.com
 * [@hpgomide](https://twitter.com/hpgomide)
 * [Linkedin](https://www.linkedin.com/in/hpgomide/)
 * [Lattes](http://lattes.cnpq.br/6230665865154742)

Arnaldo Gualberto
 * [Site](http://arnaldogualberto.com) 
 * [Linkedin](https://www.linkedin.com/in/arnaldo-gualberto-95717939/?ppe=1)
