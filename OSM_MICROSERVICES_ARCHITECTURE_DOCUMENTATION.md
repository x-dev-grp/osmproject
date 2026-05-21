# OSM Project - Comprehensive Microservices Architecture Documentation

## 📋 Overview

The **OSM (Oil Supply Management) Project** is a comprehensive microservices-based enterprise application designed for managing oil production, financial operations, human resources, and security. Built using modern Spring Boot and Spring Cloud technologies, the system follows domain-driven design principles with clear separation of concerns across multiple services.

## 🏗️ Architecture Overview

### Technology Stack
- **Framework**: Spring Boot 3.4.4
- **Java Version**: 21
- **Spring Cloud**: 2024.0.1
- **Build Tool**: Maven
- **Database**: PostgreSQL (separate databases per service)
- **Service Discovery**: Netflix Eureka
- **API Gateway**: Spring Cloud Gateway
- **Security**: OAuth2 + JWT
- **Inter-Service Communication**: OpenFeign with Resilience4j
- **Documentation**: OpenAPI/Swagger

### System Architecture Pattern
- **Microservices Architecture** with domain-driven design
- **Service Discovery** via Eureka Server
- **API Gateway** for unified entry point
- **Circuit Breaker Pattern** for fault tolerance
- **Event-driven communication** via Feign clients
- **Multi-tenant database architecture**

## 🚀 Services Overview

### 1. Discovery Server (osm-eureka)
**Port**: 8761
**Purpose**: Service registry and discovery
**Technology**: Netflix Eureka Server

**Key Features**:
- Service registration and health monitoring
- Dynamic service discovery
- Load balancing capabilities
- 5-second eviction interval for failed instances

**Configuration**:
```yaml
server.port: 8761
eureka.client.register-with-eureka: false
eureka.client.fetch-registry: false
eureka.server.eviction-interval-timer-in-ms: 5000
```

### 2. API Gateway (osm-gateway)
**Port**: 8084
**Purpose**: Unified entry point and routing
**Technology**: Spring Cloud Gateway

**Key Features**:
- Centralized routing to all microservices
- OAuth2 resource server security
- Request/response filtering
- Load balancing
- CORS configuration

**Routing Configuration**:
```yaml
routes:
  - id: security-service
    uri: lb://security-service
    predicates: [Path=/api/security/**, /oauth2/**, /jwks/**]
  - id: oilproductionservice
    uri: lb://oilproductionservice
    predicates: [Path=/api/production/**]
  - id: financeservice
    uri: lb://financeservice
    predicates: [Path=/api/finance/**]
  - id: hrService
    uri: lb://hrService
    predicates: [Path=/api/hr/**]
```

### 3. Security Service (osm-sec)
**Port**: 8088
**Purpose**: Authentication, authorization, and user management
**Database**: osmsecurity
**Technology**: Spring Security + OAuth2 Authorization Server

**Key Features**:
- OAuth2 Authorization Server
- JWT token management
- User and role management
- RSA key pair management for JWT signing
- Automatic admin user bootstrapping
- Multi-tenant security context

**Key Endpoints**:
- `POST /oauth2/token` - Token generation
- `GET /oauth2/jwks` - JWT keys
- `GET /api/security/user/**` - User management
- `GET /api/security/rsa/**` - RSA key management

**Default Admin User**:
- Username: `osmAdmin`
- Password: `osmAdmin123`
- Email: `osmAdmin@example.com`
- Role: `OSMADMIN`

### 4. Production Service (osm-prod)
**Port**: 8083
**Purpose**: Oil production operations and supply chain management
**Database**: osmproduction
**Technology**: Spring Boot + JPA + Feign Clients

**Key Features**:
- **Oil Production Management**: Oil containers, transactions, quality control
- **Supplier Management**: Supplier types, deliveries, payments
- **Waste Management**: Waste tracking with financial transaction integration
- **Planning System**: Production planning and lot management
- **Quality Control**: Oil quality testing and validation
- **Storage Management**: Storage units and oil transactions
- **Mill Operations**: Mill machine management
- **Transport Coordination**: Transporter and delivery management

**Domain Models**:
- `OilSale`, `OilContainer`, `OilTransaction`
- `Waste`, `Supplier`, `Transporter`
- `UnifiedDelivery`, `MillMachine`, `StorageUnit`
- `QualityControlRule`, `QualityControlResult`
- `Parameter`, `Planning`

**Key Endpoints**:
```
/api/production/oil_sale/**          - Oil sales management
/api/production/waste/**             - Waste operations
/api/production/deliveries/**        - Delivery management
/api/production/suppliers_type/**    - Supplier operations
/api/production/planning/**          - Production planning
/api/production/oil_transaction/**   - Oil transactions
/api/production/storage-units/**     - Storage management
/api/production/qualitycontrolrules/** - Quality control
```

