# Project Description

Access
------------------------------------------
The data I have used was sourced from KPLC's website as I couldn't access the data from Kenya Power posted on x.com (twitter), they post as soon as an interruption is about to occur (images to be collected and placed in a Kenya-Power-interruptions-folder). The unnecessaryy but web scraped pdfs were deleted then using PyPDF2 extracted the text. Using regex code was able to get the structured test into usable formats.


EPRA's reports, Kenya's Census data and any credible transformer related data.


Much of the data is in image and pdf format and will thus need extraction either manually or using a tool of some kind.


EPRA's reports are available and are where I will extract the SAIDI per month.


The census data is in pdf format and I'm currently unsure how to extract it but will find my way.


May use Kenya solar irradiation data


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
