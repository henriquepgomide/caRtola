# What? ----------------------------------------------
# This script is intended to run exploratory analysis
# and run some models to predict player fantasy 
# performance based on 2016, 2015 and 2014.
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script tem como objetivo executar algumas
# análises exploratórias e criar modelos para prever
# os resultados dos jogadores do cartola com base
# nos dados de 2016, 2015 e 2014
# ----------------------------------------------------

setwd("~/caRtola")

# Load Libraries
# Carregar pacotes R
library(dplyr)

#--------------------
# Open 2014 data-----
#--------------------

cartola_2014 <- read.csv("db/2014/Scouts.csv", stringsAsFactors = FALSE)

#--------------------
# Open 2015 data-----
#--------------------

load("db/2015/cartolaDF.rds.RData")

# TODO
# 1 - Avaliar se id e realmente identificador unico entre os bancos
# 2 - Criar variavel temporada para cada banco de dados
# 3 - Converter variavel 'Mando' para dummy
# 4 - 