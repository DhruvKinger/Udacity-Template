# SSBC Power BI Sales Analysis
## Learner Feedback Templates

Use the feedback under the matching result for each rubric point. Select **Pass** or **Fail** based on the review outcome. This is reusable feedback aligned with the supplied project rubric.


---

# Get and Transform Data in Power Query


## Rubric Point: Use the Power Query Editor to transform data from source files into desired table structures for a data model

**Requirement:** Use the Power Query Editor to transform data from source files into desired table structures for a data model.

### Pass

## Good work!

Your Power Query workflow prepares source data for the data model. Transforming the source files before building relationships and measures helps keep the model organized and the reporting layer easier to maintain.

Continue checking query purposes, column names, and data types, and confirm that the resulting tables contain the fields needed for analysis. Consistent transformations also make refreshing the report more reliable.

**Further reading:** [Microsoft Learn — Power Query documentation](https://learn.microsoft.com/en-us/power-query/)

### Fail

## Refine the Power Query transformations

The source files are not yet transformed into all the table structures required by the model. Review the queries and shape the data into the required fact and dimension structures.

Check column names, data types, unnecessary fields, and required merges or transformations. Apply the changes and verify that the resulting tables support relationships, measures, and visuals.

**Further reading:** [Microsoft Learn — Power Query documentation](https://learn.microsoft.com/en-us/power-query/)


## Rubric Point: The data model diagram shows a single fact table and four separate dimensions, three of which come from the currency, customer, and product source files

**Requirement:** The data model diagram shows a single fact table and four separate dimensions, three of which come from the currency, customer, and product source files.

### Pass

## Clear data model structure

Your model follows the expected structure of one fact table supported by four separate dimensions. Separating descriptive information from transactional data helps reduce duplication and supports consistent filtering and aggregation.

Keep the model diagram aligned with the transformed queries. Check that currency, customer, and product dimensions come from the specified source files and that the fourth dimension is clearly defined.

**Further reading:** [Microsoft Learn — Star schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)

### Fail

## Organize the model into fact and dimension tables

The model does not yet clearly show the required single fact table and four separate dimensions. Review the source files and Power Query outputs, then separate transactional data from descriptive attributes.

Make sure the currency, customer, and product dimensions use their specified sources and that the fourth dimension is present. Recheck the diagram so each table's role is clear.

**Further reading:** [Microsoft Learn — Star schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)


## Rubric Point: Clean data and correct formatting as needed to meet the needs of a given data model

**Requirement:** Clean data and correct formatting as needed to meet the needs of a given data model.

### Pass

## Thorough data preparation

Your data preparation accounts for the cleanliness and formatting needed for reliable reporting. Appropriate data types and consistent values help calculations behave as expected and reduce confusion in visuals.

Continue reviewing fields for inconsistent formats, unexpected values, nulls, and other issues. Ensure currency, dates, percentages, and quantities use suitable types and formats.

**Further reading:** [Microsoft Learn — Data types in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types)

### Fail

## Clean and format the data consistently

The data-cleaning or formatting steps do not yet meet the reporting needs. Review source fields for inconsistent values, incorrect data types, obvious errors, and formatting issues.

Apply corrections in Power Query and check the results after refresh. Pay particular attention to dates, currencies, quantities, and percentage-related fields so measures display correctly.

**Further reading:** [Microsoft Learn — Data types in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types)


## Rubric Point: Obvious typos and errors that might get in the way of data model/reporting functionality have been removed. The final matrix shows only three customer types for “Bar’, “Distributor” and “SSBC Tasting room”

**Requirement:** Obvious typos and errors that might get in the way of data model/reporting functionality have been removed. The final matrix shows only three customer types for “Bar’, “Distributor” and “SSBC Tasting room”.

### Pass

## Good attention to data quality

Your preparation supports consistent reporting categories. Standardizing customer-type values is important because spelling variations or unexpected categories can split totals across multiple labels and make a matrix misleading.

Check distinct customer-type values and confirm the final matrix contains only Bar, Distributor, and SSBC Tasting room. Verify that corrections do not unintentionally remove relevant records.

**Further reading:** [Microsoft Learn — Shape and combine data](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-shape-and-combine-data)

### Fail

## Standardize the customer categories

The data still contains obvious typos or customer-type values that may interfere with reporting. Inspect distinct values, correct clear errors, and ensure the final matrix shows only Bar, Distributor, and SSBC Tasting room.

Refresh the model and check that the matrix labels are consistent and totals reflect the intended categories.

**Further reading:** [Microsoft Learn — Shape and combine data](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-shape-and-combine-data)


## Rubric Point: Create a date table in PowerQuery that meets reporting requirements, including fiscal years

**Requirement:** Create a date table in PowerQuery that meets reporting requirements, including fiscal years. A date table has been created using Power Query that is set to dynamically update based on the fact table’s start and end data. The date table includes standard fields: continuous calendar dates; month name, month number, calendar years; fiscal periods, fiscal years, and fiscal quarters.

### Pass

## Effective date-table design

Your date table supports time-based reporting and includes calendar and fiscal fields. Building its range from the fact table helps it adapt when transactions are added, while continuous dates support reliable filtering.

Verify that the date range spans the earliest through latest fact date after refresh and has no gaps. Check month names and numbers, calendar years, fiscal periods, fiscal years, and fiscal quarters.

**Further reading:** [Microsoft Learn — Date tables in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)

### Fail

## Complete the dynamic date table

The date table does not yet include all required fields or update dynamically from the fact table. Base its start and end dates on the fact table’s minimum and maximum dates rather than fixed dates.

Include continuous dates, month name and number, calendar year, fiscal periods, fiscal years, and fiscal quarters. Refresh the model and verify the range and fiscal fields.

**Further reading:** [Microsoft Learn — Date tables in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)


---

# Build Relationships


## Rubric Point: Build relationships between tables

**Requirement:** Build relationships between tables. A one-to-many relationship exists between every dimension table (the one side) and the fact table (the many side). In the PBIX file, all arrows point towards the fact table.

### Pass

## Well-structured relationships

Your model uses the expected one-to-many relationship pattern between dimensions and the fact table. This allows dimensions to filter transaction records consistently and supports dependable aggregation.

Check that dimension keys are unique and match the appropriate fact-table keys. Confirm that every relationship has the correct cardinality and that arrows point toward the fact table, then test filtering in visuals.

**Further reading:** [Microsoft Learn — Manage relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships)

### Fail

## Correct the model relationships

The relationship setup does not yet meet all requirements. Create or correct relationships so each dimension is on the one side and the fact table is on the many side.

Check for duplicate dimension keys and unmatched records. Confirm that arrows point toward the fact table, then test that dimensions filter fact data correctly.

**Further reading:** [Microsoft Learn — Manage relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships)


---

# DAX Measures and Report Output


## Rubric Point: Build measures that meet key reporting requirements

**Requirement:** Build measures that meet key reporting requirements. The following measures have been created, are present on the data model, and are clearly labeled: Sales in USD ($); Cost of Sales USD ($); Gross Profit Margin (or GPM) in USD (%); Sales in CAD ($); Unit Sales by Product (%); Share of gross profit by Product type (%). The measures are calculated using a formula and not hardcoded.

### Pass

## Strong measure design

Your model includes the required measures and calculates results from the data rather than relying on hardcoded values. Clear labels make the model easier to navigate and help users understand report values.

Check each formula against its business definition and verify that measures respond to date, customer, and product filters. Use appropriate currency and percentage formats.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)

### Fail

## Complete and validate the DAX measures

One or more required measures are missing, unclear, incorrectly calculated, or hardcoded. Create and label all six required measures: Sales in USD, Cost of Sales USD, Gross Profit Margin in USD, Sales in CAD, Unit Sales by Product, and Share of Gross Profit by Product Type.

Use formulas that respond to report filters, test results in simple visuals, compare them with expected totals, and apply suitable currency or percentage formatting.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)


