# OSM Client File Upload API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URLs](#base-urls)
- [Common Response Format](#common-response-format)
- [Error Codes](#error-codes)
- [Generic Client File API](#generic-client-file-api)
- [Finance Service API](#finance-service-api)
- [Production Service API](#production-service-api)
- [File Types & Limitations](#file-types--limitations)
- [Testing with Postman](#testing-with-postman)
- [Code Examples](#code-examples)

## Overview

The OSM Client File Upload API provides a comprehensive system for managing client-specific file uploads across different business entities. The system implements a hierarchical folder structure in Google Drive with multi-tenant isolation.

### Key Features
- ✅ **Multi-tenant Architecture**: Each client has isolated file storage
- ✅ **Entity-based Organization**: Files organized by business entities (CONTRACTS, INVOICES, etc.)
- ✅ **Service-specific Endpoints**: Specialized endpoints for Finance and Production services
- ✅ **Comprehensive Security**: JWT authentication, file validation, and access control
- ✅ **Advanced File Management**: Upload, download, list, and metadata retrieval
- ✅ **Error Handling**: Detailed error responses with proper HTTP status codes

### Folder Structure
```
OSM Base Folder/
└── clients/
    └── {clientId}/
        ├── CONTRACTS/
        ├── INVOICES/
        ├── FINANCE_RECEIPTS/
        ├── FINANCE_CONTRACTS/
        ├── DELIVERIES/
        └── {entityName}/
            └── {objectId}.{extension}
```

## Authentication

All endpoints require JWT Bearer token authentication.

**Header Format:**
```http
Authorization: Bearer {jwt_token}
```

**Security Features:**
- JWT token validation on all endpoints
- User context tracking for audit purposes
- Role-based access control (where applicable)

## Base URLs

| Service | Base URL | Description |
|---------|----------|-------------|
| Generic Client Files | `/api/files/client` | Universal file operations |
| Finance Service | `/api/finance/client` | Financial document management |
| Production Service | `/api/production/deliveries/client` | Delivery-related files |

## Common Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

## Error Codes

| HTTP Code | Description | Common Causes |
|-----------|-------------|---------------|
| `200` | Success | Operation completed successfully |
| `400` | Bad Request | Invalid parameters, empty file, file too large |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | File or resource not found |
| `413` | Payload Too Large | File exceeds 25MB limit |
| `503` | Service Unavailable | Storage provider not configured |
| `500` | Internal Server Error | Server-side processing error |

---

# Generic Client File API

Base URL: `/api/files/client`

## Upload Client File

Upload a file for a specific client and entity.

**Endpoint:** `POST /{clientId}/{entityName}/{objectId}/upload`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `entityName` (path) - Entity type (e.g., "CONTRACTS", "INVOICES") (required)  
- `objectId` (path) - Specific object/record ID (required)
- `file` (form-data) - File to upload (required, max 25MB)

**Request Example:**
```http
POST /api/files/client/CLIENT_001/CONTRACTS/CONTRACT_001/upload
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}

file: [binary data]
```

**Response Example:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
}
```

**cURL Example:**
```bash
curl -X POST \
  "http://localhost:8080/api/files/client/CLIENT_001/CONTRACTS/CONTRACT_001/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

## Download Client File

Download a file by its unique file ID.

**Endpoint:** `GET /download/{fileId}`

**Parameters:**
- `fileId` (path) - Google Drive file ID (required)

**Request Example:**
```http
GET /api/files/client/download/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
Authorization: Bearer {jwt_token}
```

**Response:**
- Binary file content with appropriate headers
- `Content-Disposition: attachment; filename="filename.ext"`
- `Content-Type: {mime_type}`

**cURL Example:**
```bash
curl -X GET \
  "http://localhost:8080/api/files/client/download/FILE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o downloaded_file.pdf
```

## Get File Metadata

Retrieve metadata information for a specific file.

**Endpoint:** `GET /metadata/{fileId}`

**Parameters:**
- `fileId` (path) - Google Drive file ID (required)

**Response Example:**
```json
{
  "success": true,
  "message": "File metadata retrieved",
  "data": {
    "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "name": "CONTRACT_001.pdf",
    "size": 1048576,
    "mimeType": "application/pdf",
    "createdTime": "2024-01-15T10:30:45Z",
    "modifiedTime": "2024-01-15T10:30:45Z",
    "webViewLink": "https://drive.google.com/file/d/...",
    "appProperties": {
      "tenantId": "CLIENT_001",
      "entity": "CONTRACTS",
      "uploadedAt": "1705312245000"
    }
  }
}
```

## List Client Files

List files for a specific client, optionally filtered by entity.

**Endpoint:** `GET /{clientId}/files`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `entityName` (query) - Entity type filter (optional)
- `pageSize` (query) - Number of results per page (default: 20, max: 100)
- `pageToken` (query) - Pagination token (optional)

**Request Example:**
```http
GET /api/files/client/CLIENT_001/files?entityName=CONTRACTS&pageSize=20
Authorization: Bearer {jwt_token}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Files retrieved successfully",
  "data": [
    {
      "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
      "name": "CONTRACT_001.pdf",
      "size": 1048576,
      "mimeType": "application/pdf",
      "createdTime": "2024-01-15T10:30:45Z",
      "webViewLink": "https://drive.google.com/file/d/..."
    }
  ]
}
```

## Find Client File by Object ID

Find a specific file by client ID, entity, and object ID.

**Endpoint:** `GET /{clientId}/{entityName}/{objectId}`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `entityName` (path) - Entity type (required)
- `objectId` (path) - Object/record ID (required)

**Response:** Same as Get File Metadata, or 404 if not found.

---

# Finance Service API

Base URL: `/api/finance/client`

## Upload Financial Document

Upload financial documents with finance-specific validation and entity types.

**Endpoint:** `POST /{clientId}/{entityType}/{recordId}/upload`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `entityType` (path) - Financial entity type (required)
- `recordId` (path) - Financial record ID (required)
- `file` (form-data) - File to upload (required)
- `description` (form-data) - Document description (optional)

**Valid Entity Types:**
- `INVOICES` - Customer invoices
- `RECEIPTS` - Payment receipts  
- `CONTRACTS` - Financial contracts
- `STATEMENTS` - Financial statements
- `TRANSACTIONS` - Transaction records
- `REPORTS` - Financial reports
- `CERTIFICATES` - Financial certificates
- `EXPENSES` - Expense documents

**Request Example:**
```http
POST /api/finance/client/CLIENT_001/INVOICES/INV_2024_001/upload
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}

file: [binary data]
description: "Invoice for Q1 2024 oil delivery"
```

**Response Example:**
```json
{
  "success": true,
  "message": "Financial document uploaded successfully",
  "data": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
}
```

**Storage Path:** Files are stored with "FINANCE_" prefix: `clients/{clientId}/FINANCE_INVOICES/{recordId}.pdf`

## Download Financial Document

**Endpoint:** `GET /download/{fileId}`

Same as generic download but optimized for financial documents.

## List Financial Documents

List financial documents for a specific client and entity type.

**Endpoint:** `GET /{clientId}/{entityType}/files`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `entityType` (path) - Financial entity type (required)
- `pageSize` (query) - Results per page (default: 20)
- `pageToken` (query) - Pagination token (optional)

**Request Example:**
```http
GET /api/finance/client/CLIENT_001/INVOICES/files?pageSize=20
Authorization: Bearer {jwt_token}
```

## Get Specific Financial Document

**Endpoint:** `GET /{clientId}/{entityType}/{recordId}`

Find a specific financial document by record ID.

## Get Available Finance Entity Types

Get all supported financial entity types for a client.

**Endpoint:** `GET /{clientId}/entities`

**Response Example:**
```json
{
  "success": true,
  "message": "Finance entities retrieved",
  "data": [
    "INVOICES",
    "RECEIPTS", 
    "CONTRACTS",
    "STATEMENTS",
    "TRANSACTIONS",
    "REPORTS",
    "CERTIFICATES"
  ]
}
```

---

# Production Service API

Base URL: `/api/production/deliveries/client`

## Upload Delivery File

Upload files related to oil delivery operations.

**Endpoint:** `POST /{clientId}/delivery/{deliveryId}/upload`

**Parameters:**
- `clientId` (path) - Client identifier (required)
- `deliveryId` (path) - Delivery ID (required)
- `file` (form-data) - File to upload (required)
- `category` (form-data) - File category (optional)
- `description` (form-data) - File description (optional)

**Request Example:**
```http
POST /api/production/deliveries/client/CLIENT_001/delivery/DEL_2024_001/upload
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}

file: [binary data]
category: "DELIVERY_NOTE"
description: "Delivery documentation for 1000L crude oil"
```

**Storage Path:** `clients/{clientId}/DELIVERIES/{deliveryId}.pdf`

## Download Delivery File

**Endpoint:** `GET /{clientId}/delivery/{deliveryId}/download/{fileId}`

Download a specific delivery file.

## List Delivery Files

**Endpoint:** `GET /{clientId}/delivery/{deliveryId}/files`

List all files associated with a specific delivery.

---

# File Types & Limitations

## Supported File Types

| Category | MIME Types | Extensions |
|----------|------------|------------|
| **Documents** | `application/pdf`<br/>`application/msword`<br/>`application/vnd.openxmlformats-officedocument.wordprocessingml.document`<br/>`text/plain` | `.pdf`<br/>`.doc`<br/>`.docx`<br/>`.txt` |
| **Spreadsheets** | `application/vnd.ms-excel`<br/>`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`<br/>`text/csv` | `.xls`<br/>`.xlsx`<br/>`.csv` |
| **Images** | `image/jpeg`<br/>`image/png`<br/>`image/gif` | `.jpg`<br/>`.png`<br/>`.gif` |
| **Archives** | `application/zip` | `.zip` |

## File Limitations

- **Maximum File Size:** 25MB per file
- **Maximum Request Size:** 25MB total
- **File Name Length:** No specific limit (reasonable lengths recommended)
- **Concurrent Uploads:** No specific limit (rate limiting may apply)

## Security Measures

- **MIME Type Validation:** Server validates file MIME types
- **File Size Validation:** Both client and server-side validation
- **Authentication Required:** All endpoints require valid JWT tokens
- **Tenant Isolation:** Files are isolated per client
- **Audit Logging:** All operations are logged with user context

---

# Testing with Postman

## Import the Collection

1. Download the Postman collection: `CLIENT_FILE_UPLOAD_POSTMAN_COLLECTION.json`
2. Open Postman
3. Click "Import" → "Upload Files"
4. Select the downloaded collection file
5. Configure the environment variables

## Environment Variables

Set these variables in your Postman environment:

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8080` | API base URL |
| `jwt_token` | `eyJhbGciOiJIUzI1NiIs...` | JWT authentication token |
| `client_id` | `CLIENT_001` | Test client identifier |

## Test Scenarios

The collection includes comprehensive test scenarios:

### ✅ **Happy Path Tests**
- Upload files to all endpoints
- Download files by ID
- List files with pagination
- Get file metadata

### ✅ **Error Handling Tests**
- Empty file upload (400 error)
- Non-existent file download (404 error)
- Invalid entity types (400 error)
- Missing authentication (401 error)

### ✅ **Performance Tests**
- Response time validation (< 5000ms)
- File size handling
- Concurrent request handling

## Running Tests

1. **Set JWT Token:** Update the `jwt_token` variable with a valid token
2. **Select Test File:** Each upload request needs a test file attached
3. **Run Collection:** Use Postman's Collection Runner for automated testing
4. **Review Results:** Check test results and response logs

---

# Code Examples

## Frontend Integration (Angular/TypeScript)

### Service Implementation
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FileUploadService {
  private baseUrl = 'http://localhost:8080/api/files/client';

  constructor(private http: HttpClient) {}

  uploadClientFile(clientId: string, entityType: string, objectId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post(
      `${this.baseUrl}/${clientId}/${entityType}/${objectId}/upload`,
      formData
    );
  }

  downloadFile(fileId: string): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/download/${fileId}`,
      { responseType: 'blob' }
    );
  }

  listClientFiles(clientId: string, entityType?: string, pageSize: number = 20): Observable<any> {
    let url = `${this.baseUrl}/${clientId}/files?pageSize=${pageSize}`;
    if (entityType) {
      url += `&entityName=${entityType}`;
    }
    return this.http.get(url);
  }

  getFileMetadata(fileId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/metadata/${fileId}`);
  }
}
```

### Component Usage
```typescript
export class FileUploadComponent {
  constructor(private fileService: FileUploadService) {}

  onFileSelected(event: any, clientId: string, entityType: string, objectId: string) {
    const file = event.target.files[0];
    if (file) {
      this.fileService.uploadClientFile(clientId, entityType, objectId, file)
        .subscribe({
          next: (response) => {
            console.log('File uploaded successfully:', response.data);
          },
          error: (error) => {
            console.error('Upload failed:', error);
          }
        });
    }
  }

  downloadFile(fileId: string, fileName: string) {
    this.fileService.downloadFile(fileId)
      .subscribe(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        link.click();
        window.URL.revokeObjectURL(url);
      });
  }
}
```

## Backend Integration (Java/Spring Boot)

### Service Layer Usage
```java
@Service
public class DocumentManagementService {
    
    @Autowired
    private ClientFileService clientFileService;
    
    public FileUploadResponseDto uploadContractDocument(
            String clientId, 
            String contractId, 
            MultipartFile file,
            Authentication authentication) throws Exception {
        
        FileUploadRequestDto request = new FileUploadRequestDto();
        request.setClientId(clientId);
        request.setEntityName("CONTRACTS");
        request.setObjectId(contractId);
        request.setDescription("Contract documentation");
        
        return clientFileService.uploadFile(request, file, authentication);
    }
    
    public byte[] downloadDocument(String fileId) throws Exception {
        return clientFileService.downloadFile(fileId);
    }
    
    public List<StoredFileInfo> listClientDocuments(String clientId, String entityType) throws Exception {
        PageResult<StoredFileInfo> result = clientFileService.listClientFiles(
            clientId, entityType, 50, null);
        return result.getItems();
    }
}
```

### REST Controller Integration
```java
@RestController
@RequestMapping("/api/documents")
public class DocumentController {
    
    @Autowired
    private DocumentManagementService documentService;
    
    @PostMapping("/contracts/{clientId}/{contractId}/upload")
    public ResponseEntity<?> uploadContract(
            @PathVariable String clientId,
            @PathVariable String contractId,
            @RequestParam("file") MultipartFile file,
            Authentication authentication) {
        
        try {
            FileUploadResponseDto response = documentService.uploadContractDocument(
                clientId, contractId, file, authentication);
            return ResponseEntity.ok(new ApiSingleResponse<>(true, "Contract uploaded", response));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ApiSingleResponse<>(false, "Upload failed: " + e.getMessage(), null));
        }
    }
}
```

## Python Integration Example

```python
import requests
import json

class OSMFileClient:
    def __init__(self, base_url, jwt_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
    
    def upload_file(self, client_id, entity_type, object_id, file_path):
        """Upload a file to OSM client file system"""
        url = f"{self.base_url}/api/files/client/{client_id}/{entity_type}/{object_id}/upload"
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files, headers=self.headers)
        
        return response.json()
    
    def download_file(self, file_id, save_path):
        """Download a file by ID"""
        url = f"{self.base_url}/api/files/client/download/{file_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return True
        return False
    
    def list_files(self, client_id, entity_type=None, page_size=20):
        """List files for a client"""
        url = f"{self.base_url}/api/files/client/{client_id}/files"
        params = {'pageSize': page_size}
        if entity_type:
            params['entityName'] = entity_type
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

# Usage example
client = OSMFileClient('http://localhost:8080', 'your-jwt-token')

# Upload a file
result = client.upload_file('CLIENT_001', 'CONTRACTS', 'CONTRACT_001', '/path/to/contract.pdf')
print(f"Upload result: {result}")

# List files
files = client.list_files('CLIENT_001', 'CONTRACTS')
print(f"Found {len(files['data'])} files")
```

---

## Performance Considerations

### File Upload Optimization
- **File Compression:** Consider compressing large files before upload
- **Chunked Upload:** For very large files, implement chunked upload
- **Progress Tracking:** Implement upload progress indicators
- **Retry Logic:** Handle network failures with exponential backoff

### API Rate Limiting
- **Google Drive API:** Monitor quota usage and implement rate limiting
- **Concurrent Uploads:** Limit concurrent uploads per client
- **Bulk Operations:** Use batch operations for multiple file operations

### Caching Strategy
- **File Metadata:** Cache frequently accessed file metadata
- **Folder IDs:** Cache folder IDs to reduce Drive API calls
- **User Permissions:** Cache user permission lookups

---

## Security Best Practices

### Input Validation
- **File Type Verification:** Validate file content, not just MIME type
- **File Size Limits:** Enforce both client and server-side limits
- **Filename Sanitization:** Prevent path traversal attacks

### Access Control
- **JWT Validation:** Implement proper token validation and expiration
- **Role-Based Access:** Restrict access based on user roles
- **Audit Logging:** Log all file operations for compliance

### Data Protection
- **Encryption in Transit:** Use HTTPS for all API calls
- **Encryption at Rest:** Google Drive provides encryption at rest
- **Data Retention:** Implement data retention policies

---

## Troubleshooting Guide

### Common Issues

#### 1. "Storage provider not configured" (503 error)
**Cause:** Google Drive service account not properly configured
**Solution:** 
- Verify service account JSON is correctly placed
- Check base folder ID is valid
- Ensure service account has access to the base folder

#### 2. "File upload failed" (500 error)
**Cause:** Various Google Drive API issues
**Solution:**
- Check Google Drive API quotas
- Verify network connectivity
- Review server logs for specific error details

#### 3. "Invalid entity type" (400 error)
**Cause:** Using unsupported entity type for finance service
**Solution:**
- Use GET `/api/finance/client/{clientId}/entities` to get valid types
- Ensure entity type matches the service requirements

#### 4. File not found (404 error)
**Cause:** File was deleted or never existed
**Solution:**
- Verify file ID is correct
- Check if file was moved or deleted in Google Drive
- Use list endpoints to find available files

### Debugging Steps

1. **Check Authentication:** Verify JWT token is valid and not expired
2. **Validate Parameters:** Ensure all required parameters are provided
3. **Test File Size:** Verify file is under 25MB limit
4. **Check File Type:** Ensure file type is in allowed list
5. **Review Logs:** Check server logs for detailed error information
6. **Test with Postman:** Use provided collection to isolate issues

---

## Support and Maintenance

### Monitoring Endpoints
- **Health Check:** Monitor service availability
- **Metrics:** Track upload/download rates and error rates  
- **Quota Usage:** Monitor Google Drive API quota consumption

### Log Analysis
- **Error Patterns:** Identify common error scenarios
- **Performance Metrics:** Track response times and throughput
- **User Activity:** Monitor user access patterns

### Backup and Recovery
- **File Backup:** Implement automated backup strategies
- **Disaster Recovery:** Plan for Google Drive service outages
- **Data Migration:** Prepare for potential platform migrations

---

*This documentation is maintained by the OSM Development Team. For questions or issues, please contact the API team or create a support ticket.*