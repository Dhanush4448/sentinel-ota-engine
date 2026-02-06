-- CTE to group data by region and status
WITH FleetStatus AS (
    SELECT 
        region,
        update_status,
        COUNT(*) as device_count
    FROM `sentinel_project.fleet_data.ota_logs`
    GROUP BY 1, 2
)

-- Window Function to rank the most problematic regions
SELECT 
    region,
    update_status,
    device_count,
    RANK() OVER(PARTITION BY update_status ORDER BY device_count DESC) as failure_rank
FROM FleetStatus
WHERE update_status = 'Partial';