## Rubric Point: Create simple table, matrix and card visualizations in Power BI to test and validate the accuracy of a given data model, including measures

**Requirement:** Create simple table, matrix and card visualizations in Power BI to test and validate the accuracy of a given data model, including measures.

### Pass

## Useful validation through visuals

Your table, matrix, and card visuals provide a practical way to check whether the model and measures behave as expected. Simple visuals can reveal missing relationships, unexpected categories, incorrect aggregations, and formatting issues.

Compare totals across views, apply filters to test measure behavior, and investigate unexpected blanks or duplicated values before finalizing the report.

**Further reading:** [Microsoft Learn — Power BI visualization types](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a)

### Fail

## Use visuals to test the model

The project does not yet demonstrate enough validation using tables, matrices, and cards. Add simple visuals that expose key fields and measures, then compare results to check relationships and calculations.

Test different dimensions and filters, inspect unexpected blanks or repeated totals, and confirm that values use appropriate formats before finalizing the report.

**Further reading:** [Microsoft Learn — Power BI visualization types](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a)


## Rubric Point: The reporting layer includes two tabs

**Requirement:** The reporting layer includes two tabs. The first tab has: two card visualizations; one matrix; a text box that includes an executive summary of the key findings. On the first tab, the totals are as follows: Total Sales in USD: $167.57K; Total Sales in CAD: $224.21k; % Gross Profit Margin in USD (Year total): 14.7%. Each value is reflected using the right format and clearly labeled. Time periods use fiscal rather than calendar quarters.

