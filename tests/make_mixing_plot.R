library(BuenColors)
library(stringr)
library(SummarizedExperiment)
library(Matrix)
library(dplyr)

substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}
load("data/BT_K_variants.rda")

vdf <- str_split_fixed(c(BT142_var, K562_var), "_", 3)
df2 <- data.frame(
  idx = as.numeric(vdf[,1]), 
  BT142 = c(vdf[1:4,3], vdf[5:33,2]),
  K562 = c(vdf[1:4,2], vdf[5:33,3])
)

extractme <- function(cell, letter, SE){
  idxx <- df2[which(df2[,cell] == letter), "idx"]
  colSums(assays(SE)[[paste0(letter, "_counts_fw")]][idxx, ] + assays(SE)[[paste0(letter, "_counts_rev")]][idxx, ])
}

SE_old <- readRDS("test_mgatk/final/mgatk.rds")
SE_new <- readRDS("test_maester/final/maegtk.rds")

SE_old <- SE_new
df3 <- data.frame(
  barcode = colnames(SE_old),
  BT142 = extractme("BT142", "A", SE_old) +  extractme("BT142", "C", SE_old) +  extractme("BT142", "G", SE_old) +  extractme("BT142", "T", SE_old),
  K562 = extractme("K562", "A", SE_old) +  extractme("K562", "C", SE_old) +  extractme("K562", "G", SE_old) +  extractme("K562", "T", SE_old)
)
df3 <-  df3 %>% mutate(minor_population = pmin(K562/(BT142 + K562 + 0.001)*100 ,BT142/(BT142 + K562 + 0.001)*100),
                       minor_population_cut = pmin(minor_population, 10))

p1 <- ggplot(df3 , aes(x = BT142, y = K562, color = minor_population_cut)) +
  pretty_plot() + L_border()  + theme(legend.position = "bottom") +
  geom_point() + labs(x = "BT142 homoplasmic", y = "K562 homoplasmic",  color = "Minor Pop %") +
  scale_color_gradientn(colors = jdb_palette("brewer_spectra"))

p2 <- ggplot(df3 , aes(x = log10(BT142 + 1), y = log10(K562 + 1), color = minor_population_cut)) +
  pretty_plot() + L_border()  + theme(legend.position = "bottom") +
  geom_point() + labs(x = "log BT142 homoplasmic ", y = "log K562 homoplasmic",  color = "Minor Pop %") +
  scale_color_gradientn(colors = jdb_palette("brewer_spectra"))

cowplot::ggsave(cowplot::plot_grid(p1, p2, nrow = 1), file = "MAESTER_mixing_plot.png", width =7, height = 4)
