
# API Query Processor

This script leverages Azure OpenAI and the BM25 algorithm to provide context-aware answers for queries based on REST API documentation. It processes a given API documentation file, extracts relevant endpoint details, and uses natural language queries to generate detailed responses.

## Features
- Parses REST API documentation from a JSON file.
- Extracts paths, summaries, and descriptions to create a searchable corpus.
- Utilizes the BM25 algorithm to rank API endpoints based on the relevance to a user query.
- Uses Azure OpenAI (GPT-based model) to generate contextual answers for the top-ranked API endpoints.
- Supports combining partial answers from multiple relevant API paths into a final detailed response.

## How It Works
1. **Input API Documentation**: The script reads the REST API JSON file (`catalystcenter.json` by default).
2. **Corpus Creation**: Extracts summaries and descriptions from API paths to create a searchable text corpus.
3. **Query Matching**: Accepts a natural language query and uses BM25 to find the most relevant API paths.
4. **Contextual Responses**: Passes the relevant paths and documentation context to Azure OpenAI for generating detailed answers.
5. **Final Aggregation**: Combines partial responses into a comprehensive answer to the user query.

## Requirements
- Python 3.x
- Required Libraries: `json`, `pprint`, `sample_bm25`, `credentials`, `openai`
- Azure OpenAI account with an active API key.

## Usage
1. Update `credentials.azure_openai_token` with your Azure OpenAI API key.
2. Place your API documentation file in JSON format (e.g., `catalystcenter.json`).
3. Run the script:
   ```bash
   python script.py
   ```
4. Enter your query when prompted. The script will output relevant API paths and a detailed response.

## Sample Workflow
1. **Input JSON**: `catalystcenter.json` contains the REST API paths and descriptions.
2. **Query**: "How to create a new user?"
3. **Output**:
   - Relevant API paths based on query relevance.
   - A detailed answer including required fields and example usage.

## Notes
- Customize the input JSON file by uncommenting or editing the `file` variable.
- The script limits results to the top 5 relevant paths to maintain focus.
- Responses depend on the quality of input API documentation.
