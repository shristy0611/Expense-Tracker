# Multi-Agent Receipt Processing

## Overview
This project implements a modular, multi-agent system for receipt processing, including OCR, data categorization, currency conversion, user confirmation, and reporting. Each agent is in its own module and is fully unit tested.

## Directory Structure
```
receipt_processing/
├── agents/
│   ├── ocr_agent.py
│   ├── categorizer_agent.py
│   ├── currency_agent.py
│   ├── confirmation_agent.py
│   └── report_agent.py
├── orchestrator.py
├── tests/
│   ├── test_ocr_agent.py
│   ├── test_categorizer_agent.py
│   ├── test_currency_agent.py
│   ├── test_confirmation_agent.py
│   └── test_report_agent.py
├── requirements.txt
└── README.md
```

## Setup
- Install requirements: `pip install -r requirements.txt`
- Place receipt images in the working directory.

## Usage
- Run orchestrator: `python orchestrator.py <receipt_image_path> [target_currency]`
- Each agent is modular and testable. See `tests/` for examples.

## Agents
- **Agent_OCR:** Extracts text with confidence scores.
- **Agent_Categorizer:** Parses and normalizes transactions.
- **Agent_Currency:** Handles currency conversion and caching.
- **Agent_Confirmation:** Presents and edits data for user approval.
- **Agent_Report:** Generates output and logs audit trail.

## Testing
Run all tests with:
```
python -m unittest discover tests
```

## Extending
- Add new agents by creating new modules in `agents/` and updating the orchestrator.
- Improve field extraction logic in `AgentCategorizer` for more languages or formats.