### Pass

## Clear reporting and executive summary

Your first report tab brings key performance figures together. Cards make totals easy to scan, the matrix adds detail, and the executive summary explains the findings instead of leaving the audience to interpret the numbers alone.

Verify the figures are $167.57K in USD sales, $224.21K in CAD sales, and 14.7% for year-total USD gross profit margin. Check formats, labels, fiscal quarters, and consistency between the summary and visuals.

**Further reading:** [Microsoft Learn — Create reports in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-view)

### Fail

## Complete the first reporting tab

The first tab does not yet include all required visuals, summary text, or target values. Add two cards, one matrix, and an executive-summary text box, and verify the three required totals.

Use clear labels and suitable formats, use fiscal rather than calendar quarters, and ensure the executive summary matches the displayed results. Recheck values after applying filters.

**Further reading:** [Microsoft Learn — Create reports in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-view)


## Rubric Point: The second tab has a simple table with two columns showing the percentage of sales and percentage of gross profit made up by each beer produced at SSBC

**Requirement:** The second tab has a simple table with two columns showing the percentage of sales and percentage of gross profit made up by each beer produced at SSBC. These total to 100%.

### Pass

## Clear product contribution analysis

Your second tab presents each SSBC beer’s contribution to sales and gross profit in a straightforward format. Comparing both percentages can reveal differences between revenue contribution and profit contribution.

Check that all intended beers are included, each measure uses the correct overall denominator, and each column totals 100% subject to rounding. Use clear labels and percentage formatting.

**Further reading:** [Microsoft Learn — Tables in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-tables)

### Fail

## Verify product contribution percentages

The second tab does not yet meet the required structure or calculations. Create a table showing each SSBC beer’s percentage of total sales and percentage of total gross profit.

Use formula-based measures rather than hardcoded percentages. Confirm that both columns total 100% subject to rounding, and check labels, coverage, and percentage formatting.

**Further reading:** [Microsoft Learn — Tables in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-tables)


---

# Suggestions to Make the Project Stand Out


## Rubric Point: Create a matrix that shows what product type (e.g., Keg, Six-pack) is most profitable per serving for SSBC

**Requirement:** Create a matrix that shows what product type (e.g., Keg, Six-pack) is most profitable per serving for SSBC. Note that this will require an additional measure for profitability per serving. Summarize your findings below the matrix you create. This tab should be labeled “SO1 - Product Type”.

### Pass

## Useful product-type comparison

Your additional analysis compares product types by profitability per serving rather than only by total sales or gross profit. This offers a fairer comparison between formats that may provide different serving quantities.

Check that the measure uses a consistent gross-profit definition and serving quantity. Confirm that the summary matches the matrix and that the page is labeled SO1 - Product Type.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)

### Fail

## Develop the product-type profitability analysis

The optional product-type analysis does not yet provide all requested elements. Create a profitability-per-serving measure and use it in a matrix comparing formats such as kegs and six-packs.

Add a short summary identifying the most profitable type per serving, validate the calculation against sales, cost, and serving data, and label the page SO1 - Product Type.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)


## Rubric Point: Does SSBC’s beer sell differently by month?

**Requirement:** Does SSBC’s beer sell differently by month? Create a new measure called “servings sold” to help create a standard measure that accurately reflects the amount of beer sold by product type according to the number of servings provided. Use this measure to create a matrix with product name (e.g., “Bamboo Grove Grolsch”) as rows and calendar months (i.e., “January”, rather than fiscal period 5) as columns. Summarize any seasonality you notice in sales below the matrix. Label the tab “SO2 - Seasonality”. While most sales remain consistent month to month, the Imperial Poet Porter increases in popularity from Sept-January, and then drops off again by March.

