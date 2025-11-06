# PromQL Queries Reference and Optimization

This document contains all PromQL queries used in the monitoring system, along with explanations and optimization tips.

## Database Dashboard Queries

### 1. Active Connections
```promql
pg_stat_activity_count{state="active"}
```
**Purpose**: Monitor currently active database connections
**Optimization**: Use for real-time monitoring of connection load

### 2. Database Size (GB)
```promql
pg_database_size_bytes{datname="movies_db"} / 1024 / 1024 / 1024
```
**Purpose**: Track database size growth over time
**Functions Used**: Division for unit conversion
**Optimization**: Cache results for better performance

### 3. Connection Usage Rate (5min avg)
```promql
rate(pg_stat_activity_count[5m]) * 100
```
**Purpose**: Calculate rate of change in active connections
**Functions Used**: `rate()`, multiplication
**Time Filter**: `[5m]` rolling window

### 4. Query Processing Speed (QPS)
```promql
sum(rate(pg_stat_statements_calls[5m])) by (datname)
```
**Purpose**: Monitor queries per second by database
**Functions Used**: `rate()`, `sum()`, `by()`
**Optimization**: Group by database for multi-database environments

### 5. Database Uptime (hours)
```promql
(time() - pg_postmaster_start_time_seconds) / 3600
```
**Purpose**: Track database uptime since last restart
**Functions Used**: Subtraction, division, `time()` function
**Use Case**: SLA monitoring and maintenance planning

### 6. Read Operations Rate
```promql
sum(rate(pg_stat_database_blks_read[5m])) by (datname)
```
**Purpose**: Monitor disk read operations rate
**Functions Used**: `rate()`, `sum()`, `by()`
**Time Filter**: `[5m]` for recent activity

### 7. Write Operations Rate
```promql
sum(rate(pg_stat_database_blks_hit[5m])) by (datname)
```
**Purpose**: Monitor cache hit operations (effectively writes)
**Functions Used**: `rate()`, `sum()`, `by()`

### 8. Cache Hit Ratio (%)
```promql
(sum(pg_stat_database_blks_hit) / (sum(pg_stat_database_blks_hit) + sum(pg_stat_database_blks_read))) * 100
```
**Purpose**: Calculate database cache efficiency
**Functions Used**: `sum()`, division, multiplication, addition
**Optimization**: Key performance indicator for database tuning

### 9. Number of Tables
```promql
pg_stat_user_tables_count
```
**Purpose**: Track number of user tables in database
**Use Case**: Schema change monitoring

### 10. Total Rows in Database
```promql
sum(pg_stat_user_tables_n_tup_ins) - sum(pg_stat_user_tables_n_tup_del) + sum(pg_stat_user_tables_n_tup_ins)
```
**Purpose**: Estimate total rows across all user tables
**Functions Used**: `sum()`, subtraction, addition
**Note**: Approximate calculation for monitoring trends

### 11. Lock Waiting Queries
```promql
pg_stat_activity_count{waiting="true"}
```
**Purpose**: Monitor queries waiting for locks
**Use Case**: Concurrency and performance issue detection

### 12. Average Query Duration (ms)
```promql
avg(pg_stat_statements_mean_exec_time) * 1000
```
**Purpose**: Track average query execution time
**Functions Used**: `avg()`, multiplication
**Unit Conversion**: Seconds to milliseconds

## System Dashboard Queries

### 1. CPU Usage per Core (%)
```promql
100 - (avg by (instance, cpu) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
**Purpose**: Calculate CPU usage per core
**Functions Used**: `avg()`, `irate()`, `by()`, subtraction, multiplication
**Time Filter**: `[5m]` for recent CPU usage
**Optimization**: Use `irate()` for counter metrics

### 2. Load Average (1 minute)
```promql
node_load1
```
**Purpose**: System load average over 1 minute
**Use Case**: System load monitoring

### 3. Load Average (5 minute)
```promql
node_load5
```
**Purpose**: System load average over 5 minutes

### 4. Load Average (15 minute)
```promql
node_load15
```
**Purpose**: System load average over 15 minutes

### 5. Memory Usage (%)
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```
**Purpose**: Calculate percentage of memory used
**Functions Used**: Subtraction, division, multiplication
**Optimization**: More accurate than used/total ratio

