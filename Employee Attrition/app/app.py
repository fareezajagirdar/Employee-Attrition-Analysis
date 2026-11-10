import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Employee Attrition Analysis & Pattern Classification",
    page_icon="📊",
    layout="wide",
)

st.title("Employee Attrition Analysis & Pattern Classification")

st.caption(
    "An interactive platform for employee attrition analysis, pattern identification, "
    "data exploration and machine learning. You can also upload other tabular datasets "
    "to explore and build classification models."
)


# ---------------- HELPER FUNCTIONS ----------------

def load_dataset(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


def prepare_features(data, target_column, dropped_columns):

    working = data.dropna(subset=[target_column]).copy()

    y = working[target_column].astype(str)

    X = working.drop(
        columns=[target_column] + dropped_columns,
        errors="ignore"
    )

    constant_columns = [
        col for col in X.columns
        if X[col].nunique(dropna=True) <= 1
    ]

    X = X.drop(columns=constant_columns, errors="ignore")

    for col in X.columns:

        if pd.api.types.is_datetime64_any_dtype(X[col]):
            X[col] = X[col].astype(str)

    numeric_columns = X.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = [
        col for col in X.columns
        if col not in numeric_columns
    ]

    transformers = []

    if numeric_columns:

        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]
        )

        transformers.append(
            ("numeric", numeric_pipeline, numeric_columns)
        )

    if categorical_columns:

        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ]
        )

        transformers.append(
            ("categorical", categorical_pipeline, categorical_columns)
        )

    if not transformers:

        raise ValueError(
            "No usable feature columns remain. Keep at least one feature column."
        )

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    return (
        working,
        X,
        y,
        preprocessor,
        numeric_columns,
        categorical_columns,
        constant_columns
    )


# ---------------- DATASET UPLOAD ----------------

uploaded = st.file_uploader(
    "Upload your dataset (CSV or Excel)",
    type=["csv", "xlsx", "xls"],
    help="Use a tabular dataset with column headings in the first row."
)

if uploaded is None:

    st.info(
        "Upload a CSV or Excel file to begin. "
        "Your original Employee Attrition CSV can also be used."
    )

    st.stop()


try:

    original_df = load_dataset(uploaded)

except Exception as error:

    st.error(f"Could not read this file: {error}")
    st.stop()


if original_df.empty:

    st.error("The uploaded file has no rows.")
    st.stop()


df = original_df.copy()

df.columns = [
    str(col).strip()
    for col in df.columns
]

df = df.loc[:, ~pd.Index(df.columns).duplicated()]

st.success(f"Loaded **{uploaded.name}** successfully.")


# ---------------- EXECUTIVE ATTRITION DASHBOARD ----------------

