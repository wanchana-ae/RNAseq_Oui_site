# Files — 2026-05-01

Output files จาก FastQC, HISAT2 pipeline และ prepDE.py

| File | Location | Description |
|------|----------|-------------|
| FastQC reports (HTML/ZIP) | `../FastQC/<SAMPLE>/` | QC report ทุก sample (26 ไฟล์) |
| Pipeline logs | `../File/logs/<SAMPLE>_pipeline.log` | Log ของแต่ละ sample (13 ไฟล์) |
| sample_list_oui.txt | `../File/sample_list_oui.txt` | Input list สำหรับ prepDE.py |
| prepDE.py | `../File/prepDE.py` | Script สร้าง count matrix |
| gene_count_matrix.csv | `../File/gene_count_matrix.csv` | Gene count matrix (36,057 genes × 13 samples) |
| transcript_count_matrix.csv | `../File/transcript_count_matrix.csv` | Transcript count matrix (40,249 transcripts × 13 samples) |
