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

### Invalid Data Validation Test

To test error handling, one Product ID in a separate copy of the Sales dataset was changed from P01 to P999, which does not exist in the Products lookup table.

When the modified dataset was uploaded, the application correctly displayed the error message "Some sales records have unmatched lookup IDs." and stopped processing.

The original Sales dataset was then restored, confirming that the application could resume normal operation with valid data.

**Result: Passed**

### Missing Data Validation Test

To test how the application handles missing required data, a separate copy of the Sales dataset was created. The Product ID in cell F2 was removed, leaving the field blank.

When the modified dataset was uploaded, the application correctly displayed the error message "Some sales records have unmatched lookup IDs." and stopped processing.

The original Sales dataset was restored, and the dashboard resumed normal operation.

**Result: Passed**

### Incorrect File Format Validation Test

To test file format restrictions, a separate copy of the Sales dataset was saved as a CSV file named Sales_Format_Test.csv.

When attempting to upload this file, the Streamlit Sales uploader blocked the CSV format because it only accepts Excel (.xlsx) files.

The original Sales.xlsx file was restored, and the dashboard continued operating normally.

**Result: Passed**

### Revenue Verification Test

The Streamlit dashboard was tested using the original datasets with all filters set to All.

The displayed results were compared against the previously verified dataset totals:

- Total Revenue: $42,174,440
- Website Revenue: $27,218,880
- Brick-and-Mortar Revenue: $14,955,560
- Total Sales Records: 25,200

All four dashboard values matched the expected results exactly.

**Result: Passed**

### Data Import and Preparation

The application uses Pandas to import the five uploaded Excel and CSV datasets. Revenue values are converted to numeric format, and sales dates are converted to datetime format for analysis.

The application accepts updated files through Streamlit's file upload interface rather than relying on hardcoded revenue totals.

### Merge Validation

Three left joins connect Sales with Products, Categories, and Stores.

The application uses `validate="many_to_one"` to verify that each sales record matches no more than one record in each lookup table.

Additional validation compares the original Sales row count and total revenue with the merged dataset. If either changes unexpectedly, the application displays an error and stops processing.

| Merge Stage | Sales Records | Total Revenue |
|---|---:|---:|
| Original Sales | 25,200 | $42,174,440 |
| After Products | 25,200 | $42,174,440 |
| After Categories | 25,200 | $42,174,440 |
| After Stores | 25,200 | $42,174,440 |

All three merges preserved the original 25,200 sales records and total revenue of $42,174,440. This confirms that the joins did not duplicate or remove sales transactions or alter total revenue in the original dataset.

### Data Quality Findings

- Duplicate Sales IDs: 0
- Duplicate Survey Store ID and Year combinations: 0
- Survey records: 105
- Missing City values: 1,200 in the full dataset
- Missing City values associated with brick-and-mortar sales: 0
- Unmatched Sales Product IDs: 0
- Unmatched Sales Category IDs: 0
- Unmatched Sales Store IDs: 0

The missing City values are associated with website sales, which do not have a physical store city in the current dataset.

### Additional Validation Still Required

- Test additional missing required fields in the uploaded datasets.
- Compare Streamlit revenue calculations against Power BI results for independent verification.
- Perform the required $1,000 modified-revenue test.
