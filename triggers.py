def triggers_commands(cursor):
    cursor.execute("DROP TRIGGER IF EXISTS on_customer_login_attempt;")
    cursor.execute("DROP TRIGGER IF EXISTS password_change_trigger;")
    cursor.execute("DROP TRIGGER IF EXISTS check_duplicate_email;")
    cursor.execute("DROP TRIGGER IF EXISTS update_inventory_on_purchase;")
    cursor.execute("DROP TRIGGER IF EXISTS low_stock_notification;")
    cursor.execute("DROP TRIGGER IF EXISTS check_cart_item_quantity;")
    cursor.execute("DROP TRIGGER IF EXISTS update_membership_info;")

    #First Trigger: Login Counter
    cursor.execute(
'''CREATE TRIGGER on_customer_login_attempt
BEFORE INSERT ON Customer_Login
FOR EACH ROW
BEGIN
    DECLARE attempt_count INT;
    SET attempt_count = (SELECT COUNT(*) FROM Customer_Login_Attempts WHERE Username = NEW.Username AND DATE(Date_Time) = CURDATE());

    IF attempt_count >= 3 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exceeded maximum login attempts';
    END IF;
END;''')
    
    #Second Trigger: Password Change Trigger
    cursor.execute(
'''CREATE TRIGGER password_change_trigger
BEFORE UPDATE ON Customer_Login
FOR EACH ROW
BEGIN
    -- Check if the Password column is being updated
    IF NEW.Password IS NOT NULL THEN
        -- Enforce password complexity rules
        IF LENGTH(NEW.Password) < 8 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must be at least 8 characters long';
        END IF;

        IF NOT (NEW.Password REGEXP '[[:digit:]]' AND NEW.Password REGEXP '[[:lower:]]' AND NEW.Password REGEXP '[[:upper:]]' AND NEW.Password REGEXP '[[:punct:]]') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character';
        END IF;
    END IF;
END;''')
    
    #Third Trigger: Duplicate Email Check Trigger
    cursor.execute(
'''CREATE TRIGGER check_duplicate_email
BEFORE INSERT ON Customer_Login
FOR EACH ROW
BEGIN
    DECLARE email_count INT;
    SET email_count = (SELECT COUNT(*) FROM Customer_Login WHERE Username = NEW.Username);

    IF email_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email address already exists';
    END IF;
END;''')
    
    #Trigger 4: Update Quantity on Purchase: When a purchase is made, decrease the quantity of the purchased items from the inventory.
    cursor.execute(
'''CREATE TRIGGER update_inventory_on_purchase
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    UPDATE Product_Inventory
    SET Stock = Stock - NEW.Quantity
    WHERE Product_ID = NEW.Product_ID;
END;''')
    
#Trigger 5: Low Stock Notification: If the quantity of an item falls below a certain threshold, trigger an alert to notify administrators to restock.
    cursor.execute(
'''CREATE TRIGGER low_stock_notification
AFTER UPDATE ON Product_Inventory
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
    SET current_stock = NEW.Stock;
    
    IF current_stock <= 10 THEN
        -- Generate manager order for restocking
        INSERT INTO Manager_Orders (Product_ID, Quantity)
        VALUES (NEW.Product_ID, 50); -- Assuming 50 as the quantity to restock, you can adjust this value

        -- Update the ordered stock in the Product_Inventory table
        UPDATE Product_Inventory
        SET Stock = Stock + 50 -- Assuming 50 as the quantity ordered for restocking
        WHERE Product_ID = NEW.Product_ID;

        -- You can add additional logic here such as sending notifications to managers or logging the restocking order.
    END IF;
END;''')
    
#Trigger 6: Check Cart Item Quantity : To ensure that the quantity of each item entered in the cart is above the current stock quantity
    cursor.execute(
'''CREATE TRIGGER check_cart_item_quantity
BEFORE INSERT ON Cart_Items
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
    SET current_stock = (SELECT Stock FROM Product_Inventory WHERE Product_ID = NEW.Product_ID);
    
    IF NEW.Quantity > current_stock THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity in cart exceeds current stock quantity';
    END IF;
END;''')
    
# #Trigger 7: Add membership points : To create a trigger that automatically adds membership points to customers proportional to 10% of the ordered amount after each order
# # AND 
# # Membership Upgrade Trigger : Upgrades the customer membership level ("Bronze"-0 (by default),"Silver"-1000,"Gold"-2000) after each update on Membership Column in Customer.
#     cursor.execute(
# '''CREATE TRIGGER update_membership_info
# AFTER INSERT ON Orders
# FOR EACH ROW
# BEGIN
#     DECLARE order_total INT;
#     DECLARE points_to_add INT;
#     DECLARE new_membership VARCHAR(10);

#     -- Calculate the total amount of the order
#     SET order_total = NEW.Total_Amount;

#     -- Calculate the points to add (10% of the order total)
#     SET points_to_add = FLOOR(order_total * 0.1);

#     -- Update the customer's points
#     UPDATE Customer
#     SET Points = Points + points_to_add
#     WHERE Customer_ID = NEW.Customer_ID;

#     -- Check the new membership level based on points
#     IF (NEW.Points + points_to_add) >= 2000 THEN
#         SET new_membership = 'Gold';
#     ELSEIF (NEW.Points + points_to_add) >= 1000 THEN
#         SET new_membership = 'Silver';
#     ELSE
#         SET new_membership = 'Bronze';
#     END IF;
    
#     -- Update the membership level
#     UPDATE Customer
#     SET Membership = new_membership
#     WHERE Customer_ID = NEW.Customer_ID;
# END;''')
    
    print("Triggers created successfully!")