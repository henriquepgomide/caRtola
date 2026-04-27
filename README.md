# 🎩 CaRtola FC: Ciência de Dados e Futebol desde 2014 até 2026

> Felizmente, existe um repositório no GitHub chamado caRtola, no qual toda a parte de obtenção e tratamento dos dados do jogo já foi realizada. (Ribeiro, 2019)

## 🔊 Servidor Discord

Entre no nosso [servidor do Discord][discord] para trocar experiências sobre projetos e do uso de estatísticas no Cartola FC.

## 🎲 Dados

Você encontra os dados raw do *Cartola FC* desde 2014 na pasta [data/01_raw][folder_data].

## 🛠 Pipeline (Cartola Aggregation)

Pipeline local que agrega os dados do *Cartola FC* de 2014 a 2026 em um único
CSV harmonizado de 38 colunas (contexto + clube + jogador + estado de jogo +
21 scouts).

> ⚠️ 2021 ainda não está incluso: o raw daquele ano está em formato JSON
> (`Mercado_N.txt`) e exige um leitor dedicado, planejado como follow-up.

### Setup

```bash
uv sync --extra ui --group dev
```

### Rodando

```bash
uv run cartola aggregate                       # todos os anos
uv run cartola aggregate --years 2024,2025,2026
uv run cartola aggregate --track               # envia o run para a Hamilton UI
uv run cartola viz                             # abre a UI em http://localhost:8241
```

Saídas:

- `data/03_primary/cartola_<year>.csv` — um por ano processado
- `data/04_aggregated/cartola_2014_2026.csv` — concat final (apenas em runs completos)

### Testes

```bash
make test-fast    # unit + integração; roda em segundos
make test-slow    # smoke test contra todos os dados reais; ~10s
make test         # ambos
```

Detalhes de design e decisões em
[`docs/superpowers/specs/2026-04-27-cartola-aggregation-pipeline-design.md`](docs/superpowers/specs/2026-04-27-cartola-aggregation-pipeline-design.md).

## 🧑‍🏫 Tutoriais

Estes são alguns tutoriais que escrevemos. Contribuições são sempre bem vindas!

### Python

- [Como ler todos os arquivos das rodadas deste repositório com Python?][tutorial-py-1]
- [Seleção automática de jogadores feita com Markov Chain e programação linear][tutorial-py-2]
- [Média global ou média com mando de campo? O que usar para escalar seus jogadores][tutorial-py-3]
- [Algoritmo de valorização dos Jogadores do Cartola PFC][tutorial-py-4]
- [Estudo sobre algoritmo de valorizaço dos jogadores do Cartola, parte I][tutorial-py-5]
- [Estudo sobre algoritmo de valorizaço dos jogadores do Cartola, parte II][tutorial-py-6]

### R

- [Parte I - Analisando os atacantes do primeiro turno com Affinity Propagation][tutorial-r-1]
- [Parte II - Quais meias escalar: Defensivos ou ofensivos?][tutorial-r-2]
- [Parte III - Analisando jogadores de defesa com Affinity Propagation][tutorial-r-3]
- [Como montar defesas no Cartola usando regressão de Poisson?][tutorial-r-4]

### C++

- [Fórmula do algoritmo de valorização do Cartola FC][tutorial-cpp-1]

## 🃏 Jogo Cartola - Super PFC

Criamos [um jogo de cartas][supertrunfo-site] com base nos dados (em VueJS). Detalhe: também é de [código-aberto][supertrunfo-repo]!

## :octocat: Contribuições

O repositório __caRtola__ é totalmente aberto a novas contribuições. Quer ajudar a gente, mas não sabe como? A gente te dá algumas ideias:

- Você já fez alguma análise estatística do *Cartola FC* que acha legal e gostaria de compartilhar aqui?
- Você também tem um modelo preditivo para tentar prever os melhores jogadores?
- Ou simplesmente você viu um erro nos nossos dados/análises?

Sinta-se à vontade para submeter um Pull Request ou abrir uma issue! Nós vamos adorar ter isso no __caRtola__! ✌️

## 📰 Na Mídia

- Marchesini, L. [Cartola FC - Saiba como a pandemia pode influenciar os times mandantes][metropoles] 2020.

## 🎓 Trabalhos Acadêmicos

- E. Mota, D. Coimbra, and M. Peixoto, “Cartola FC Data Analysis: A simulation, analysis, and visualization tool based on Cartola FC Fantasy Game,” in Proceedings of the XIV Brazilian Symposium on Information Systems, Caxias do Sul, Brazil, Jun. 2018, pp. 1–8, doi: 10.1145/3229345.3229366.

- L. E. da S. Ribeiro, “Predição de escalações para o jogo CartolaFC utilizando aprendizado de máquina e otimização,” Prediction of escalations for CartolaFC fantasy game using machine learning and optimization, Jul. 2019, Accessed: Jul. 23, 2020. [Online]. Available: <https://repositorio.ufu.br/handle/123456789/26681>.

