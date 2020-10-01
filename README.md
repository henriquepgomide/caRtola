#  CaRtola FC: Ciência de Dados e Futebol desde 2014.

> Felizmente, existe um repositório no GitHub chamado caRtola, no qual toda a parte de obtenção e tratamento dos dados do jogo já foi realizada. (Ribeiro, 2019) 

## Dados :memo:
Para ter acesso a todo o histórico de dados do _Cartola FC_ é só acessar a pasta [data](data/). Lá você encontra os dados organizados por ano e ainda um arquivo com os dados agregados de todos os anos. Está tudo disponível em arquivos separados por vírgulas. Você pode usar nosso [tutorial de python](https://github.com/henriquepgomide/caRtola/blob/master/src/python/colabs/caRtola_como_ler_repositório_do_github_com_BeautifulSoup_e_Pandas.ipynb), mas até o Excel abre. :wink:

## Tutoriais

Estes são alguns tutoriais que escrevemos. Contribuições são sempre bem vindas!

### Python
* [Como ler todos os arquivos das rodadas deste repositório com Python?](https://github.com/henriquepgomide/caRtola/blob/master/src/python/colabs/caRtola_como_ler_repositório_do_github_com_BeautifulSoup_e_Pandas.ipynb)
* [Seleção automática de jogadores feita com Markov Chain e programação linear](https://github.com/henriquepgomide/caRtola/blob/master/src/python/markov-chain-lpp.ipynb)
* [Média global ou média com mando de campo? O que usar para escalar seus jogadores](https://github.com/henriquepgomide/caRtola/blob/master/src/python/colabs/caRtola_media_media_movel_media_casa_ou_fora_o_que_usar.ipynb)
* [Algoritmo de valorização dos Jogadores do Cartola PFC](https://github.com/henriquepgomide/caRtola/blob/master/src/python/desafio_valorizacao/Desafio%20da%20Valorização.ipynb)
* [Estudo sobre algoritmo de valorizaço dos jogadores do Cartola, parte I](https://github.com/henriquepgomide/caRtola/blob/master/src/python/desafio_valorizacao/%23%20Descobrindo%20o%20algoritmo%20de%20valorização%20do%20Cartola%20FC%20-%20Parte%20I.ipynb)

### R
#### Análise de agrupamentos
* [Parte I - Analisando os atacantes do primeiro turno com Affinity Propagation](https://medium.com/@hpgomide/cartola-pfc-analisando-os-atacantes-do-primeiro-turno-com-affinity-propagation-89df6304b4e4)
* [Parte II - Quais meias escalar: Defensivos ou ofensivos?](https://medium.com/@hpgomide/cartola-pfc-quais-meias-escalar-no-cartola-ofensivos-ou-defensivos-abe8d7db121d)
* [Parte III - Analisando jogadores de defesa com Affinity Propagation](https://medium.com/@hpgomide/cartola-pfc-analisando-jogadores-de-defesa-com-affinity-propagation-parte-iii-4b3c35df2c0c)
#### Regressão
* [Como montar defesas no Cartola usando regressão de Poisson?](https://medium.com/@hpgomide/como-montamos-defesas-no-cartolafc-com-estatística-e-modelagem-de-dados-6f5d58ac1034)


### C++
* [Fórmula do algoritmo de valorização do Cartola FC](https://medium.com/cartolaanalitico/a-f%C3%B3rmula-de-valoriza%C3%A7%C3%A3o-8064b82b0f0). Solução pelo cientista de primeira categoria, João B Coelho. Implementação em [C++](https://github.com/joaoabcoelho/ModeloCartoletas).



## Previsões :dart:

Tem um modelo preditivo? Ajude-nos a montar um. Você pode conferir o resultado das previsões do nosso modelo preditivo em 2017 [nessa planilha](https://docs.google.com/spreadsheets/d/1knS8pE-JtIaeilUcjI_grIKBeox94QWAuMGKlfCfQSk/edit?usp=sharing). Nela, você vai encontrar os jogadores que o nosso modelo previu que iam fazer boas predições e a pontuação real do jogador naquela rodada. __Você acha que o modelo mandou bem? Foi ruim?__ [Vem resenhar com a gente, parça!](https://github.com/henriquepgomide/caRtola/issues/33)  :speech_balloon:

Ah, o nosso modelo preditivo é de domínio público também! Quer saber como ele foi treinado e como você pode utilizá-lo? [Confira aqui](src/python/Análise%20dos%20Dados.ipynb).

## Jogo Cartola - Super PFC

Criamos [um jogo de cartas](https://henriquepgomide.github.io/cartola-supertrunfo/) com base nos dados (em VueJS). Detalhe: também é de código-aberto! 
Link para repositório: [https://henriquepgomide.github.io/cartola-supertrunfo/](https://github.com/henriquepgomide/cartola-supertrunfo)

## Contribuições :octocat:

O repositório __caRtola__ é totalmente aberto a novas contribuições. Quer ajudar a gente, mas não sabe como? A gente te dá algumas ideias:

- Você já fez alguma análise estatística do _Cartola FC_ que acha legal e gostaria de compartilhar aqui?
- Você também tem um modelo preditivo para tentar prever os melhores jogadores?
- Ou simplesmente você viu um erro nos nossos dados/análises?

Sinta-se à vontade para submeter um Pull Request ou abrir uma issue! Nós vamos adorar ter isso no __caRtola__! :v:

## Na mídia

* Marchesini, L. [Cartola FC - Saiba como a pandemia pode influenciar os times mandantes](https://www.metropoles.com/esportes/cartola-fc-saiba-como-a-pandemia-pode-influenciar-os-times-mandantes) 2020.

## Em trabalhos acadêmicos

* E. Mota, D. Coimbra, and M. Peixoto, “Cartola FC Data Analysis: A simulation, analysis, and visualization tool based on Cartola FC Fantasy Game,” in Proceedings of the XIV Brazilian Symposium on Information Systems, Caxias do Sul, Brazil, Jun. 2018, pp. 1–8, doi: 10.1145/3229345.3229366.

* L. E. da S. Ribeiro, “Predição de escalações para o jogo CartolaFC utilizando aprendizado de máquina e otimização,” Prediction of escalations for CartolaFC fantasy game using machine learning and optimization, Jul. 2019, Accessed: Jul. 23, 2020. [Online]. Available: https://repositorio.ufu.br/handle/123456789/26681.

* E. F. Vernier, R. Garcia, I. P. da Silva, J. L. D. Comba, and A. C. Telea, “Quantitative Evaluation of Time-Dependent Multidimensional Projection Techniques,” arXiv:2002.07481 [cs], Feb. 2020, Accessed: Jul. 23, 2020. [Online]. Available: http://arxiv.org/abs/2002.07481.

Está faltando o seu? Envie para gente e colocamos aqui.


### Como citar?

Por favor, cite-nos.


[1]H. Gomide e A. Gualberto, CaRtola: Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python. https://github.com/henriquepgomide/caRtola/. 2020.

```
 @book{
     title={CaRtola: Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python}, 
     url={https://github.com/henriquepgomide/caRtola}, 
     abstractNote={Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python}, 
     author={Gomide, Henrique and Gualberto, Arnaldo}, 
     year={2020}
}
```



### Autores :busts_in_silhouette:

:bust_in_silhouette: __Henrique Gomide__:
* [Site Pessoal](http://henriquepgomide.github.io)
* [Twitter](https://twitter.com/hpgomide)
* [Linkedin](https://www.linkedin.com/in/hpgomide/)

:bust_in_silhouette: __Arnaldo Gualberto__:

* arnaldo.g12@gmail.com
* [Github](https://github.com/arnaldog12)
* [Site Pessoal](http://arnaldogualberto.com)

:bust_in_silhouette: __Julio Oliveira__:
* [Site pessoal](https://jcalvesoliveira.github.io)
* [Github](https://github.com/jcalvesoliveira)
* [Linkedin](https://www.linkedin.com/in/jcalvesoliveira/)