if "Attrition" in df.columns:

    st.divider()
    st.header("Executive Dashboard")
    st.caption(
        "Use the slicers below to filter the employee data. "
        "All dashboard KPIs, charts and the summary table update together."
    )

    dashboard_df = df.copy()

    dashboard_df["_Attrition_Label"] = (
        dashboard_df["Attrition"].fillna("Unknown").astype(str).str.strip()
    )
    dashboard_df["_Attrition_Flag"] = (
        dashboard_df["_Attrition_Label"].str.lower()
        .isin(["yes", "1", "true"])
    )

    slicer_columns = [
        ("Department", "Department"),
        ("Job Role", "JobRole"),
        ("Gender", "Gender"),
        ("Overtime", "OverTime"),
        ("Marital Status", "MaritalStatus"),
        ("Business Travel", "BusinessTravel"),
    ]

    available_slicers = [
        (label, column)
        for label, column in slicer_columns
        if column in dashboard_df.columns
    ]

    if available_slicers:
        slicer_columns_ui = st.columns(min(3, len(available_slicers)))
        selected_filters = {}

        for index, (label, column) in enumerate(available_slicers):
            with slicer_columns_ui[index % len(slicer_columns_ui)]:
                options = sorted(
                    dashboard_df[column].dropna().astype(str).unique().tolist()
                )
                selected = st.multiselect(
                    label,
                    options,
                    default=options,
                    key=f"dashboard_filter_{column}",
                )
                selected_filters[column] = selected

        for column, selected in selected_filters.items():
            if selected:
                dashboard_df = dashboard_df[
                    dashboard_df[column].fillna("Unknown").astype(str).isin(selected)
                ]
            else:
                dashboard_df = dashboard_df.iloc[0:0]

    if dashboard_df.empty:
        st.warning("No employees match the selected filters. Select one or more values in the slicers.")
    else:
        total_employees = len(dashboard_df)
        attrition_count = int(dashboard_df["_Attrition_Flag"].sum())
        active_count = total_employees - attrition_count
        attrition_rate_dashboard = (
            attrition_count / total_employees * 100 if total_employees else 0
        )
        average_age = (
            pd.to_numeric(dashboard_df["Age"], errors="coerce").mean()
            if "Age" in dashboard_df.columns else np.nan
        )

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Employees", f"{total_employees:,}")
        k2.metric("Employees Left", f"{attrition_count:,}")
        k3.metric("Active Employees", f"{active_count:,}")
        k4.metric("Attrition Rate", f"{attrition_rate_dashboard:.2f}%")
        k5.metric("Average Age", f"{average_age:.1f}" if pd.notna(average_age) else "N/A")

        st.markdown("#### Employee Attrition Visual Analysis")

        def dashboard_bar_chart(data, category, title, x_label, y_label="Employees"):
            chart_data = data.copy()
            chart_data[category] = chart_data[category].fillna("Unknown").astype(str)
            chart_data["_Attrition_Display"] = np.where(
                chart_data["_Attrition_Flag"], "Left", "Stayed"
            )
            grouped_data = pd.crosstab(
                chart_data[category], chart_data["_Attrition_Display"]
            )
            if "Left" not in grouped_data.columns:
                grouped_data["Left"] = 0
            if "Stayed" not in grouped_data.columns:
                grouped_data["Stayed"] = 0
            grouped_data = grouped_data[["Stayed", "Left"]]
            fig, ax = plt.subplots(figsize=(6.2, 3.2))
            grouped_data.plot(kind="bar", ax=ax, width=0.78)
            ax.set_title(title, fontsize=11, pad=10)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.tick_params(axis="x", rotation=30, labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            ax.legend(title="Status", fontsize=8)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        row1 = st.columns(3)

        if "Department" in dashboard_df.columns:
            with row1[0]:
                dashboard_bar_chart(
                    dashboard_df, "Department",
                    "Attrition by Department", "Department"
                )

        with row1[1]:
            fig, ax = plt.subplots(figsize=(6.2, 3.2))
            status_counts = pd.Series({
                "Stayed": active_count,
                "Left": attrition_count
            })
            ax.pie(
                status_counts.values,
                labels=status_counts.index,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"width": 0.42}
            )
            ax.set_title("Employee Status Distribution", fontsize=11, pad=10)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        if "JobRole" in dashboard_df.columns:
            with row1[2]:
                dashboard_bar_chart(
                    dashboard_df, "JobRole",
                    "Attrition by Job Role", "Job Role"
                )

        row2 = st.columns(3)

        if "Gender" in dashboard_df.columns:
            with row2[0]:
                dashboard_bar_chart(
                    dashboard_df, "Gender",
                    "Attrition by Gender", "Gender"
                )

        if "OverTime" in dashboard_df.columns:
            with row2[1]:
                dashboard_bar_chart(
                    dashboard_df, "OverTime",
                    "Attrition by Overtime", "Overtime"
                )

        if "MaritalStatus" in dashboard_df.columns:
            with row2[2]:
                dashboard_bar_chart(
                    dashboard_df, "MaritalStatus",
                    "Attrition by Marital Status", "Marital Status"
                )

        row3 = st.columns(3)

        if "Age" in dashboard_df.columns:
            with row3[0]:
                age_data = dashboard_df.copy()
                age_data["Age"] = pd.to_numeric(age_data["Age"], errors="coerce")
                age_data = age_data.dropna(subset=["Age"])
                if not age_data.empty:
                    age_data["Age Group"] = pd.cut(
                        age_data["Age"],
                        bins=[0, 25, 35, 45, 55, 100],
                        labels=["18–25", "26–35", "36–45", "46–55", "56+"],
                        include_lowest=True
                    )
                    dashboard_bar_chart(
                        age_data, "Age Group",
                        "Attrition by Age Group", "Age Group"
                    )

        if "BusinessTravel" in dashboard_df.columns:
            with row3[1]:
                dashboard_bar_chart(
                    dashboard_df, "BusinessTravel",
                    "Attrition by Business Travel", "Business Travel"
                )

        if "MonthlyIncome" in dashboard_df.columns:
            with row3[2]:
                income_data = dashboard_df.copy()
                income_data["MonthlyIncome"] = pd.to_numeric(
                    income_data["MonthlyIncome"], errors="coerce"
                )
                income_data["_Status"] = np.where(
                    income_data["_Attrition_Flag"], "Left", "Stayed"
                )
                income_summary = income_data.groupby(
                    "_Status"
                )["MonthlyIncome"].mean().reindex(["Stayed", "Left"])
                fig, ax = plt.subplots(figsize=(6.2, 3.2))
                income_summary.plot(kind="bar", ax=ax, width=0.55)
                ax.set_title("Average Monthly Income by Status", fontsize=11, pad=10)
                ax.set_xlabel("Employee Status")
                ax.set_ylabel("Average Monthly Income")
                ax.tick_params(axis="x", rotation=0, labelsize=8)
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

        if "Department" in dashboard_df.columns:
            st.markdown("#### Department Summary")
            summary_source = dashboard_df.copy()
            summary_source["_Status"] = np.where(
                summary_source["_Attrition_Flag"], "Left", "Stayed"
            )
            department_summary = summary_source.groupby("Department").agg(
                Total_Employees=("Department", "size"),
                Employees_Left=("_Attrition_Flag", "sum"),
            )
            department_summary["Attrition_Rate"] = (
                department_summary["Employees_Left"]
                / department_summary["Total_Employees"] * 100
            )
            department_summary = department_summary.reset_index()
            department_summary.columns = [
                "Department", "Total Employees", "Employees Left", "Attrition Rate (%)"
            ]
            st.dataframe(
                department_summary.style.format({"Attrition Rate (%)": "{:.2f}%"}),
                use_container_width=True,
                hide_index=True
            )

    st.divider()