- E. F. Vernier, R. Garcia, I. P. da Silva, J. L. D. Comba, and A. C. Telea, “Quantitative Evaluation of Time-Dependent Multidimensional Projection Techniques,” arXiv:2002.07481 [cs], Feb. 2020, Accessed: Jul. 23, 2020. [Online]. Available: <http://arxiv.org/abs/2002.07481>.

- BARBOSA, D. A. C. Should he stay or should he go? head coaches turnover in brazilian football 2014-2019. Rio de Janeiro: Pontifícia Universidade Católica do Rio de Janeiro, 2020.

Está faltando o seu? Envie para gente e colocamos aqui.

### Como citar?

Por favor, cite-nos.

H. Gomide e A. Gualberto, CaRtola: Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python. <https://github.com/henriquepgomide/caRtola/>. 2022.

```{latex}
@book{
     title={CaRtola: Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python}, 
     url={https://github.com/henriquepgomide/caRtola}, 
     abstractNote={Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python}, 
     author={Gomide, Henrique and Gualberto, Arnaldo}, 
     year={2022}
}
```

## Créditos

- Os dados de 2014 e 2015 foram obtidos do repositório [CartolaFCDados](https://github.com/thevtm/CartolaFCDados)
- Os dados dos times são extraídos do [site da CBF](https://www.cbf.com.br/competicoes/brasileiro-serie-a#.WiqMZbbOpTY).

## 👥 Autores

👤 __Henrique Gomide__:

- [Site Pessoal](http://henriquepgomide.github.io)
- [Twitter](https://twitter.com/hpgomide)
- [Linkedin](https://www.linkedin.com/in/hpgomide/)

👤 __Arnaldo Gualberto__:

- [Site Pessoal](http://arnaldogualberto.com)
- [Github](https://github.com/arnaldog12)
- [Medium](https://medium.com/@arnaldog12)
- [Twitter](https://twitter.com/arnaldog12_)
- [Linkedin](https://www.linkedin.com/in/arnaldo-gualberto/)

> In Memoriam de Mário Guilherme (Von Marius)

[discord]: https://discord.gg/YVAzA2unMB
[folder_data]: data/01_raw/
[metropoles]: https://www.metropoles.com/esportes/cartola-fc-saiba-como-a-pandemia-pode-influenciar-os-times-mandantes
[supertrunfo-site]: https://henriquepgomide.github.io/cartola-supertrunfo/
[supertrunfo-repo]: https://github.com/henriquepgomide/cartola-supertrunfo
[tutorial-py-1]: https://github.com/henriquepgomide/caRtola/tree/master/notebooks/colabs/caRtola_como_ler_repositório_do_github_com_BeautifulSoup_e_Pandas.ipynb
[tutorial-py-2]: https://github.com/henriquepgomide/caRtola/tree/master/notebooks/markov-chain-lpp.ipynb
[tutorial-py-3]: https://github.com/henriquepgomide/caRtola/tree/master/notebooks/colabs/caRtola_media_media_movel_media_casa_ou_fora_o_que_usar.ipynb
[tutorial-py-4]: https://github.com/henriquepgomide/caRtola/tree/master/notebooks/desafio_valorizacao/Desafio%20da%20Valorização.ipynb
[tutorial-py-5]: https://github.com/henriquepgomide/caRtola/blob/master/notebooks/desafio_valorizacao/Descobrindo%20o%20algoritmo%20de%20valoriza%C3%A7%C3%A3o%20do%20Cartola%20FC%20-%20Parte%20I.ipynb
[tutorial-py-6]: https://github.com/henriquepgomide/caRtola/blob/master/notebooks/desafio_valorizacao/Descobrindo%20o%20algoritmo%20de%20valoriza%C3%A7%C3%A3o%20do%20Cartola%20FC%20-%20Parte%20I.ipynb
[tutorial-r-1]: https://medium.com/@hpgomide/cartola-pfc-analisando-os-atacantes-do-primeiro-turno-com-affinity-propagation-89df6304b4e4
[tutorial-r-2]: https://medium.com/@hpgomide/cartola-pfc-quais-meias-escalar-no-cartola-ofensivos-ou-defensivos-abe8d7db121d
[tutorial-r-3]: https://medium.com/@hpgomide/cartola-pfc-analisando-jogadores-de-defesa-com-affinity-propagation-parte-iii-4b3c35df2c0c
[tutorial-r-4]: https://medium.com/@hpgomide/como-montamos-defesas-no-cartolafc-com-estatística-e-modelagem-de-dados-6f5d58ac1034
[tutorial-cpp-1]: https://medium.com/cartolaanalitico/a-f%C3%B3rmula-de-valoriza%C3%A7%C3%A3o-8064b82b0f0
