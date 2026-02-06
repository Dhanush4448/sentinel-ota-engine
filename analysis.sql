WITH FleetStatus AS (
    SELECT 
        region,
        update_status,
        COUNT(*) as device_count,
        SUM(COUNT(*)) OVER(PARTITION BY region) as total_region_devices
    FROM `sentinel_project.fleet_data.ota_logs`
    GROUP BY 1, 2
)
SELECT 
    region,
    update_status,
    device_count,
    -- Calculate the failure rate to justify the 65-75% success narrative
    ROUND((device_count / total_region_devices) * 100, 2) as failure_rate_percentage,
    RANK() OVER(PARTITION BY update_status ORDER BY device_count DESC) as failure_rank
FROM FleetStatus
WHERE update_status = 'Partial';