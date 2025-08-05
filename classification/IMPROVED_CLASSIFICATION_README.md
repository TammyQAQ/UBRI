# Improved UBRI Paper Classification System

This improved system addresses the issues with the previous classification by:

1. **Reading Excel files directly** using pandas
2. **Assigning papers to 3 most relevant categories** instead of just one
3. **Creating new categories dynamically** for papers that don't fit existing ones
4. **Reading abstracts** for better understanding of paper content
5. **Providing more granular categorization** with confidence levels

## 📁 **Updated Folder Structure**

```
classification/
├── improved_classify_papers.py      # Main improved classification script
├── improved_view_classifications.py # Enhanced results viewer
├── test_excel_reading.py           # Test Excel reading functionality
├── IMPROVED_CLASSIFICATION_README.md # This documentation
├── paper_classifications.json       # Previous classification results (legacy)
├── view_classifications.py          # Previous viewer (legacy)
├── classify_papers.py              # Previous classifier (legacy)
└── CLASSIFICATION_README.md        # Previous documentation (legacy)
```

## 🚀 **Key Improvements**

### 1. **Multi-Category Assignment**
- Each paper is assigned to **3 most relevant categories** (primary, secondary, tertiary)
- Provides better understanding of interdisciplinary papers
- Reduces the "Other" category problem

### 2. **Dynamic Category Creation**
- LLM can suggest new categories when papers don't fit existing ones
- Categories are added dynamically during processing
- More responsive to the actual content of the papers

### 3. **Excel File Reading**
- **Direct Excel file reading** using pandas
- No need to convert to JSON first
- Supports both main Excel files in the data directory

### 4. **Enhanced Analysis**
- Confidence levels for each classification
- Reasoning for classification decisions
- Better handling of non-blockchain papers

## 📊 **Enhanced Categories**

The system starts with 25 base categories and can create more:

### Core Blockchain Categories
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

### Application Categories
11. **Game Theory & Mechanism Design** - Incentive mechanisms, strategic behavior analysis
12. **Regulation & Legal Analysis** - Legal frameworks, regulatory compliance, policy analysis
13. **Security & Cryptography** - Cryptographic security, attack vectors, defense mechanisms
14. **Energy & Sustainability** - Energy consumption, green blockchain, sustainability
15. **Healthcare & Digital Health** - Medical applications, health data, pharmaceutical supply chains
16. **Supply Chain & Logistics** - Supply chain transparency, logistics optimization
17. **Governance & DAOs** - Decentralized governance, voting mechanisms, organizational structures
18. **FinTech & Traditional Finance** - Integration with traditional finance, banking applications
19. **Machine Learning & AI Applications** - AI in blockchain, predictive models, automated systems

### Emerging Categories
20. **IoT & Edge Computing** - Internet of Things, edge computing applications
21. **Metaverse & Virtual Reality** - Virtual worlds, digital assets, VR/AR applications
22. **Digital Identity & Authentication** - Identity management, authentication systems
23. **Tokenomics & Token Design** - Token economics, incentive design, token mechanics
24. **Blockchain Infrastructure & Development** - Development tools, infrastructure, platforms
25. **Academic Research & Methodology** - Research methods, academic frameworks

## 🛠️ **Setup**

1. **Install Dependencies**:
   ```bash
   pip install pandas openpyxl openai
   ```

2. **Set OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Place your updated Excel file** in `data/raw/Publications/`:
   - `UBRI Publications_.xlsx` (main file)
   - `UBRI Publication Highlights - External Share.xlsx` (alternative)

## 📋 **Usage**

### 1. Test Excel Reading (Recommended First Step)

Test that your Excel file can be read correctly:

```bash
cd classification
python test_excel_reading.py
```

This will:
- Check if Excel files exist
- Verify column structure
- Show sample data
- Confirm data extraction works

### 2. Run Improved Classification

Run the complete improved classification:

```bash
cd classification
python improved_classify_papers.py
```

This will:
- Read papers directly from Excel
- Assign each paper to 3 categories
- Create new categories as needed
- Save results with timestamps
- Generate detailed reports

### 3. View Results

Use the improved viewer to explore results:

```bash
cd classification
python improved_view_classifications.py
```

## 📈 **Output Files**

### `improved_paper_classifications_YYYYMMDD_HHMMSS.json`
Complete classification results with multi-category assignments:

```json
{
  "summary": {
    "total_papers_processed": 500,
    "blockchain_related_papers": 450,
    "not_blockchain_papers": 50,
    "classification_timestamp": "2025-01-XX...",
    "categories_used": ["DeFi", "Security", "New Category 1", ...],
    "category_distribution": {...},
    "university_distribution": {...}
  },
  "classified_papers": [
    {
      "paper_id": "paper_1",
      "title": "Example Paper",
      "authors": "Author Name",
      "university": "University Name",
      "year": 2023,
      "is_blockchain_related": true,
      "primary_category": "DeFi (Decentralized Finance)",
      "secondary_category": "Security & Cryptography", 
      "tertiary_category": "Game Theory & Mechanism Design",
      "confidence_levels": {
        "primary": "high",
        "secondary": "medium", 
        "tertiary": "low"
      },
      "new_categories_suggested": [],
      "reasoning": "This paper focuses on DeFi security..."
    }
  ]
}
```

### `improved_paper_classifications_YYYYMMDD_HHMMSS_summary.txt`
Human-readable summary with:
- Overall statistics
- Category distribution (including multi-category counts)
- University analysis
- Sample papers by category
- New categories created

## 🔍 **Enhanced Viewer Features**

The improved viewer (`improved_view_classifications.py`) provides:

1. **Summary Statistics** - Overall numbers and distributions
2. **Multi-Category Browsing** - Papers grouped by all categories
3. **University Analysis** - Detailed university-specific insights
4. **Advanced Search** - Search by title, author, or university
5. **Category Combination Analysis** - See which categories often appear together
6. **Excel Export** - Export results for further analysis

## 💰 **Cost Estimation**

Using GPT-4o-mini:
- ~500 papers × ~$0.001 per classification = ~$0.50 total cost
- Rate limited to avoid API limits
- Batch processing with intermediate saves

## 🔧 **Customization**

### Modify Base Categories
Edit the `BASE_CATEGORIES` list in `improved_classify_papers.py` to change starting categories.

### Adjust Batch Size
Change the `batch_size` parameter in `process_papers_batch()` to process more/fewer papers at once.

### Change Model
Modify the `model` parameter in the API call to use different OpenAI models.

## 🚨 **Troubleshooting**

### Excel File Issues
- Ensure Excel file is in `data/raw/Publications/`
- Check column names match expected format
- Run `test_excel_reading.py` to verify

### API Key Issues
- Ensure `OPENAI_API_KEY` environment variable is set
- Check API key validity and billing status

### Rate Limits
- The script includes delays to avoid rate limits
- If you hit limits, increase the `time.sleep()` delays

### Memory Issues
- For large datasets, reduce batch size
- Monitor memory usage during processing

## 📊 **Expected Improvements**

Compared to the previous system, you should see:

1. **Reduced "Other" category** - From ~29% to <10%
2. **Better category distribution** - More papers in relevant categories
3. **Interdisciplinary insights** - Papers appearing in multiple categories
4. **New emerging categories** - Automatically created based on content
5. **Higher confidence classifications** - Better understanding of paper content

## 🆘 **Support**

For issues or questions:
1. Run `test_excel_reading.py` first to verify setup
2. Check the troubleshooting section
3. Verify your OpenAI API key and billing status
4. Review intermediate results files for debugging 