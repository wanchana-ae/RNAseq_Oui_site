if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install("DESeq2")
BiocManager::install("tximport")
BiocManager::install("tximportData")
BiocManager::install("gplots")
BiocManager::install("ggplot2")
BiocManager::install("pheatmap")
BiocManager::install("vsn")
BiocManager::install("hexbin")
BiocManager::install("VennDetail")
###################################
library("DESeq2")
library("RColorBrewer")
library("pheatmap")
library("readr")
library("RColorBrewer")
library("pheatmap")
library("readr")
library("BiocParallel")
library("tximport")
library("tximportData")
library("gplots")
library("vsn")
library("hexbin")
library("ggplot2")
library("stats")
library("gplots")
library("RColorBrewer")
library("EnhancedVolcano")

colors <- colorRampPalette(brewer.pal(9, "Blues"))(255)
hmcol  <- colorRampPalette(brewer.pal(9, "GnBu"))(255)
hmcol2  <- rev(colorRampPalette(brewer.pal(9, "Spectral"))(255))
my_palette <- colorRampPalette(c("green", "black", "red"))(255)
my_palette2 <- colorRampPalette(c("purple", "black", "orange"))(255)

countData <- as.matrix(read.table("gene_count_matrix_2.csv", sep=',', row.names = 1, header = 1))
head(countData)
colData <- read.csv("sample_list_DESeq2_v2.txt", sep="\t", row.names=1, stringsAsFactors = 1)
all(rownames(colData) %in% colnames(countData))
countData <- countData[, rownames(colData)]
all(rownames(colData) == colnames(countData))

sum(is.na(countData))   # นับจำนวน NA ทั้งหมด
which(is.na(countData), arr.ind = TRUE)   # ตำแหน่ง NA
countData <- countData[rowSums(is.na(countData)) == 0, ] #ลบ gene NA
#countData[is.na(countData)] <- 0 #หรือแทนที่ด้วย 0

#Create a DESeqDataSet from count matrix and labels
dds <- DESeqDataSetFromMatrix(countData = countData,
                              colData = colData, 
                              design = ~Conditon)

colData(dds)
resultsNames(dds)
## Optionsnal #####
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]
##########
dds <- DESeq(dds)
res <- results(dds, parallel=TRUE)
res
resultsNames(dds)
#=========================================================================
#QC part
plotCounts(dds, gene=which.min(res$padj), intgroup="Conditon")
d <- plotCounts(dds, gene=which.min(res$padj), intgroup="Conditon", 
                returnData=TRUE)

library("ggplot2")
ggplot(d, aes(x=Conditon, y=count)) + 
  geom_point(position=position_jitter(w=0.1,h=0)) + 
  scale_y_log10(breaks=c(25,100,400))
vsd <- vst(dds, blind=FALSE)
#rld <- rlog(dds, blind=FALSE)
head(assay(vsd), 3)

#Normalized Counts
ntd <- normTransform(dds)

library("vsn")
library("hexbin")

# --- เซฟกราฟของ ntd (Log transform) ---
pdf("Plot_meanSd_NTD.pdf", width = 7, height = 5)
meanSdPlot(assay(ntd), main = "Mean-SD Plot: NTD")
dev.off()

# --- เซฟกราฟของ vsd (VST transform) ---
pdf("Plot_meanSd_VSD.pdf", width = 7, height = 5)
meanSdPlot(assay(vsd), main = "Mean-SD Plot: VSD")
dev.off()

#meanSdPlot(assay(rld))
sampleDists <- dist(t(assay(vsd)))

library("RColorBrewer")
sampleDistMatrix <- as.matrix(sampleDists)
rownames(sampleDistMatrix) <- paste(vsd$Conditon, sep="-",vsd$Rep)
colnames(sampleDistMatrix) <- NULL
colors <- colorRampPalette( rev(brewer.pal(9, "Blues")) )(255)

#save sample DistMatrix
pdf("Sample_Distance_Heatmap.pdf", width = 8, height = 7)
pheatmap(sampleDistMatrix,
         clustering_distance_rows=sampleDists,
         clustering_distance_cols=sampleDists,
         col=colors)
dev.off()

pdf("PCA_plot_vsd.pdf", width = 7, height = 6)
plotPCA(vsd, intgroup="Conditon")
dev.off()

pdf("PCA_plot_vsd_with_Rep.pdf", width = 7, height = 6)
pcaData <- plotPCA(vsd, intgroup=c("Conditon", "Rep"), returnData=TRUE)
percentVar <- round(100 * attr(pcaData, "percentVar"))
ggplot(pcaData, aes(PC1, PC2, color=Conditon, shape=factor(Rep))) +
  geom_point(size=3) +
  xlab(paste0("PC1: ",percentVar[1],"% variance")) +
  ylab(paste0("PC2: ",percentVar[2],"% variance")) + 
  coord_fixed()
dev.off()

plotMA(res, ylim=c(-20,20))

summary(res)
#Save summary file
sink("deseq2_summary.txt")
summary(res)
sink()

res
#=========================================================================
colData(dds)

#contrast = c("Condition", "A", "B")
#First is Treatment, Second is Control (A - B) or log2(A/B)

# 1.Compact vs Control in Variety PTT1
one_PTT1_Compact_vs_Control <- results(dds, 
                                       contrast=c("Conditon", "PTT1_Compact", "PTT1_Control"), 
                                       alpha = 0.01)

# 2. Compact vs Control in Variety Dharia
two_Dharia_Compact_vs_Control <- results(dds, 
                                         contrast=c("Conditon", "Dharia_Compact", "Dharia_Control"), 
                                         alpha = 0.01)

