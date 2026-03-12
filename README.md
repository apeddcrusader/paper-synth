        # paper-synth

        Offline-first literature synthesis tool for aggregating findings across research abstracts

        ## Why this exists

        Reading 10 papers is slow. This tool synthesizes findings across a set of local abstracts, identifying consensus, disagreements, and gaps — producing a structured synthesis report without requiring network access or API keys.

        ## Features

        - Local file ingestion (JSON abstracts)
- Keyword-based topic clustering
- Consensus and disagreement detection
- Gap analysis and next-experiment suggestions
- Markdown synthesis report output

        ## Install

        ```bash
        pip install -e ".[dev]"
        ```

        ## Quickstart

        ```bash
        python -m paper_synth --help
        python -m paper_synth.cli synthesize --input-dir demo_data/abstracts/
        ```

        ## Demo data

        Sample data is provided in `demo_data/` for immediate testing without external dependencies.

        ## Limitations

        - Not intended for clinical use
- Uses lightweight heuristics and demo data
- Not a substitute for expert biological interpretation

        ## Roadmap

        - Add more comprehensive test datasets
- Optional LLM integration for enhanced analysis
- Performance benchmarking and optimization

        ## License

        MIT
