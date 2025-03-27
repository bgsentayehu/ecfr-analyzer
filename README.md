#  eCFR Analyzer

Analyze the Electronic Code of Federal Regulations (eCFR) by agency, using publicly available APIs.  
This project counts the number of words associated with each federal agency across CFR titles, including tracking changes over time.

---

##  Features

- Word count per federal agency using CFR metadata
- Historical trend tracking (by agency and date)
- Interactive frontend with bar chart, table, and CSV download
- Built using Python, Streamlit, and the eCFR public API

---

## Project Structure
##  Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecfr-analyzer.git
   cd ecfr-analyzer
2. **Install Dependencies**
   ```bash
   pip install requests lxml streamlit pandas
3. **Generate back end**
   ```bash
   python ecfr_agency_wordcount.py
   python ecfr_historical_trends.py
4. **Launch the front end**
   ```bash
   streamlit run app.py
# Data Source 
All data is pulled directly from the eCFR public API at https://www.ecfr.gov/developers/documentation/api/v1#/.





   
