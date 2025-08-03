# GCode Evaluation API Documentation

## Overview

The GCode Evaluation API is a Django REST API service that provides image processing and evaluation metrics for G-code generation quality assessment. This stateless API handles compute-intensive operations and works alongside the GCode Core API to provide comprehensive signature processing capabilities.

## Base Information

- **Base URL**: `http://localhost:8001/api/`
- **API Version**: 1.0.0
- **Content Type**: `application/json` (default), `multipart/form-data` (file uploads)
- **Authentication**: None required (stateless API)

## Endpoints

### 1. Health Check

**GET** `/health/`

Returns the current status and information about the Evaluation API service.

#### Response

```json
{
  "status": "healthy",
  "service": "GCode Evaluation API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "endpoints": {
    "ssim": "/api/evaluate/ssim/",
    "smoothness": "/api/evaluate/smoothness/",
    "execution_error": "/api/evaluate/execution-error/"
  }
}
```

#### Status Codes

- `200`: Service is healthy

---

### 2. SSIM Evaluation

**POST** `/evaluate/ssim/`

Calculate the Structural Similarity Index (SSIM) between two images. SSIM returns a value between 0 and 1, where 1 indicates identical images.

#### Request Formats

**Option 1: File Upload (multipart/form-data)**

```
Content-Type: multipart/form-data

original_image: <image file>
reproduced_image: <image file>
```

**Option 2: Base64 Data (application/json)**

```json
{
  "original_image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "reproduced_image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### Response

```json
{
  "success": true,
  "ssim_score": 0.8542,
  "message": "SSIM calculated successfully",
  "interpretation": "High similarity"
}
```

#### Interpretation Scale

- `0.9 - 1.0`: Very high similarity
- `0.7 - 0.9`: High similarity
- `0.5 - 0.7`: Moderate similarity
- `0.3 - 0.5`: Low similarity
- `0.0 - 0.3`: Very low similarity

#### Status Codes

- `200`: Calculation successful
- `400`: Invalid image data or missing parameters
- `500`: Internal server error

#### Error Response Example

```json
{
  "success": false,
  "error": "Invalid image data",
  "details": "Unable to decode base64 image data"
}
```

---

### 3. Smoothness Evaluation

**POST** `/evaluate/smoothness/`

Analyze the smoothness of lines in a signature image. Returns a score between 0 and 1, where 1 indicates very smooth lines.

#### Request Formats

**Option 1: File Upload (multipart/form-data)**

```
Content-Type: multipart/form-data

image: <image file>
```

**Option 2: Base64 Data (application/json)**

```json
{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### Response

```json
{
  "success": true,
  "smoothness_score": 0.7234,
  "message": "Smoothness calculated successfully",
  "interpretation": "Good line smoothness"
}
```

#### Interpretation Scale

- `0.8 - 1.0`: Excellent line smoothness
- `0.6 - 0.8`: Good line smoothness
- `0.4 - 0.6`: Fair line smoothness
- `0.2 - 0.4`: Poor line smoothness
- `0.0 - 0.2`: Very poor line smoothness

#### Status Codes

- `200`: Calculation successful
- `400`: Invalid image data or missing parameters
- `500`: Internal server error

---

### 4. Execution Error Evaluation

**POST** `/evaluate/execution-error/`

Calculate the execution error between expected and actual G-code toolpaths. Compares coordinate arrays and returns distance-based error metrics.

#### Request Format

```json
{
  "expected_toolpath": [
    [0, 0],
    [10, 10],
    [20, 20]
  ],
  "actual_toolpath": [
    [0, 1],
    [9, 11],
    [21, 19]
  ]
}
```

#### Request Parameters

- `expected_toolpath`: Array of [x, y] coordinate pairs representing the intended toolpath
- `actual_toolpath`: Array of [x, y] coordinate pairs representing the actual executed toolpath

#### Response

```json
{
  "success": true,
  "mean_error": 1.2345,
  "individual_errors": [1.0, 1.4142, 1.4142],
  "message": "Execution error calculated successfully",
  "analysis": {
    "max_error": 1.4142,
    "min_error": 1.0,
    "error_std": 0.2357,
    "total_points": 3
  }
}
```

#### Response Fields

- `mean_error`: Average distance error across all points
- `individual_errors`: Array of distance errors for each coordinate pair
- `analysis.max_error`: Maximum error distance
- `analysis.min_error`: Minimum error distance
- `analysis.error_std`: Standard deviation of errors
- `analysis.total_points`: Number of coordinate pairs compared

#### Status Codes

- `200`: Calculation successful
- `400`: Invalid toolpath data (mismatched lengths, invalid coordinates)
- `500`: Internal server error

#### Error Response Example

```json
{
  "success": false,
  "error": "Invalid toolpath data",
  "details": "Expected and actual toolpaths must have the same length"
}
```

---

## Common Error Responses

### Validation Error (400)

```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### Internal Server Error (500)

```json
{
  "success": false,
  "error": "Internal server error",
  "details": "An unexpected error occurred during processing"
}
```

## Request Examples

### cURL Examples

**Health Check**

```bash
curl -X GET http://localhost:8001/api/health/
```

**SSIM with Base64 Data**

```bash
curl -X POST http://localhost:8001/api/evaluate/ssim/ \
  -H "Content-Type: application/json" \
  -d '{
    "original_image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
    "reproduced_image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
  }'
