select count(*) as count from foxsec_metrics.baseline_sites where day = "date_format"((current_date - INTERVAL '1' DAY), '%Y-%m-%d')