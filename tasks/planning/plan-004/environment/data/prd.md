# Product Requirements Document: Online Bookstore API

## Overview

We are building the backend REST API for an online bookstore. The API must
support browsing the catalog, customer accounts, a shopping cart, order
placement, and book reviews. This document describes the required capabilities;
the deliverable is a complete API design.

## Users

- **Guests** can browse and search the catalog and read reviews.
- **Customers** can register, log in, manage their profile, use a cart, place
  orders, view their order history, and write reviews for books they purchased.
- **Admins** can add, update, and remove books, and update order status.

## Functional Requirements

### Catalog
1. List books with pagination, filtering, and search.
2. Retrieve full details for a single book (title, author, ISBN, price,
   category, format, stock, cover image, publication date, average rating).
3. List all categories.

### Authentication & Accounts
4. Register a new customer account (email, password, name).
5. Log in and receive a JWT token with an expiry.
6. Retrieve and update the current user's profile, including shipping address.

### Administration
7. Add a new book to the catalog (admin only).
8. Update an existing book (admin only).
9. Remove a book from the catalog (admin only).

### Shopping Cart
10. Add a book to the cart with a quantity.
11. View the current cart contents and total price.
12. Remove an item from the cart.

### Orders
13. Place an order from the current cart, providing a shipping address.
14. List the current user's order history.
15. Retrieve details of a specific order.
16. Update an order's status (admin only): processing, shipped, delivered,
    cancelled.

### Reviews
17. Write a review (rating 1-5 and comment) for a purchased book.
18. List all reviews for a book, including the average rating.
19. Delete a review (review owner or admin).

## Non-Functional Requirements

- All write operations and account-specific reads require authentication.
- Catalog browsing and review reading are available to guests.
- Responses are JSON. List endpoints return pagination metadata.
- Prices are numbers; ratings are integers in the range 1-5.