**Integrated Financial Transactions**:
- Automatic financial transaction creation for waste operations
- Payment processing integration with Finance service
- Uses dedicated waste endpoint for financial transactions

### 5. Finance Service (osm-fin)
**Port**: 8085
**Purpose**: Financial operations and transaction management
**Database**: osmfinance
**Technology**: Spring Boot + JPA + Circuit Breaker

**Key Features**:
- **Financial Transaction Management**: Complete transaction lifecycle
- **Oil Credit System**: Credit management for oil operations
- **Bank Account Management**: Multi-bank account support
- **Expense Tracking**: Comprehensive expense management
- **Waste Financial Integration**: Specialized waste transaction processing
- **Payment Processing**: Multiple payment method support
- **Resilience Patterns**: Circuit breaker and retry mechanisms

**Domain Models**:
- `FinancialTransaction`, `OilCredit`, `BankAccount`, `Expense`

**Key Endpoints**:
```
/api/finance/transactions/**         - Financial transactions
/api/finance/transactions/waste      - Waste-specific transactions
/api/finance/oil-credit/**          - Oil credit management
/api/finance/banks/**               - Bank account management
/api/finance/expense/**             - Expense management
```

**Waste Financial Integration**:
- Dedicated `/waste` endpoint for simplified transaction creation
- No payment processing - uses frontend data as-is
- Supports WASTE_SALE, WASTE_PAYMENT, WASTE_DISPOSAL_COST transaction types

**Resilience Configuration**:
```yaml
resilience4j:
  circuitbreaker:
    instances.genericService:
      failure-rate-threshold: 50%
      minimum-number-of-calls: 5
      wait-duration-in-open-state: 30s
  retry:
    instances.genericService:
      max-attempts: 3
      wait-duration: 2s
```

### 6. HR Service (osm-hr)
**Port**: 8086
**Purpose**: Human resources management
**Database**: osmRh
**Technology**: Spring Boot + JPA

**Key Features**:
- Employee management and HR operations
- Integrated with security service for user management
- Supports multi-tenant operations
- Circuit breaker patterns for external service calls

**Domain Models**:
- HR-specific entities (structure to be detailed based on requirements)

**Key Endpoints**:
```
/api/hr/**                          - HR operations
```

## 🔧 Shared Components

### Parent Module (osm-parent)
Central Maven parent project providing:
- Dependency management
- Common configurations
- Shared modules

### Base Module (xdev-base)
**Purpose**: Common utilities and base classes
**Key Components**:
- `BaseEntity` - Common entity framework
- `BaseController` - REST controller foundation
- `BaseService` - Service layer abstractions
- `OSMLogger` - Centralized logging utility
- `ApiResponse`/`ApiSingleResponse` - Standardized response formats
- File upload and management utilities
- PDF and Excel generation capabilities

### Security Module (xdev-security)
**Purpose**: Shared security configurations
**Key Components**:
- JWT token utilities
- OAuth2 configurations
- Security filters and interceptors
- Feign client security integration

### Communicator Module (comunicator)
**Purpose**: Inter-service communication framework
**Key Components**:
- `BaseFeignController` - Standardized Feign interfaces
- `BaseFeignService` - Service layer for Feign clients
- Shared DTOs and enums
- Circuit breaker configurations
- Exception handling for distributed calls

**Shared Enums**:
- `TransactionType` (WASTE_SALE, WASTE_PAYMENT, etc.)
- `PaymentMethod`, `Currency`, `TransactionDirection`
- `WasteType` (MARGINE, POMACE, VEGETAL_SOLIDS, OTHER)

## 🌐 Network and Deployment

### Port Configuration
```
8761 - Eureka Discovery Server
8084 - API Gateway
8088 - Security Service  
8083 - Production Service
8085 - Finance Service
8086 - HR Service
```

### Database Configuration
```
osmproduction - Production Service Database
osmfinance    - Finance Service Database
osmRh         - HR Service Database
osmsecurity   - Security Service Database
```

### Environment Variables Support
All services support environment-based configuration:
```
SERVER_PORT, DB_URL, DB_USER, DB_PASS
EUREKA_DEFAULT_ZONE, JWT_ISSUER_URI
MAIL_HOST, MAIL_USER, MAIL_PASS
```

## 🔐 Security Architecture

### OAuth2 Flow
1. **Client Authentication**: OAuth2 client credentials flow
2. **JWT Tokens**: RSA-signed JWT tokens for stateless authentication
3. **Resource Server**: All services act as OAuth2 resource servers
4. **Token Propagation**: Automatic JWT propagation via Feign clients

### Multi-tenant Security
- Tenant-based data isolation
- Header-based tenant identification (`X-Tenant-ID`)
- Secure cross-service communication

