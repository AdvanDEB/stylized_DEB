# DEB Stylized Facts - Agentic Literature Review System

This project implements an AI-powered system to assess literature support for 1,200 Dynamic Energy Budget (DEB) theory stylized facts using RAG (Retrieval Augmented Generation) and large language models.

## System Overview

The system uses a 3-phase pipeline:

1. **Phase 1: PDF Extraction** - Extract text from 1,306 scientific papers
2. **Phase 2: RAG Indexing** - Chunk documents, generate embeddings, build vector search index
3. **Phase 3: Literature Review** - Assess each fact using RAG retrieval + LLM analysis

## Architecture

- **MongoDB**: Document storage, vector search, and assessment results
- **LlamaIndex**: RAG framework for document retrieval
- **Ollama** with `gpt-oss:120b`: Local LLM for assessment
- **Embedding Model**: `nomic-embed-text` via Ollama
- **Features**: Hybrid search, reranking, checkpointing, resumability

## Setup

### 1. Prerequisites

- MongoDB running on `localhost:27017`
- Ollama running with `gpt-oss:120b` and `nomic-embed-text` models
- Conda package manager

### 2. Create Conda Environment

```bash
conda create -n stylized_deb python=3.11 -y
conda activate stylized_deb
```

### 3. Install Dependencies

```bash
pip install pymongo pandas tqdm pymupdf numpy ollama flask flask-cors
pip install llama-index llama-index-vector-stores-mongodb llama-index-embeddings-ollama llama-index-llms-ollama sentence-transformers
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Run Individual Phases

```bash
# Phase 1: Extract PDFs to MongoDB
python scripts/run_phase1_extraction.py

# Phase 2: Generate embeddings and build index
python scripts/run_phase2_indexing.py

# Phase 3: Run literature review (test mode - 10 facts)
python scripts/run_phase3_review.py --test

# Phase 3: Run full review (all 1,200 facts)
python scripts/run_phase3_review.py
```

### Run All Phases

```bash
# Run complete pipeline (test mode)
python scripts/run_pipeline.py --all --test

# Run complete pipeline (production)
python scripts/run_pipeline.py --all
```

## Project Structure

```
stylized_DEB/
├── csv_files/                          # Stylized facts CSVs
│   ├── README.md
│   └── [12 CSV files with 1,200 facts]
│
├── files/                              # 1,306 PDFs (gitignored)
│   └── [Numbered directories with PDFs]
│
├── literature_review/                  # Main package
│   ├── config.py                      # Configuration
│   │
│   ├── phase1_extraction/             # PDF extraction
│   │   ├── pdf_extractor.py
│   │   └── extraction_pipeline.py
│   │
│   ├── phase2_indexing/               # RAG indexing
│   │   ├── document_processor.py
│   │   ├── embedding_generator.py
│   │   └── indexing_pipeline.py
│   │
│   ├── phase3_review/                 # Assessment agent
│   │   ├── rag_retriever.py
│   │   ├── ollama_client.py
│   │   ├── assessment_agent.py
│   │   ├── checkpoint_manager.py
│   │   ├── csv_updater.py
│   │   └── review_pipeline.py
│   │
│   └── utils/                         # Utilities
│       ├── mongodb_client.py
│       ├── logging_config.py
│       └── fact_loader.py
│
├── scripts/                           # Executable scripts
│   ├── run_phase1_extraction.py
│   ├── run_phase2_indexing.py
│   ├── run_phase3_review.py
│   └── run_pipeline.py
│
├── data/                              # Generated data (gitignored)
│   ├── logs/
│   └── checkpoints/
│
└── requirements.txt                   # Python dependencies
```

## Assessment Output

For each stylized fact, the system generates:

- **Literature Support Score (1-100)**: Quantitative assessment
  - 1-20: No/contradictory evidence
  - 21-40: Weak/indirect support
  - 41-60: Moderate support
  - 61-80: Strong support
  - 81-100: Very strong support
- **Number of Papers Reviewed**: Count of relevant papers
- **Supporting Papers**: List of supporting documents
- **Key Evidence Summary**: Brief summary of evidence
- **Assessment Confidence**: Low/Medium/High
- **Last Updated**: Timestamp

Results are stored in:
1. MongoDB `assessments` collection
2. Updated CSV files with new columns

## Configuration

Edit `literature_review/config.py` to customize:

- MongoDB connection
- Ollama model and server
- Chunking parameters
- Retrieval settings (top-k, hybrid search, reranking)
- LLM parameters (temperature, context size)

## Checkpointing & Resumability

The system automatically saves progress after each fact. If interrupted:

```bash
# Simply rerun Phase 3 - it will resume from last completed fact
python scripts/run_phase3_review.py
```

Checkpoint location: `data/checkpoints/review_checkpoint.json`

## Performance Estimates

- **Phase 1** (PDF Extraction): ~2-3 hours for 1,306 PDFs
- **Phase 2** (Indexing): ~1-2 hours for embeddings
- **Phase 3** (Review): ~24-48 hours for 1,200 facts
  - ~45-90 seconds per fact (retrieval + LLM inference)
  - Using gpt-oss:120b on appropriate hardware

## Testing

Before running the full pipeline, test on 10 sample facts:

```bash
python scripts/run_phase3_review.py --test
```

This will:
- Sample 10 facts evenly across all sections
- Run complete assessment pipeline
- Allow validation of results before full run

## Monitoring

- **CLI**: Progress bars with tqdm
- **Logs**: Detailed logs in `data/logs/`
- **MongoDB**: Query assessment collection for real-time stats

## Development

The type checker warnings in the editor are expected - all packages are installed in the conda environment and work correctly at runtime.

To verify setup:
```bash
conda activate stylized_deb
python -c "import pymongo; import ollama; from llama_index.core import VectorStoreIndex; print('✓ All packages working')"
```

## License

See main repository for license information.

## Contact

Part of the AdvanDEB organization's research on Dynamic Energy Budget theory.