# ---------------- 1. DATASET OVERVIEW ----------------

st.header("1. Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{df.shape[0]:,}")
c2.metric("Columns", f"{df.shape[1]:,}")

c3.metric(
    "Duplicate rows",
    f"{int(df.duplicated().sum()):,}"
)

c4.metric(
    "Missing cells",
    f"{int(df.isna().sum().sum()):,}"
)


with st.expander("Preview dataset", expanded=True):

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


with st.expander("Column information"):

    info_df = pd.DataFrame({

        "Column": df.columns,

        "Data type": [
            str(df[col].dtype)
            for col in df.columns
        ],

        "Non-missing values": [
            int(df[col].notna().sum())
            for col in df.columns
        ],

        "Missing values": [
            int(df[col].isna().sum())
            for col in df.columns
        ],

        "Unique values": [
            int(df[col].nunique(dropna=True))
            for col in df.columns
        ],

    })

    st.dataframe(
        info_df,
        use_container_width=True
    )


# ---------------- 2. DATA CLEANING ----------------

st.header("2. Data Cleaning")

st.write(
    "Choose cleaning actions below. "
    "The uploaded original data is not changed."
)

clean_col1, clean_col2 = st.columns(2)

with clean_col1:

    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True
    )

with clean_col2:

    remove_empty_columns = st.checkbox(
        "Remove completely empty columns",
        value=True
    )


clean_df = df.copy()

if remove_duplicates:

    clean_df = clean_df.drop_duplicates()

if remove_empty_columns:

    clean_df = clean_df.dropna(axis=1, how="all")


missing_strategy = st.selectbox(

    "Missing-value treatment for the cleaned download",

    [
        "Keep missing values",
        "Drop rows containing missing values",
        "Fill numeric with median and text with mode"
    ]

)