### 6. Total Memory (GB)
```promql
node_memory_MemTotal_bytes / 1024 / 1024 / 1024
```
**Purpose**: Display total system memory in GB
**Unit Conversion**: Bytes to gigabytes

### 7. Available Memory (GB)
```promql
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024
```
**Purpose**: Display available memory in GB

### 8. Used Memory (GB)
```promql
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024
```
**Purpose**: Calculate used memory in GB
**Functions Used**: Subtraction, division

### 9. Free Disk Space (GB)
```promql
node_filesystem_avail_bytes{fstype!~"tmpfs|rootfs"} / 1024 / 1024 / 1024
```
**Purpose**: Show free disk space excluding temporary filesystems
**Filter**: `fstype!~"tmpfs|rootfs"` to exclude temp files
**Unit Conversion**: Bytes to gigabytes

### 10. Disk I/O Read Rate (bytes/sec)
```promql
sum(rate(node_disk_read_bytes_total[5m])) by (instance)
```
**Purpose**: Monitor disk read operations rate
**Functions Used**: `rate()`, `sum()`, `by()`

### 11. Disk I/O Write Rate (bytes/sec)
```promql
sum(rate(node_disk_written_bytes_total[5m])) by (instance)
```
**Purpose**: Monitor disk write operations rate

### 12. Network Incoming Traffic (Mbit/sec)
```promql
sum(rate(node_network_receive_bytes_total[5m])) * 8 / 1024 / 1024
```
**Purpose**: Calculate incoming network traffic in megabits
**Functions Used**: `rate()`, `sum()`, multiplication, division
**Unit Conversion**: Bytes to megabits (8 bits per byte)

### 13. Network Outgoing Traffic (Mbit/sec)
```promql
sum(rate(node_network_transmit_bytes_total[5m])) * 8 / 1024 / 1024
```
**Purpose**: Calculate outgoing network traffic in megabits

### 14. CPU Temperature (Celsius)
```promql
node_hwmon_temp_celsius
```
**Purpose**: Monitor CPU temperature
**Use Case**: Hardware health monitoring

### 15. System Uptime (days)
```promql
time() - node_boot_time_seconds / 86400
```
**Purpose**: Calculate system uptime in days
**Functions Used`: `time()`, subtraction, division
**Time Conversion**: Seconds to days

## Custom API Dashboard Queries

### 1. Average Temperature Across Cities
```promql
avg(weather_temperature_celsius)
```
**Purpose**: Calculate average temperature across all monitored cities
**Functions Used**: `avg()`

### 2. Temperature by City (Time Series)
```promql
weather_temperature_celsius
```
**Purpose**: Display temperature trends for each city
**Filter Usage**: Use with city_selector variable

### 3. Humidity vs Temperature Correlation
```promql
weather_humidity_percent / weather_temperature_celsius
```
**Purpose**: Calculate humidity-to-temperature ratio
**Functions Used**: Division
**Use Case**: Weather pattern analysis

### 4. Exchange Rate Volatility (5m rate of change)
```promql
rate(exchange_rate[5m]) * 100
```
**Purpose**: Calculate exchange rate volatility as percentage
**Functions Used**: `rate()`, multiplication
**Time Filter**: `[5m]` for recent volatility

### 5. USD to EUR Exchange Rate
```promql
exchange_rate{from_currency="USD", to_currency="EUR"}
```
**Purpose**: Display specific exchange rate
**Filter Usage`: Currency pair selection

### 6. GitHub Stars Growth Rate
```promql
increase(github_repository_stars[1h])
```
**Purpose**: Calculate star growth over last hour
**Functions Used**: `increase()`
**Time Filter**: `[1h]` for hourly growth

### 7. Top Repositories by Stars
```promql
topk(5, github_repository_stars)
```
**Purpose**: Show top 5 repositories by star count
**Functions Used**: `topk()`
**Use Case**: Popular repository identification

### 8. API Request Success Rate
```promql
(sum(rate(api_requests_total{status="success"}[5m])) / sum(rate(api_requests_total[5m]))) * 100
```
**Purpose**: Calculate API success rate percentage
**Functions Used**: `rate()`, `sum()`, division, multiplication
**Filter**: `status="success"` for successful requests

### 9. Average API Response Time
```promql
avg(api_response_time_seconds) by (api_name)
```
**Purpose**: Show average response time by API
**Functions Used**: `avg()`, `by()`
**Use Case**: API performance monitoring

