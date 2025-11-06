# Troubleshooting Guide

This comprehensive guide addresses common issues and provides solutions for the monitoring system.

## Quick Diagnostic Commands

```bash
# Check all container status
docker compose ps

# View container logs
docker compose logs -f [service-name]

# Check resource usage
docker stats

# Verify port availability
netstat -tulpn | grep -E "(3000|9090|9187|9100|9099)"

# Test endpoint connectivity
curl -s http://localhost:9090/targets | jq .
curl -s http://localhost:3000/api/health
```

## Container Issues

### Container Won't Start

**Symptoms**: Docker compose up fails or shows restarting containers

**Diagnostic Steps**:
```bash
# Check for port conflicts
sudo netstat -tulpn | grep -E "(3000|9090|9187|9100|9099)"

# Check Docker daemon status
sudo systemctl status docker

# View detailed error logs
docker compose logs [service-name]

# Check for resource constraints
free -h
df -h
```

**Common Solutions**:

1. **Port Conflicts**:
   ```bash
   # Kill conflicting processes
   sudo kill -9 $(lsof -t -i:9090)

   # Or change ports in docker-compose.yml
   ports:
     - "9091:9090"  # Use different external port
   ```

2. **Resource Limits**:
   ```bash
   # Check memory usage
   free -h

   # Clean up unused Docker resources
   docker system prune -a
   ```

3. **Permission Issues**:
   ```bash
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### Container Restarting Loop

**Symptoms**: Container shows "Restarting" status

**Diagnostic Steps**:
```bash
# Check last logs before restart
docker compose logs [service-name] --tail 50

# Inspect container exit code
docker inspect $(docker compose ps -q [service-name]) | grep ExitCode
```

**Common Solutions**:

1. **Configuration Errors**:
   ```yaml
   # Verify environment variables in docker-compose.yml
   environment:
     - DATA_SOURCE_NAME=postgresql://user:pass@host:5432/db
   ```

2. **Missing Dependencies**:
   ```bash
   # Rebuild with --no-cache
   docker compose build --no-cache [service-name]
   ```

## Prometheus Issues

### Targets Not Showing "UP"

**Symptoms**: Prometheus targets page shows "DOWN" status

**Diagnostic Steps**:
```bash
# Test exporter endpoints directly
curl -s http://localhost:9187/metrics | head -5
curl -s http://localhost:9100/metrics | head -5
curl -s http://localhost:9099/metrics | head -5

# Check network connectivity between containers
docker compose exec prometheus ping postgres-exporter
```

**Common Solutions**:

1. **Network Issues**:
   ```yaml
   # Ensure all services use the same network
   networks:
     - monitoring
   ```

2. **Exporter Configuration**:
   ```bash
   # PostgreSQL Exporter
   # Verify database connection string
   docker compose exec postgres-exporter env | grep DATA_SOURCE

   # Test database connectivity
   psql -h host.docker.internal -U postgres -d movies_db -c "SELECT 1;"
   ```

3. **Firewall Issues**:
   ```bash
   # Check if ports are blocked
   sudo ufw status
   sudo iptables -L
   ```

### Prometheus Not Collecting Data

**Symptoms**: Prometheus runs but shows no metrics

**Diagnostic Steps**:
```bash
# Check Prometheus configuration
docker compose exec prometheus cat /etc/prometheus/prometheus.yml

# Reload configuration
curl -X POST http://localhost:9090/-/reload

# Check target configuration
curl -s http://localhost:9090/api/v1/targets
```

**Common Solutions**:

1. **Configuration Errors**:
   ```yaml
   # Correct prometheus.yml syntax
   scrape_configs:
     - job_name: 'postgres-exporter'
       static_configs:
         - targets: ['postgres-exporter:9187']
   ```

2. **Timing Issues**:
   ```yaml
   # Give exporters time to start
   depends_on:
     - prometheus
   restart: unless-stopped
   ```

## Grafana Issues

### Grafana Can't Connect to Prometheus

**Symptoms**: Grafana shows "Datasource not found" errors

**Diagnostic Steps**:
```bash
# Test Prometheus connectivity from Grafana container
docker compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Check Grafana configuration
docker compose exec grafana cat /etc/grafana/provisioning/datasources/prometheus.yml
```

**Common Solutions**:

1. **Network Configuration**:
   ```yaml
   # Ensure proper service names in datasource config
   url: http://prometheus:9090  # Not localhost
   ```

2. **Service Discovery**:
   ```bash
   # Restart Grafana after configuration changes
   docker compose restart grafana
   ```

### Dashboards Not Loading

**Symptoms**: Dashboard panels show "No data" or errors

**Diagnostic Steps**:
```bash
# Check dashboard provisioning
docker compose exec grafana ls -la /etc/grafana/provisioning/dashboards/

