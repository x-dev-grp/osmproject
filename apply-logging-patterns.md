# Quick Reference: Applying Logging Patterns

## 1. Replace Logger Declaration

### Before:
```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

private static final Logger log = LoggerFactory.getLogger(YourClass.class);
```

### After:
```java
import org.slf4j.Logger;
import com.xdev.xdevbase.utils.LoggingUtils;

private static final Logger log = LoggingUtils.getLogger(YourClass.class);
```

## 2. Controller Method Pattern

### Before:
```java
@GetMapping("/endpoint")
public ResponseEntity<?> method() {
    log.info("Processing request");
    try {
        // ... business logic
        return ResponseEntity.ok(result);
    } catch (Exception e) {
        log.error("Error: {}", e.getMessage());
        return ResponseEntity.badRequest().body("Error");
    }
}
```

### After:
```java
@GetMapping("/endpoint")
public ResponseEntity<?> method() {
    LoggingUtils.logMethodEntry(log, "method");
    try {
        // ... business logic
        LoggingUtils.logInfo(log, "Request processed successfully");
        LoggingUtils.logMethodExit(log, "method", result);
        return ResponseEntity.ok(result);
    } catch (Exception e) {
        LoggingUtils.logError(log, "Error processing request", e);
        return ResponseEntity.badRequest().body("Error");
    }
}
```

## 3. Service Method Pattern

### Before:
```java
public void businessMethod(String param) {
    log.info("Processing with param: {}", param);
    // ... business logic
    log.info("Completed successfully");
}
```

### After:
```java
public void businessMethod(String param) {
    LoggingUtils.logMethodEntry(log, "businessMethod", "param", param);
    // ... business logic
    LoggingUtils.logInfo(log, "Business operation completed successfully");
    LoggingUtils.logMethodExit(log, "businessMethod");
}
```

## 4. Error Handling Pattern

### Before:
```java
try {
    // ... risky operation
} catch (Exception e) {
    log.error("Operation failed: {}", e.getMessage());
    throw new RuntimeException("Failed", e);
}
```

### After:
```java
try {
    // ... risky operation
} catch (Exception e) {
    LoggingUtils.logError(log, "Operation failed", e);
    throw new RuntimeException("Failed", e);
}
```

## 5. Warning Pattern

### Before:
```java
log.warn("User not found: {}", userId);
```

### After:
```java
LoggingUtils.logWarning(log, "User not found: {}", userId);
```

## 6. Info Pattern

### Before:
```java
log.info("Created entity with ID: {}", entityId);
```

### After:
```java
LoggingUtils.logInfo(log, "Created entity with ID: {}", entityId);
```

## 7. Debug Pattern (for detailed troubleshooting)

### Before:
```java
log.debug("Entering method with params: {}", params);
```

### After:
```java
LoggingUtils.logMethodEntry(log, "methodName", "params", params);
```

## Common Patterns Summary

| Old Pattern | New Pattern |
|-------------|-------------|
| `log.info("message")` | `LoggingUtils.logInfo(log, "message")` |
| `log.error("message", e)` | `LoggingUtils.logError(log, "message", e)` |
| `log.warn("message")` | `LoggingUtils.logWarning(log, "message")` |
| `log.debug("entering method")` | `LoggingUtils.logMethodEntry(log, "methodName")` |
| `log.debug("exiting method")` | `LoggingUtils.logMethodExit(log, "methodName")` |

## Benefits of New Pattern

1. **Automatic Trace ID**: Every log entry includes trace ID
2. **Service Context**: Service name automatically included
3. **Consistent Format**: All logs follow same structure
4. **Better Debugging**: Method entry/exit tracking
5. **Error Context**: Better error information with stack traces

## Migration Checklist

- [ ] Replace `LoggerFactory.getLogger()` with `LoggingUtils.getLogger()`
- [ ] Replace `log.info()` with `LoggingUtils.logInfo()`
- [ ] Replace `log.error()` with `LoggingUtils.logError()`
- [ ] Replace `log.warn()` with `LoggingUtils.logWarning()`
- [ ] Add method entry/exit logging for complex methods
- [ ] Update error handling to use new pattern
- [ ] Test logging output in development environment 