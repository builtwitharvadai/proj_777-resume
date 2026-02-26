## Description

<!-- Provide a clear and concise description of what this PR does -->

### Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (code improvement without changing functionality)
- [ ] Documentation update
- [ ] Configuration change
- [ ] Performance improvement
- [ ] Security fix

### Related Issues

<!-- Link related issues here using #issue_number -->

Fixes #
Closes #
Related to #

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing Checklist

<!-- Mark completed items with an 'x' -->

### Unit Tests
- [ ] All existing unit tests pass
- [ ] New unit tests added for new functionality
- [ ] Test coverage maintained or improved (minimum 80%)
- [ ] Edge cases are covered by tests

### Integration Tests
- [ ] Integration tests pass
- [ ] API endpoints tested (if applicable)
- [ ] Database migrations tested (if applicable)

### Manual Testing
- [ ] Tested locally in development environment
- [ ] Tested with Docker Compose
- [ ] Verified frontend functionality (if applicable)
- [ ] Verified backend functionality (if applicable)
- [ ] Tested error handling and edge cases

### Browser/Platform Testing (if frontend changes)
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile responsive design verified

## Security Considerations

<!-- Mark completed items with an 'x' -->

- [ ] No sensitive data (credentials, API keys, tokens) committed
- [ ] Input validation implemented where necessary
- [ ] SQL injection prevention measures in place
- [ ] XSS prevention measures implemented
- [ ] CSRF protection verified
- [ ] Authentication and authorization checks in place
- [ ] No new security vulnerabilities introduced
- [ ] Dependencies scanned for vulnerabilities
- [ ] Security best practices followed

## Code Quality

<!-- Mark completed items with an 'x' -->

- [ ] Code follows project style guidelines
- [ ] Linting passes (Flake8, ESLint)
- [ ] Type checking passes (MyPy for Python, TypeScript)
- [ ] Code is self-documenting with clear variable/function names
- [ ] Complex logic has explanatory comments
- [ ] No commented-out code left in files
- [ ] No console.log or debug print statements in production code
- [ ] Error handling is appropriate and comprehensive

## Documentation

<!-- Mark completed items with an 'x' -->

- [ ] Code documentation/docstrings added or updated
- [ ] README updated (if needed)
- [ ] API documentation updated (if applicable)
- [ ] Environment variables documented (if new ones added)
- [ ] Database schema changes documented (if applicable)
- [ ] Architecture decisions documented (if significant changes)

## Database Changes

<!-- Mark completed items with an 'x', or mark N/A if not applicable -->

- [ ] Database migrations created
- [ ] Migrations tested (upgrade and downgrade)
- [ ] Migration is reversible
- [ ] Database indexes added where appropriate
- [ ] Data migration plan documented (if needed)
- [ ] Backward compatibility considered
- [ ] N/A - No database changes

## Deployment Notes

<!-- Mark completed items with an 'x' -->

### Pre-deployment
- [ ] Environment variables documented
- [ ] Dependencies updated in requirements/package files
- [ ] Configuration changes documented

### Deployment Steps
<!-- List any special deployment steps or considerations -->

1.
2.
3.

### Post-deployment
- [ ] Health checks verified
- [ ] Monitoring and alerting configured
- [ ] Rollback plan documented
- [ ] Performance impact assessed

### Breaking Changes
<!-- If this PR introduces breaking changes, describe them here -->

- [ ] N/A - No breaking changes
- [ ] Breaking changes documented below:

<!-- Describe breaking changes and migration path -->

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No significant performance impact
- [ ] Performance improved
- [ ] Performance impact assessed and acceptable
- [ ] Load testing performed (if significant changes)

## Configuration Changes

<!-- Mark completed items with an 'x' -->

- [ ] No configuration changes required
- [ ] New environment variables added (documented above)
- [ ] Configuration file changes documented
- [ ] Docker Compose changes documented
- [ ] CI/CD pipeline changes documented

## Screenshots/Videos

<!-- If applicable, add screenshots or videos demonstrating the changes -->

### Before


### After


## Additional Context

<!-- Add any other context, considerations, or information reviewers should know -->

## Reviewer Checklist

<!-- For reviewers - mark items as you review -->

- [ ] Code changes reviewed and approved
- [ ] Tests are adequate and passing
- [ ] Documentation is complete and accurate
- [ ] Security considerations addressed
- [ ] No obvious performance issues
- [ ] Deployment plan is clear
- [ ] Breaking changes are acceptable and documented
- [ ] Overall architecture and design are sound

## Post-Merge Actions

<!-- List any actions that need to be taken after merging -->

- [ ] N/A
- [ ] Deploy to development environment
- [ ] Run database migrations
- [ ] Update documentation site
- [ ] Notify team of changes
- [ ] Monitor metrics and logs