# 3.Variety (PTT1 vs Dharia) only Control group
three_Control_PTT1_vs_Dharia <- results(dds, 
                                        contrast=c("Conditon", "PTT1_Control", "Dharia_Control"), 
                                        alpha = 0.01)

# 4.Variety (PTT1 vs Dharia) only Compact group
four_Compact_PTT1_vs_Dharia <- results(dds, 
                                       contrast=c("Conditon", "PTT1_Compact", "Dharia_Compact"), 
                                       alpha = 0.01)


# รวมผลลัพธ์ไว้ใน List
results_list <- list(
  PTT1_Comp_vs_Ctrl = one_PTT1_Compact_vs_Control,
  Dharia_Comp_vs_Ctrl = two_Dharia_Compact_vs_Control,
  Control_PTT1_vs_Dharia = three_Control_PTT1_vs_Dharia,
  Compact_PTT1_vs_Dharia = four_Compact_PTT1_vs_Dharia
)

library(EnhancedVolcano)
library(ggplot2)

for (res_name in names(results_list)) {
  
  # ดึงข้อมูลจาก List
  current_res <- results_list[[res_name]]
  
  message(">>> Saving results for: ", res_name)
  
  # 1. สร้างโฟลเดอร์แยกตามชื่อการเปรียบเทียบ
  dir.create(res_name, showWarnings = FALSE)
  
  # 2. จัดเรียงตามค่า padj และบันทึก Full Result
  resOrdered <- current_res[order(current_res$padj), ]
  write.csv(as.data.frame(resOrdered), 
            file = file.path(res_name, paste0(res_name, "_Result.csv")))
  
  # 3. คัดกรอง Significant Genes (padj < 0.01)
  resSig <- subset(resOrdered, padj < 0.01)
  write.csv(as.data.frame(resSig), 
            file = file.path(res_name, paste0(res_name, "_Significant.csv")))
  
  # 4. แยกสาย Up-regulated (LFC >= 0)
  resUp <- subset(resSig, log2FoldChange >= 0)
  write.csv(as.data.frame(resUp), 
            file = file.path(res_name, paste0(res_name, "_Upregulate.csv")))
  
  # 5. แยกสาย Down-regulated (LFC < 0)
  resDown <- subset(resSig, log2FoldChange < 0)
  write.csv(as.data.frame(resDown), 
            file = file.path(res_name, paste0(res_name, "_Downregulate.csv")))
  
  # 6. บันทึก Summary ของแต่ละกลุ่มลงใน Text File เดียวกัน
  summary_file <- file.path(res_name, paste0(res_name, "_Summary_Log.txt"))
  sink(summary_file)
  cat("--- Summary for: ", res_name, " ---\n\n")
  cat("Full Results:\n")
  summary(resOrdered)
  cat("\nSignificant (padj < 0.01):\n")
  summary(resSig)
  cat("\nUp-regulated:\n")
  summary(resUp)
  cat("\nDown-regulated:\n")
  summary(resDown)
  sink()
  
  # 7. สร้างและบันทึก Volcano Plot
  p <- EnhancedVolcano(current_res,
                       lab = rownames(current_res),
                       x = 'log2FoldChange',
                       y = 'pvalue',
                       title = paste("Volcano Plot:", res_name),
                       pCutoff = 1e-3,
                       FCcutoff = 2.0,
                       pointSize = 1.0,
                       labSize = 2.0,
                       colAlpha = 1,
                       legendPosition = 'right')
  
  ggsave(file.path(res_name, paste0(res_name, "_Volcano.png")), plot = p, width = 10, height = 8)
  
  # ล้างตัวแปรชั่วคราว
  rm(resOrdered, resSig, resUp, resDown, p)
}

message("Completed! All files are organized in their folders.")

#-----------------
library(VennDetail)

# 1. เตรียมรายชื่อยีน (Gene names) จากผลลัพธ์แต่ละชุด (คัดที่ padj < 0.01)
# ดึงจาก results_list ที่สร้างไว้ก่อนหน้านี้
one_genes   <- rownames(subset(results_list$PTT1_Comp_vs_Ctrl, padj < 0.01))
two_genes   <- rownames(subset(results_list$Dharia_Comp_vs_Ctrl, padj < 0.01))
three_genes <- rownames(subset(results_list$Control_PTT1_vs_Dharia, padj < 0.01))
four_genes  <- rownames(subset(results_list$Compact_PTT1_vs_Dharia, padj < 0.01))

# 3. จัดการและบันทึกผลลัพธ์
dir.create("venn_diagram_results", showWarnings = FALSE)

# 2. รัน VennDetail โดยใช้รูปแบบ List
ven <- venndetail(list(
  one_PTT1_Comp_vs_Ctrl      = one_genes,
  two_Dharia_Comp_vs_Ctrl    = two_genes,
  three_Control_PTT1_vs_Dharia = three_genes,
  four_Compact_PTT1_vs_Dharia  = four_genes
))

png("venn_diagram_results/Venn_Plot.png", width = 1168, height = 822, res = 120)
plot(ven)
dev.off()

pdf("venn_diagram_results/Venn_Plot.pdf", width = 7, height = 6)
plot(ven)
dev.off()

result(ven)
detail(ven)

vendetail <- as.data.frame(detail(ven))
venn <- subset(vendetail, `detail(ven)` != 0)

for (i in row.names(venn)) {
  print(i)
  write.table( getSet(ven, i) , file=paste0("venn_diagram_results/",i,".xls"), sep = "\t" , quote = F )
}
