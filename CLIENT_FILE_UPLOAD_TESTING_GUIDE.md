# OSM Client File Upload Testing Guide

## Quick Start

### 1. Import Postman Collection
1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `CLIENT_FILE_UPLOAD_POSTMAN_COLLECTION.json`
4. Import `CLIENT_FILE_UPLOAD_POSTMAN_ENVIRONMENT.json`

### 2. Configure Environment
1. Select "OSM Client File Upload Environment"
2. Update these critical variables:
   - `jwt_token`: Your actual JWT authentication token
   - `base_url`: Your API server URL (default: http://localhost:8080)
   - `client_id`: Test client identifier (default: CLIENT_001)

### 3. Prepare Test Files
Create sample test files in different formats:
- **PDF**: `test_contract.pdf` (under 25MB)
- **Word**: `test_invoice.docx`
- **Excel**: `test_report.xlsx`  
- **Image**: `test_photo.jpg`
- **Large File**: `large_test.pdf` (over 25MB for error testing)

---

## Test Scenarios

### 🧪 **Test Suite 1: Generic Client File Upload**

#### Test 1.1: Successful File Upload
**Endpoint:** `POST /api/files/client/{clientId}/{entityName}/{objectId}/upload`

**Steps:**
1. Select "Upload Client File" request
2. Attach a test PDF file (under 25MB)
3. Ensure JWT token is set in environment
4. Send request

**Expected Results:**
- ✅ Status Code: 200
- ✅ Response: `{"success": true, "message": "File uploaded successfully", "data": "file-id"}`
- ✅ File ID is returned and stored in `test_file_id` variable

**Validation:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success true", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.eql(true);
});