```

**Smoothness with File Upload**

```bash
curl -X POST http://localhost:8001/api/evaluate/smoothness/ \
  -F "image=@signature.png"
```

**Execution Error**

```bash
curl -X POST http://localhost:8001/api/evaluate/execution-error/ \
  -H "Content-Type: application/json" \
  -d '{
    "expected_toolpath": [[0, 0], [10, 10], [20, 20]],
    "actual_toolpath": [[0, 1], [9, 11], [21, 19]]
  }'
```

### Python Examples

**Using requests library**

```python
import requests
import base64

# SSIM Evaluation
with open('original.png', 'rb') as f:
    original_b64 = base64.b64encode(f.read()).decode()
with open('reproduced.png', 'rb') as f:
    reproduced_b64 = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8001/api/evaluate/ssim/', json={
    'original_image_data': original_b64,
    'reproduced_image_data': reproduced_b64
})

if response.status_code == 200:
    result = response.json()
    print(f"SSIM Score: {result['ssim_score']}")
else:
    print(f"Error: {response.json()}")

# Smoothness Evaluation
with open('signature.png', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:8001/api/evaluate/smoothness/', files=files)

# Execution Error
response = requests.post('http://localhost:8001/api/evaluate/execution-error/', json={
    'expected_toolpath': [[0, 0], [10, 10], [20, 20]],
    'actual_toolpath': [[0, 1], [9, 11], [21, 19]]
})
```

## Image Format Support

### Supported Formats

- PNG
- JPEG/JPG
- SVG (converted to raster for processing)
- BMP
- GIF

### Recommendations

- **PNG**: Best for signatures and line art (lossless)
- **JPEG**: Acceptable for photographs (may introduce compression artifacts)
- **SVG**: Converted to raster format internally

### Size Limits

- Maximum file size: 10MB
- Recommended resolution: 500x500 to 2000x2000 pixels
- Memory optimization for PythonAnywhere 512MB limit

## Performance Characteristics

### Response Times (approximate)

- **Health Check**: < 10ms
- **SSIM Evaluation**: 100-500ms (depends on image size)
- **Smoothness Analysis**: 200-800ms (depends on image complexity)
- **Execution Error**: < 50ms (depends on toolpath length)

### Memory Usage

- Base service: ~50-80MB
- Per request overhead: 20-100MB (temporary processing)
- Optimized for 512MB total memory limit

## Integration with Core API

This Evaluation API is designed to work with the GCode Core API in a frontend-orchestrated architecture:

1. **Frontend** makes requests to both APIs
2. **Core API** handles data persistence and user management
3. **Evaluation API** handles compute-intensive processing
4. **No direct communication** between the two APIs

### Typical Workflow

1. User uploads signature to frontend
2. Frontend sends signature to Core API for conversion
3. Frontend sends images to Evaluation API for metrics
4. Frontend displays combined results

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider implementing rate limiting based on:

- Requests per minute per IP
- Concurrent request limits
- Resource usage monitoring

## Monitoring and Logging

### Log Levels

- **INFO**: Successful operations and metrics
- **ERROR**: Failed operations and exceptions
- **DEBUG**: Detailed processing information (development only)

### Health Monitoring

Use the `/health/` endpoint for service monitoring and uptime checks.

## Deployment Notes

### Environment Variables

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,yourapi.com
```

### Production Considerations

- Use proper WSGI server (gunicorn)
- Configure reverse proxy (nginx)
- Set up proper logging
- Monitor memory usage
- Implement proper error tracking

## Troubleshooting

### Common Issues

**"Invalid image data" errors**

- Ensure base64 data is properly encoded
- Check file format compatibility
- Verify file is not corrupted

**Memory errors**

- Reduce image size
- Process images sequentially, not in parallel
- Monitor total memory usage

**Timeout errors**

- Increase timeout limits for large images
- Consider image preprocessing/optimization
- Check system resources

### Debug Mode

Enable debug mode for detailed error information:

```env
DEBUG=True
```

⚠️ **Never use debug mode in production**

## API Versioning

Current version: **1.0.0**

Future versions will maintain backward compatibility where possible. Breaking changes will be introduced in major version updates with proper migration documentation.
