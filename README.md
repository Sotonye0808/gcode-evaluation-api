# GCode Evaluation API

A Django REST API service for evaluating G-code generation quality through image processing and analysis. This API provides stateless endpoints for calculating SSIM (Structural Similarity Index), line smoothness analysis, and G-code execution error metrics.

## Features

- **SSIM Evaluation**: Calculate structural similarity between original and reproduced images
- **Smoothness Analysis**: Evaluate line smoothness quality in signature images
- **Execution Error Analysis**: Calculate accuracy metrics for G-code toolpath execution
- **Health Monitoring**: Built-in health check endpoints
- **Multi-format Input**: Supports both file uploads and base64 encoded data
- **Comprehensive Error Handling**: Detailed error responses and logging

## Architecture

This API is designed as a stateless microservice that handles compute-intensive image processing operations. It works in conjunction with the GCode Core API for complete signature processing workflows.

### Key Components

- **Views**: RESTful API endpoints with comprehensive documentation
- **Services**: Business logic for image processing and metric calculations
- **Serializers**: Request/response validation and formatting
- **Evaluation Modules**: Core algorithms for SSIM, smoothness, and error calculations

## API Endpoints

### Base URL

```
http://localhost:8001/api/
```

### Available Endpoints

| Endpoint                     | Method | Description                          |
| ---------------------------- | ------ | ------------------------------------ |
| `/health/`                   | GET    | Health check and service information |
| `/evaluate/ssim/`            | POST   | Calculate SSIM between two images    |
| `/evaluate/smoothness/`      | POST   | Analyze line smoothness in an image  |
| `/evaluate/execution-error/` | POST   | Calculate G-code execution accuracy  |

## Quick Start

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. **Clone or extract the project**

   ```bash
   cd gcode-evaluation-api
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver 8001
   ```

The API will be available at `http://localhost:8001/`

## Usage Examples

### SSIM Evaluation

Calculate similarity between two images:

```python
import requests
import base64

# Using base64 data
with open('original.png', 'rb') as f:
    original_b64 = base64.b64encode(f.read()).decode()
with open('reproduced.png', 'rb') as f:
    reproduced_b64 = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8001/api/evaluate/ssim/', json={
    'original_image_data': original_b64,
    'reproduced_image_data': reproduced_b64
})

result = response.json()
print(f"SSIM Score: {result['ssim_score']}")
print(f"Interpretation: {result['interpretation']}")
```

### Smoothness Analysis

Analyze line smoothness in a signature image:

```python
import requests
import base64

with open('signature.png', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8001/api/evaluate/smoothness/', json={
    'image_data': image_b64
})

result = response.json()
print(f"Smoothness Score: {result['smoothness_score']}")
print(f"Interpretation: {result['interpretation']}")
```

### Execution Error Analysis

Calculate G-code execution accuracy:

```python
import requests

response = requests.post('http://localhost:8001/api/evaluate/execution-error/', json={
    'expected_toolpath': [[0, 0], [10, 10], [20, 20]],
    'actual_toolpath': [[0, 1], [9, 11], [21, 19]]
})

result = response.json()
print(f"Mean Error: {result['mean_error']}")
print(f"Max Error: {result['analysis']['max_error']}")
```

## Input Formats

### Image Data

- **File Upload**: Multipart form data with image files
- **Base64**: JSON with base64 encoded image data
- **Supported Formats**: PNG, JPEG, SVG

### Toolpath Data

- **Format**: Array of [x, y] coordinate pairs
- **Example**: `[[0, 0], [10, 10], [20, 20]]`

## Response Format

All endpoints return JSON responses with consistent structure:

```json
{
  "success": true,
  "data": "...",
  "message": "Operation completed successfully",
  "interpretation": "Result interpretation"
}
```

Error responses include detailed error information:

```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error description"
}
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

The codebase follows Django best practices with:

- Comprehensive error handling
- Request/response validation
- Detailed logging
- Type hints and documentation
- Unit test coverage

### Environment Variables

Create a `.env` file for configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in settings
2. Configure proper `SECRET_KEY`
3. Set appropriate `ALLOWED_HOSTS`
4. Use production WSGI server (gunicorn)

### Memory Optimization

This API is optimized for the 512MB memory limit:

- Stateless design (no database)
- Efficient image processing
- Minimal dependency footprint
- Memory-conscious temporary file handling

## Monitoring

### Health Check

Check service status:

```bash
curl http://localhost:8001/api/health/
```

### Logs

Application logs are written to:

- Console output (development)
- Log files (production, if configured)

## Integration

This API is designed to work with the GCode Core API:

1. Core API handles data persistence and user management
2. Evaluation API handles compute-intensive processing
3. Frontend orchestrates communication between services

## Dependencies

Key dependencies and their purposes:

- **Django 4.2.7**: Web framework
- **djangorestframework**: REST API functionality
- **django-cors-headers**: CORS handling
- **opencv-python**: Image processing
- **scikit-image**: Advanced image analysis
- **numpy**: Numerical computations
- **Pillow**: Image format support

## Contributing

1. Follow Django coding standards
2. Add tests for new functionality
3. Update documentation
4. Ensure memory efficiency

## License

This project is part of a final year academic project.

## Support

For issues or questions related to the Evaluation API, please refer to the API documentation or check the logs for detailed error information.
