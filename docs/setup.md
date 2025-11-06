# Detailed Setup and Configuration Guide

This guide provides comprehensive instructions for setting up the complete monitoring system.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, recommended 8GB
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for external APIs

### Software Requirements

1. **Docker & Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **PostgreSQL Server**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib

   # macOS (with Homebrew)
   brew install postgresql
   brew services start postgresql

   # Start PostgreSQL service
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

3. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git

   # macOS
   brew install git
   ```

## Database Setup

### 1. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE movies_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE movies_db TO postgres;
\q
```

### 2. Verify Database Connection

```bash
psql -h localhost -U postgres -d movies_db -c "SELECT version();"
```

## API Keys Setup

### 1. OpenWeatherMap API Key

1. Register at https://openweathermap.org/api
2. Get free API key
3. Add to `.env` file:
   ```bash
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

### 2. Optional: GitHub Personal Access Token

For higher rate limits with GitHub API:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `public_repo` scope
3. Add to custom_exporter.py if needed

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd movies-analytics
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Add your configuration:
```bash
# Required: OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional: Custom update interval
UPDATE_INTERVAL=20
```

### 3. Verify File Structure

Ensure you have this structure:
```
movies-analytics/
├── docker-compose.yml
├── prometheus.yml
├── alert_rules.yml
├── custom_exporter.py
├── Dockerfile.custom_exporter
├── .env
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── dashboards/
│               ├── database-dashboard.json
│               ├── system-dashboard.json
│               └── custom-dashboard.json
└── docs/
    ├── setup.md
    ├── queries.md
    └── troubleshooting.md
```

### 4. Start the Monitoring Stack

```bash
# Build and start all containers
docker compose up -d --build

# View container logs
docker compose logs -f

# Check container status
docker compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
custom-exporter     "python custom_expor…"   custom-exporter     running             0.0.0.0:9099->9099/tcp
grafana             "/run.sh"                grafana             running             0.0.0.0:3000->3000/tcp
node-exporter       "/bin/node_exporter …"   node-exporter       running             0.0.0.0:9100->9100/tcp
postgres-exporter   "/postgres_exporter …"   postgres-exporter   running             0.0.0.0:9187->9187/tcp
prometheus          "/bin/prometheus --…"    prometheus          running             0.0.0.0:9090->9090/tcp
```

## Verification Steps

### 1. Check Exporter Endpoints

```bash
# Test PostgreSQL Exporter
curl http://localhost:9187/metrics | head -10

# Test Node Exporter
curl http://localhost:9100/metrics | head -10

# Test Custom Exporter
curl http://localhost:9099/metrics | head -10
```

### 2. Verify Prometheus Targets

Open http://localhost:9090/targets in your browser. All targets should be "UP":

- prometheus (http://localhost:9090/metrics)
- postgres-exporter (http://postgres-exporter:9187/metrics)
- node-exporter (http://node-exporter:9100/metrics)
- custom-exporter (http://custom-exporter:9099/metrics)

### 3. Access Grafana

Open http://localhost:3000 in your browser:
- Username: `admin`
- Password: `admin`

You should see three dashboards:
1. PostgreSQL Database Performance
2. System Performance Monitoring
3. External API Monitoring

## Advanced Configuration

### Custom Ports

Edit `docker-compose.yml` to change ports:

```yaml
services:
  prometheus:
    ports:
      - "9091:9090"  # Change to 9091
  grafana:
    ports:
      - "3001:3000"  # Change to 3001
```

### Prometheus Retention

Edit `prometheus.yml` to adjust data retention:

```yaml
command:
  - '--storage.tsdb.retention.time=30d'  # Keep 30 days of data
```

### Custom Alerting

Add custom alerts in `alert_rules.yml`:

```yaml
- alert: CustomHighMetric
  expr: your_metric > threshold
  for: duration
  labels:
    severity: warning
  annotations:
    summary: "Custom alert summary"
    description: "Detailed description"
```

## Security Considerations

### 1. Change Default Credentials

Edit `docker-compose.yml`:

```yaml
services:
  grafana:
    environment:
      - GF_SECURITY_ADMIN_USER=your_username
      - GF_SECURITY_ADMIN_PASSWORD=your_secure_password
```

### 2. Network Security

Consider using Docker networks or firewalls to restrict access:

```bash
# Only allow local access
iptables -A INPUT -p tcp --dport 3000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 9090 -s 127.0.0.1 -j ACCEPT
```

### 3. SSL/TLS Configuration

For production, configure HTTPS:
- Use reverse proxy (nginx/traefik)
- Configure SSL certificates
- Enable secure headers

## Performance Optimization

### 1. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### 2. Storage Optimization

Use fast storage for Prometheus data:

```yaml
volumes:
  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /fast/ssd/path/prometheus
```

## Monitoring the Monitoring System

### Health Checks

Add health checks to `docker-compose.yml`:

```yaml
services:
  prometheus:
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Log Management

Configure log rotation:

```yaml
services:
  prometheus:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Backup and Recovery

### 1. Configuration Backup

```bash
# Backup all configuration files
tar -czf monitoring-config-$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    prometheus.yml \
    alert_rules.yml \
    custom_exporter.py \
    grafana/
```

### 2. Data Backup

```bash
# Backup Prometheus data
docker compose exec prometheus tar -czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp $(docker compose ps -q prometheus):/tmp/prometheus-backup.tar.gz ./prometheus-backup-$(date +%Y%m%d).tar.gz

# Backup Grafana data
docker compose exec grafana tar -czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp $(docker compose ps -q grafana):/tmp/grafana-backup.tar.gz ./grafana-backup-$(date +%Y%m%d).tar.gz
```

### 3. Recovery

```bash
# Stop containers
docker compose down

# Restore Prometheus data
docker cp ./prometheus-backup-YYYYMMDD.tar.gz $(docker compose run -d prometheus):/tmp/
docker compose exec prometheus tar -xzf /tmp/prometheus-backup-YYYYMMDD.tar.gz -C /

# Restart
docker compose up -d
```

## Troubleshooting Setup Issues

### Common Problems and Solutions

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   sudo netstat -tulpn | grep :9090
   sudo netstat -tulpn | grep :3000
   ```

2. **Permission Issues**
   ```bash
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Database Connection Issues**
   ```bash
   # Test PostgreSQL connection
   psql -h localhost -U postgres -d movies_db -c "SELECT 1;"
   ```

4. **Memory Issues**
   ```bash
   # Check system memory
   free -h

   # Check container memory usage
   docker stats
   ```

For more troubleshooting, see `docs/troubleshooting.md`.