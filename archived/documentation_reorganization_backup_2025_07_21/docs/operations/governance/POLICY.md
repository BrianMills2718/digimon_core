---
status: living
---

# Policy-as-Code Guardrails (OPA/Rego)

## Overview
KGAS uses Open Policy Agent (OPA) and Rego policies to enforce security and compliance guardrails at runtime and in CI.

## Example Policy: Deny Export of Email Property
```rego
package kgas.export

deny_export_email {
  input.property == "email"
}
```
- This policy denies any export operation that includes the "email" property.

## Policy List
- **deny_export_email**: Prevents export of email addresses
- **allow_only_verified_users**: Restricts sensitive actions to verified users
- **limit_export_size**: Caps the number of records exported per request
- **enforce_pii_redaction**: Ensures PII is redacted before export

## Policy Management
- All policies are stored in `policies/` and loaded by OPA at runtime.
- CI runs `opa test` to validate policy compliance before merge.

---
For integration and reload instructions, see SECURITY.md and OPERATIONS.md. 