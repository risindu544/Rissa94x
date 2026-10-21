#!/usr/bin/env python3
"""
SQL Dumper Advanced - Database Extraction Tool
Production Ready - Security Hardened

Developer: rissa_94x
Repository: https://github.com/rissa-94x/sqldumper
License: MIT
Version: 1.0.0
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
import psycopg2
import sqlite3
import pymongo
from urllib.parse import urlparse
import json
import csv
import io
from datetime import datetime, timedelta
import logging
import hashlib
import socket
import os

app = Flask(__name__)
CORS(app)

# Security Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['JSON_SORT_KEYS'] = False

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('sqldumper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Key Authentication
VALID_API_KEYS = os.environ.get('API_KEYS', 'default-key-change-in-production').split(',')

dump_logs = []

def check_api_key():
    """Verify API key for protected endpoints"""
    if request.path.startswith('/api/'):
        key = request.headers.get('X-API-Key')
        if not key or key not in VALID_API_KEYS:
            return False
    return True

@app.before_request
def verify_auth():
    """Check authentication before each request"""
    if request.path.startswith('/api/') and request.path not in ['/api/logs']:
        if not check_api_key():
            return jsonify({'error': 'Unauthorized - Invalid API Key'}), 401

class DatabaseConnector:
    def __init__(self, db_type, connection_string):
        self.db_type = db_type
        self.conn = None
        self.cursor = None
        self.banner = None
        self.is_dba = False
        self.tables_count = 0
        self.connect(connection_string)
    
    def connect(self, connection_string):
        try:
            if self.db_type == 'mysql':
                parsed = urlparse(f'mysql://{connection_string}')
                self.conn = mysql.connector.connect(
                    host=parsed.hostname or 'localhost',
                    user=parsed.username or 'root',
                    password=parsed.password or '',
                    database=parsed.path.lstrip('/') or 'mysql',
                    port=parsed.port or 3306,
                    autocommit=False,
                    connection_timeout=5
                )
            elif self.db_type == 'postgresql':
                self.conn = psycopg2.connect(
                    connection_string,
                    connect_timeout=5
                )
            elif self.db_type == 'sqlite':
                self.conn = sqlite3.connect(connection_string)
                self.conn.row_factory = sqlite3.Row
            elif self.db_type == 'mongodb':
                self.client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                self.client.admin.command('ping')
                self.conn = self.client
            
            if self.db_type != 'mongodb':
                self.cursor = self.conn.cursor()
            
            self.get_banner()
            self.check_dba()
            add_log(f"Connected to {self.db_type}: {self.banner}", 'success')
            return True
        except Exception as e:
            add_log(f"Connection failed: {str(e)}", 'error')
            raise
    
    def get_banner(self):
        try:
            if self.db_type == 'mysql':
                self.cursor.execute("SELECT VERSION()")
                self.banner = self.cursor.fetchone()[0]
            elif self.db_type == 'postgresql':
                self.cursor.execute("SELECT version()")
                self.banner = self.cursor.fetchone()[0]
            elif self.db_type == 'sqlite':
                self.cursor.execute("SELECT sqlite_version()")
                self.banner = self.cursor.fetchone()[0]
            elif self.db_type == 'mongodb':
                self.banner = "MongoDB"
        except:
            self.banner = "Unknown"
    
    def check_dba(self):
        try:
            if self.db_type == 'mysql':
                self.cursor.execute("SELECT SUPER_PRIV FROM mysql.user WHERE user=CURRENT_USER()")
                result = self.cursor.fetchone()
                self.is_dba = result and result[0] == 'Y'
            elif self.db_type == 'postgresql':
                self.cursor.execute("SELECT current_user")
                user = self.cursor.fetchone()[0]
                self.cursor.execute(f"SELECT usesuper FROM pg_user WHERE usename=%s", (user,))
                result = self.cursor.fetchone()
                self.is_dba = result and result[0]
        except:
            self.is_dba = False
    
    def auto_detect(self, host, port=None):
        """Auto-detect database type by port scanning"""
        try:
            detection = {}
            ports = {3306: 'mysql', 5432: 'postgresql', 27017: 'mongodb', 1433: 'mssql'}
            
            for p, db_type in ports.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, p))
                    if result == 0:
                        detection[db_type] = p
                    sock.close()
                except:
                    pass
            
            return detection if detection else {'status': 'unknown'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_users(self):
        try:
            users = []
            if self.db_type == 'mysql':
                self.cursor.execute("SELECT user, host FROM mysql.user LIMIT 100")
                users = [{'user': u[0], 'host': u[1]} for u in self.cursor.fetchall()]
            elif self.db_type == 'postgresql':
                self.cursor.execute("SELECT usename, usesuper FROM pg_user LIMIT 100")
                users = [{'user': u[0], 'is_super': u[1]} for u in self.cursor.fetchall()]
            return users
        except Exception as e:
            add_log(f"Get users failed: {str(e)}", 'error')
            return []
    
    def get_sensitive_data(self):
        """Search for sensitive columns"""
        try:
            sensitive = {}
            patterns = ['password', 'credit', 'ssn', 'secret', 'token', 'api', 'key', 'hash']
            
            tables = self.get_tables()
            
            for table in tables[:50]:
                cols = self.get_columns(table)
                matching = [c for c in cols if any(p in c.lower() for p in patterns)]
                if matching:
                    sensitive[table] = matching
            
            return sensitive
        except Exception as e:
            add_log(f"Sensitive search failed: {str(e)}", 'error')
            return {}
    
    def get_dump_stats(self):
        """Generate database statistics"""
        try:
            stats = {
                'total_tables': 0,
                'total_rows': 0,
                'largest_table': {'name': '', 'rows': 0},
                'table_breakdown': []
            }
            
            tables = self.get_tables()
            stats['total_tables'] = len(tables)
            
            for table in tables[:100]:
                try:
                    if self.db_type in ['mysql', 'postgresql', 'sqlite']:
                        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = self.cursor.fetchone()[0]
                    else:
                        count = 0
                    
                    stats['total_rows'] += count
                    stats['table_breakdown'].append({'table': table, 'rows': count})
                    
                    if count > stats['largest_table']['rows']:
                        stats['largest_table'] = {'name': table, 'rows': count}
                except:
                    pass
            
            return stats
        except Exception as e:
            add_log(f"Stats failed: {str(e)}", 'error')
            return {}
    
    def get_tables(self):
        try:
            tables = []
            if self.db_type == 'mysql':
                self.cursor.execute("SHOW TABLES")
                tables = [t[0] for t in self.cursor.fetchall()]
            elif self.db_type == 'postgresql':
                self.cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                tables = [t[0] for t in self.cursor.fetchall()]
            elif self.db_type == 'sqlite':
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in self.cursor.fetchall()]
            elif self.db_type == 'mongodb':
                tables = self.conn.get_database().list_collection_names()
            return tables[:200]
        except Exception as e:
            add_log(f"Get tables failed: {str(e)}", 'error')
            return []
    
    def get_columns(self, table):
        try:
            cols = []
            if self.db_type == 'mysql':
                self.cursor.execute(f"DESCRIBE `{table}`")
                cols = [c[0] for c in self.cursor.fetchall()]
            elif self.db_type == 'postgresql':
                self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name=%s", (table,))
                cols = [c[0] for c in self.cursor.fetchall()]
            elif self.db_type == 'sqlite':
                self.cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in self.cursor.fetchall()]
            return cols
        except Exception as e:
            add_log(f"Get columns failed: {str(e)}", 'error')
            return []
    
    def dump_table(self, table, limit=1000):
        try:
            if self.db_type == 'mongodb':
                data = list(self.conn.get_database()[table].find().limit(limit))
                for doc in data:
                    doc['_id'] = str(doc['_id'])
                return data
            else:
                limit = min(limit, 10000)
                self.cursor.execute(f"SELECT * FROM `{table}` LIMIT {limit}")
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            add_log(f"Dump failed: {str(e)}", 'error')
            return []
    
    def execute_raw_query(self, query):
        try:
            query = query.strip()
            if not query:
                return {'error': 'Empty query'}
            
            self.cursor.execute(query)
            
            if query.upper().startswith('SELECT'):
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows[:1000]]
            else:
                self.conn.commit()
                return {'status': 'executed', 'rows_affected': self.cursor.rowcount}
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except:
            pass

db_instance = None

def add_log(msg, level='info'):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level.upper()}] {msg}"
    dump_logs.append(log_entry)
    if len(dump_logs) > 500:
        dump_logs.pop(0)
    getattr(logger, level.lower())(msg)

# Routes
@app.route('/')
def index():
    return render_template('advanced.html')

@app.route('/api/detect', methods=['POST'])
@limiter.limit("10 per minute")
def detect_db():
    data = request.json
    host = data.get('host')
    
    if not host:
        return jsonify({'error': 'No host provided'}), 400
    
    try:
        detector = DatabaseConnector('sqlite', ':memory:')
        result = detector.auto_detect(host)
        add_log(f"Auto-detection on {host}: {result}")
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/connect', methods=['POST'])
@limiter.limit("10 per minute")
def connect():
    global db_instance
    data = request.json
    db_type = data.get('db_type')
    connection_string = data.get('connection_string')
    
    if not db_type or not connection_string:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        if db_instance:
            db_instance.close()
        
        db_instance = DatabaseConnector(db_type, connection_string)
        
        return jsonify({
            'status': 'connected',
            'db_type': db_type,
            'banner': db_instance.banner,
            'is_dba': db_instance.is_dba
        })
    except Exception as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 400

@app.route('/api/tables', methods=['GET'])
@limiter.limit("30 per minute")
def get_tables():
    if not db_instance or not db_instance.conn:
        return jsonify({'error': 'No connection'}), 400
    tables = db_instance.get_tables()
    add_log(f"Retrieved {len(tables)} tables")
    return jsonify({'tables': tables})

@app.route('/api/columns/<table>', methods=['GET'])
@limiter.limit("30 per minute")
def get_columns(table):
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    columns = db_instance.get_columns(table)
    return jsonify({'columns': columns})

@app.route('/api/dump/<table>', methods=['GET'])
@limiter.limit("20 per minute")
def dump_table(table):
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    limit = request.args.get('limit', 1000, type=int)
    data = db_instance.dump_table(table, limit)
    add_log(f"Dumped {len(data)} rows from {table}")
    return jsonify({'table': table, 'rows': len(data), 'data': data})

@app.route('/api/users', methods=['GET'])
@limiter.limit("10 per minute")
def get_users():
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    users = db_instance.get_all_users()
    add_log(f"Retrieved {len(users)} users")
    return jsonify({'users': users})

@app.route('/api/sensitive', methods=['GET'])
@limiter.limit("10 per minute")
def find_sensitive():
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    sensitive = db_instance.get_sensitive_data()
    add_log(f"Found {len(sensitive)} tables with sensitive columns")
    return jsonify({'sensitive': sensitive})

@app.route('/api/stats', methods=['GET'])
@limiter.limit("10 per minute")
def dump_stats():
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    stats = db_instance.get_dump_stats()
    add_log(f"Stats: {stats['total_tables']} tables, {stats['total_rows']} rows")
    return jsonify(stats)

@app.route('/api/execute', methods=['POST'])
@limiter.limit("10 per minute")
def execute_query():
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    data = request.json
    query = data.get('query', '')
    result = db_instance.execute_raw_query(query)
    add_log(f"Query executed: {query[:50]}...")
    return jsonify(result)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': dump_logs[-100:]})

@app.route('/api/export/<table>/<format>', methods=['GET'])
@limiter.limit("10 per minute")
def export_table(table, format):
    if not db_instance:
        return jsonify({'error': 'No connection'}), 400
    
    data = db_instance.dump_table(table, 10000)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'json':
        output = io.StringIO()
        json.dump(data, output, indent=2, default=str)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{table}_{timestamp}.json'
        )
    
    elif format == 'csv':
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table}_{timestamp}.csv'
        )

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    add_log("SQL Dumper Advanced started")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
