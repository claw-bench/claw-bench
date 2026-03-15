# API Reference Guide

### Error Handling

When an error occurs, the API returns a JSON object with an `error` field containing a human-readable message and a `code` field with a machine-readable error code.

Common error codes:
- `AUTH_FAILED` - Authentication failed
- `NOT_FOUND` - Resource not found
- `RATE_LIMITED` - Too many requests
- `INVALID_INPUT` - Invalid request parameters
- `SERVER_ERROR` - Internal server error

## Getting Started

To get started with the API, you need to obtain an API key from the developer portal.

#### Rate Limits

The API enforces rate limits to ensure fair usage:
- Free tier: 100 requests per minute
- Pro tier: 1000 requests per minute
- Enterprise tier: 10000 requests per minute

If you exceed the rate limit, you will receive a 429 status code.

## Authentication

All API requests must include an `Authorization` header with your API key.

```
Authorization: Bearer YOUR_API_KEY
```

There are two types of API keys:
- **Test keys** start with `tk_` and can only access sandbox data.
- **Live keys** start with `lk_` and access production data.

# Installation

Install the SDK using pip:

```
pip install ourapi-sdk
```

Or using npm for JavaScript:

```
npm install @ourapi/sdk
```

### Pagination

List endpoints support pagination using `page` and `per_page` parameters.

Example: `GET /api/users?page=2&per_page=25`

The response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "current_page": 2,
    "per_page": 25,
    "total_pages": 10,
    "total_items": 250
  }
}
```

## Endpoints

### Users

#### List Users

`GET /api/users`

Returns a paginated list of users.

Parameters:
- `page` (optional) - Page number, default 1
- `per_page` (optional) - Items per page, default 20
- `status` (optional) - Filter by status: active, inactive

#### Create User

`POST /api/users`

Creates a new user account.

Required fields:
- `name` - User's full name
- `email` - User's email address

Optional fields:
- `role` - User role (admin, member, viewer), default: member
- `department` - Department name

#### Get User

`GET /api/users/:id`

Returns details for a specific user.

### Orders

#### List Orders

`GET /api/orders`

Returns a paginated list of orders.

Parameters:
- `page` (optional) - Page number
- `status` (optional) - Filter by status: pending, completed, cancelled
- `date_from` (optional) - Filter orders from this date
- `date_to` (optional) - Filter orders to this date

#### Create Order

`POST /api/orders`

Creates a new order.

Required fields:
- `user_id` - ID of the user placing the order
- `items` - Array of item objects with `product_id` and `quantity`

#### Get Order

`GET /api/orders/:id`

Returns details for a specific order.

## Webhooks

Configure webhooks to receive real-time notifications about events.

Supported events:
- `user.created` - New user registered
- `user.updated` - User profile updated
- `order.created` - New order placed
- `order.completed` - Order fulfilled
- `order.cancelled` - Order cancelled

### Webhook Security

All webhook payloads are signed with your webhook secret. Verify the signature using the `X-Signature` header.

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Retry Policy

Failed webhook deliveries are retried up to 5 times with exponential backoff:
- 1st retry: 1 minute
- 2nd retry: 5 minutes
- 3rd retry: 30 minutes
- 4th retry: 2 hours
- 5th retry: 24 hours

## Quick Start Example

Here is a complete example to get you started:

```python
from ourapi import Client

client = Client(api_key="tk_your_test_key")

# Create a user
user = client.users.create(
    name="Jane Smith",
    email="jane@example.com"
)

# Create an order
order = client.orders.create(
    user_id=user.id,
    items=[
        {"product_id": "prod_123", "quantity": 2},
        {"product_id": "prod_456", "quantity": 1}
    ]
)

print(f"Order {order.id} created successfully!")
```

### SDK Configuration

The SDK can be configured with additional options:

```python
client = Client(
    api_key="tk_your_test_key",
    timeout=30,
    max_retries=3,
    base_url="https://api.example.com"
)
```

## Support

For help and support:
- Documentation: https://docs.example.com
- Email: support@example.com
- Community Forum: https://forum.example.com
- Status Page: https://status.example.com
