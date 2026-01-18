# Funding Allocation System - Deployment Guide

## Quick Start

### Local Development

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
4. **Open browser:** Navigate to `http://localhost:8501`

### Docker Deployment

1. **Build the container:**
   ```bash
   docker build -t funding-allocation-system .
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up
   ```

3. **Access the application:** Navigate to `http://localhost:8501`

## Production Deployment

### Prerequisites

- **Server Requirements:**
  - 4+ CPU cores
  - 8GB+ RAM
  - 50GB+ storage
  - Ubuntu 20.04+ or CentOS 8+

- **Network Requirements:**
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
  - Port 8501 (Streamlit)

### Step-by-Step Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 2. Application Deployment

```bash
# Clone repository
git clone <repository-url>
cd funding_allocation_system

# Create production environment file
cp .env.template .env.production

# Edit configuration
nano config/config.yaml

# Build and start containers
docker-compose --profile production up -d
```

#### 3. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to SSL directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/
```

#### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server funding-dashboard:8501;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://streamlit;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

#### 5. Auto-Restart Configuration

Create systemd service:

```bash
sudo nano /etc/systemd/system/funding-dashboard.service
```

Add:

```ini
[Unit]
Description=Funding Allocation System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/funding_allocation_system
ExecStart=/usr/local/bin/docker-compose --profile production up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable funding-dashboard
sudo systemctl start funding-dashboard
```

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 Instance

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.large
   - Security Groups: Allow ports 80, 443, 8501

2. **Install Docker and deploy:**
   ```bash
   # Follow local deployment steps
   ```

#### Option 2: ECS (Elastic Container Service)

Create `ecs-task-definition.json`:

```json
{
  "family": "funding-dashboard",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "funding-dashboard",
      "image": "your-ecr-repo/funding-allocation-system:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "STREAMLIT_SERVER_PORT",
          "value": "8501"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/funding-dashboard",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Deploy:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs create-service --cluster your-cluster --service-name funding-dashboard --task-definition funding-dashboard --desired-count 1
```

### Azure Deployment

#### Option 1: Azure Container Instances

```bash
# Create resource group
az group create --name funding-rg --location eastus

# Deploy container
az container create \
  --resource-group funding-rg \
  --name funding-dashboard \
  --image your-registry/funding-allocation-system:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8501 \
  --environment-variables STREAMLIT_SERVER_PORT=8501
```

#### Option 2: Azure App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name funding-app-plan \
  --resource-group funding-rg \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group funding-rg \
  --plan funding-app-plan \
  --name funding-dashboard \
  --deployment-container-image-name your-registry/funding-allocation-system:latest
```

### Google Cloud Platform

#### Option 1: Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy funding-dashboard \
  --image gcr.io/your-project/funding-allocation-system:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars STREAMLIT_SERVER_PORT=8501
```

#### Option 2: Google Kubernetes Engine

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: funding-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: funding-dashboard
  template:
    metadata:
      labels:
        app: funding-dashboard
    spec:
      containers:
      - name: funding-dashboard
        image: gcr.io/your-project/funding-allocation-system:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_PORT
          value: "8501"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: funding-dashboard-service
spec:
  selector:
    app: funding-dashboard
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f k8s-deployment.yaml
```

## Monitoring and Logging

### Application Monitoring

#### 1. Set up CloudWatch (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

#### 2. Set up Azure Monitor

```bash
# Install Azure Monitor agent
curl -sSL https://aka.ms/azcmagent-install | bash

# Connect to Azure
azcmagent connect --resource-group funding-rg --location eastus
```

#### 3. Set up Google Cloud Monitoring

```bash
# Install monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
```

### Log Aggregation

#### ELK Stack Setup

Create `docker-compose-elk.yml`:

```yaml
version: '3.7'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    ports:
      - "5000:5000"
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch-data:
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker exec funding-dashboard pg_dump -U postgres funding_db > backup_$DATE.sql
gzip backup_$DATE.sql
aws s3 cp backup_$DATE.sql.gz s3://your-backup-bucket/
```

### Application Backup

```bash
#!/bin/bash
# app-backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf funding-app-backup_$DATE.tar.gz /path/to/funding_allocation_system
aws s3 cp funding-app-backup_$DATE.tar.gz s3://your-backup-bucket/
```

### Automated Backup Schedule

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
0 3 * * 0 /path/to/app-backup.sh
```

## Security Hardening

### 1. Firewall Configuration

```bash
# UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. SSL/TLS Configuration

Update nginx.conf:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 3. Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 4. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## Performance Optimization

### 1. Caching Configuration

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=funding_cache:10m max_size=1g;

location / {
    proxy_cache funding_cache;
    proxy_cache_valid 200 1h;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
}
```

### 2. Compression

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 3. Load Balancing

```nginx
upstream streamlit_backend {
    least_conn;
    server funding-dashboard-1:8501 weight=1 max_fails=3 fail_timeout=30s;
    server funding-dashboard-2:8501 weight=1 max_fails=3 fail_timeout=30s;
    server funding-dashboard-3:8501 weight=1 max_fails=3 fail_timeout=30s;
}
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker logs funding-dashboard

# Check configuration
docker-compose config

# Restart service
docker-compose restart
```

#### 2. Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  funding-dashboard:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 3. Database Connection Issues

```bash
# Check database connectivity
docker exec funding-dashboard pg_isready -h localhost -p 5432

# Check network connectivity
docker network ls
docker network inspect funding_default
```

#### 4. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Renew certificate
sudo certbot renew --dry-run
```

### Log Analysis

#### Application Logs

```bash
# View application logs
docker logs -f funding-dashboard

# Search for errors
docker logs funding-dashboard 2>&1 | grep ERROR
```

#### System Logs

```bash
# System logs
sudo journalctl -u funding-dashboard -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Check application health
- Review error logs
- Monitor resource usage

#### Weekly
- Review performance metrics
- Check backup status
- Update security patches

#### Monthly
- Full system backup
- Performance optimization review
- Security audit

#### Quarterly
- Disaster recovery testing
- Capacity planning review
- User access review

### Update Procedures

#### Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

#### Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

## Support and Documentation

### Internal Documentation

- **Runbook**: Emergency procedures
- **Architecture Diagram**: System components
- **API Documentation**: Technical reference
- **User Guide**: End-user documentation

### External Support

- **Vendor Support**: Cloud provider support
- **Community Support**: Stack Overflow, GitHub issues
- **Professional Services**: Consulting and training

---

For additional support, contact: support@agcy.gov
