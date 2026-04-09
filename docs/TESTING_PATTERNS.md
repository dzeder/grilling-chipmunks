# Testing Patterns

Quick reference for common testing patterns. Adapted from `addyosmani/agent-skills` testing-patterns with Ohanafy-specific additions.

## Test Structure (Arrange-Act-Assert)

```typescript
it('describes expected behavior', () => {
  // Arrange: Set up test data and preconditions
  const input = { title: 'Test Task', priority: 'high' };

  // Act: Perform the action being tested
  const result = createTask(input);

  // Assert: Verify the outcome
  expect(result.title).toBe('Test Task');
  expect(result.status).toBe('pending');
});
```

## Test Naming Conventions

```typescript
// Pattern: [unit] [expected behavior] [condition]
describe('OrderService.createOrder', () => {
  it('creates an order with default pending status', () => {});
  it('throws ValidationError when items array is empty', () => {});
  it('calculates total from line item quantities and prices', () => {});
});
```

## Mock at Boundaries Only

```
Mock these:                    Don't mock these:
├── Database calls             ├── Internal utility functions
├── HTTP requests              ├── Business logic
├── File system operations     ├── Data transformations
├── External API calls         ├── Validation functions
└── Time/Date (when needed)    └── Pure functions
```

## Ohanafy-Specific Patterns

### Salesforce API Mocking

```typescript
// Mock SF REST API responses for integration tests
const mockSfResponse = {
  totalSize: 1,
  done: true,
  records: [{ Id: '001xx000003ABCDEF', Name: 'Test Account' }]
};

jest.mock('./sf-client', () => ({
  query: jest.fn().mockResolvedValue(mockSfResponse)
}));
```

### Tray Webhook Simulation

```typescript
// Test HMAC signature validation
it('rejects webhooks with invalid HMAC signature', async () => {
  const payload = JSON.stringify({ event: 'order.created' });
  const invalidSignature = 'sha256=invalid';

  const response = await request(app)
    .post('/webhooks/tray')
    .set('X-Tray-Signature', invalidSignature)
    .send(payload)
    .expect(401);
});
```

### Tray Script Testing

Use `/test-script` skill for integration testing of Tray scripts. Follow the validate-transform-batch-output flow pattern.

## API / Integration Testing

```typescript
describe('POST /api/orders', () => {
  it('creates an order and returns 201', async () => {
    const response = await request(app)
      .post('/api/orders')
      .send({ items: [{ sku: 'BEV-001', qty: 10 }] })
      .set('Authorization', `Bearer ${testToken}`)
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      status: 'pending',
    });
  });

  it('returns 401 without authentication', async () => {
    await request(app)
      .post('/api/orders')
      .send({ items: [{ sku: 'BEV-001', qty: 10 }] })
      .expect(401);
  });
});
```

## Test Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|---|---|---|
| Testing implementation details | Breaks on refactor | Test inputs/outputs |
| Snapshot everything | No one reviews diffs | Assert specific values |
| Shared mutable state | Tests pollute each other | Setup/teardown per test |
| Testing third-party code | Wastes time | Mock the boundary |
| `test.skip` permanently | Dead code | Remove or fix it |
| Overly broad assertions | Doesn't catch regressions | Be specific |
| No async error handling | Swallowed errors | Always `await` async tests |
| Mocking internal logic | Brittle, locks implementation | Only mock at system boundaries |

## Salesforce Apex Testing

- Target 85%+ code coverage with meaningful assertions
- Bulkify test data (test with 200+ records)
- Use `Test.startTest()` / `Test.stopTest()` for governor limit isolation
- Never use `seeAllData=true`
- Assert both positive and negative cases

## Learned From

Adapted from `addyosmani/agent-skills` testing-patterns reference (2026-04-09), extended with Ohanafy platform-specific patterns (Salesforce, Tray, beverage supply chain).
