-- Query 1: Overall Employee Attrition
-- Purpose: To calculate total employees, employees who left,
-- employees who stayed, and the overall attrition rate.

SELECT
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    SUM(CASE WHEN Attrition = 'No' THEN 1 ELSE 0 END) AS employees_stayed,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    ) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`;

-- Query 2: Department-wise Employee Attrition
-- Purpose: To identify which department has the highest attrition rate.

SELECT
    Department,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    ) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY Department
ORDER BY attrition_rate DESC;

-- Query 3: Overtime vs Employee Attrition
-- Purpose: To compare attrition rates of employees who work overtime and those who do not.

SELECT
    OverTime,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    ) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY OverTime
ORDER BY attrition_rate DESC;

-- Query 4: Job Satisfaction vs Employee Attrition
-- Purpose: To analyse attrition based on job satisfaction levels.

SELECT
    JobSatisfaction,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY JobSatisfaction
ORDER BY JobSatisfaction;

-- Query 5: Age Group-wise Employee Attrition
-- Purpose: To identify attrition rates across different age groups.

SELECT
    CASE
        WHEN Age < 25 THEN 'Below 25'
        WHEN Age BETWEEN 25 AND 34 THEN '25-34'
        WHEN Age BETWEEN 35 AND 44 THEN '35-44'
        WHEN Age BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55 and Above'
    END AS age_group,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY age_group
ORDER BY attrition_rate DESC;

-- Query 6: Years at Company vs Employee Attrition
-- Purpose: To analyse attrition based on employees' years of service.

SELECT
    CASE
        WHEN YearsAtCompany BETWEEN 0 AND 2 THEN '0-2 Years'
        WHEN YearsAtCompany BETWEEN 3 AND 5 THEN '3-5 Years'
        WHEN YearsAtCompany BETWEEN 6 AND 10 THEN '6-10 Years'
        ELSE 'Above 10 Years'
    END AS experience_group,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY experience_group
ORDER BY attrition_rate DESC;

-- Query 7: Job Role-wise Employee Attrition
-- Purpose: To identify which job roles have higher attrition rates.

SELECT
    JobRole,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY JobRole
ORDER BY attrition_rate DESC;

-- Query 8: Education Field-wise Employee Attrition
-- Purpose: To compare attrition rates across different education fields.

SELECT
    EducationField,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY EducationField
ORDER BY attrition_rate DESC;

-- Query 9: Monthly Income vs Employee Attrition
-- Purpose: To analyse attrition across different salary groups.

SELECT
    CASE
        WHEN MonthlyIncome < 3000 THEN 'Below 3000'
        WHEN MonthlyIncome BETWEEN 3000 AND 5999 THEN '3000-5999'
        WHEN MonthlyIncome BETWEEN 6000 AND 9999 THEN '6000-9999'
        ELSE '10000 and Above'
    END AS salary_group,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY salary_group
ORDER BY attrition_rate DESC;

-- Query 10: Marital Status vs Employee Attrition
-- Purpose: To compare attrition rates based on marital status.

SELECT
    MaritalStatus,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attrition_rate
FROM `wa_fn-usec_-hr-employee-attrition`
GROUP BY MaritalStatus
ORDER BY attrition_rate DESC;