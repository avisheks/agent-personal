---
title: "hmac-request-signing"
summary: ""
sources:
  - claude-code/claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md
createdAt: 2026-07-30T16:50:09.765337+00:00
updatedAt: 2026-07-30T16:50:09.765337+00:00
---
# HMAC Request Signing

**HMAC Request Signing** is a cryptographic authentication mechanism used to verify the integrity and authenticity of API requests. It involves generating a Hash-based Message Authentication Code (HMAC) using a shared secret key and request data, which is then included with the request to prove it originated from an authorized client.

## Overview

HMAC request signing provides a way for servers to verify that incoming requests are legitimate and have not been tampered with during transmission. The client generates a signature using a cryptographic hash function (typically SHA-256) combined with a secret key known only to the client and server. This signature is sent alongside the request, allowing the server to independently compute the same signature and verify authenticity.

## Implementation in Claude Code

[[Claude Code]] implements HMAC request signing as part of its API security architecture. Every API request to Anthropic's servers includes a custom `cch` header containing a cryptographic signature. This signature is generated using HMAC-SHA256 and incorporates both the request content and a timestamp to prevent replay attacks. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

The signing mechanism serves multiple purposes in Claude Code's architecture. It enables Anthropic to implement rate limiting and abuse prevention by verifying that requests originate from genuine Claude Code clients rather than unauthorized API scrapers. The signature scheme follows standard security practices, using HMAC-SHA256 with the request body and timestamp as inputs to prevent both tampering and replay attacks. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

## Technical Implementation

The HMAC request signing process typically involves:

1. **Timestamp Generation**: Creating a current timestamp to include in the signature
2. **Message Construction**: Combining the request body with the timestamp
3. **Signature Generation**: Computing HMAC-SHA256 of the constructed message using a client-side secret
4. **Header Inclusion**: Adding the signature and timestamp to request headers
5. **Server Verification**: The server independently computes the signature and compares it with the received signature

## Security Properties

HMAC request signing provides several important security guarantees:

- **Authentication**: Verifies the request comes from a client possessing the correct secret key
- **Integrity**: Ensures the request content has not been modified in transit  
- **Replay Protection**: When combined with timestamps, prevents old requests from being reused maliciously
- **Non-repudiation**: Provides cryptographic proof of request origin

## Common Use Cases

HMAC request signing is widely used in production systems for:

- API authentication and authorization
- Webhook verification (ensuring callbacks come from legitimate sources)
- Rate limiting and abuse prevention
- Compliance with security standards requiring request authentication

## Related Concepts

HMAC request signing is often implemented alongside other security mechanisms such as [[permission-gating-system]]s and [[opentelemetry-agent-tracing]] for comprehensive API security and monitoring.
