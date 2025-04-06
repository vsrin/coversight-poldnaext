#!/bin/bash
# run_modules.sh - Script to run Policy DNA Extractor modules individually or together

# Default values
OUTPUT_DIR="output"
INPUT_FILE=""
PHASE=""

# Function to display help
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -p, --phase PHASE      Processing phase to run (1, 2, 3, 4, or all)"
    echo "  -i, --input FILE       Input file (document or previous phase result)"
    echo "  -o, --output DIR       Output directory (default: output)"
    echo "  -h, --help             Display this help message"
    echo ""
    echo "Phase 1: Document Processing and Segmentation"
    echo "Phase 2: Element Extraction and Classification"
    echo "Phase 3: Deep Language Analysis"
    echo "Phase 4: Cross-Reference and Dependency Mapping"
    echo "all: Run all phases"
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--phase)
            PHASE="$2"
            shift 2
            ;;
        -i|--input)
            INPUT_FILE="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate phase
if [[ -n "$PHASE" ]]; then
    if [[ ! "$PHASE" =~ ^[1-4]$|^all$ ]]; then
        echo "Error: Phase must be 1, 2, 3, 4, or all"
        exit 1
    fi
fi

# Build command
CMD="python run_example.py"

if [[ -n "$PHASE" ]]; then
    CMD="$CMD --phase $PHASE"
fi

if [[ -n "$INPUT_FILE" ]]; then
    CMD="$CMD --input $INPUT_FILE"
fi

CMD="$CMD --output-dir $OUTPUT_DIR"

# Run the command
echo "Running command: $CMD"
eval $CMD