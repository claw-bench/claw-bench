#!/usr/bin/env bash
# Oracle solution for sec-008-encryption-validation
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

audit = [
    {
        'component': 'web_server',
        'setting': 'tls_version',
        'current_value': 'TLS 1.0',
        'issue': 'TLS 1.0 is deprecated and has known vulnerabilities (POODLE, BEAST)',
        'recommendation': 'Upgrade to TLS 1.2 or TLS 1.3',
        'severity': 'critical'
    },
    {
        'component': 'web_server',
        'setting': 'cipher_suites',
        'current_value': 'TLS_RSA_WITH_RC4_128_SHA',
        'issue': 'RC4 cipher is broken and prohibited by RFC 7465',
        'recommendation': 'Use ECDHE-based cipher suites with AES-GCM (e.g., TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384)',
        'severity': 'critical'
    },
    {
        'component': 'password_storage',
        'setting': 'algorithm',
        'current_value': 'MD5',
        'issue': 'MD5 is cryptographically broken and unsuitable for password hashing',
        'recommendation': 'Use bcrypt, scrypt, or Argon2id with appropriate cost factors',
        'severity': 'critical'
    },
    {
        'component': 'file_encryption',
        'setting': 'algorithm',
        'current_value': 'DES',
        'issue': 'DES has a 56-bit key length and is trivially breakable with modern hardware',
        'recommendation': 'Use AES-256-GCM for authenticated encryption',
        'severity': 'critical'
    },
    {
        'component': 'file_encryption',
        'setting': 'mode',
        'current_value': 'ECB',
        'issue': 'ECB mode does not provide semantic security — identical plaintext blocks produce identical ciphertext',
        'recommendation': 'Use GCM or CBC mode with random IV',
        'severity': 'high'
    },
    {
        'component': 'email_service',
        'setting': 'tls_version',
        'current_value': 'TLS 1.1',
        'issue': 'TLS 1.1 is deprecated and has known weaknesses',
        'recommendation': 'Upgrade to TLS 1.2 or TLS 1.3',
        'severity': 'high'
    },
    {
        'component': 'email_service',
        'setting': 'certificate_validation',
        'current_value': False,
        'issue': 'Disabled certificate validation allows man-in-the-middle attacks',
        'recommendation': 'Enable certificate validation with trusted CA certificates',
        'severity': 'critical'
    },
    {
        'component': 'internal_api',
        'setting': 'transport_encryption',
        'current_value': 'none',
        'issue': 'No transport encryption exposes all data in transit to interception',
        'recommendation': 'Enable TLS 1.2+ for all API communication',
        'severity': 'critical'
    },
    {
        'component': 'internal_api',
        'setting': 'rsa_key_size',
        'current_value': 1024,
        'issue': 'RSA 1024-bit keys are considered insecure and can be factored',
        'recommendation': 'Use RSA 2048-bit or preferably 4096-bit keys',
        'severity': 'high'
    },
    {
        'component': 'internal_api',
        'setting': 'signing_algorithm',
        'current_value': 'SHA1withRSA',
        'issue': 'SHA-1 is deprecated for digital signatures due to collision attacks',
        'recommendation': 'Use SHA256withRSA or SHA384withRSA',
        'severity': 'high'
    }
]

with open('$WORKSPACE/crypto_audit.json', 'w') as f:
    json.dump(audit, f, indent=2)
"

echo "Solution written to $WORKSPACE/crypto_audit.json"
