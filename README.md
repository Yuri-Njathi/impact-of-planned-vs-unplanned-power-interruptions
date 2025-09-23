# Probability of a blackout in Kenya

Abstract
------------------------------------------
Reliable electricity is essential for Kenya’s economic growth, social well-being, and technological development. However, both planned and unplanned power interruptions continue to affect households and businesses nationwide. This mini project investigates which counties have the greatest impact on grid reliability during planned outages and how this information can help households plan around electricity disruptions.

Using two years of scheduled maintenance blackout records from Kenya Power, collected via web-scraping and text extraction, combined with census data on electrified households and national reliability indicators (SAIDI, SAIFI, CAIDI) from the Energy and Petroleum Regulatory Authority, the study analyzed the frequency, duration, and geographic distribution of planned outages.

Key insights include: the average Kenyan household experiences 3.8 outages per year, each lasting 2 and 1/2 hours; blackout risk varies widely across counties; and counties around Nairobi account for a disproportionately large share of planned interruptions. Preliminary maps suggest that these geographic disparities could guide more targeted maintenance planning.

Understanding both the probability of outages and their household impact provides actionable guidance for Kenya Power, policymakers, and residents. By prioritizing investments and optimizing outage schedules, it is possible to reduce the disruption caused by blackouts, strengthen grid resilience, and help households better anticipate and manage electricity interruptions.

<img width="873" height="1964" alt="Spider concept map (1)" src="https://github.com/user-attachments/assets/347c237e-077a-4d1f-94af-2c7199ae3a56" />



Access
------------------------------------------
Workflow Steps

1. Source Identification
- Identify Kenya Power PDF notices of planned outages.

2. Data Extraction
- Web-scraping the PDFs using Python + BeautifulSoup/requests [notebook](https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/notebooks/download-kplc-interruptions-data.ipynb).
- Text extraction from PDFs (parse dates, counties, outage times, and locations) [notebook](https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/notebooks/read-save-kplc-interruptions-data.ipynb).

3. Data Cleaning & Structuring
- Standardize date/time formats.
- Normalize county names and merge duplicates, use county code to merge counties.
- Structure into a table: `County` | `Date` | `Start Time` | `End Time` | `Locations`.
  [notebook](https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/notebooks/quality-check-kplc-interruptions-data.ipynb)

4. Combine with Census Data
- Merge county electrified household counts extracted from the 2019 Census data [notebook](https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/notebooks/merge-census-data.ipynb).

5. Combine with Reliability Data
- Integrate national SAIDI, SAIFI, CAIDI indicators extracted from EPRA reports [23/24](https://www.epra.go.ke/sites/default/files/2024-10/EPRA%20Energy%20and%20Petroleum%20Statistics%20Report%20FY%202023-2024_2.pdf) and [24/25](https://www.epra.go.ke/bi-annual-energy-petroleum-statistics-report-20242025).
6. Analysis
- Count planned outages per county and per month.
- Compute blackout occurences per county.
- Compare planned vs unplanned interruptions.

7. Visualization & Storytelling
- National-level reliability summary.

8. Insights & Recommendations
- Highlight high-risk counties.
- Present findings in notebook and github documentation.

The data I have used was sourced from KPLC's website as I couldn't access the data from Kenya Power posted on x.com (twitter), they post as soon as an interruption is about to occur (images to be collected and placed in a Kenya-Power-interruptions-folder). The unnecessaryy but web scraped pdfs were deleted then using PyPDF2 extracted the text. Using regex code was able to get the structured test into usable formats.


Assess
----------------------------------------
Using OSMnx try to plot Kenya's population per county and subcounty, Kenya's household density per location, outages plots 


Address
-----------------------------
Try and predict the SAIDI  for July 2024 to present.



## Framework Structure

The template provides a structured approach to implementing the Fynesse framework:

```
fynesse/
├── access.py      # Data access functionality
├── assess.py      # Data assessment and quality checks
├── address.py     # Question addressing and analysis
├── config.py      # Configuration management
├── defaults.yml   # Default configuration values
└── tests/         # Comprehensive test suite
    ├── test_access.py
    ├── test_assess.py
    └── test_address.py
```