if missing_strategy == "Drop rows containing missing values":

    clean_df = clean_df.dropna()


elif missing_strategy == "Fill numeric with median and text with mode":

    for col in clean_df.columns:

        if clean_df[col].isna().any():

            if pd.api.types.is_numeric_dtype(clean_df[col]):

                median_value = clean_df[col].median()

                clean_df[col] = clean_df[col].fillna(
                    median_value
                )

            else:

                modes = clean_df[col].mode(dropna=True)

                fill_value = (
                    modes.iloc[0]
                    if not modes.empty
                    else "Unknown"
                )

                clean_df[col] = clean_df[col].fillna(
                    fill_value
                )


st.write(
    f"Cleaned dataset shape: "
    f"**{clean_df.shape[0]:,} rows × {clean_df.shape[1]:,} columns**"
)


st.download_button(

    "Download cleaned dataset (CSV)",

    data=clean_df.to_csv(index=False).encode("utf-8"),

    file_name="cleaned_dataset.csv",

    mime="text/csv"

)


# ---------------- 3. DATA ANALYSIS ----------------

st.header("3. Data Analysis")

analysis_df = (
    clean_df
    if not clean_df.empty
    else df
)


left, right = st.columns(2)

with left:

    selected_column = st.selectbox(
        "Choose a column to analyse",
        analysis_df.columns.tolist()
    )

with right:

    chart_type = st.selectbox(

        "Choose chart type",

        [
            "Automatic",
            "Bar chart",
            "Histogram"
        ]

    )


series = analysis_df[selected_column].dropna()


if (
    pd.api.types.is_numeric_dtype(series)
    and chart_type != "Bar chart"
):

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.hist(
        series,
        bins=20,
        edgecolor="black"
    )

    ax.set_title(
        f"Distribution of {selected_column}"
    )

    ax.set_xlabel(selected_column)
    ax.set_ylabel("Frequency")

    st.pyplot(fig)

    plt.close(fig)


else:

    counts = (
        series.astype(str)
        .value_counts()
        .head(20)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        f"Top values in {selected_column}"
    )

    ax.set_xlabel(selected_column)
    ax.set_ylabel("Count")

    plt.xticks(
        rotation=35,
        ha="right"
    )

    fig.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# Numerical relationship analysis

numeric_cols = analysis_df.select_dtypes(
    include=np.number
).columns.tolist()


if len(numeric_cols) >= 2:

    st.subheader(
        "Relationship between numerical columns"
    )

    x_col, y_col = st.columns(2)

    with x_col:

        x_axis = st.selectbox(
            "X-axis",
            numeric_cols,
            index=0
        )

    with y_col:

        y_axis = st.selectbox(
            "Y-axis",
            numeric_cols,
            index=1
        )


    fig, ax = plt.subplots(figsize=(8, 4))

    ax.scatter(
        analysis_df[x_axis],
        analysis_df[y_axis],
        alpha=0.6
    )

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)

    ax.set_title(
        f"{y_axis} vs {x_axis}"
    )

    st.pyplot(fig)

    plt.close(fig)


# Correlation matrix

if len(numeric_cols) >= 2:

    with st.expander("Numerical correlation matrix"):

        corr = analysis_df[numeric_cols].corr(
            numeric_only=True
        )

        fig, ax = plt.subplots(figsize=(9, 6))

        image = ax.imshow(
            corr,
            aspect="auto"
        )

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))

        ax.set_xticklabels(
            corr.columns,
            rotation=90
        )

        ax.set_yticklabels(
            corr.columns
        )

        ax.set_title("Correlation matrix")

        fig.colorbar(image, ax=ax)

        fig.tight_layout()

        st.pyplot(fig)

        plt.close(fig)


# ---------------- 4. EMPLOYEE ATTRITION INSIGHTS ----------------

