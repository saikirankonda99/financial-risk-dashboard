SELECT
    calc_date,
    method,
    portfolio_value,
    var_dollar,
    es_dollar,
    var_dollar / portfolio_value AS var_pct,
    es_dollar / portfolio_value  AS es_pct
FROM analytics.daily_var
WHERE calc_date >= current_date - INTERVAL '90 days'
ORDER BY calc_date, method;
