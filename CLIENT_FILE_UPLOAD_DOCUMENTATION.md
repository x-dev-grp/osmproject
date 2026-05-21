# Client File Upload System Documentation

## Overview

The OSM system now supports client-specific file uploads with organized folder structures in Google Drive. Each client has their own dedicated folder space with sub-folders organized by entity types.

## Folder Structure

The system creates the following folder hierarchy in Google Drive:

```
OSM Base Folder/
└── clients/
    └── {clientId}/
        ├── DELIVERIES/
        │   └── {deliveryId}.{extension}
        ├── FINANCE_INVOICES/
        │   └── {invoiceId}.{extension}
        ├── FINANCE_RECEIPTS/
        │   └── {receiptId}.{extension}
        ├── FINANCE_CONTRACTS/
        │   └── {contractId}.{extension}
        ├── FINANCE_STATEMENTS/
        │   └── {statementId}.{extension}
        └── FINANCE_REPORTS/
            └── {reportId}.{extension}
```

## API Endpoints

### 1. Generic Client File Controller

**Base URL**: `/api/files/client`

#### Upload File
```http
POST /api/files/client/{clientId}/{entityName}/{objectId}/upload
Content-Type: multipart/form-data

Parameters:
- clientId: String - Client identifier
- entityName: String - Entity type (e.g., "CONTRACTS", "INVOICES")
- objectId: String - Specific object/record ID
- file: MultipartFile - The file to upload

Response:
{
  "success": true,
  "message": "File uploaded successfully",
  "data": "file-id-from-google-drive"
}
```

#### Download File
```http
GET /api/files/client/download/{fileId}

Response: Binary file content with appropriate headers
```

#### List Client Files
```http
GET /api/files/client/{clientId}/files?entityName={entityName}&pageSize=20&pageToken={token}

Response:
{
  "success": true,
  "message": "Files retrieved successfully",
  "data": [
    {
      "id": "file-id",
      "name": "filename.pdf",
      "size": 1048576,
      "mimeType": "application/pdf",
      "createdTime": "2024-01-15T10:30:45Z",
      "webViewLink": "https://drive.google.com/file/d/..."
    }
  ]
}
```

### 2. Production Service - Delivery Files

**Base URL**: `/api/production/deliveries`

#### Upload Delivery File
```http
POST /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/upload
Content-Type: multipart/form-data

Parameters:
- clientId: String - Client identifier
- deliveryId: String - Delivery ID
- file: MultipartFile - The file to upload
- category: String (optional) - File category
- description: String (optional) - File description
```

#### Download Delivery File
```http
GET /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/download/{fileId}
```

#### List Delivery Files
```http
GET /api/production/deliveries/client/{clientId}/delivery/{deliveryId}/files
```

### 3. Finance Service - Financial Documents

**Base URL**: `/api/finance/client`

#### Upload Financial Document
```http
POST /api/finance/client/{clientId}/{entityType}/{recordId}/upload
Content-Type: multipart/form-data

Parameters:
- clientId: String - Client identifier
- entityType: String - Document type (INVOICES, RECEIPTS, CONTRACTS, STATEMENTS, etc.)
- recordId: String - Record ID
- file: MultipartFile - The file to upload
- description: String (optional) - Document description

Supported Entity Types:
- INVOICES
- RECEIPTS
- CONTRACTS
- STATEMENTS
- TRANSACTIONS
- REPORTS
- CERTIFICATES
- EXPENSES
```

#### Download Financial Document
```http
GET /api/finance/client/download/{fileId}
```

#### List Financial Documents
```http
GET /api/finance/client/{clientId}/{entityType}/files?pageSize=20&pageToken={token}
```

#### Get Available Finance Entities
```http
GET /api/finance/client/{clientId}/entities

Response:
{
  "success": true,
  "data": ["INVOICES", "RECEIPTS", "CONTRACTS", "STATEMENTS", "TRANSACTIONS", "REPORTS", "CERTIFICATES"]
}
```

## Security & Access Control

### Authentication
All endpoints require authentication via JWT tokens. The system uses the security context to:
- Validate user permissions
- Track file upload/download activities
- Audit file operations

### Authorization
- Users can only access files for clients they have permission to
- Client-specific isolation is enforced at the storage level
- Entity-based access control is supported

### File Validation
- **Size Limit**: 25MB per file (configurable via Spring Boot)
- **Type Validation**: Supports common business file types
- **Security Scanning**: Basic MIME type validation (extensible for virus scanning)

