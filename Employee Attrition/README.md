# Employee Attrition Analysis & Pattern Classification

## 1. Project Overview

Employee Attrition Analysis & Pattern Classification is a machine learning-based web application developed using Python and Streamlit.

The application helps analyze employee attrition patterns, explore workforce data, visualize important insights, and build machine learning classification models to predict employee attrition.

It provides an interactive dashboard where users can upload datasets, explore data, analyze patterns, and evaluate machine learning models.

## 2. Dataset

The project primarily uses the IBM HR Analytics Employee Attrition dataset.

Expected dataset filename:

`WA_Fn-UseC-HR-Employee-Attrition.csv`

Users can upload their own compatible CSV or Excel datasets through the application.

The available analysis and machine learning features depend on the columns and structure of the uploaded dataset.

## 3. Key Features

- Interactive employee analytics dashboard.
- Dataset upload using CSV and Excel formats.
- Dataset overview and data cleaning.
- Employee attrition analysis and visualizations.
- Department-wise employee analysis.
- Interactive filters and slicers.
- Machine learning classification using:
  - Decision Tree
  - Random Forest
  - Logistic Regression
- Model performance comparison.
- Confusion matrix and classification report.
- Feature importance visualization.
- Example employee attrition prediction.
- Downloadable analysis results.

## 4. Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- SQL

## 5. Project Structure

```text
Employee Attrition/
│
├── app/
│   └── app.py
│
├── Results/
│   ├── 01_Attrition_Analysis.png
│   ├── learned_decision_rules.txt
│   └── model_metrics.csv
│
├── sql/
│   ├── Analysis_queries.sql
│   └── attrition_analysis.sql
│
├── requirements.txt
└── README.md
```

## 6. Requirements

Python and the libraries listed in `requirements.txt` are required to run the application.

Install the dependencies using:

```bash
pip install -r requirements.txt
```

## 7. How to Run

1. Open Command Prompt or the VS Code terminal.
2. Navigate to the project directory.
3. Install the required libraries.
4. Run the following command:

```bash
python -m streamlit run app/app.py
```

5. The application will open in your web browser.
6. Upload a compatible CSV or Excel dataset to begin the analysis.

## 8. Results

The application generates interactive visualizations, employee attrition insights, machine learning model evaluation metrics, confusion matrices, and classification reports.

Users can also download supported analysis results from the application.

## 9. Important Note

This project is developed for educational and academic purposes. The predictions are intended for demonstration and decision-support learning, not as the sole basis for actual employee-related decisions.