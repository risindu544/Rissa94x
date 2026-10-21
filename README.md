# SQL Dumper Advanced - Database Extraction Tool

⚡ **Production-ready SQL database dumper with auto-detection, sensitive data discovery, and multi-database support.**

**Developer**: [rissa_94x](https://github.com/rissa-94x) | **License**: MIT | **Version**: 1.0.0

---

## 🎯 Features

- ✅ Multi-database support (MySQL, PostgreSQL, SQLite, MongoDB)
- ✅ Auto-detection of database services
- ✅ User enumeration & privilege detection
- ✅ Sensitive data automatic discovery
- ✅ Database statistics & analysis
- ✅ Raw SQL query execution
- ✅ Export data (JSON, CSV, HTML)
- ✅ Rate limiting & API key authentication
- ✅ SSL/TLS support
- ✅ Docker deployment ready
- ✅ Mobile-responsive UI

---

## 📋 Requirements

- Python 3.10+ OR Docker
- Network access to target database
- API key for production use

---

## 🚀 Quick Start

### Option 1: Local Installation (Windows/Linux/Mac)

```bash
# Step 1: Clone repository
git clone https://github.com/YOUR-USERNAME/sqldumper.git
cd sqldumper

# Step 2: Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Configure (optional)
cp .env.example .env
# Edit .env with your API key

# Step 5: Run
python app.py

# Access: http://localhost:5000
```

### Option 2: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Access: http://localhost or https://your-domain.com
```

---

## 📦 Deployment Options

### 1️⃣ **Linux/Ubuntu Server (VPS)**

```bash
# SSH into your server
ssh user@your-server-ip

# Clone repo
git clone https://github.com/YOUR-USERNAME/sqldumper.git
cd sqldumper

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/sqldumper.service
```

**Paste this:**
```ini
[Unit]
Description=SQL Dumper Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/user/sqldumper
Environment="PATH=/home/user/sqldumper/venv/bin"
ExecStart=/home/user/sqldumper/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable & start:**
```bash
sudo systemctl daemon-reload
sudo systemctl start sqldumper
sudo systemctl enable sqldumper
```

### 2️⃣ **Docker Compose (Production)**

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Check logs
docker-compose logs -f sqldumper

# Stop
docker-compose down
```

### 3️⃣ **Cloud Platforms**

#### AWS EC2
```bash
# 1. Launch t3.micro instance (free tier)
# 2. Install Docker & Docker Compose
sudo apt update
sudo apt install docker.io docker-compose -y

# 3. Clone & deploy
git clone your-repo
cd sqldumper
docker-compose up -d

# 4. Get Elastic IP & associate domain
# 5. Use Let's Encrypt for SSL (certbot)
sudo certbot certonly --standalone -d your-domain.com
```

#### DigitalOcean
```bash
# 1. Create App Platform project
# 2. Connect GitHub repository
# 3. Build command: pip install -r requirements.txt
# 4. Run command: python app.py
# 5. Deploy!
```

#### Heroku
```bash
# 1. Add Procfile
echo "web: python app.py" > Procfile

# 2. Deploy
heroku create sqldumper
git push heroku main
heroku ps:scale web=1
heroku logs --tail
```

---

## 🔐 Security Configuration

### 1. Change API Key
```bash
# Edit .env
API_KEYS=your-super-secret-key,backup-key
```

### 2. Enable SSL/TLS
```bash
# Generate Let's Encrypt certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy to nginx folder
sudo cp /etc/letsencrypt/live/your-domain/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain/privkey.pem ssl/key.pem

# Update nginx.conf with your domain
```

### 3. Firewall Setup
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# AWS Security Groups
# Inbound: SSH (22), HTTP (80), HTTPS (443)
# Outbound: All
```

### 4. Database User Permissions
```sql
-- MySQL: Create limited user
CREATE USER 'dumper'@'localhost' IDENTIFIED BY 'strong-password';
GRANT SELECT ON production_db.* TO 'dumper'@'localhost';

-- PostgreSQL: Create limited user
CREATE USER dumper WITH PASSWORD 'strong-password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dumper;
```

---

## 📱 Usage

### 1. Connect to Database

1. Select database type (MySQL, PostgreSQL, SQLite, MongoDB)
2. Enter connection string:
   - **MySQL**: `user:password@localhost:3306/dbname`
   - **PostgreSQL**: `postgresql://user:password@localhost/dbname`
   - **SQLite**: `/path/to/database.db`
   - **MongoDB**: `mongodb://user:password@localhost:27017/dbname`
3. Click **Connect**

### 2. Quick Actions

| Button | Function |
|--------|----------|
| 👤 Users | List all database users |
| 📚 DBs | Enumerate all databases |
| 🔐 Sensitive | Find password/credit card columns |
| 📊 Stats | Database size & table breakdown |
| 💻 Query | Execute raw SQL |

### 3. Data Extraction

1. Click table name → View data preview
2. Click **JSON/CSV** → Download all rows
3. Or use **Raw Query** for custom filters

---

## 🔌 API Endpoints

All endpoints require `X-API-Key` header:

```bash
curl -H "X-API-Key: your-key" http://localhost:5000/api/tables
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/connect` | Connect to database |
| POST | `/api/detect` | Auto-detect DB type |
| GET | `/api/tables` | List tables |
| GET | `/api/columns/<table>` | List columns |
| GET | `/api/dump/<table>` | Dump table data |
| GET | `/api/users` | List users |
| GET | `/api/sensitive` | Find sensitive data |
| GET | `/api/stats` | Database stats |
| POST | `/api/execute` | Execute query |
| GET | `/api/export/<table>/<format>` | Export data |

---

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status sqldumper
```

### View Logs
```bash
# Local
tail -f sqldumper.log

# Docker
docker logs -f sqldumper-app

# Systemd
journalctl -u sqldumper -f
```

### Performance Monitoring
```bash
# CPU/Memory
docker stats sqldumper-app

# Or
htop
ps aux | grep python
```

---

## 🐛 Troubleshooting

### Connection Failed
```
✗ Error: Connection refused
```
**Solution**: Check database credentials, firewall, and network access

### Rate Limit Exceeded
```
✗ Error: Rate limit exceeded
```
**Solution**: Wait or adjust `RATE_LIMIT` in `.env`

### Module Not Found
```
✗ ModuleNotFoundError: No module named 'flask'
```
**Solution**: `pip install -r requirements.txt`

### Port Already in Use
```
✗ Address already in use
```
**Solution**: 
```bash
# Find process
lsof -i :5000
# Kill it
kill -9 <PID>
```

---

## 📝 API Key Management

### Generate Strong Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Rotate Keys
```bash
# Edit .env
API_KEYS=old-key,new-key
# Later remove old-key
API_KEYS=new-key
docker-compose restart sqldumper
```

---

## 🔄 Auto-Updates

### GitHub Auto-Deployment
```bash
# Enable Actions in GitHub
# Secrets needed:
# - DOCKER_USERNAME
# - DOCKER_PASSWORD

# Push to main branch triggers auto-build & push to Docker Hub
git push origin main
```

### Pull Latest Image
```bash
docker pull your-username/sqldumper:latest
docker-compose up -d
```

---

## 📜 Legal Notice

⚠️ **For authorized security testing only.** Unauthorized access to databases is illegal. Ensure you have proper authorization before using this tool.

---

## 🤝 Contributing

```bash
git clone <your-fork>
cd sqldumper
git checkout -b feature/your-feature
# Make changes
git commit -m "Add feature"
git push origin feature/your-feature
# Create Pull Request
```

---

## 👨‍💻 Developer

**rissa_94x** - Full Stack Security Engineer
- GitHub: [@rissa-94x](https://github.com/rissa-94x)
- Project: SQL Dumper Advanced v1.0
- Built with: Flask, Docker, Nginx, Python 3.11+

## 📄 License

MIT License - See LICENSE file | Copyright (c) 2024 rissa_94x

---

## 🆘 Support

- **GitHub Issues**: Report bugs
- **Discussions**: Ask questions
- **Wiki**: Full documentation

---

## 🎯 Roadmap

- [ ] Web GUI for database management
- [ ] Scheduled backups
- [ ] Data encryption at rest
- [ ] LDAP authentication
- [ ] Multi-user access control
- [ ] Database replication
- [ ] Data anonymization
- [ ] Audit logging

---

**Version**: 1.0.0 | **Updated**: 2024 | **Status**: Production Ready

Strike clean. Deploy sharp. Talons out.
