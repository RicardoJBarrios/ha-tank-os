# Tasks

## 1. Application Query

- [x] 1.1 Add an application query that selects the latest observation per parameter using measurement time or the recording-time fallback, and verify unit tests cover mixed timestamp bases, optional parameter filtering, empty results, and tied timestamps.
- [x] 1.2 Extend application tests to verify returned observations retain all serialized fields and expose the ordering timestamp and time basis without claiming validity.

## 2. Home Assistant Service

- [x] 2.1 Register a response-capable native service for the latest-observation query with the existing Tank and optional parameter selectors, and verify its service schema and response in Home Assistant integration tests.
- [x] 2.2 Document the new service and its response fields in the integration service metadata, and verify the documented filter and time-basis behavior matches the spec.

## 3. Integration Verification

- [x] 3.1 Run `pnpm quality:checks` and verify the full repository quality gate passes, including `pnpm test:python`.
- [x] 3.2 Run `openspec validate --all` and `pnpm validate:readiness --change expose-latest-observation-query`; verify structural validation and change readiness report their results separately.
