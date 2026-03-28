# Known Issues

## Compilation Errors

The library has the following pre-existing compilation errors that need to be fixed:

### 1. Missing trait bounds in BaseAggregate
```
error[E0277]: the trait bound `E: Clone` is not satisfied
  --> src/domain/aggregate.rs:41:17
```

**Fix**: Add `Clone` bound to `BaseAggregate` or remove the `Clone` requirement.

### 2. Missing trait bound for DomainError
```
error[E0405]: cannot find trait `DomainError` in this scope
  --> src/application/service.rs:35:40
```

**Fix**: Import `DomainError` trait or use a different error type.

### 3. Undefined type EventBus
```
error[E0425]: cannot find value `EventBus` in this scope
  --> src/application/service.rs:35:40
```

**Fix**: Import `EventBus` or remove the usage.

### 4. Unstable Rust features
```
error[E0658]: trait objects without an explicit `dyn` are unstable
```

**Fix**: Use `dyn Trait` syntax instead of bare trait objects.

### 5. Type parameter coverage
```
error[E0210]: type parameter `T` must be covered by another type
  --> src/application/dto.rs:28:6
```

**Fix**: Reorder type parameters or use an inner type.

## Priority

1. **High**: Fix compilation blockers (1-3)
2. **Medium**: Update to stable Rust (4)
3. **Low**: Improve type safety (5)
