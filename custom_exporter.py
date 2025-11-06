#!/usr/bin/env python3

from prometheus_client import start_http_server, Gauge, Counter
import requests
import time
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather metrics (OpenWeatherMap)
weather_temp = Gauge('weather_temperature_celsius', 'Current temperature in Celsius', ['city'])
weather_humidity = Gauge('weather_humidity_percent', 'Current humidity percentage', ['city'])
weather_pressure = Gauge('weather_pressure_hpa', 'Current atmospheric pressure', ['city'])

# Exchange rate metrics
exchange_rate = Gauge('exchange_rate', 'Currency exchange rate', ['from_currency', 'to_currency'])
exchange_rate_updated = Gauge('exchange_rate_last_update', 'Last update timestamp', ['currency_pair'])

# GitHub API metrics
github_stars = Gauge('github_repository_stars', 'Number of stars', ['repository', 'owner'])
github_forks = Gauge('github_repository_forks', 'Number of forks', ['repository', 'owner'])
github_issues = Gauge('github_repository_issues', 'Number of open issues', ['repository', 'owner'])
github_commits = Gauge('github_repository_commits_24h', 'Commits in last 24 hours', ['repository', 'owner'])

# System metrics
api_requests_total = Counter('api_requests_total', 'Total API requests made', ['api_name', 'status'])
api_response_time = Gauge('api_response_time_seconds', 'API response time', ['api_name'])

def collect_weather_data():
    """Collect weather data from OpenWeatherMap API"""
    cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney']
    api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')

    for city in cities:
        start_time = time.time()
        try:
            response = requests.get(
                f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric',
                timeout=10
            )
            response_time = time.time() - start_time
            api_response_time.labels(api_name='openweather').set(response_time)

            if response.status_code == 200:
                data = response.json()
                weather_temp.labels(city=city).set(data['main']['temp'])
                weather_humidity.labels(city=city).set(data['main']['humidity'])
                weather_pressure.labels(city=city).set(data['main']['pressure'])
                api_requests_total.labels(api_name='openweather', status='success').inc()
                logger.info(f"Weather data collected for {city}: {data['main']['temp']}°C")
            else:
                api_requests_total.labels(api_name='openweather', status='error').inc()
                logger.warning(f"Weather API error for {city}: {response.status_code}")

        except Exception as e:
            response_time = time.time() - start_time
            api_response_time.labels(api_name='openweather').set(response_time)
            api_requests_total.labels(api_name='openweather', status='error').inc()
            logger.error(f"Weather API exception for {city}: {str(e)}")

def collect_exchange_rates():
    """Collect exchange rate data"""
    base_currency = 'USD'
    targets = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD']

    start_time = time.time()
    try:
        response = requests.get(
            f'https://api.exchangerate-api.com/v4/latest/{base_currency}',
            timeout=10
        )
        response_time = time.time() - start_time
        api_response_time.labels(api_name='exchange').set(response_time)

        if response.status_code == 200:
            data = response.json()
            timestamp = time.time()

            for target in targets:
                rate = data['rates'].get(target)
                if rate:
                    exchange_rate.labels(from_currency=base_currency, to_currency=target).set(rate)
                    pair = f"{base_currency}_{target}"
                    exchange_rate_updated.labels(currency_pair=pair).set(timestamp)

            api_requests_total.labels(api_name='exchange', status='success').inc()
            logger.info(f"Exchange rates collected for {len(targets)} currencies")
        else:
            api_requests_total.labels(api_name='exchange', status='error').inc()
            logger.warning(f"Exchange API error: {response.status_code}")

    except Exception as e:
        response_time = time.time() - start_time
        api_response_time.labels(api_name='exchange').set(response_time)
        api_requests_total.labels(api_name='exchange', status='error').inc()
        logger.error(f"Exchange API exception: {str(e)}")

def collect_github_data():
    """Collect GitHub repository data"""
    repos = [
        {'owner': 'microsoft', 'repo': 'vscode'},
        {'owner': 'facebook', 'repo': 'react'},
        {'owner': 'torvalds', 'repo': 'linux'}
    ]

    for repo_info in repos:
        start_time = time.time()
        try:
            # Repository info
            repo_response = requests.get(
                f'https://api.github.com/repos/{repo_info["owner"]}/{repo_info["repo"]}',
                timeout=10
            )

            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                github_stars.labels(
                    repository=repo_info['repo'],
                    owner=repo_info['owner']
                ).set(repo_data['stargazers_count'])

                github_forks.labels(
                    repository=repo_info['repo'],
                    owner=repo_info['owner']
                ).set(repo_data['forks_count'])

                github_issues.labels(
                    repository=repo_info['repo'],
                    owner=repo_info['owner']
                ).set(repo_data['open_issues_count'])

                logger.info(f"GitHub data for {repo_info['owner']}/{repo_info['repo']}: "
                          f"{repo_data['stargazers_count']} stars")

            # Commits in last 24h
            commits_response = requests.get(
                f'https://api.github.com/repos/{repo_info["owner"]}/{repo_info["repo"]}/commits',
                params={'since': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z')},
                timeout=10
            )

            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                github_commits.labels(
                    repository=repo_info['repo'],
                    owner=repo_info['owner']
                ).set(len(commits_data))

                logger.info(f"GitHub commits for {repo_info['owner']}/{repo_info['repo']}: "
                          f"{len(commits_data)} commits today")

            response_time = time.time() - start_time
            api_response_time.labels(api_name='github').set(response_time)
            api_requests_total.labels(api_name='github', status='success').inc()

        except Exception as e:
            response_time = time.time() - start_time
            api_response_time.labels(api_name='github').set(response_time)
            api_requests_total.labels(api_name='github', status='error').inc()
            logger.error(f"GitHub API exception for {repo_info['owner']}/{repo_info['repo']}: {str(e)}")

def collect_metrics():
    """Main function to collect all metrics"""
    logger.info("Starting metrics collection...")

    collect_weather_data()
    collect_exchange_rates()
    collect_github_data()

    logger.info("Metrics collection completed")

def main():
    """Main function"""
    # Get update interval from environment variable
    update_interval = int(os.getenv('UPDATE_INTERVAL', 20))

    logger.info(f"Starting custom exporter on port 9099, update interval: {update_interval}s")

    # Start HTTP server
    start_http_server(9099)

    # Initial collection
    collect_metrics()

    # Periodic collection
    while True:
        time.sleep(update_interval)
        collect_metrics()

if __name__ == '__main__':
    main()