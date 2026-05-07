# 🎩 cartola — pipeline de agregação

Pacote Python que agrega os dados raw do **Cartola FC** (2014–2026) em um único
CSV harmonizado de 38 colunas (contexto + clube + jogador + estado de jogo +
21 scouts), usando [Hamilton](https://hamilton.dagworks.io/) para o DAG e
[Typer](https://typer.tiangolo.com/) para a CLI.

---

## ✅ Pré-requisitos

- **Python 3.12+**.
- **[uv](https://docs.astral.sh/uv/)** — gerenciador de venv/dependências.
- **git**

## ⚙️ 1. Setup do repo

```bash
git clone https://github.com/henriquepgomide/caRtola.git
cd caRtola
make install
```

---

## 💻 2. Rodando o pipeline

Para rodar a agregação, você pode usar o comando do Makefile:

```bash
make aggregate    # todos os anos
```

ou usando uv (que aceita também subset de anos):

```bash
uv run cartola aggregate                            # todos os anos
uv run cartola aggregate --years 2024,2025,2026     # subset
```

> Em runs parciais, **apenas** os CSVs por ano são gravados — o CSV agregado
> final só é regerado em runs completos para não enganar consumidores
> downstream.

Saídas:

| Caminho                                    | Quando é gerado            | Conteúdo                          |
| ------------------------------------------ | -------------------------- | --------------------------------- |
| `data/03_primary/cartola_<year>.csv`       | sempre (um por ano rodado) | uma temporada no schema canônico  |
| `data/04_aggregated/cartola_2014_2026.csv` | só em runs completos       | concat final de todos os anos     |

### Hamilton UI (opcional)

Para visualizar o DAG e acompanhar runs:

1. Suba a UI em `http://localhost:8241`:

   ```bash
   make viz
   # equivalente a:
   uv run cartola viz
   ```

2. Na UI, crie um projeto chamado **`cartola`** (nome esperado pelo tracker).

3. Em outro terminal, dispare o pipeline enviando o run para a UI:

   ```bash
   uv run cartola aggregate --track
   ```

---

## 🧪 3. Testes

A suíte está em `tests/` e é dividida em três famílias:

| Pasta                  | Marker   | O que cobre                                                  |
| ---------------------- | -------- | ------------------------------------------------------------ |
| `tests/unit/`          | —        | nodes, readers, schema, CLI — rápido (segundos)              |
| `tests/integration/`   | —        | pipeline end-to-end com fixtures sintéticas                  |
| `tests/data_quality/`  | `slow`   | smoke test contra todos os dados reais em `data/01_raw/`     |

Para rodar testes, você pode usar os comandos do Makefile:

```bash
make test         # todos os testes (unit + integration + slow)
make test-fast    # tudo, exceto os marcados como `slow`
make test-slow    # apenas o smoke test contra dados reais (~10s)
```

ou usando uv:

```bash
uv run pytest
uv run pytest -m "not slow"
uv run pytest -m slow
```

> 💡 Cobertura é exigida em **100%**
