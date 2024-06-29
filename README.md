# Hike Retail Store

## Project Overview

Hike is an online B2C retail clothing store that efficiently manages operations through a comprehensive database management system. This system handles various aspects of the business, including inventory management, order processing, customer accounts, and membership rewards.

## Key Features

1. **Product Management**: 
   - Supports various clothing categories such as T-shirts, Jeans, Shirts, Jackets, Socks, and Pants.
   - Each product has a set of reviews, which are averaged and displayed to the user.

2. **Inventory Handling System**: 
   - Constantly checks stock levels in real-time and stores these requests in another table.
   - Once the order requirement hits a particular threshold, it sends the list of requirements to the manager for confirmation.
   - Ensures that Hike always has the right products available for customers to purchase.

3. **Customer Accounts**: 
   - Allows customers to log in/sign up to the online platform.
   - Customers can view available products, add items to their cart, and place orders through various payment methods.
   - Customers can add reviews of the products and return products within 14 days.

4. **Membership System**: 
   - Awards points for each purchase to the customer's account.
   - Upgrades membership levels based on points accumulated.

## Triggers

1. **Password Change Trigger**: 
   - Enforces password complexity rules and updates the password's hash in the database upon password change.

2. **Duplicate Email Check Trigger and Password Enforcement**: 
   - Ensures the email address is not already associated with an existing account and enforces password complexity rules during user registration.

3. **Update Quantity on Purchase**: 
   - Decreases the quantity of purchased items from the inventory.
   - Notifies administrators to restock when the quantity of an item falls below a certain threshold.

4. **Check Cart Item Quantity**: 
   - Ensures the quantity of each item entered in the cart does not exceed the current stock quantity.

5. **Add Membership Points**: 
   - Automatically adds membership points to customers proportional to 10% of the ordered amount after each order.
   - Upgrades the customer membership level based on points accumulated.

## Concurrency Management

The system includes a schema called `concurrency_manager` to handle concurrency locks, ensuring data integrity and consistency during simultaneous operations.
