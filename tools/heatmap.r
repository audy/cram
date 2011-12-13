data <- read.csv('short.csv', sep="\t", header=T, row.names=1)

data <- data.matrix(data)

heatmap <- heatmap(data, Rowv=NA, Colv=NA, col = cm.colors(256), scale="column", margin=c(5, 25))