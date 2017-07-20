# Select team
library(Rglpk)

# Number of variables
num.players <- length(df_pred_r2$next_round)

# Objective
obj <- df_pred_r2$next_round

# Vars
var.types <- rep("B", num.players)

# Model constraints
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
    df_pred_r2$next_round
  )

direction <- c( ">=",
                "<=",
                ">=",
                "<=",
                ">=",
                "<=",
                ">=",
                "<=",
                "==",
                "=="
)

rhs <- c(3, # Striker Max
         1, # Sriker Min
         5, # Mid Max
         3, # Mid Min
         3, # Def Max
         2, # Def Min
         2, # RB/LB Max
         1, # RB/LB Min
         1, # Keeper
         1, # Coach
         rep(1, num.players), #HERE, you need to enter a number that indicates how
         #risk you are willing to be, 1 being low risk,
         # 10 being high risk.  10 is max.
         120) 

sol <- Rglpk_solve_LP(obj = obj, mat = matrix, dir = direction, rhs = rhs,
                      types = var.types, max = TRUE)


a <- matrix(0, nrow = 6, ncol = length(df_pred_r2$next_round))
