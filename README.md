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

### Dynamic Revenue Calculation Test

To verify that the dashboard dynamically calculates revenue from uploaded data, a separate copy of Sales.xlsx was created.

One revenue value was increased by $1,000, and the modified dataset was uploaded to Streamlit.

The dashboard correctly updated the following metrics:

- Total Revenue: Increased from $42,174,440 to $42,175,440.
- Website Revenue: Increased from $27,218,880 to $27,219,880.
- Brick-and-Mortar Revenue: Remained $14,955,560.
- Sales Records: Remained 25,200.

The original Sales dataset was restored after testing.

This confirms that the dashboard recalculates revenue when the underlying uploaded data changes rather than relying on hardcoded totals.

**Result: Passed**

### Power BI Revenue Verification

Revenue calculations from the Streamlit dashboard were independently compared against the original Power BI report.

The following results matched:

- Website Revenue: $27,218,880
- Brick-and-Mortar Revenue: $14,955,560
- Combined Total Revenue: $42,174,440

The Power BI revenue figures matched the Streamlit results exactly, confirming consistency between the two applications.

**Result: Passed**

### Missing Revenue Validation Test

To test how the application handles missing revenue data, a separate copy of Sales.xlsx was created, and the Revenue value in cell G2 ($6,780) was removed.

During the initial test, the dashboard continued processing and displayed an incorrect total revenue of $42,167,660 instead of $42,174,440.

To resolve this issue, additional validation was added to detect missing or invalid Revenue values and stop processing when they are found.

After implementing the fix, the modified dataset was uploaded again. The application correctly displayed the error message "Some sales records have missing or invalid revenue values." and stopped processing.

The original Sales dataset was restored, and the dashboard resumed normal operation.

**Result: Passed after correction**

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

- Continue testing other required fields for missing or invalid values as part of final application testing.

## Independent Calculation and AI Validation Tests

### Test 1: Independent Excel Revenue Calculation

**Objective:** Verify that the dashboard's total revenue matches an independently calculated result in Excel.

**Procedure:**
1. Opened the original `Sales.xlsx` dataset containing 25,200 sales records.
2. Entered the Excel formula `=SUM(G2:G25201)` in cell G25202.
3. Compared the Excel result with the total revenue reported by the Streamlit dashboard and AI Analyst.
4. Removed the temporary formula afterward to preserve the original dataset.

**Results:**

| Measurement | Result |
|---|---:|
| Total sales records | 25,200 |
| Independent Excel calculation | $42,174,440 |
| Dashboard and AI revenue | $42,174,440 |
| Difference | $0 |

**Outcome: PASS**

The independent Excel calculation matched the dashboard and AI revenue totals, confirming the accuracy of the overall revenue aggregation for the original dataset.

### Test 2: Modified Dataset and AI Recalculation

**Objective:** Verify that the dashboard and AI Analyst recalculate results when the underlying dataset changes.

**Procedure:**
1. Used a separate test copy of the Sales dataset with one Website transaction's revenue increased by $1,000.
2. Uploaded the modified Sales file along with the four unchanged supporting datasets.
3. Confirmed that the dashboard displayed the updated revenue.
4. Asked the AI Analyst: "What is E-Presso's total revenue across all sales channels?"
5. Examined the analytical tool-call log to verify the function used and its raw calculated results.
6. Restored the original dataset after testing.

**Results:**

| Measurement | Original Dataset | Modified Dataset |
|---|---:|---:|
| Total revenue | $42,174,440 | $42,175,440 |
| Website revenue | $27,218,880 | $27,219,880 |
| Brick & Mortar revenue | $14,955,560 | $14,955,560 |

**Analytical function:** `get_revenue_by_channel`

**Function arguments:** `{}`

**Verified raw result:** `total_revenue = 42175440`

**Outcome: PASS**

The dashboard and AI Analyst correctly reflected the $1,000 increase. The AI's reported figures matched the raw analytical function output, demonstrating that its numerical answers are based on the currently uploaded dataset rather than fixed or previously calculated values.

### Validation Summary

Both tests passed. Together, they provide evidence of independent calculation accuracy, approved analytical function usage, transparent tool-call logging, and recalculation when source data changes.

These tests verify the specific calculations and data changes described above; they do not establish that every possible AI question or dataset variation has been tested.

