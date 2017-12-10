library(rjson)

matches <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)

write(toJSON(matches), file = "~/cartolapfc/cartola/static/blog/matches.json")
write(toJSON(matches), file = "~/matches.json")

toJSON(head(matches))