### 10. Temperature Anomaly Detection
```promql
weather_temperature_celsius - avg_over_time(weather_temperature_celsius[1h])
```
**Purpose**: Detect temperature anomalies from 1-hour average
**Functions Used**: `avg_over_time()`, subtraction
**Time Filter`: `[1h]` for baseline comparison

### 11. GitHub Issues to Stars Ratio
```promql
github_repository_issues / github_repository_stars * 100
```
**Purpose**: Calculate issues-to-stars ratio as percentage
**Functions Used**: Division, multiplication
**Use Case**: Repository health indicator

### 12. Pressure Trend (1h derivative)
```promql
deriv(weather_pressure_hpa[1h])
```
**Purpose**: Calculate pressure change rate over 1 hour
**Functions Used**: `deriv()`
**Time Filter**: `[1h]` for trend analysis

## Query Optimization Tips

### 1. Use Appropriate Functions

**For Counters**: Use `rate()` or `increase()`
```promql
# Good
rate(http_requests_total[5m])

# Avoid
http_requests_total
```

**For Gauges**: Use `avg()`, `max()`, `min()`
```promql
# Good
avg(cpu_usage)

# Avoid unnecessary functions for simple values
```

### 2. Time Range Selection

**Short-term monitoring**: Use 1-5 minute ranges
```promql
rate(cpu_usage[1m])  # Real-time
```

**Long-term trends**: Use 1-hour ranges
```promql
avg_over_time(cpu_usage[1h])  # Hourly average
```

### 3. Efficient Filtering

**Filter early**:
```promql
# Good
sum(rate(http_requests_total{status="200"}[5m]))

# Less efficient
sum(rate(http_requests_total[5m])) by (status)
```

**Use labels effectively**:
```promql
# Good
cpu_usage{instance="web-server-1"}

# Avoid complex regex when simple labels exist
```

### 4. Aggregation Best Practices

**Use appropriate grouping**:
```promql
# Group by meaningful labels
sum(rate(http_requests_total[5m])) by (method, status)

# Avoid over-grouping
```

**Use `by()` for efficient aggregation**:
```promql
# Efficient
sum by (instance) (cpu_usage)

# Less efficient for large datasets
group by (instance) (sum(cpu_usage))
```

### 5. Performance Considerations

**Avoid complex calculations in dashboards**:
```promql
# Pre-calculate in recording rules if possible
# Simple operations are preferred for real-time queries
```

**Use recording rules for complex queries**:
```yaml
# In prometheus.yml
recording_rules:
  - name: instance:cpu_usage:rate5m
    expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### 6. Memory Efficiency

**Use `topk()` for large result sets**:
```promql
# Show only top results
topk(10, http_requests_total)

# Instead of all results which may be expensive
```

**Limit time ranges for large datasets**:
```promql
# Specify reasonable time ranges
rate(http_requests_total[5m])  # Good
rate(http_requests_total[1h])  # May be expensive for high-cardinality metrics
```

## Alert Query Optimization

### 1. Alert Threshold Design

**Use appropriate for durations**:
```promql
# Good - sustained issues
cpu_usage > 80 for 5m

# Avoid - too sensitive for transient spikes
cpu_usage > 80 for 1m
```

### 2. Alert Performance

**Keep alert queries simple**:
```promql
# Simple and fast
rate(http_requests_total[5m]) < 100

# Complex queries in alerts can impact performance
```

### 3. Label Usage in Alerts

**Use informative labels**:
```promql
# Good for alert routing
alert: HighCPUUsage
expr: cpu_usage{job="node-exporter"} > 80
labels:
  severity: warning
  instance: "{{ $labels.instance }}"
```

## Query Testing and Validation

### 1. Use Prometheus Query UI

Test queries at http://localhost:9090/graph:
- Verify syntax
- Check result sets
- Validate performance

### 2. Query Performance Analysis

Monitor query execution time:
```bash
# Check Prometheus logs for slow queries
docker compose logs prometheus | grep "query_slow"
```

### 3. Data Validation

Verify query accuracy:
```promql
# Cross-check with multiple approaches
# Example: CPU usage calculation
# Method 1
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Method 2 (if available)
cpu_usage_percentage
```

This query reference provides a comprehensive foundation for understanding and optimizing the monitoring system's PromQL queries.