# Activity Performance Report

## Overview
The Activity Performance Report provides a comprehensive view of cleaning activity completion rates compared to budgeted percentages.

## Features

### 1. Metrics Displayed
- **Unit**: Location of the cleaning activity
- **Activity**: Name of the cleaning task
- **Frequency**: How often the activity should be performed (TWICE_DAILY, DAILY, EVERY_2_DAYS, WEEKLY, BIWEEKLY, MONTHLY)
- **Expected Completions**: Number of times the activity should be completed in the month based on frequency
- **Actual Completions**: Number of times the activity was actually completed (COMPLETED or VERIFIED status)
- **Actual %**: (Actual / Expected) × 100
- **Budgeted %**: Target budget percentage allocated for this activity
- **Variance**: Difference between Actual % and Budgeted % (positive = over-performing, negative = under-performing)

### 2. Calculation Logic

#### Expected Completions by Frequency:
- **TWICE_DAILY**: Days in month × 2
- **DAILY**: Days in month
- **EVERY_2_DAYS**: Days in month ÷ 2
- **WEEKLY**: 4 (approximately 4 weeks per month)
- **BIWEEKLY**: 2
- **MONTHLY**: 1

#### Actual Completions:
Counts CleaningRecord entries with:
- `activity` matching the activity
- `scheduled_date` within the selected month
- `status` in ['COMPLETED', 'VERIFIED']

#### Percentages:
- **Actual %** = (Actual Completions / Expected Completions) × 100
- **Variance** = Actual % - Budgeted %

### 3. Color Coding
- **Actual Percentage**:
  - Green (≥100%): Fully completed
  - Blue (75-99%): Good progress
  - Yellow (50-74%): Moderate progress
  - Red (<50%): Needs attention

- **Variance**:
  - Green text: Positive variance (above budget)
  - Red text: Negative variance (below budget)

## Access
- **URL**: `/cleaning/reports/performance/`
- **Permission**: Manager only
- **Links**: Available from:
  - Cleaning Records List (top right "Performance Report" button)
  - Cleaning Activities List (top right "Performance Report" button)

## Filters
- **Month**: Select from last 12 months
- **Unit**: Optional filter to show activities for a specific unit only

## Usage
1. Select the month you want to analyze
2. Optionally filter by unit
3. Review the table to identify:
   - Under-performing activities (low actual %, negative variance)
   - Over-performing activities (high actual %, positive variance)
   - Activities meeting budget targets (variance near 0)
