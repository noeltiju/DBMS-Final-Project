def triggers_commands(cursor, connection):
    cursor.execute("DROP TRIGGER IF EXISTS password_change_trigger;")
    cursor.execute("DROP TRIGGER IF EXISTS enforce_password_complexity_and_unique_email;")
    cursor.execute("DROP TRIGGER IF EXISTS update_inventory_on_purchase;")
    cursor.execute("DROP TRIGGER IF EXISTS check_cart_item_quantity;")
    cursor.execute("DROP TRIGGER IF EXISTS add_membership_points;")

    cursor.execute(
"""CREATE TRIGGER password_change_trigger
BEFORE UPDATE ON Customer_Login
FOR EACH ROW
BEGIN
    IF NEW.Password IS NOT NULL THEN
        IF LENGTH(NEW.Password) < 8 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must be at least 8 characters long';
        END IF;

        IF NOT (NEW.Password REGEXP '[[:digit:]]' AND NEW.Password REGEXP '[[:lower:]]' AND NEW.Password REGEXP '[[:upper:]]' AND NEW.Password REGEXP '[[:punct:]]') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character';
        END IF;
    END IF;
END;""")
    connection.commit()





    cursor.execute(
"""CREATE TRIGGER enforce_password_complexity_and_unique_email
BEFORE INSERT ON Customer_Login
FOR EACH ROW
BEGIN
    IF NEW.Password IS NOT NULL THEN
        IF LENGTH(NEW.Password) < 8 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must be at least 8 characters long';
        END IF;

        IF NOT (NEW.Password REGEXP '[[:digit:]]' AND NEW.Password REGEXP '[[:lower:]]' AND NEW.Password REGEXP '[[:upper:]]' AND NEW.Password REGEXP '[[:punct:]]') THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character';
        END IF;
    END IF;

    IF NEW.Username IS NOT NULL THEN
        IF EXISTS (SELECT 1 FROM Customer_Login WHERE Username = NEW.Username) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email address already exists';
        END IF;
    END IF;
END;""")
    connection.commit()




    cursor.execute(
"""CREATE TRIGGER update_inventory_on_purchase
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
DECLARE curr_date DATE;

SELECT CURRENT_DATE() INTO curr_date;

    SELECT Stock into current_stock from Product_Inventory WHERE Product_ID = NEW.Product_ID;
    SET current_stock = current_stock - NEW.Quantity;
   
    IF current_stock <= 10 THEN
        INSERT INTO Manager_Alert (Product_ID, current_Quantity, Approval, Alert_Date)
        VALUES (NEW.Product_ID, current_stock, "NO",curr_date);
END IF;
   
    UPDATE Product_Inventory
    SET Stock = Stock - NEW.Quantity
    WHERE Product_ID = NEW.Product_ID;
END;""")
    connection.commit()




    cursor.execute(
"""CREATE TRIGGER check_cart_item_quantity
BEFORE INSERT ON Cart_Items
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
    SET current_stock = (SELECT Stock FROM Product_Inventory WHERE Product_ID = NEW.Product_ID);
   
    IF NEW.Quantity > current_stock THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity in cart exceeds current stock quantity';
    END IF;
END;""")
    connection.commit()



    cursor.execute(
"""CREATE TRIGGER add_membership_points
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    DECLARE order_total INT;
    DECLARE points_to_add INT;
DECLARE total_points INT;
    DECLARE new_membership VARCHAR(10);
    DECLARE current_Points INT;
   
    SET order_total = NEW.Total_Amount;

    SELECT Points INTO current_Points FROM Customer WHERE Customer_ID = NEW.Customer_ID;

    SET points_to_add = FLOOR(order_total * 0.1);
   
SET total_points = current_Points + points_to_add;
   
IF total_points >= 2000 THEN
        SET new_membership = 'Gold';
    ELSEIF total_points >= 1000 THEN
        SET new_membership = 'Silver';
    ELSE
        SET new_membership = 'Bronze';
    END IF;
   
    UPDATE Customer
    SET Points = total_points,
Membership = new_membership
    WHERE Customer_ID = NEW.Customer_ID;

END;""")
    connection.commit()
    print("Triggers created successfully!")