pm.test("File ID is returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data).to.not.be.empty;
});
```

#### Test 1.2: Download Uploaded File
**Endpoint:** `GET /api/files/client/download/{fileId}`

**Prerequisites:** Test 1.1 must pass to populate `test_file_id`

**Steps:**
1. Select "Download Client File" request
2. Verify `test_file_id` is populated from previous test
3. Send request

**Expected Results:**
- ✅ Status Code: 200
- ✅ Binary file content returned
- ✅ `Content-Disposition` header with filename
- ✅ Appropriate `Content-Type` header

#### Test 1.3: Get File Metadata
**Endpoint:** `GET /api/files/client/metadata/{fileId}`

**Expected Results:**
```json
{
  "success": true,
  "message": "File metadata retrieved",
  "data": {
    "id": "file-id",
    "name": "filename.pdf",
    "size": 1048576,
    "mimeType": "application/pdf",
    "createdTime": "2024-01-15T10:30:45Z",
    "modifiedTime": "2024-01-15T10:30:45Z",
    "webViewLink": "https://drive.google.com/..."
  }
}
```

#### Test 1.4: List Client Files
**Endpoint:** `GET /api/files/client/{clientId}/files`

**Query Parameters:**
- `entityName=CONTRACTS`
- `pageSize=20`

**Expected Results:**
- ✅ Status Code: 200
- ✅ Array of file objects returned
- ✅ Each file object contains required metadata fields

#### Test 1.5: Find File by Object ID
**Endpoint:** `GET /api/files/client/{clientId}/{entityName}/{objectId}`

**Expected Results:**
- ✅ Status Code: 200 (if file exists) or 404 (if not found)
- ✅ File metadata returned if found

---

### 🧪 **Test Suite 2: Finance Service File Upload**

#### Test 2.1: Upload Financial Document
**Endpoint:** `POST /api/finance/client/{clientId}/{entityType}/{recordId}/upload`

**Test Data:**
- `entityType`: INVOICES, RECEIPTS, CONTRACTS, STATEMENTS
- `recordId`: INV_2024_001, REC_2024_001, etc.
- Include `description` in form data

**Steps:**
1. Select "Upload Financial Document" request
2. Set entity type to "INVOICES"
3. Attach test invoice PDF
4. Add description: "Sample invoice document"
5. Send request

**Expected Results:**
- ✅ Status Code: 200
- ✅ Success message mentioning "Financial document uploaded successfully"
- ✅ File stored with "FINANCE_" prefix in entity path

#### Test 2.2: Invalid Entity Type
**Endpoint:** `POST /api/finance/client/{clientId}/INVALID_TYPE/{recordId}/upload`

**Expected Results:**
- ✅ Status Code: 400
- ✅ Error message: "Invalid entity type for finance service"

#### Test 2.3: List Financial Documents
**Endpoint:** `GET /api/finance/client/{clientId}/{entityType}/files`

**Expected Results:**
- ✅ Status Code: 200
- ✅ Array of financial documents
- ✅ Only documents of specified entity type returned

#### Test 2.4: Get Finance Entity Types
**Endpoint:** `GET /api/finance/client/{clientId}/entities`

**Expected Results:**
```json
{
  "success": true,
  "message": "Finance entities retrieved",
  "data": [
    "INVOICES", "RECEIPTS", "CONTRACTS", "STATEMENTS",
    "TRANSACTIONS", "REPORTS", "CERTIFICATES"
  ]
}
```

---

### 🧪 **Test Suite 3: Production Service File Upload**

#### Test 3.1: Upload Delivery File
**Endpoint:** `POST /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/upload`

**Form Data:**
- `file`: Delivery document PDF
- `category`: "DELIVERY_NOTE"
- `description`: "Delivery documentation"

**Expected Results:**
- ✅ Status Code: 200
- ✅ File uploaded successfully
- ✅ File stored in DELIVERIES entity folder

#### Test 3.2: Download Delivery File
**Endpoint:** `GET /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/download/{fileId}`

#### Test 3.3: List Delivery Files
**Endpoint:** `GET /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/files`

---

### 🧪 **Test Suite 4: Error Handling**

#### Test 4.1: Empty File Upload
**Setup:** Attach an empty file or no file

**Expected Results:**
- ✅ Status Code: 400
- ✅ Error message: "File cannot be empty"

#### Test 4.2: File Too Large
**Setup:** Attach file larger than 25MB

**Expected Results:**
- ✅ Status Code: 400 or 413
- ✅ Error message mentioning file size limit

#### Test 4.3: Invalid Authentication
**Setup:** Remove or corrupt JWT token

**Expected Results:**
- ✅ Status Code: 401
- ✅ Authentication error message

#### Test 4.4: Non-existent File Download
**Setup:** Use invalid file ID

**Expected Results:**
- ✅ Status Code: 404
- ✅ File not found response

#### Test 4.5: Storage Service Unavailable
**Setup:** Stop Google Drive service or misconfigure

**Expected Results:**
- ✅ Status Code: 503
- ✅ Error message: "File storage service not available"

---

### 🧪 **Test Suite 5: Security Testing**

#### Test 5.1: Cross-Client Access
**Setup:** Try to access Client A's files using Client B's credentials

**Expected Results:**
- ✅ Status Code: 403 or 404
- ✅ Access denied or file not found

#### Test 5.2: Malicious File Upload
**Setup:** Upload executable or script files

**Expected Results:**
- ✅ Status Code: 400
- ✅ File type validation error

#### Test 5.3: Path Traversal
**Setup:** Use malicious filenames with "../" patterns

**Expected Results:**
- ✅ Status Code: 400
- ✅ Filename sanitization prevents path traversal

---

### 🧪 **Test Suite 6: Performance Testing**

#### Test 6.1: Response Time
**Validation:**
```javascript
pm.test("Response time is less than 5000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

#### Test 6.2: Concurrent Uploads
**Setup:** Run multiple upload requests simultaneously

**Expected Results:**
- ✅ All requests complete successfully
- ✅ No race conditions or conflicts
- ✅ Acceptable response times maintained

#### Test 6.3: Large File Handling
**Setup:** Upload files of various sizes (1MB, 5MB, 10MB, 20MB)

**Expected Results:**
- ✅ All files under 25MB upload successfully
- ✅ Response times scale appropriately with file size

---

## Test Data Management

### Sample Test Files

Create these test files for comprehensive testing:

```
test-files/
├── small/
│   ├── contract.pdf (1MB)
│   ├── invoice.docx (500KB)
│   └── receipt.jpg (200KB)
├── medium/
│   ├── report.xlsx (5MB)
│   ├── presentation.pdf (10MB)
│   └── manual.doc (8MB)
├── large/
│   ├── archive.zip (20MB)
│   └── video.mp4 (24MB)
└── invalid/
    ├── empty.txt (0 bytes)
    ├── huge.pdf (30MB)
    └── malicious.exe (executable)
```

### Test Client Data

```json
{
  "clients": [
    {
      "id": "CLIENT_001",
      "name": "Acme Oil Company",
      "entities": ["CONTRACTS", "INVOICES", "DELIVERIES"]
    },
    {
      "id": "CLIENT_002", 
      "name": "Global Energy Corp",
      "entities": ["RECEIPTS", "STATEMENTS", "REPORTS"]
    }
  ]
}
```

---

## Automated Testing Scripts

### Pre-request Script (Collection Level)
```javascript
// Set timestamp for unique object IDs
pm.collectionVariables.set("timestamp", Date.now());

// Generate unique test IDs
pm.collectionVariables.set("test_contract_id", `CONTRACT_${Date.now()}`);
pm.collectionVariables.set("test_invoice_id", `INV_${Date.now()}`);
pm.collectionVariables.set("test_delivery_id", `DEL_${Date.now()}`);

// Validate JWT token
const jwtToken = pm.collectionVariables.get('jwt_token');
if (!jwtToken || jwtToken === 'your-jwt-token-here') {
    console.error('⚠️ WARNING: JWT token is not set properly!');
    console.error('Please update the jwt_token collection variable with a valid token.');
}
```

### Global Test Script
```javascript
// Global response validation
pm.test('Response has required structure', function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('success');
    pm.expect(response).to.have.property('message');
    pm.expect(response).to.have.property('data');
});

// Performance validation
pm.test('Response time is acceptable', function () {
    pm.expect(pm.response.responseTime).to.be.below(10000);
});

// Log errors for debugging
if (pm.response.code >= 400) {
    console.error(`❌ Request failed: ${pm.response.code} ${pm.response.status}`);
    console.error(`Response: ${pm.response.text()}`);
}
```

---

## Test Reporting

### Collection Runner Configuration

1. **Iterations:** 1 (for functional testing) or 10+ (for load testing)
2. **Delay:** 1000ms between requests (to avoid rate limiting)
3. **Data File:** Optional CSV with test data
4. **Environment:** OSM Client File Upload Environment

### Expected Test Results

**Functional Testing (Single Run):**
- ✅ All upload tests: 100% pass rate
- ✅ All download tests: 100% pass rate  
- ✅ All metadata tests: 100% pass rate
- ✅ All error tests: 100% pass rate
- ✅ Average response time: < 2000ms

**Load Testing (10 Iterations):**
- ✅ Success rate: > 95%
- ✅ Average response time: < 5000ms
- ✅ No timeouts or connection errors
- ✅ All file operations complete successfully

### Generating Reports

1. **HTML Report:** Use Newman CLI for detailed HTML reports
2. **JSON Report:** Export results for automated analysis
3. **Dashboard:** Import results into monitoring dashboards

```bash
# Run tests with Newman CLI
newman run CLIENT_FILE_UPLOAD_POSTMAN_COLLECTION.json \
  -e CLIENT_FILE_UPLOAD_POSTMAN_ENVIRONMENT.json \
  -r html,json \
  --reporter-html-export test-report.html \
  --reporter-json-export test-results.json
```

---

## Troubleshooting Common Issues

### Issue 1: JWT Token Errors
**Symptoms:** 401 Unauthorized responses
**Solutions:**
- Verify token is valid and not expired
- Check token format (should start with 'Bearer ')
- Ensure token has required permissions

### Issue 2: File Upload Failures
**Symptoms:** 500 Internal Server Error on uploads
**Solutions:**
- Check file size (must be under 25MB)
- Verify file type is in allowed list
- Ensure Google Drive service is configured
- Check server logs for specific errors

### Issue 3: File Not Found Errors
**Symptoms:** 404 errors when downloading/accessing files
**Solutions:**
- Verify file ID is correct (should be Google Drive file ID)
- Check if file was deleted or moved
- Ensure client has access to the file
- Use list endpoints to verify file existence

### Issue 4: Permission Errors
**Symptoms:** 403 Forbidden responses
**Solutions:**
- Verify user has access to specified client
- Check Google Drive folder permissions
- Ensure service account has proper access
- Review user role assignments

### Issue 5: Performance Issues
**Symptoms:** Slow response times or timeouts
**Solutions:**
- Check network connectivity
- Monitor Google Drive API quotas
- Reduce file sizes for testing
- Check server resource utilization

---

## Test Environment Setup

### Local Development Setup

1. **Start OSM Services:**
   ```bash
   # Start Eureka Server (port 8761)
   java -jar osm-eureka-0.0.1-SNAPSHOT.jar
   
   # Start Gateway (port 8080)
   java -jar osm-gateway-0.0.1-SNAPSHOT.jar
   
   # Start Finance Service (port 8081)
   java -jar osm-fin-0.0.1-SNAPSHOT.jar
   
   # Start Production Service (port 8082)
   java -jar osm-prod-0.0.1-SNAPSHOT.jar
   ```

2. **Verify Services:**
   - Eureka Dashboard: http://localhost:8761
   - Gateway Health: http://localhost:8080/actuator/health
   - Services registered in Eureka

3. **Configure Google Drive:**
   - Service account JSON in classpath
   - Base folder shared with service account
   - Proper folder ID in configuration

### Test Data Cleanup

After testing, clean up test files:

1. **Manual Cleanup:**
   - Delete test files from Google Drive
   - Remove test client folders
   - Clear test database records

2. **Automated Cleanup Script:**
   ```javascript
   // Postman cleanup script
   const testFileIds = [
       pm.collectionVariables.get('test_file_id'),
       pm.collectionVariables.get('finance_file_id'),
       pm.collectionVariables.get('delivery_file_id')
   ];
   
   // Store for cleanup (implement actual deletion logic)
   pm.collectionVariables.set('files_to_cleanup', JSON.stringify(testFileIds));
   ```

---

## Continuous Integration

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                script {
                    // Start test environment
                    sh 'docker-compose up -d osm-services'
                    // Wait for services to be ready
                    sh 'sleep 60'
                }
            }
        }
        
        stage('API Testing') {
            steps {
                script {
                    // Run Postman tests
                    sh '''
                        newman run CLIENT_FILE_UPLOAD_POSTMAN_COLLECTION.json \
                          -e CLIENT_FILE_UPLOAD_POSTMAN_ENVIRONMENT.json \
                          -r junit,json \
                          --reporter-junit-export test-results.xml \
                          --reporter-json-export test-results.json
                    '''
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    // Stop test environment
                    sh 'docker-compose down'
                }
            }
        }
    }
    
    post {
        always {
            // Publish test results
            junit 'test-results.xml'
            // Archive test artifacts
            archiveArtifacts 'test-results.json'
        }
    }
}
```

---

## Advanced Testing Scenarios

### Multi-tenant Testing
1. Create multiple client environments
2. Verify file isolation between clients
3. Test concurrent access from different clients
4. Validate client-specific entity types

### API Version Testing
1. Test with different API versions
2. Verify backward compatibility
3. Test version header handling
4. Validate deprecation warnings

### Integration Testing
1. Test end-to-end workflows
2. Verify service-to-service communication
3. Test error propagation between services
4. Validate transaction consistency

### Disaster Recovery Testing
1. Test Google Drive service outage scenarios
2. Verify graceful degradation
3. Test backup and restore procedures
4. Validate error handling during outages

---

*This testing guide is maintained by the OSM QA Team. For testing questions or issues, please contact the testing team or create a support ticket.*