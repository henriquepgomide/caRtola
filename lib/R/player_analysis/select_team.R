library(lpSolve)

# Matrix
matrix <- rbind(
    as.numeric(df_pred_r2$Posicao == "ata"), # Num strikers
    as.numeric(df_pred_r2$Posicao == "ata"), # Num strikers
    as.numeric(df_pred_r2$Posicao == "mei"), # Num Mid
    as.numeric(df_pred_r2$Posicao == "mei"), # Num Mid
    as.numeric(df_pred_r2$Posicao == "zag"), # Num Defenders
    as.numeric(df_pred_r2$Posicao == "zag"), # Num Defenders
    as.numeric(df_pred_r2$Posicao == "lat"), # Num Right or left back
    as.numeric(df_pred_r2$Posicao == "lat"), # Num Right or left back
    as.numeric(df_pred_r2$Posicao == "gol"), # Num goalkeeper
    as.numeric(df_pred_r2$Posicao == "tec"),  # Num head coach
    diag(df_pred_r2$risk_points),
    df_pred_r2$Preco
  )

# Prepare input for LP solver
objective.in <- df_pred_r2$next_round
const.dir <- c( "<=", ">=",
                "<=", ">=",
                "<=", ">=",
                "<=", ">=",
                "==",
                "==",
                rep("<=", length(df_pred_r2$next_round)),
                "<="
)
const.rhs <- c(3, 1, 
               5, 3, 
               3, 2,
               2, 0,
               1, 1,
               rep(5, length(df_pred_r2$next_round)),
               97.11)


sol <- lp(direction = "max", objective.in, # maximize objective function
          matrix, const.dir, const.rhs,   # constraints
          all.bin = TRUE)
inds <- which(sol$solution == 1)
df_pred_r2[inds, c("Apelido", "Posicao", "next_round", "Preco", "risk_points", "variable", "pred.home.score",
                   "pred.away.score"), ]