## Supported File Types

The system accepts the following file types:
- Documents: PDF, DOC, DOCX, TXT
- Spreadsheets: XLS, XLSX, CSV
- Images: JPEG, PNG, GIF
- Archives: ZIP
- Others: Configurable via service configuration

## Configuration

### Spring Boot Configuration
```yaml
spring:
  servlet:
    multipart:
      max-file-size: 25MB
      max-request-size: 25MB

gdrive:
  enabled: true
  credentials: classpath:service-account.json
  applicationName: OSM
  baseFolderId: 19gcrwX-Q6Y2IVWUcjgAtXcpAoOrL6KXv
  tenantQuotaBytes: 0  # 0 = unlimited
```

### Google Drive Setup
1. Create a service account in Google Cloud Console
2. Enable Google Drive API
3. Generate and download service account JSON key
4. Share the base folder with the service account email
5. Configure the folder ID in application properties

## Error Handling

### Common Error Responses

#### Storage Service Unavailable
```json
{
  "success": false,
  "message": "File storage service not available",
  "data": null
}
```

#### File Not Found
```json
{
  "success": false,
  "message": "File not found",
  "data": null
}
```

#### File Too Large
```json
{
  "success": false,
  "message": "File size exceeds 25MB limit",
  "data": null
}
```

#### Invalid Entity Type
```json
{
  "success": false,
  "message": "Invalid entity type for finance service",
  "data": null
}
```

## Usage Examples

### Frontend Integration (Angular/TypeScript)

```typescript
// Upload file for a client
uploadClientFile(clientId: string, entityType: string, recordId: string, file: File): Observable<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  return this.http.post(
    `/api/finance/client/${clientId}/${entityType}/${recordId}/upload`,
    formData
  );
}

// Download file
downloadFile(fileId: string): Observable<Blob> {
  return this.http.get(`/api/files/client/download/${fileId}`, {
    responseType: 'blob'
  });
}

// List client files
listClientFiles(clientId: string, entityType: string): Observable<any> {
  return this.http.get(`/api/finance/client/${clientId}/${entityType}/files`);
}
```

### Backend Integration (Java)

```java
// Using the ClientFileService
@Autowired
private ClientFileService clientFileService;

public FileUploadResponseDto uploadFile(String clientId, String entityName, 
                                       String objectId, MultipartFile file) {
    FileUploadRequestDto request = new FileUploadRequestDto(clientId, entityName, objectId);
    return clientFileService.uploadFile(request, file, authentication);
}
```

## Monitoring & Logging

### Log Events
- File upload/download operations
- Client access patterns
- Error occurrences
- Performance metrics

### Metrics
- Upload/download counts per client
- Storage usage per client
- File type distribution
- Error rates

## Best Practices

### File Organization
1. Use consistent naming conventions for objectIds
2. Organize files by logical entity types
3. Include metadata in file descriptions
4. Use appropriate file categories

### Performance
1. Implement pagination for file listings
2. Use streaming for large file downloads
3. Consider caching for frequently accessed files
4. Monitor storage quotas

### Security
1. Validate file types before upload
2. Scan files for malware (recommended)
3. Implement access logging
4. Regular security audits

## Future Enhancements

### Planned Features
1. **File Versioning**: Track file versions and changes
2. **Bulk Operations**: Upload/download multiple files
3. **Advanced Search**: Search files by metadata
4. **Automated Cleanup**: Remove old or unnecessary files
5. **Integration**: Direct frontend upload with signed URLs
6. **Notifications**: Email notifications for file operations

### Scalability Improvements
1. **Multiple Storage Providers**: Support for AWS S3, Azure Blob
2. **CDN Integration**: Faster file delivery
3. **Async Processing**: Background file processing
4. **Load Balancing**: Distribute file operations

## Troubleshooting

### Common Issues

1. **Storage Provider Not Configured**
   - Ensure Google Drive credentials are properly configured
   - Check service account permissions

2. **File Upload Fails**
   - Verify file size limits
   - Check network connectivity
   - Validate file type restrictions

3. **Files Not Found**
   - Confirm client ID and entity name are correct
   - Check folder permissions in Google Drive
   - Verify file wasn't deleted

4. **Performance Issues**
   - Monitor Google Drive API quotas
   - Check network bandwidth
   - Consider file size optimization