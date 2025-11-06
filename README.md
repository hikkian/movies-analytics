# Complete Monitoring System

A comprehensive monitoring solution with Prometheus, Grafana, and three specialized exporters for database performance, system metrics, and external API monitoring.

## Architecture

This monitoring system includes:

- **Prometheus Server** (Port 9090) - Metrics collection and storage
- **Grafana** (Port 3000) - Visualization and dashboarding
- **PostgreSQL Exporter** (Port 9187) - Database performance metrics
- **Node Exporter** (Port 9100) - System resource monitoring
- **Custom Exporter** (Port 9099) - External API data collection

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database running on localhost:5432 with database `movies_db`
- OpenWeatherMap API key (optional, for weather data)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd movies-analytics
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenWeatherMap API key
   ```

3. **Start the monitoring stack**:
   ```bash
   docker compose up -d
   ```

4. **Verify all services are running**:
   ```bash
   docker compose ps
   ```

### Access Points

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **PostgreSQL Exporter**: http://localhost:9187/metrics
- **Node Exporter**: http://localhost:9100/metrics
- **Custom Exporter**: http://localhost:9099/metrics

## Dashboards

### 1. PostgreSQL Database Performance (30 Points)

**Metrics Collected**:
- Active connections and connection usage rate
- Database size (GB) and growth trends
- Query processing speed (QPS)
- Read/write operations rates
- Cache hit ratio
- Lock waiting queries
- Average query duration
- Total tables and row counts
- Database uptime

**Alerts**:
- High connection usage (>80%)
- Low cache hit ratio (<90%)
- Rapid database size growth (>1GB/hour)

### 2. System Performance Monitoring (25 Points)

**Metrics Collected**:
- CPU usage per core and load averages (1m, 5m, 15m)
- Memory usage (total, available, used) in GB
- Disk I/O rates (read/write bytes/sec)
- Network traffic (incoming/outgoing Mbit/sec)
- Free disk space and filesystem usage
- CPU temperature
- System uptime

**Alerts**:
- High CPU usage (>80% for 5min)
- High memory usage (>90% for 3min)
- Low disk space (<10% free)
- High load average (>2x CPU cores)

### 3. External API Monitoring (45 Points)

**Data Sources**:
- OpenWeatherMap API: Temperature, humidity, pressure for 5 cities
- Exchange Rate API: USD to EUR, GBP, JPY, CAD, AUD
- GitHub API: Repository stars, forks, issues, commits

**Metrics Collected**:
- Weather data with anomaly detection
- Exchange rate volatility analysis
- GitHub repository statistics
- API success rates and response times
- Total API requests and error tracking

**Alerts**:
- API success rate below 95%
- High API response time (>5 seconds)
- Temperature anomalies (>10°C deviation)
- High exchange rate volatility (>5% change)

## Features

### Global Variables (Dashboard Filters)

Each dashboard includes configurable global variables:
- **Database Dashboard**: Database name selector, time range selector
- **System Dashboard**: Instance selector, CPU core selector, network interface selector
- **Custom Dashboard**: City selector, currency pair selector, GitHub repository selector

### PromQL Queries

All dashboards include 10+ PromQL queries with mathematical functions:
- **60%+ queries use functions**: `rate()`, `avg()`, `sum()`, `increase()`, `deriv()`, `avg_over_time()`
- **Time filters**: `[5m]`, `[1h]` intervals
- **Grouping and aggregation**: `by()`, `topk()`, mathematical operations

### Visualization Types

Each dashboard uses 4+ different visualization types:
- Time Series (trends over time)
- Gauge (current values with thresholds)
- Stat (key performance indicators)
- Pie Chart (proportional data)
- Heatmap (density distributions)
- Bar Chart (comparisons)

## Configuration Files

### Core Configuration
- `docker-compose.yml` - Multi-container orchestration
- `prometheus.yml` - Prometheus server configuration
- `alert_rules.yml` - Alert rules for all dashboards

### Custom Exporter
- `custom_exporter.py` - Python script for external API data collection
- `Dockerfile.custom_exporter` - Container build configuration

### Grafana Configuration
- `grafana/provisioning/datasources/prometheus.yml` - Data source configuration
- `grafana/provisioning/dashboards/dashboard.yml` - Dashboard provisioning
- `grafana/provisioning/dashboards/dashboards/` - Dashboard JSON exports

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# OpenWeatherMap API Key for weather data
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Custom exporter update interval (seconds)
UPDATE_INTERVAL=20
```

## Load Testing

For system dashboard validation, perform load testing:

```bash
# Install stress-ng (if not available)
sudo apt-get install stress-ng

# Run stress test
stress-ng --cpu 4 --io 4 --vm 2 --vm-bytes 128M --timeout 5m

# Monitor the effects in the System Performance Dashboard
```

## Requirements Compliance

This implementation satisfies all 12 assignment requirements for each dashboard:

✅ **Requirement 1**: Prometheus and Grafana connected
✅ **Requirement 2**: All exporters running on specified ports
✅ **Requirement 3**: 10+ PromQL queries per dashboard
✅ **Requirement 4**: 60%+ queries using functions/filters
✅ **Requirement 5**: All queries tested and functional
✅ **Requirement 6**: 1-5 hours data collection capability
✅ **Requirement 7**: 10+ visualizations with 4+ types per dashboard
✅ **Requirement 8**: Global filters working across panels
✅ **Requirement 9**: Alert rules configured per dashboard
✅ **Requirement 10**: Real-time data updates (30s refresh)
✅ **Requirement 11**: Complete GitHub repository with all files
✅ **Requirement 12**: Defense demonstration ready

## Troubleshooting

### Common Issues

1. **Containers won't start**:
   ```bash
   docker compose logs [service-name]
   # Check for port conflicts or missing dependencies
   ```

2. **PostgreSQL Exporter can't connect**:
   - Ensure PostgreSQL is running on localhost:5432
   - Verify database name is `movies_db`
   - Check credentials in docker-compose.yml

3. **Custom Exporter shows no data**:
   - Verify OpenWeatherMap API key in .env file
   - Check internet connectivity for external API calls

4. **Grafana can't connect to Prometheus**:
   - Ensure both containers are running
   - Check network configuration in docker-compose.yml

### Performance Tips

- Prometheus retention: 200 hours (configurable in prometheus.yml)
- Scrape intervals: 15-20 seconds for optimal performance
- Dashboard refresh: 30 seconds (balanced for real-time vs load)

## Documentation

- `docs/setup.md` - Detailed installation and configuration guide
- `docs/queries.md` - Complete PromQL query reference and optimization
- `docs/troubleshooting.md` - Common issues and solutions

## Support

For technical issues or questions:
1. Check the troubleshooting guide
2. Review container logs: `docker compose logs`
3. Verify all prerequisites are met
4. Validate configuration files for syntax errors

---

**Monitoring System Architecture**:
```
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Node Exporter │
│     Exporter    │    │                 │
│   (Port 9187)   │    │   (Port 9100)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌─────────────────┐    ┌─────────────────┐
          │   Prometheus    │    │  Custom Exporter│
          │   Server        │    │                 │
          │  (Port 9090)    │    │   (Port 9099)   │
          └─────────┬───────┘    └─────────┬───────┘
                    │                      │
                    └──────────┬───────────┘
                               │
                    ┌─────────────────┐
                    │     Grafana     │
                    │                 │
                    │   (Port 3000)   │
                    └─────────────────┘
```