# Check Grafana logs for errors
docker compose logs grafana | grep -i error
```

**Common Solutions**:

1. **JSON Syntax Errors**:
   ```bash
   # Validate dashboard JSON
   cat dashboard.json | jq . >/dev/null
   ```

2. **Metric Name Issues**:
   ```bash
   # Test queries in Prometheus UI first
   # Then use in Grafana
   curl -G 'http://localhost:9090/api/v1/query' \
     --data-urlencode 'query=pg_stat_activity_count'
   ```

## PostgreSQL Exporter Issues

### Connection Refused

**Symptoms**: PostgreSQL exporter logs show connection errors

**Diagnostic Steps**:
```bash
# Test database connection
docker compose exec postgres-exporter \
  psql "$DATA_SOURCE_NAME" -c "SELECT 1;"

# Check database is accessible from container
docker compose exec postgres-exporter \
  ping -c 1 host.docker.internal
```

**Common Solutions**:

1. **Connection String**:
   ```bash
   # Update DATA_SOURCE_NAME in docker-compose.yml
   DATA_SOURCE_NAME: "postgresql://postgres:postgres@host.docker.internal:5432/movies_db?sslmode=disable"
   ```

2. **Database Permissions**:
   ```sql
   -- In PostgreSQL
   GRANT SELECT ON pg_stat_database TO postgres;
   GRANT SELECT ON pg_stat_activity TO postgres;
   ```

### Missing Metrics

**Symptoms**: Only basic metrics available, missing PostgreSQL-specific ones

**Diagnostic Steps**:
```bash
# Check available metrics
curl -s http://localhost:9187/metrics | grep pg_

# Check PostgreSQL extensions
docker compose exec postgres psql movies_db -c "\dx"
```

**Common Solutions**:

1. **Enable Extensions**:
   ```sql
   -- In PostgreSQL
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
   ```

2. **Configure Exporter**:
   ```yaml
   # Add environment variables to docker-compose.yml
   environment:
     - PG_EXPORTER_DISABLE_DEFAULT_METRICS=false
     - PG_EXPORTER_INCLUDE_DATABASE=movies_db
   ```

## Node Exporter Issues

### Missing System Metrics

**Symptoms**: Some system metrics not appearing

**Diagnostic Steps**:
```bash
# Check enabled collectors
curl -s http://localhost:9100/metrics | grep node_collector_success

# Test individual metrics
curl -s http://localhost:9100/metrics | grep node_cpu
```

**Common Solutions**:

1. **Enable Required Collectors**:
   ```yaml
   # Add to docker-compose.yml
   command:
     - '--collector.cpu'
     - '--collector.meminfo'
     - '--collector.diskstats'
     - '--collector.netdev'
   ```

2. **File System Permissions**:
   ```bash
   # Ensure proper volume mounts
   volumes:
     - /proc:/host/proc:ro
     - /sys:/host/sys:ro
     - /:/rootfs:ro
   ```

## Custom Exporter Issues

### No API Data

**Symptoms**: Custom exporter shows no metrics from external APIs

**Diagnostic Steps**:
```bash
# Check custom exporter logs
docker compose logs custom-exporter

# Test API connectivity
curl -s "http://api.openweathermap.org/data/2.5/weather?q=London&appid=$API_KEY&units=metric"
```

**Common Solutions**:

1. **API Key Issues**:
   ```bash
   # Verify API key is valid
   export API_KEY="your_key"
   curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=$API_KEY"
   ```

2. **Network Connectivity**:
   ```bash
   # Test internet access from container
   docker compose exec custom-exporter ping -c 1 8.8.8.8
   ```

3. **Rate Limiting**:
   ```python
   # Add delays in custom_exporter.py
   time.sleep(1)  # Between API calls
   ```

### Python Errors

**Symptoms**: Custom exporter crashes with Python errors

**Diagnostic Steps**:
```bash
# Check Python syntax
python3 -m py_compile custom_exporter.py

