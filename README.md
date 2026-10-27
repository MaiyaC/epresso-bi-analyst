# E-Presso Business Intelligence and AI Analytics

## Project Overview

This project is a Python-based business intelligence application developed using Streamlit. It analyzes E-Presso sales and business performance through interactive visualizations, revenue calculations, and data filtering.

The application is designed to help users explore sales trends, compare website and brick-and-mortar revenue, and evaluate performance across product categories and years.

The project also includes the development of an analytical assistant that will allow users to ask business questions and receive answers based on calculations performed using the uploaded datasets.

## Technologies Used

- Python
- Streamlit
- Pandas
- Altair
- Microsoft Excel and CSV datasets
- GitHub
- Streamlit Community Cloud

## Data Sources and Dataset Structure

The application uses five E-Presso datasets. The Sales, Products, and Categories tables were exported from Microsoft Access into Excel format. The Stores and Survey datasets were provided as CSV and Excel files.

The following table describes the structure and grain of each original dataset.

| Dataset | Rows | Columns | One Row Represents | Key | Contains Revenue? |
|---|---:|---:|---|---|---|
| Sales | 25,200 | 7 | One sales transaction | Sales ID | Yes |
| Products | 20 | 2 | One product | Product ID | No |
| Categories | 5 | 2 | One product category | Category ID | No |
| Stores | 21 | 9 | One store or sales channel location | ID | No |
| Survey | 105 | 5 | One store-year survey record | Store ID + Year | No |

These row counts reflect the original datasets used during development. The application is designed to accept updated files, so row counts may change when new datasets are uploaded.

## Dataset Relationships

The Sales table is the primary transaction-level dataset. Python uses Pandas to connect the supporting lookup tables to Sales through the following relationships:

- Sales to Products: `Product ID`
- Sales to Categories: `Category ID`
- Sales to Stores: `Store ID` in Sales matches `ID` in Stores.

All three relationships use left joins with `many_to_one` validation to prevent duplicate lookup records from multiplying sales transactions.

The Survey dataset is maintained separately from the transaction-level Sales data. Each Store ID and Year combination was verified to be unique in the original Survey dataset, with zero duplicate combinations.

For survey-based revenue analysis, sales must first be aggregated to the appropriate store-year level before being combined with survey results. This avoids duplicating revenue.

## Data Validation and Merge Checks

### Data Import and Preparation

The application uses Pandas to import the five uploaded Excel and CSV datasets. Revenue values are converted to numeric format, and sales dates are converted to datetime format for analysis.

The application accepts updated files through Streamlit's file upload interface rather than relying on hardcoded revenue totals.

### Merge Validation

Three left joins connect Sales with Products, Categories, and Stores.

The application uses `validate="many_to_one"` to verify that each sales record matches no more than one record in each lookup table.

Additional validation compares the original Sales row count and total revenue with the merged dataset. If either changes unexpectedly, the application displays an error and stops processing.

| Validation Measure | Original Sales | After All Three Merges |
|---|---:|---:|
| Sales records | 25,200 | 25,200 |
| Total revenue | $42,174,440 | $42,174,440 |

These values reflect the original E-Presso dataset. Individual before-and-after results for each merge still need to be recorded.

### Data Quality Findings

- Duplicate Sales IDs: 0
- Duplicate Survey Store ID and Year combinations: 0
- Survey records: 105
- Missing City values: 1,200 in the full dataset
- Missing City values associated with brick-and-mortar sales: 0

The missing City values are associated with website sales, which do not have a physical store city in the current dataset.

### Additional Validation Still Required

- Record row counts and revenue totals after each individual merge.
- Verify that all Sales foreign keys match their corresponding lookup tables.
- Test how the application handles missing or invalid uploaded data.
- Complete independent revenue calculations and compare results with Power BI.
- Perform the required $1,000 modified-revenue test.