### Pass

## Good seasonality analysis

Your seasonality analysis compares sales by beer and calendar month. The servings-sold measure matters because product types provide different numbers of servings, so it can represent the amount sold more accurately than simply counting units.

Check that beer names are rows and calendar month names are columns. Summarize the patterns shown, including whether Imperial Poet Porter rises from September through January and drops by March, and label the page SO2 - Seasonality.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)

### Fail

## Complete the monthly seasonality analysis

The seasonality page does not yet demonstrate all requested elements. Create a servings-sold measure that accounts for the servings provided by each product type, then build a matrix with beer names as rows and calendar months as columns.

Summarize the monthly patterns beneath the matrix, check the rubric’s observation about Imperial Poet Porter, and label the page SO2 - Seasonality. Ensure the written summary matches the data.

**Further reading:** [Microsoft Learn — Measures in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures)


---

# Overall Project Feedback

Use the feedback matching the final review result.

## Pass

### 🎉 Congratulations on passing!

Congratulations on successfully completing the SSBC Power BI project! 🎉 Your work brings together data transformation, a structured model, relationships, DAX measures, and report pages that communicate sales and profitability information. These layers need to work together for the results to be accurate and useful to a business audience.

Keep maintaining the quality of the model and report by focusing on these areas:

- **Data preparation:** Keep source queries organized, correct obvious errors, and standardize customer types so the report uses consistent categories.
- **Date and relationships:** Verify that the date table updates with the fact data, includes the required fiscal fields, and filters the fact table through the intended one-to-many relationships.
- **DAX measures:** Check that measures are formula-based, clearly labeled, formatted correctly, and responsive to report filters.
- **Report validation:** Recheck the required USD, CAD, and gross profit margin totals, and ensure the executive summary matches the displayed results.
- **Product insights:** Use product contribution and optional per-serving or seasonality analysis to explain what the data suggests, not just what the totals are.

Passing is a strong milestone. Keep testing refresh behavior and documenting the reasoning behind measures and conclusions so the model remains dependable and the report is easy for another person to understand. 🚀

## Fail

### 💪 Good effort — keep improving!

Thank you for the effort you’ve put into this project. 💪 A Power BI report depends on several connected layers, so a problem in source queries or the model can affect measures and visuals further down the line. Use the rubric feedback as a practical checklist and work through the gaps in a structured order.

Focus your revisions on these areas:

- **Power Query:** Confirm that the model contains one fact table and four dimensions, remove obvious errors, standardize the three permitted customer types, and build a dynamic date table with the required calendar and fiscal fields.
- **Relationships:** Check that every dimension has a one-to-many relationship with the fact table and that the model diagram shows the expected filter direction.
- **Measures:** Create all six required DAX measures using formulas, then validate their calculations and formatting in simple visuals.
- **Core report:** Check the two cards, matrix, executive summary, required USD and CAD totals, 14.7% gross profit margin, and use of fiscal quarters.
- **Product table:** Confirm that the second tab shows each SSBC beer’s share of sales and gross profit and that both percentage columns total 100%.
- **Optional analysis:** If completing the standout suggestions, validate profitability per serving on “SO1 - Product Type” and monthly servings patterns on “SO2 - Seasonality”.

Make one set of changes at a time, refresh the model, and retest the affected measures and visuals. Clear labels and a short explanation of the findings will help the final report communicate its results more effectively. Keep going — careful validation is a key part of building a reliable Power BI solution. 🌱

## Ungradable — Required Files Missing

### 📂 Project files required for review

The project cannot be graded fairly if the required Power BI file or supporting source materials are missing or cannot be opened. Without the PBIX file and the data needed to inspect transformations, relationships, measures, and report pages, it is not possible to verify the project against the rubric.

Before resubmitting, check that:

- The **PBIX file** is included and opens correctly in Power BI Desktop.
- The source files required for the Power Query steps are included or accessible.
- The model diagram, date table, relationships, and DAX measures can be inspected.
- Both required report tabs are present and their visuals render correctly.
- Any supporting notes needed to understand the executive summary or optional analyses are included.

This status reflects missing or inaccessible materials, not a judgement about your ability or the work you may have completed. Once the required files are available, the project can be reviewed fairly against the same criteria. 👍