# Test script locally
python3 custom_exporter.py
```

**Common Solutions**:

1. **Missing Dependencies**:
   ```dockerfile
   # Update Dockerfile
   RUN pip install prometheus_client requests
   ```

2. **Import Errors**:
   ```python
   # Add error handling
   try:
       import requests
   except ImportError:
       print("Requests module not found")
       sys.exit(1)
   ```

## Performance Issues

### High Resource Usage

**Symptoms**: System slow, high CPU/memory usage

**Diagnostic Steps**:
```bash
# Check container resource usage
docker stats

# Monitor system resources
htop
iotop
```

**Common Solutions**:

1. **Resource Limits**:
   ```yaml
   # Add to docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '0.5'
   ```

2. **Prometheus Optimization**:
   ```yaml
   # Reduce data retention
   command:
     - '--storage.tsdb.retention.time=30d'
   ```

### Slow Query Performance

**Symptoms**: Dashboards load slowly

**Diagnostic Steps**:
```bash
# Check query performance
curl -G 'http://localhost:9090/api/v1/query_range' \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode 'start=1h' \
  --data-urlencode 'end=now'
```

**Common Solutions**:

1. **Recording Rules**:
   ```yaml
   # Add to prometheus.yml
   recording_rules:
     - name: instance:cpu_rate:5m
       expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
   ```

2. **Query Optimization**:
   ```promql
   # Use more efficient queries
   topk(10, rate(http_requests_total[5m]))
   # Instead of all requests
   rate(http_requests_total[5m])
   ```

## Data Issues

### Gaps in Metrics

**Symptoms**: Missing data points in time series

**Diagnostic Steps**:
```bash
# Check target availability
curl -s http://localhost:9090/api/v1/targets

# Check scrape intervals
curl -s http://localhost:9090/api/v1/config
```

**Common Solutions**:

1. **Scrape Configuration**:
   ```yaml
   # Adjust scrape intervals in prometheus.yml
   scrape_interval: 15s
   scrape_timeout: 10s
   ```

2. **Network Stability**:
   ```yaml
   # Add retry configurations
   scrape_configs:
     - job_name: 'node-exporter'
       scrape_interval: 15s
       static_configs:
         - targets: ['node-exporter:9100']
       metric_relabel_configs:
         - source_labels: [__address__]
           target_label: instance
           replacement: 'node-exporter'
   ```

## Alert Issues

### Alerts Not Firing

**Symptoms**: Alert rules configured but not triggering

**Diagnostic Steps**:
```bash
# Check alert rules
curl -s http://localhost:9090/api/v1/rules

# Test alert conditions
curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=cpu_usage > 80'
```

**Common Solutions**:

1. **Rule Configuration**:
   ```yaml
   # Ensure proper syntax in alert_rules.yml
   - alert: HighCPUUsage
     expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
     for: 5m
   ```

2. **Alert Manager**:
   ```yaml
   # Configure alertmanager if needed
   alerting:
     alertmanagers:
       - static_configs:
           - targets:
             - alertmanager:9093
   ```

## Getting Help

### Log Collection

```bash
# Collect all logs for analysis
docker compose logs > monitoring-logs-$(date +%Y%m%d).txt

# Collect system information
docker info > docker-info-$(date +%Y%m%d).txt
docker version > docker-version-$(date +%Y%m%d).txt
```

### Support Information

When seeking support, provide:
1. System information (OS, Docker version)
2. Configuration files (docker-compose.yml, prometheus.yml)
3. Error logs
4. Steps to reproduce
5. Expected vs actual behavior

### Recovery Procedures

```bash
# Complete system reset
docker compose down
docker system prune -a
docker compose up -d --build

# Restore from backup
# (See setup.md for backup procedures)
```

This troubleshooting guide covers the most common issues and provides systematic approaches to diagnosing and resolving problems in the monitoring system.