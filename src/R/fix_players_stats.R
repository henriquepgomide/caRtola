# Correct and fix attributes -------------------------------------------------

# You must run create players stats until line 40.
df <-  
data %>%
  dplyr::filter(has.played == TRUE) %>%
  dplyr::group_by(atletas.atleta_id) %>%
  dplyr::mutate(score_cum = cumsum(atletas.pontos_num),
                n_games = row_number())

df[, 16:33] <- sapply(df[, 16:33], function(x) ifelse(is.na(x), 0, x))


# 1. Feature Engineering ---------------------------------------------------
# Remove clean sheet bonus
df$score.no.cleansheets <- 
  (df$CA * -2) + (df$FC * -0.5) + (df$RB * 1.5) +
  (df$GC * -5) + (df$CV * -5)   + #(df$SG * 5) +
  (df$FS * .5) + (df$PE * -.3)  + (df$A * 5)  +
  (df$FT * 3)  + (df$FD * 1.2)  + (df$FF * .8) +
  (df$G * 8)   + (df$I * -.5)   + (df$PP * -4) +
  (df$DD * 3)  + (df$DP * 7)    + (df$GS * -2)

# Compute fouls for each round
df$faltas <- df$FC + df$CA + df$CV

# Compute shots on goal
df$shotsX <- df$G + df$FT + df$FD + df$FF

# Estimate means 
df_with_means <- 
  df %>%
  group_by(atletas.atleta_id) %>%
  mutate(
    FS_mean =  FS / n_games,
    RB_mean =  RB / n_games,
    PE_mean =  PE / n_games,
    FC_mean =  FC / n_games,
    G_mean  =  G  / n_games,
    FF_mean =  FF / n_games,
    FT_mean =  FT / n_games,
    FD_mean =  FD / n_games,
    DD_mean =  DD / n_games,
    GS_mean =  GS / n_games,
    SG_mean =  SG / n_games,
    A_mean  =  A  / n_games,
    CA_mean =  CA / n_games,
    I_mean  =  I / n_games,
    CV_mean =  CV / n_games,
    PP_mean =  PP / n_games,
    GC_mean =  GC / n_games,
    DP_mean =  DP / n_games,
    score_cum_mean =  score_cum / n_games,
    score.no.cleansheets_mean = score.no.cleansheets / n_games,
    faltas_mean =  faltas / n_games,
    shotsX_mean =  shotsX / n_games) 

# Home and away scores
df_ha <- 
  data %>%
  dplyr::group_by(atleta.id, home_away) %>%
  dplyr::mutate(score_cum = cumsum(pontuacao),
                n_games = row_number())
 
# What to do next?
# 1. Estimate scouts aggregated scouts
# 2. Estimate home/away scores 
# Plot Gabigol Stats ------------------------------------------------------
gabigol <- 
  data %>%
  filter(atletas.atleta_id == 83257)

ggplot(gabigol, 
       aes(y = pontuacao, 
           x = rodadaF, 
           group = 1)) +
  geom_line()

ggplot(gabigol, 
       aes(y = pontuacao_mean, 
           x = rodadaF, 
           group = 1)) +
  geom_line()

attackers <- 
  deaggregate_scouts %>%
  filter(atletas.posicao_id %in% c("ata", "mei") &
           n_games > 10 &
           atletas.rodada_id > 8)

ggplot(attackers, 
       aes(x = G_mean , 
           y = shotsX_mean,
           color = atletas.posicao_id)) +
  geom_point() +
  geom_smooth()
