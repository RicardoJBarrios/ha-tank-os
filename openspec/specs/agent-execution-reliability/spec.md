# Agent-Execution-Reliability Specification

## Purpose

This capability defines safe, observable execution policies so transient failures are recoverable while non-idempotent or unsafe operations are not repeated automatically.

## Requirements

### Requirement: The system SHALL classify failures before retrying

Failures MUST be classified as transient, permanent, cancelled, or timed out. Only transient failures for operations explicitly declared idempotent MAY be retried.

#### Scenario: Retry a transient idempotent failure
- **WHEN** an idempotent operation fails transiently and attempts remain
- **THEN** the policy schedules a bounded retry

#### Scenario: Do not retry a permanent or unsafe failure
- **WHEN** a permanent failure or non-idempotent operation fails
- **THEN** the policy returns a terminal decision without scheduling a retry

### Requirement: The system SHALL enforce bounded attempts and deadlines

Policies MUST define a maximum attempt count and execution deadline. The decision MUST expose the next delay, attempt number, and reason without exceeding configured bounds.

#### Scenario: Attempt limit is reached
- **WHEN** a transient failure occurs after the maximum attempt count
- **THEN** the policy returns terminal failure

#### Scenario: Deadline is exceeded
- **WHEN** the current time is at or beyond the execution deadline
- **THEN** the policy returns timed out and no retry is scheduled

### Requirement: The system SHALL represent cancellation explicitly

Cancellation MUST be distinguishable from failure and MUST prevent future retries for the execution.

#### Scenario: Cancel a retrying execution
- **WHEN** cancellation is requested before the next attempt
- **THEN** the policy returns cancelled and does not schedule another attempt
