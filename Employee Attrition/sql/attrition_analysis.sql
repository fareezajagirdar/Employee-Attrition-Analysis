-- Employee Attrition Analysis: starter SQL queries
-- Import the dataset into a table named employee_attrition first.
-- Adjust table/column quoting to match your SQL database.

-- 1. Overall employee count and attrition count
SELECT
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_percent
FROM employee_attrition;

-- 2. Attrition rate by department
SELECT
    Department,
    COUNT(*) AS employee_count,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_percent
FROM employee_attrition
GROUP BY Department
ORDER BY attrition_rate_percent DESC;

-- 3. Attrition by overtime
SELECT
    OverTime,
    COUNT(*) AS employee_count,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_percent
FROM employee_attrition
GROUP BY OverTime
ORDER BY attrition_rate_percent DESC;

-- 4. Attrition by job satisfaction
SELECT
    JobSatisfaction,
    COUNT(*) AS employee_count,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left
FROM employee_attrition
GROUP BY JobSatisfaction
ORDER BY JobSatisfaction;
