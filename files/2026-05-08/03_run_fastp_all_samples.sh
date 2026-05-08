#!/bin/bash
# =============================================================================
# 03_run_fastp_all_samples.sh
# fastp Quality Trimming — RNAseq Oui (13 samples, Paired-end)
# Run AFTER FastQC, BEFORE HISAT2
# Usage: bash 03_run_fastp_all_samples.sh [--resume]
# =============================================================================

set -euo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
RAWDATA_DIR="/fs4/Mining_data/Method/RNAseq/Oui/20260428_HN00271762_TRR_Report/rawdata"
TRIMMED_DIR="/fs4/Mining_data/Method/RNAseq/Oui/Trimmed"
LOG_DIR="/fs4/Mining_data/Method/RNAseq/Oui/logs/fastp"
SAMPLE_LIST="/fs4/Mining_data/Method/RNAseq/Oui/scripts/sample_list.txt"

# ── fastp parameters ─────────────────────────────────────────────────────────
THREADS=8
QUAL=20        # --qualified_quality_phred
MIN_LEN=36     # --length_required

# ── Setup ────────────────────────────────────────────────────────────────────
mkdir -p "$TRIMMED_DIR" "$LOG_DIR"

RESUME=false
if [[ "${1:-}" == "--resume" ]]; then
    RESUME=true
    echo "[INFO] Resume mode: skipping samples that already have output"
fi

echo "=============================================="
echo " fastp Trimming — RNAseq Oui"
echo " Started: $(date)"
echo "=============================================="

# ── Loop all samples ─────────────────────────────────────────────────────────
while IFS= read -r SAMPLE || [[ -n "$SAMPLE" ]]; do
    [[ -z "$SAMPLE" || "$SAMPLE" =~ ^# ]] && continue

    R1="${RAWDATA_DIR}/${SAMPLE}_1.fastq.gz"
    R2="${RAWDATA_DIR}/${SAMPLE}_2.fastq.gz"
    OUT1="${TRIMMED_DIR}/${SAMPLE}_1.trimmed.fastq.gz"
    OUT2="${TRIMMED_DIR}/${SAMPLE}_2.trimmed.fastq.gz"
    JSON_OUT="${LOG_DIR}/${SAMPLE}_fastp.json"
    HTML_OUT="${LOG_DIR}/${SAMPLE}_fastp.html"
    LOG_OUT="${LOG_DIR}/${SAMPLE}_fastp.log"

    # Check input files
    if [[ ! -f "$R1" || ! -f "$R2" ]]; then
        echo "[SKIP] $SAMPLE — raw data not found"
        continue
    fi

    # Resume mode
    if $RESUME && [[ -f "$OUT1" && -f "$OUT2" ]]; then
        echo "[SKIP] $SAMPLE — trimmed output already exists"
        continue
    fi

    echo ""
    echo "----------------------------------------------"
    echo " Processing: $SAMPLE  ($(date +%H:%M:%S))"
    echo "----------------------------------------------"

    fastp \
        --in1  "$R1" \
        --in2  "$R2" \
        --out1 "$OUT1" \
        --out2 "$OUT2" \
        --json "$JSON_OUT" \
        --html "$HTML_OUT" \
        --thread "$THREADS" \
        --qualified_quality_phred "$QUAL" \
        --length_required "$MIN_LEN" \
        --detect_adapter_for_pe \
        --correction \
        --overrepresentation_analysis \
        2>&1 | tee "$LOG_OUT"

    echo "[DONE] $SAMPLE"

done < "$SAMPLE_LIST"

echo ""
echo "=============================================="
echo " All samples trimmed!"
echo " Finished: $(date)"
echo " Output: $TRIMMED_DIR"
echo " Reports: $LOG_DIR"
echo "=============================================="