if "Attrition" in analysis_df.columns:

    st.header("4. Employee Attrition Insights")

    attrition_series = (
        analysis_df["Attrition"]
        .astype(str)
        .str.strip()
    )

    attrition_rate = (
        attrition_series.str.lower()
        .isin(["yes", "1", "true"])
        .mean() * 100
    )

    a1, a2 = st.columns(2)

    a1.metric(
        "Attrition rate",
        f"{attrition_rate:.2f}%"
    )

    a2.metric(
        "Employees in dataset",
        f"{len(analysis_df):,}"
    )


    attrition_counts = attrition_series.value_counts()

    fig, ax = plt.subplots(figsize=(7, 3.5))

    attrition_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Employee attrition count")
    ax.set_xlabel("Attrition")
    ax.set_ylabel("Employees")

    plt.xticks(rotation=0)

    fig.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    possible_group_columns = [

        col for col in [
            "Department",
            "JobRole",
            "OverTime",
            "MaritalStatus",
            "Gender"
        ]

        if col in analysis_df.columns

    ]


    if possible_group_columns:

        group_col = st.selectbox(
            "Compare attrition by",
            possible_group_columns
        )

        grouped = pd.crosstab(
            analysis_df[group_col],
            attrition_series,
            normalize="index"
        ) * 100

        st.dataframe(
            grouped.round(2),
            use_container_width=True
        )


# ---------------- 5. CLASSIFICATION MODEL ----------------

st.header("5. Classification Model")

st.write(
    "Select the column you want the model to predict. "
    "This section is for classification, with categories such as "
    "Yes/No, Low/Medium/High, or class labels."
)


target_options = clean_df.columns.tolist()

if not target_options:

    st.error(
        "No columns are available for model training after cleaning."
    )

    st.stop()


default_target_index = (
    target_options.index("Attrition")
    if "Attrition" in target_options
    else 0
)


target_column = st.selectbox(

    "Select target column",

    target_options,

    index=default_target_index

)


target_counts = (
    clean_df[target_column]
    .dropna()
    .astype(str)
    .value_counts()
)


st.write(
    f"Target classes found: **{target_counts.shape[0]}**"
)


if target_counts.shape[0] < 2:

    st.warning(
        "The selected target needs at least two different classes."
    )

    st.stop()


if target_counts.shape[0] > 30:

    st.warning(
        "This target has more than 30 distinct values. "
        "It may be a continuous value or an ID, not a classification target."
    )

    st.stop()


candidate_drop_columns = [

    col for col in clean_df.columns
    if col != target_column

]


default_drop = [

    col for col in candidate_drop_columns

    if (
        clean_df[col].nunique(dropna=True)
        == len(clean_df)
        and len(clean_df) > 1
    )

]


drop_columns = st.multiselect(

    "Optional: exclude columns from model input (for example, employee IDs)",

    candidate_drop_columns,

    default=default_drop

)


test_size = st.slider(

    "Test data percentage",

    min_value=20,

    max_value=40,

    value=25,

    step=5

)


tree_depth = st.slider(

    "Decision Tree maximum depth",

    min_value=2,

    max_value=8,

    value=4

)


prediction_row_number = st.number_input(

    "Choose a row number for the example prediction",

    min_value=0,

    max_value=max(0, len(clean_df) - 1),

    value=0,

    step=1

)


# ---------------- MODEL TRAINING ----------------

