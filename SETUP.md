# GCode Evaluation API Setup Guide

This guide provides step-by-step instructions for setting up and deploying the GCode Evaluation API locally and on PythonAnywhere.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [PythonAnywhere Deployment](#pythonanywhere-deployment)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.9 or higher
- pip package manager
- Git (for deployment)
- 512MB RAM minimum (for PythonAnywhere free tier)

### Knowledge Requirements

- Basic Python/Django knowledge
- REST API concepts
- Command line usage

## Local Development Setup

### 1. Environment Preparation

**Create Project Directory**

```bash
mkdir gcode-evaluation-api
cd gcode-evaluation-api
```

**Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

**Install from requirements.txt**

```bash
pip install -r requirements.txt
```

**Verify Installation**

```bash
pip list
```

You should see:

- Django==4.2.7
- djangorestframework==3.14.0
- django-cors-headers==4.3.1
- python-dotenv==1.0.0
- opencv-python==4.8.1.78
- numpy==1.24.3
- scikit-image==0.21.0
- Pillow==10.0.1

### 3. Database Setup

**Run Migrations** (minimal, as this is stateless)

```bash
python manage.py migrate
```

**Create Superuser** (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 4. Environment Configuration

**Create .env file**

```bash
# Create .env file in project root
```

**Add configuration**

```env
# .env file contents
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Start Development Server

```bash
python manage.py runserver 8001
```

**Verify Installation**

- Visit: `http://localhost:8001/`
- Should see API service information
- Visit: `http://localhost:8001/api/health/`
- Should return health status

### 6. Test Endpoints

**Test with curl**

```bash
# Health check
curl http://localhost:8001/api/health/

# Should return service status
```

## PythonAnywhere Deployment

### 1. Prepare Files for Upload

**Create deployment package**

```bash
# Ensure all files are ready
pip freeze > requirements.txt
```

**Files to upload:**

- All Python source files
- requirements.txt
- evaluation_modules/ directory
- .env file (with production settings)

### 2. PythonAnywhere Setup

**Upload Files**

1. Use PythonAnywhere file manager or git clone
2. Upload to `/home/yourusername/gcode-evaluation-api/`

**Create Virtual Environment**

```bash
# In PythonAnywhere bash console
cd /home/yourusername/gcode-evaluation-api
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Web App Configuration

**Create Web App**

1. Go to PythonAnywhere Dashboard → Web
2. Click "Add a new web app"
3. Choose Manual configuration
4. Select Python 3.9

**Configure WSGI File**
Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/gcode-evaluation-api'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'gcode_evaluation.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Configure Virtual Environment**

- Set virtual environment path: `/home/yourusername/gcode-evaluation-api/venv/`

**Configure Static Files**

- URL: `/static/`
- Directory: `/home/yourusername/gcode-evaluation-api/static/`

### 4. Production Environment Configuration

**Create production .env**

```env
DEBUG=False
SECRET_KEY=your-secure-production-secret-key-here
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

**Run Production Setup**

```bash
# In PythonAnywhere bash console
cd /home/yourusername/gcode-evaluation-api
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
```

### 5. Restart Web App

1. Go to PythonAnywhere Dashboard → Web
2. Click "Reload yourusername.pythonanywhere.com"

### 6. Verify Deployment

**Test endpoints:**

- `https://yourusername.pythonanywhere.com/`
- `https://yourusername.pythonanywhere.com/api/health/`

## Configuration

### Environment Variables

| Variable               | Description       | Development             | Production           |
| ---------------------- | ----------------- | ----------------------- | -------------------- |
| `DEBUG`                | Enable debug mode | `True`                  | `False`              |
| `SECRET_KEY`           | Django secret key | Any string              | Secure random string |
| `ALLOWED_HOSTS`        | Allowed hostnames | `localhost,127.0.0.1`   | Your domain          |
| `CORS_ALLOWED_ORIGINS` | CORS origins      | `http://localhost:3000` | Your frontend URL    |

### Django Settings

**Key settings in settings.py:**

```python
# CORS configuration for cross-origin requests
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",
]

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'evaluation_api.log',
        },
    },
    'loggers': {
        'evaluation_api': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Testing

### 1. Run Unit Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test evaluation_api.tests

# Run with verbose output
python manage.py test --verbosity=2
```

### 2. Manual API Testing

**Using curl:**

```bash
# Health check
curl https://yourusername.pythonanywhere.com/api/health/

# SSIM test (requires base64 image data)
curl -X POST https://yourusername.pythonanywhere.com/api/evaluate/ssim/ \
  -H "Content-Type: application/json" \
  -d '{"original_image_data": "base64data...", "reproduced_image_data": "base64data..."}'
```

**Using Python:**

```python
import requests

# Test health endpoint
response = requests.get('https://yourusername.pythonanywhere.com/api/health/')
print(response.json())

# Test execution error endpoint
response = requests.post('https://yourusername.pythonanywhere.com/api/evaluate/execution-error/', json={
    'expected_toolpath': [[0, 0], [10, 10]],
    'actual_toolpath': [[0, 1], [9, 11]]
})
print(response.json())
```

### 3. Load Testing

**Simple load test with Python:**

```python
import requests
import time
import threading

def test_endpoint():
    start_time = time.time()
    response = requests.get('https://yourusername.pythonanywhere.com/api/health/')
    end_time = time.time()
    print(f"Response time: {end_time - start_time:.2f}s, Status: {response.status_code}")

# Run 10 concurrent requests
threads = []
for i in range(10):
    thread = threading.Thread(target=test_endpoint)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Error:** `ModuleNotFoundError: No module named 'evaluation_modules'`

**Solution:**

```bash
# Ensure evaluation_modules directory is in the project root
# Verify __init__.py files exist in all module directories
```

#### 2. Memory Issues

**Error:** `MemoryError` or application crashes

**Solutions:**

- Reduce image size before processing
- Optimize OpenCV operations
- Monitor memory usage:

```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

#### 3. CORS Issues

**Error:** Cross-origin requests blocked

**Solution:**

```python
# In settings.py, add your frontend domain
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",
    "http://localhost:3000",  # For development
]
```

#### 4. Static Files Issues

**Error:** Admin interface styling broken

**Solution:**

```bash
# Run collectstatic
python manage.py collectstatic --noinput

# Verify static files configuration in settings.py
```

#### 5. OpenCV Issues

**Error:** `ImportError: libGL.so.1: cannot open shared object file`

**Solution for PythonAnywhere:**

```python
# Add to settings.py or before OpenCV imports
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
```

### Debug Mode

**Enable detailed error reporting:**

```env
DEBUG=True
```

**Check logs:**

```bash
# PythonAnywhere error log
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Server log
tail -f /var/log/yourusername.pythonanywhere.com.server.log
```

### Performance Monitoring

**Add performance logging:**

```python
import time
import logging

logger = logging.getLogger(__name__)

def timed_operation(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

### Memory Monitoring

**Monitor memory usage:**

```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Your code here

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

## Security Considerations

### Production Security

1. **Use strong SECRET_KEY**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Set proper ALLOWED_HOSTS**

```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

3. **Configure HTTPS (PythonAnywhere handles this automatically)**

4. **Validate file uploads**

```python
# Already implemented in serializers
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.svg']
```

## Maintenance

### Regular Tasks

1. **Monitor resource usage**
2. **Check error logs regularly**
3. **Update dependencies periodically**
4. **Test API endpoints**
5. **Monitor response times**

### Updates

**Update dependencies:**

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

**Restart application:**

```bash
# PythonAnywhere: Use web interface to reload
# Local: Restart development server
```

## Support

For additional help:

1. Check Django documentation: https://docs.djangoproject.com/
2. Check DRF documentation: https://www.django-rest-framework.org/
3. PythonAnywhere help: https://help.pythonanywhere.com/
4. Review application logs for specific error details

## Next Steps

After successful setup:

1. **Integrate with Core API** - Set up frontend to communicate with both APIs
2. **Monitor Performance** - Set up monitoring and alerting
3. **Optimize Memory Usage** - Profile and optimize for 512MB limit
4. **Add Features** - Extend evaluation metrics as needed
5. **Documentation** - Keep API documentation updated
