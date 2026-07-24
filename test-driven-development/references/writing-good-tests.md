# Writing Good Tests

Load this reference when writing or changing tests, mocks, fixtures, generated
artifact checks, or test-only helpers.

## Contents

1. Two gates
2. Name the break
3. Derive expectations independently
4. Exercise the real thing
5. Keep test-only behavior out of production
6. Mutation check
7. Quick checklist

## Two gates

Every useful test passes both gates:

1. It names a realistic production break that it catches.
2. It exercises observable behavior of the real component.

## Name the break

Before writing a test body, answer:

> What production change should make this test fail, and would that change be a
> bug rather than an intentional redesign?

If no realistic bug makes it fail, the test is probably a change detector,
framework test, or tautology.

Prefer:

- Wrong branch or handler.
- Missing side effect or state transition.
- Wrong boundary value.
- Missing authorization or validation.
- Incorrect payload, query, or externally visible error.

Avoid:

- Exact source text, private names, or formatting.
- Constants tested without exercising the behavior that depends on them.
- Constructors, getters, or forwarding methods with no behavior.
- Tests proving that a third-party framework behaves as documented.

For scripts and generated artifacts, run them against controlled input and
assert output, side effects, or exit status. Grepping the source only proves
that the source contains the searched text.

## Derive expectations independently

Do not use the code under test or one of its helpers to calculate the expected
value:

```typescript
// Tautology: the same implementation computes both sides.
const expected = buildQuery({ tag: 'urgent' });
expect(buildQuery({ tag: 'urgent' })).toBe(expected);

// Independent expectation.
expect(buildQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

Use literals, hand-checked fixtures, or a genuinely independent oracle.

## Exercise the real thing

Assert the behavior of the component, not the presence or call count of a mock.
Mocks earn their place only at slow, nondeterministic, or external boundaries.

Before mocking a method:

1. List its real side effects.
2. Keep side effects the test depends on real.
3. Mock the lower slow or external layer.
4. Mirror the complete documented response shape.
5. Use a separate fixture for success, error, and malformed branches.

If mock setup is larger than the behavior under test, prefer a small
integration test with real components.

## Keep test-only behavior out of production

A cleanup or inspection method used only by tests belongs in test utilities,
unless the production class genuinely owns that resource lifecycle. Do not
weaken production encapsulation solely to make a unit test convenient.

## Mutation check

Before finishing, mentally mutate the implementation:

- Change an argument or constant.
- Select the wrong branch.
- Remove a state change or side effect.
- Return an empty/default result.
- Remove handling for zero, empty, unauthorized, nil, or malformed input.

At least one test should fail for each realistic mutation that would matter to
users. A mutation nothing catches marks either unprotected behavior or a test
that does not prove what it claims.

## Quick checklist

- [ ] The test names one realistic bug it catches.
- [ ] The expected value is independently derived.
- [ ] The assertion observes a public result or side effect.
- [ ] Mocks replace only slow/external boundaries.
- [ ] Mock data mirrors the real response shape.
- [ ] Test-only helpers remain outside production classes.
- [ ] Relevant mutations would make at least one test fail.