if st.button(
    "Train and compare models",
    type="primary"
):

    try:

        (
            working,
            X,
            y,
            preprocessor,
            numeric_columns,
            categorical_columns,
            constant_columns
        ) = prepare_features(
            clean_df,
            target_column,
            drop_columns
        )


        if len(working) < 10:

            st.error(
                "At least 10 usable rows are recommended for a train/test split."
            )

            st.stop()


        class_counts = y.value_counts()

        stratify_values = (
            y
            if class_counts.min() >= 2
            else None
        )


        if stratify_values is None:

            st.warning(
                "Some classes have fewer than two rows, "
                "so the split will not be stratified."
            )


        X_train, X_test, y_train, y_test = train_test_split(

            X,

            y,

            test_size=test_size / 100,

            random_state=42,

            stratify=stratify_values

        )


        # Three classification algorithms

        models = {

            "Decision Tree": DecisionTreeClassifier(

                max_depth=tree_depth,

                class_weight="balanced",

                random_state=42

            ),

            "Random Forest": RandomForestClassifier(

                n_estimators=150,

                class_weight="balanced",

                random_state=42,

                n_jobs=-1

            ),

            "Logistic Regression": LogisticRegression(

                max_iter=1000,

                class_weight="balanced"

            )

        }


        trained_models = {}

        metric_rows = []


        for model_name, classifier in models.items():

            pipeline = Pipeline(

                steps=[

                    ("preprocessor", preprocessor),

                    ("classifier", classifier)

                ]

            )


            pipeline.fit(
                X_train,
                y_train
            )


            predictions = pipeline.predict(
                X_test
            )


            trained_models[model_name] = pipeline


            metric_rows.append({

                "Model": model_name,

                "Accuracy": accuracy_score(
                    y_test,
                    predictions
                ),

                "Precision (weighted)": precision_score(
                    y_test,
                    predictions,
                    average="weighted",
                    zero_division=0
                ),

                "Recall (weighted)": recall_score(
                    y_test,
                    predictions,
                    average="weighted",
                    zero_division=0
                ),

                "F1-score (weighted)": f1_score(
                    y_test,
                    predictions,
                    average="weighted",
                    zero_division=0
                )

            })


        metrics_df = pd.DataFrame(
            metric_rows
        ).sort_values(
            "F1-score (weighted)",
            ascending=False
        )


        st.session_state["trained_models"] = trained_models

        st.session_state["metrics_df"] = metrics_df

        st.session_state["X_test"] = X_test

        st.session_state["y_test"] = y_test

        st.session_state["target_column"] = target_column

        st.session_state["feature_columns"] = X.columns.tolist()

        st.session_state["tree_depth"] = tree_depth


        # ---------------- MODEL COMPARISON ----------------

        st.subheader("Model Comparison")

        st.dataframe(

            metrics_df.style.format({

                "Accuracy": "{:.3f}",

                "Precision (weighted)": "{:.3f}",

                "Recall (weighted)": "{:.3f}",

                "F1-score (weighted)": "{:.3f}"

            }),

            use_container_width=True

        )


        best_model_name = metrics_df.iloc[0]["Model"]

        st.success(

            f"Highest weighted F1-score in this test: "
            f"**{best_model_name}**. Results can vary with the dataset and split."

        )


        # ---------------- SELECT MODEL ----------------

        selected_model_name = st.selectbox(

            "Inspect a trained model",

            list(trained_models.keys()),

            key="inspect_model_choice"

        )


        selected_model = trained_models[selected_model_name]

        test_predictions = selected_model.predict(
            X_test
        )


        m1, m2, m3, m4 = st.columns(4)


        m1.metric(

            "Accuracy",

            f"{accuracy_score(y_test, test_predictions):.3f}"

        )


        m2.metric(

            "Precision",

            f"{precision_score(y_test, test_predictions, average='weighted', zero_division=0):.3f}"

        )


        m3.metric(

            "Recall",

            f"{recall_score(y_test, test_predictions, average='weighted', zero_division=0):.3f}"

        )


        m4.metric(

            "F1-score",

            f"{f1_score(y_test, test_predictions, average='weighted', zero_division=0):.3f}"

        )


        # ---------------- COMPACT CONFUSION MATRIX ----------------

        st.subheader("Confusion Matrix")

        class_labels = sorted(y_test.unique().tolist())

        cm = confusion_matrix(
            y_test,
            test_predictions,
            labels=class_labels
        )

        fig, ax = plt.subplots(figsize=(3.2, 2.6), dpi=120)

        image = ax.imshow(cm, cmap="Blues", aspect="equal")

        ax.set_title(
            f"{selected_model_name} - Confusion Matrix",
            fontsize=9,
            pad=8
        )
        ax.set_xlabel("Predicted label", fontsize=8)
        ax.set_ylabel("Actual label", fontsize=8)

        ax.set_xticks(range(len(class_labels)))
        ax.set_yticks(range(len(class_labels)))

        ax.set_xticklabels(
            class_labels,
            rotation=35,
            ha="right",
            fontsize=7
        )
        ax.set_yticklabels(class_labels, fontsize=7)

        threshold = cm.max() / 2 if cm.size and cm.max() > 0 else 0

        for row in range(cm.shape[0]):
            for col in range(cm.shape[1]):
                ax.text(
                    col,
                    row,
                    str(cm[row, col]),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if cm[row, col] > threshold else "black"
                )

        ax.set_xticks(
            np.arange(-0.5, len(class_labels), 1),
            minor=True
        )
        ax.set_yticks(
            np.arange(-0.5, len(class_labels), 1),
            minor=True
        )
        ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
        ax.tick_params(which="minor", bottom=False, left=False)

        fig.tight_layout(pad=1.0)

        matrix_buffer = BytesIO()
        fig.savefig(
            matrix_buffer,
            format="png",
            dpi=120,
            bbox_inches="tight",
            facecolor="white"
        )
        matrix_buffer.seek(0)
        plt.close(fig)

        matrix_left, matrix_center, matrix_right = st.columns([1, 1, 1])
        with matrix_center:
            st.image(matrix_buffer, width=360)

        # ---------------- CLASSIFICATION REPORT ----------------

        with st.expander("Detailed classification report"):

            report = classification_report(

                y_test,

                test_predictions,

                zero_division=0

            )

            st.text(report)


        # ---------------- DOWNLOAD RESULTS ----------------

        st.download_button(

            "Download model comparison (CSV)",

            data=metrics_df.to_csv(
                index=False
            ).encode("utf-8"),

            file_name="model_comparison.csv",

            mime="text/csv"

        )


        # ---------------- DECISION TREE EXPLANATION ----------------

        st.subheader("Decision Tree Explanation")


        tree_pipeline = trained_models["Decision Tree"]

        tree_classifier = tree_pipeline.named_steps["classifier"]

        fitted_preprocessor = tree_pipeline.named_steps["preprocessor"]

        feature_names = fitted_preprocessor.get_feature_names_out()


        fig, ax = plt.subplots(
            figsize=(18, 8)
        )


        plot_tree(

            tree_classifier,

            feature_names=feature_names,

            class_names=[
                str(c)
                for c in tree_classifier.classes_
            ],

            filled=True,

            rounded=True,

            max_depth=3,

            fontsize=7,

            ax=ax

        )


        ax.set_title(
            "Decision Tree (first three levels)"
        )


        fig.tight_layout()

        st.pyplot(fig)

        plt.close(fig)


        # ---------------- FEATURE IMPORTANCE ----------------

        importance = pd.DataFrame({

            "Feature": feature_names,

            "Importance": tree_classifier.feature_importances_

        }).sort_values(

            "Importance",

            ascending=False

        ).head(15)


        st.write(
            "Most influential features in the Decision Tree:"
        )


        st.dataframe(

            importance,

            use_container_width=True

        )


        # ---------------- EXAMPLE PREDICTION ----------------

        st.subheader("Example Prediction")


        safe_row_number = min(

            int(prediction_row_number),

            len(X) - 1

        )


        prediction_input = X.iloc[[
            safe_row_number
        ]]


        predicted_class = tree_pipeline.predict(
            prediction_input
        )[0]


        st.success(

            f"Decision Tree prediction for row "
            f"{safe_row_number}: **{predicted_class}**"

        )


        if hasattr(tree_pipeline, "predict_proba"):

            probabilities = tree_pipeline.predict_proba(
                prediction_input
            )[0]


            probability_df = pd.DataFrame({

                "Class": tree_classifier.classes_,

                "Probability": probabilities

            }).sort_values(

                "Probability",

                ascending=False

            )


            st.dataframe(

                probability_df,

                use_container_width=True

            )


    except Exception as error:

        st.error(
            f"Model training could not be completed: {error}"
        )

        st.info(

            "Check that the target column contains categories, "
            "remove ID-like columns, and make sure the dataset "
            "has enough rows for each class."

        )


# ---------------- FOOTER ----------------

st.caption(

    "Note: Model scores are estimates from a held-out test set. "
    "They do not guarantee the same performance on new data. "
    "Correlation and feature importance do not prove causation."

)