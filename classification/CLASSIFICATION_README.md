# UBRI Paper Classification System

This system uses OpenAI's API to automatically classify all papers in the UBRI dataset into specific blockchain research categories.

## 📁 **Folder Structure**

All classification-related files are now organized in the `classification/` folder:

```
classification/
├── classify_papers.py              # Main classification script
├── test_classification.py          # Test script for small samples
├── view_classifications.py         # Interactive results viewer
├── CLASSIFICATION_README.md        # This documentation
├── paper_classifications.json      # Complete classification results
├── test_classifications.json       # Test results
└── classification_summary_report.txt # Human-readable summary
```

## Features

- **20 Specific Categories**: Specialized classification for blockchain research
- **Preserves Key Information**: Title, authors, and university for each paper
- **Batch Processing**: Handles rate limits and processes papers efficiently
- **Detailed Reports**: Generates both JSON data and human-readable reports
- **Interactive Viewer**: Browse and search classification results

## Categories

The system classifies papers into these 20 specific blockchain research categories:

1. **DeFi (Decentralized Finance)** - Lending, borrowing, yield farming, liquidity protocols
2. **Cryptocurrency Economics & Market Analysis** - Price analysis, market dynamics, trading behavior
3. **Stablecoins & CBDCs** - Stablecoin mechanisms, central bank digital currencies
4. **RWA (Real World Assets)** - Tokenization of real assets, real estate, commodities
5. **Smart Contract Security & Vulnerabilities** - Contract audits, exploits, security analysis
6. **Consensus Mechanisms & Protocols** - Proof-of-work, proof-of-stake, consensus algorithms
7. **Zero-Knowledge Proofs & Privacy** - ZK protocols, privacy-preserving techniques
8. **Scalability & Performance Optimization** - Layer 2 solutions, throughput optimization
9. **Cross-Chain & Interoperability** - Multi-chain protocols, bridges, cross-chain communication
10. **Network Analysis & Graph Theory** - Blockchain network structure, graph analysis
11. **Game Theory & Mechanism Design** - Incentive mechanisms, strategic behavior analysis
12. **Regulation & Legal Analysis** - Legal frameworks, regulatory compliance, policy analysis
13. **Security & Cryptography** - Cryptographic security, attack vectors, defense mechanisms
14. **Energy & Sustainability** - Energy consumption, green blockchain, sustainability
15. **Healthcare & Digital Health** - Medical applications, health data, pharmaceutical supply chains
16. **Supply Chain & Logistics** - Supply chain transparency, logistics optimization
17. **Governance & DAOs** - Decentralized governance, voting mechanisms, organizational structures
18. **FinTech & Traditional Finance** - Integration with traditional finance, banking applications
19. **Machine Learning & AI Applications** - AI in blockchain, predictive models, automated systems
20. **Other** - Papers that don't fit the above categories

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

### 1. Test Classification (Recommended First Step)

Run a test on a small sample to verify everything works:

```bash
cd classification
python test_classification.py
```

This will:
- Test with 5 papers
- Show sample classifications
- Save results to `test_classifications.json`

### 2. Full Classification

Run the complete classification on all papers:

```bash
cd classification
python classify_papers.py
```

This will:
- Process all ~496 papers
- Take approximately 10-15 minutes (with rate limiting)
- Save results to `paper_classifications.json`
- Generate a summary report `classification_summary_report.txt`

### 3. View Results

Use the interactive viewer to explore results:

```bash
cd classification
python view_classifications.py
```

Or view a specific results file:
```bash
cd classification
python view_classifications.py your_results_file.json
```

## Output Files

### `paper_classifications.json`
Complete classification results in JSON format:
```json
{
  "summary": {
    "total_papers_classified": 496,
    "classification_timestamp": "2025-07-30T12:38:34...",
    "category_distribution": {...},
    "universities_represented": 63,
    "years_covered": [2017, 2018, ...]
  },
  "classified_papers": [
    {
      "paper_id": "paper_2",
      "title": "Commercializing Blockchain...",
      "authors": ["Antony Welfare"],
      "university": "UCL",
      "year": 2019,
      "category": "FinTech & Traditional Finance",
      "category_number": 18,
      "classification_confidence": "high"
    }
  ],
  "categories": [...]
}
```

### `classification_summary_report.txt`
Human-readable summary with:
- Overall statistics
- Category distribution
- Top universities
- Sample papers by category

## Interactive Viewer Features

The viewer (`view_classifications.py`) provides:

1. **Summary Statistics** - Overall numbers and distributions
2. **Papers by Category** - Browse papers grouped by topic
3. **University Statistics** - See which universities focus on which topics
4. **Search Papers** - Find papers by title or author
5. **Category Details** - View all papers in a specific category

## Recent Results (July 30, 2025)

**Total Papers Classified:** 496 papers  
**Universities Represented:** 63  
**Years Covered:** 2017-2025  

### Top 5 Categories (Previous Classification):
1. **Other** - 93 papers (18.8%)
2. **Blockchain Applications (Non-Financial)** - 76 papers (15.3%)
3. **Blockchain Technology & Infrastructure** - 60 papers (12.1%)
4. **Cryptocurrency Economics & Markets** - 50 papers (10.1%)
5. **Security & Privacy** - 41 papers (8.3%)

*Note: These results are from the previous broad categorization. The new specific categories will provide much more useful insights.*

### Top Universities:
1. **UCL** - 96 papers
2. **University of Oregon** - 26 papers
3. **IIIT-H** - 23 papers
4. **Delft University of Technology** - 20 papers
5. **IIIT Hyderabad** - 19 papers

## Cost Estimation

Using GPT-4o-mini:
- ~496 papers × ~$0.001 per classification = ~$0.50 total cost
- Rate limited to avoid API limits

## Customization

### Modify Categories
Edit the `classification_categories` list in `classify_papers.py` to change or add categories.

### Adjust Batch Size
Change the `batch_size` parameter in `classify_all_papers()` to process more/fewer papers at once.

### Change Model
Modify the `model` parameter in the API call to use different OpenAI models.

## Troubleshooting

### API Key Issues
- Ensure `OPENAI_API_KEY` environment variable is set
- Check API key validity and billing status

### Rate Limits
- The script includes delays to avoid rate limits
- If you hit limits, increase the `time.sleep()` delay

### Memory Issues
- For large datasets, consider processing in smaller batches
- Monitor memory usage during processing

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test output first
3. Verify your OpenAI API key and billing status 