## 📊 Logging and Monitoring

### Centralized Logging
- **OSMLogger**: Standardized logging across all services
- **Method Entry/Exit**: Automatic method tracing
- **Performance Logging**: Execution time tracking
- **Business Event Logging**: Domain-specific event tracking
- **Exception Logging**: Comprehensive error tracking

### Log Levels Configuration
```yaml
logging:
  level:
    com.osm.*: DEBUG
    com.xdev.*: DEBUG
    org.springframework.security: DEBUG
    feign: DEBUG
    io.github.resilience4j: DEBUG
```

## 🚦 Integration Patterns

### Inter-Service Communication
- **OpenFeign Clients**: Type-safe HTTP clients
- **Circuit Breaker**: Resilience4j implementation
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Timeout Management**: Configurable timeouts per service

### Example Integration Flow (Waste Financial Transaction):
```
1. Frontend → Production Service (/api/production/waste/create-sale)
2. Production Service → Finance Service (/api/finance/transactions/waste)
3. Finance Service creates transaction using provided data as-is
4. Response propagated back through the chain
```

## 📈 Scalability and Performance

### Performance Optimizations
- **Connection Pooling**: Optimized database connections
- **Caching**: Strategic caching at service level
- **Async Processing**: Non-blocking operations where applicable
- **Load Balancing**: Built-in load balancing via Eureka

### Monitoring Capabilities
- **Health Checks**: Spring Boot Actuator integration
- **Circuit Breaker Metrics**: Real-time resilience monitoring
- **Performance Metrics**: Method-level performance tracking
- **Business Metrics**: Domain-specific KPI tracking

## 🛠️ Development and Testing

### Code Organization
- **Domain-Driven Design**: Clear domain boundaries
- **Layered Architecture**: Controller → Service → Repository
- **Dependency Injection**: Spring-managed dependencies
- **Configuration Management**: Environment-specific configs

### Testing Strategy
- **Unit Tests**: Service and controller layer testing
- **Integration Tests**: Cross-service integration validation
- **Contract Testing**: API contract verification
- **Performance Tests**: Load and stress testing capabilities

### Development Tools
- **Maven**: Build and dependency management
- **Docker**: Containerization support
- **OpenAPI**: API documentation generation
- **IDE Integration**: Full IntelliJ IDEA support

## 🔄 Deployment Architecture

### Docker Support
Each service includes Dockerfile for containerization:
```dockerfile
FROM maven:3.9.6-eclipse-temurin-21-alpine as build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE [PORT]
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Service Dependencies
```
1. Eureka Discovery Server (Independent)
2. Security Service (Depends on Eureka)
3. API Gateway (Depends on Eureka, Security)
4. Domain Services (Depend on Eureka, Security, optionally others)
```

## 📋 API Documentation

Each service exposes OpenAPI documentation:
- **Production Service**: `http://localhost:8083/swagger-ui.html`
- **Finance Service**: `http://localhost:8085/swagger-ui.html`
- **HR Service**: `http://localhost:8086/swagger-ui.html`
- **Security Service**: `http://localhost:8088/swagger-ui.html`

## 🎯 Business Capabilities

### Production Management
- Complete oil production lifecycle management
- Quality control and testing procedures
- Supplier relationship management
- Inventory and storage optimization
- Waste tracking and monetization

### Financial Operations
- Multi-currency transaction support
- Automated financial transaction creation
- Credit management systems
- Expense tracking and reporting
- Bank account reconciliation

### Human Resources
- Employee lifecycle management
- Integration with security and authentication
- Role-based access control
- Organizational structure management

### System Administration
- User and role management
- System configuration and parameters
- Audit logging and compliance
- Multi-tenant data management

## 🔍 Monitoring and Maintenance

### Health Monitoring
- Service health endpoints via Spring Boot Actuator
- Database connectivity monitoring
- External service dependency checks
- Real-time status dashboards

### Operational Metrics
- Request/response time tracking
- Error rate monitoring
- Circuit breaker status
- Business KPI tracking

## 📞 Support and Documentation

### Additional Documentation
- `CLIENT_FILE_UPLOAD_API_DOCUMENTATION.md` - File upload API reference
- `PAYMENT_LOGIC_IMPLEMENTATION_ANALYSIS.md` - Payment workflow analysis
- `LOGGING_OPTIMIZATION.md` - Logging best practices
- `PAYMENT_WORKFLOW_ANALYSIS.md` - Financial transaction flows

### Testing Resources
- Postman collections for API testing
- Environment configurations for different deployment stages
- Integration testing guides

This comprehensive architecture provides a robust, scalable, and maintainable platform for oil supply management operations with clear separation of concerns, strong security, and excellent observability.