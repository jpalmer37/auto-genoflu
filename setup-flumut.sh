#!/bin/bash
# Setup script for auto_flumut

set -e

echo "🚀 auto_flumut Setup Script"
echo "============================"
echo ""

# Check if flumut is installed
if ! command -v flumut &> /dev/null; then
    echo "⚠️  Warning: flumut not found in PATH"
    echo "   Install with: mamba install -c bioconda flumut"
    echo ""
fi

# Get base directory from user or use default
read -p "Enter base directory for flumut (default: ~/flumut): " BASE_DIR
BASE_DIR=${BASE_DIR:-~/flumut}
BASE_DIR=$(eval echo "$BASE_DIR")  # Expand ~ if present

echo ""
echo "📁 Creating directories..."
mkdir -p "$BASE_DIR"/{inputs,outputs,logs}
echo "   ✓ Created $BASE_DIR/inputs"
echo "   ✓ Created $BASE_DIR/outputs"
echo "   ✓ Created $BASE_DIR/logs"

# Get scan interval
read -p "Enter scan interval in seconds (default: 60): " SCAN_INTERVAL
SCAN_INTERVAL=${SCAN_INTERVAL:-60}

echo ""
echo "📝 Creating configuration file..."
cat > "$BASE_DIR/config.json" << EOF
{
  "input_dir": "$BASE_DIR/inputs/",
  "output_dir": "$BASE_DIR/outputs/",
  "provenance_dir": "$BASE_DIR/logs/",
  "scan_interval_seconds": $SCAN_INTERVAL
}
EOF
echo "   ✓ Created $BASE_DIR/config.json"

echo ""
echo "🔧 Installing auto_flumut..."
if [ -f "pyproject.toml" ]; then
    pip install -e . --quiet
    echo "   ✓ Installed auto_flumut"
else
    echo "   ⚠️  Warning: pyproject.toml not found. Run this from the repository root."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Place FASTA files in: $BASE_DIR/inputs/"
echo "   2. Run: auto_flumut -c $BASE_DIR/config.json"
echo "   3. Check outputs in: $BASE_DIR/outputs/"
echo "   4. Check provenance in: $BASE_DIR/logs/"
echo ""
echo "💡 Tips:"
echo "   - Use --log-level DEBUG for detailed logging"
echo "   - Press Ctrl+C to stop the service"
echo "   - Check BUILD_TEST.md for more options"
echo ""

# Offer to create a sample FASTA file
read -p "Create a sample test file? (y/N): " CREATE_SAMPLE
if [[ "$CREATE_SAMPLE" =~ ^[Yy]$ ]]; then
    cat > "$BASE_DIR/inputs/sample_test.fasta" << 'EOF'
>sample_sequence_1|H1N1|2024-01-15
ATGGAGAGAATAAAAGAACTGAGAGATCTAATGTCACAGTCCCGCACTCGCGAGATACTCACTAAGACCACTGTGG
ACCATATGGCCATAATCAAGAAATACACATCAGGAAGACAAGAGAAGAACCCCGCACTCAGAATGAAGTGGATGAT
>sample_sequence_2|H3N2|2024-01-15
ATGGAGTCTTCTAACCGAGGTCGAAACGTACGTTCTCTCTATCGTCCCGTCAGGCCCCCTCAAAGCCGAGATCGCA
CAGAGACTTGAAGATGTCTTTGCAGGGAAGAACACCGATCTTGAGGTTCTCATGGAATGGCTAAAGACAAGACCAA
EOF
    echo "   ✓ Created sample test file: $BASE_DIR/inputs/sample_test.fasta"
    echo ""
fi

echo "Ready to run! Execute:"
echo "  auto_flumut -c $BASE_DIR/config.json --log-level INFO"
