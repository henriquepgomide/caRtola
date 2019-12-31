Dentro dessa pasta, você vai encontrar os seguintes arquivos:

- **Análise dos Dados.ipynb**: contém toda as etapas de importação dos dados, limpeza, criação das amostras e treinamento do modelo. Tudo bem organizado e explicadinho para qualquer um entender.
- **cartola.yml**: dependências python para rodar o código desse repositório.
- **markov chain lpp**: escalador de times com base em previsões feitas usando Markov Chains e programação linear.

Na pasta __models__, você encontra os modelos de Rede Neural treinados por nós para fazer as predições. Lá, há dois modelos:

- **nn.pkl**: Esse modelo é atualizado a cada rodada do Brasileirão. Você pode pegar outros modelos pelo histórico do git.
- **nn_31.pkl**: modelo que foi treinado para a rodada 31 do Brasileirão 2017, onde obtivemos ótimos resultados. A partir dessa rodada, nós comparávamos esse modelo com o _nn.pkl_.

Você pode ver como esses modelos foram treinados e como utilizá-los no arquivo [Análise de Dados.ipynb](src/python/Análise%20dos%20Dados.ipynb).

## Desafio Valorização
- Vamos quebrar o algoritmo de valorização do cartola em 2018? Deixe sua contribuição na pasta __desafio_valorizacao__. Você econtrará os dados necessários em ~/caRtola/data/desafio_valorizacao e o script em Python nesta pasta.

## E como faço para rodar os códigos?

Aconselha-se utilizar o [Miniconda](https://conda.io/miniconda.html) para instalar todas as dependências _python_ desse repositório.

Com o Miniconda instalado, vá para diretório dessa pasta e digite:
```sh
$ conda env create -f cartola.yml
```

Para ativar o ambiente (Linux/Mac):
```sh
$ source activate cartola
```
Para ativar o ambiente (Windows):
```sh
$ activate cartola
```
Depois, é só rodar o Jupyter Notebook:
```sh
$ jupyter notebook
```
