-- OAPC 3rd lab student bootstrap script
--
-- Run as the assigned TRAINxx user.
-- Purpose:
--   1. Recreate missing Northwind demo tables.
--   2. Re-seed required demo rows without deleting existing rows.
--   3. Recreate the Select AI profile named TRAINxx_AI.
--
-- This script does not drop existing tables. If a table is corrupted, drop the
-- five Northwind tables manually and rerun this script.

SET DEFINE OFF
SET SERVEROUTPUT ON SIZE UNLIMITED

DECLARE
  PROCEDURE create_table_if_missing (
    p_table_name IN VARCHAR2,
    p_sql        IN VARCHAR2
  ) IS
    l_count NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   l_count
    FROM   user_tables
    WHERE  table_name = UPPER(p_table_name);

    IF l_count = 0 THEN
      EXECUTE IMMEDIATE p_sql;
      DBMS_OUTPUT.PUT_LINE('CREATED TABLE ' || UPPER(p_table_name));
    ELSE
      DBMS_OUTPUT.PUT_LINE('TABLE EXISTS ' || UPPER(p_table_name));
    END IF;
  END;
BEGIN
  create_table_if_missing('CATEGORIES', q'[
    CREATE TABLE categories (
      category_id   NUMBER PRIMARY KEY,
      category_name VARCHAR2(15),
      description   VARCHAR2(300)
    )
  ]');

  create_table_if_missing('CUSTOMERS', q'[
    CREATE TABLE customers (
      customer_id   VARCHAR2(5) PRIMARY KEY,
      company_name  VARCHAR2(40),
      contact_name  VARCHAR2(30),
      contact_title VARCHAR2(30),
      address       VARCHAR2(60),
      city          VARCHAR2(15),
      region        VARCHAR2(15),
      postal_code   VARCHAR2(10),
      country       VARCHAR2(15),
      phone         VARCHAR2(24),
      fax           VARCHAR2(24)
    )
  ]');

  create_table_if_missing('PRODUCTS', q'[
    CREATE TABLE products (
      product_id        NUMBER PRIMARY KEY,
      product_name      VARCHAR2(40),
      supplier_id       NUMBER,
      category_id       NUMBER,
      quantity_per_unit VARCHAR2(20),
      unit_price        NUMBER(10,2),
      units_in_stock    NUMBER,
      units_on_order    NUMBER,
      reorder_level     NUMBER,
      discontinued      NUMBER(1),
      CONSTRAINT products_category_fk FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
  ]');

  create_table_if_missing('ORDERS', q'[
    CREATE TABLE orders (
      order_id         NUMBER PRIMARY KEY,
      customer_id      VARCHAR2(5),
      employee_id      NUMBER,
      order_date       DATE,
      required_date    DATE,
      shipped_date     DATE,
      ship_via         NUMBER,
      freight          NUMBER(10,2),
      ship_name        VARCHAR2(40),
      ship_address     VARCHAR2(60),
      ship_city        VARCHAR2(15),
      ship_region      VARCHAR2(15),
      ship_postal_code VARCHAR2(10),
      ship_country     VARCHAR2(15),
      CONSTRAINT orders_customer_fk FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
  ]');

  create_table_if_missing('ORDER_DETAILS', q'[
    CREATE TABLE order_details (
      order_id   NUMBER,
      product_id NUMBER,
      unit_price NUMBER(10,2),
      quantity   NUMBER,
      discount   NUMBER(4,2),
      CONSTRAINT order_details_pk PRIMARY KEY (order_id, product_id),
      CONSTRAINT order_details_order_fk FOREIGN KEY (order_id) REFERENCES orders(order_id),
      CONSTRAINT order_details_product_fk FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
  ]');
END;
/

COMMENT ON TABLE categories IS 'Product categories. Each category groups similar types of products.';
COMMENT ON COLUMN categories.category_id IS 'Primary key. Unique identifier for each product category.';
COMMENT ON COLUMN categories.category_name IS 'Name of the category, such as Beverages or Condiments.';
COMMENT ON COLUMN categories.description IS 'Optional description of the category.';

COMMENT ON TABLE customers IS 'List of customers who place orders. Linked to ORDERS through CUSTOMER_ID.';
COMMENT ON COLUMN customers.customer_id IS 'Primary key. Unique customer code.';
COMMENT ON COLUMN customers.company_name IS 'Customer company name.';
COMMENT ON COLUMN customers.contact_name IS 'Main contact person at the customer company.';
COMMENT ON COLUMN customers.contact_title IS 'Job title of the contact person.';
COMMENT ON COLUMN customers.address IS 'Customer address.';
COMMENT ON COLUMN customers.city IS 'Customer city.';
COMMENT ON COLUMN customers.region IS 'Customer region or state.';
COMMENT ON COLUMN customers.postal_code IS 'Postal or ZIP code.';
COMMENT ON COLUMN customers.country IS 'Customer country.';
COMMENT ON COLUMN customers.phone IS 'Customer phone number.';
COMMENT ON COLUMN customers.fax IS 'Customer fax number.';

COMMENT ON TABLE products IS '{"comment":"Sales product master data","annotation":{"description":"All products sold by the company, including price, inventory, supplier id, and category."}}';
COMMENT ON COLUMN products.product_id IS 'Primary key. Unique product identifier.';
COMMENT ON COLUMN products.product_name IS 'Product name.';
COMMENT ON COLUMN products.supplier_id IS 'Supplier identifier. Supplier table is not part of this training schema.';
COMMENT ON COLUMN products.category_id IS 'Foreign key to CATEGORIES.CATEGORY_ID.';
COMMENT ON COLUMN products.quantity_per_unit IS 'Package or quantity description per unit.';
COMMENT ON COLUMN products.unit_price IS '{"comment":"Unit price","annotation":{"currency":"USD","description":"Base sales price per product before discount."}}';
COMMENT ON COLUMN products.units_in_stock IS '{"comment":"Inventory quantity","annotation":{"meaning":"Physical quantity currently available in warehouse."}}';
COMMENT ON COLUMN products.units_on_order IS '{"comment":"Ordered quantity","annotation":{"meaning":"Quantity already ordered from suppliers but not yet received."}}';
COMMENT ON COLUMN products.reorder_level IS 'Minimum stock level before reorder is required.';
COMMENT ON COLUMN products.discontinued IS 'Whether the product is discontinued. 0 means active, 1 means discontinued.';

COMMENT ON TABLE orders IS '{"comment":"Customer order header","annotation":{"description":"Customer order header, including order date, required date, shipped date, freight, and shipping address."}}';
COMMENT ON COLUMN orders.order_id IS 'Primary key. Unique order identifier.';
COMMENT ON COLUMN orders.customer_id IS 'Foreign key to CUSTOMERS.CUSTOMER_ID.';
COMMENT ON COLUMN orders.employee_id IS 'Employee id handling the order. Employee table is not part of this training schema.';
COMMENT ON COLUMN orders.order_date IS 'Date when the order was placed.';
COMMENT ON COLUMN orders.required_date IS 'Date when delivery is required.';
COMMENT ON COLUMN orders.shipped_date IS 'Date when the order was shipped.';
COMMENT ON COLUMN orders.ship_via IS 'Shipping method identifier.';
COMMENT ON COLUMN orders.freight IS 'Shipping cost.';
COMMENT ON COLUMN orders.ship_name IS 'Shipping recipient or company name.';
COMMENT ON COLUMN orders.ship_address IS 'Shipping address.';
COMMENT ON COLUMN orders.ship_city IS 'Shipping city.';
COMMENT ON COLUMN orders.ship_region IS 'Shipping region or state.';
COMMENT ON COLUMN orders.ship_postal_code IS 'Shipping postal or ZIP code.';
COMMENT ON COLUMN orders.ship_country IS 'Shipping country.';

COMMENT ON TABLE order_details IS 'Line items of each order. Links ORDERS and PRODUCTS and stores quantity, price, and discount.';
COMMENT ON COLUMN order_details.order_id IS 'Foreign key to ORDERS.ORDER_ID.';
COMMENT ON COLUMN order_details.product_id IS 'Foreign key to PRODUCTS.PRODUCT_ID.';
COMMENT ON COLUMN order_details.unit_price IS 'Unit price at the time of order.';
COMMENT ON COLUMN order_details.quantity IS 'Quantity ordered.';
COMMENT ON COLUMN order_details.discount IS 'Discount ratio from 0 to 1.';

MERGE INTO categories d USING (SELECT 1 category_id, 'Beverages' category_name, 'Soft drinks, coffees, teas, beers, and ales' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 2 category_id, 'Condiments' category_name, 'Sweet and savory sauces, relishes, spreads, and seasonings' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 3 category_id, 'Confections' category_name, 'Desserts, candies, and sweet breads' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 4 category_id, 'Dairy Products' category_name, 'Cheeses' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 5 category_id, 'Grains/Cereals' category_name, 'Breads, crackers, pasta, and cereal' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 6 category_id, 'Meat/Poultry' category_name, 'Prepared meats' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 7 category_id, 'Produce' category_name, 'Dried fruit and bean curd' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);
MERGE INTO categories d USING (SELECT 8 category_id, 'Seafood' category_name, 'Seaweed and fish' description FROM dual) s ON (d.category_id = s.category_id) WHEN NOT MATCHED THEN INSERT VALUES (s.category_id, s.category_name, s.description);

MERGE INTO customers d USING (SELECT 'ALFKI' customer_id, 'Alfreds Futterkiste' company_name, 'Maria Anders' contact_name, 'Sales Representative' contact_title, 'Obere Str. 57' address, 'Berlin' city, CAST(NULL AS VARCHAR2(15)) region, '12209' postal_code, 'Germany' country, '030-0074321' phone, '030-0076545' fax FROM dual) s ON (d.customer_id = s.customer_id) WHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.company_name, s.contact_name, s.contact_title, s.address, s.city, s.region, s.postal_code, s.country, s.phone, s.fax);
MERGE INTO customers d USING (SELECT 'ANATR' customer_id, 'Ana Trujillo Emparedados y helados' company_name, 'Ana Trujillo' contact_name, 'Owner' contact_title, 'Avda. de la Constitucion 2222' address, 'Mexico D.F.' city, CAST(NULL AS VARCHAR2(15)) region, '05021' postal_code, 'Mexico' country, '(5) 555-4729' phone, '(5) 555-3745' fax FROM dual) s ON (d.customer_id = s.customer_id) WHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.company_name, s.contact_name, s.contact_title, s.address, s.city, s.region, s.postal_code, s.country, s.phone, s.fax);
MERGE INTO customers d USING (SELECT 'ANTON' customer_id, 'Antonio Moreno Taqueria' company_name, 'Antonio Moreno' contact_name, 'Owner' contact_title, 'Mataderos 2312' address, 'Mexico D.F.' city, CAST(NULL AS VARCHAR2(15)) region, '05023' postal_code, 'Mexico' country, '(5) 555-3932' phone, CAST(NULL AS VARCHAR2(24)) fax FROM dual) s ON (d.customer_id = s.customer_id) WHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.company_name, s.contact_name, s.contact_title, s.address, s.city, s.region, s.postal_code, s.country, s.phone, s.fax);
MERGE INTO customers d USING (SELECT 'AROUT' customer_id, 'Around the Horn' company_name, 'Thomas Hardy' contact_name, 'Sales Representative' contact_title, '120 Hanover Sq.' address, 'London' city, CAST(NULL AS VARCHAR2(15)) region, 'WA1 1DP' postal_code, 'UK' country, '(171) 555-7788' phone, '(171) 555-6750' fax FROM dual) s ON (d.customer_id = s.customer_id) WHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.company_name, s.contact_name, s.contact_title, s.address, s.city, s.region, s.postal_code, s.country, s.phone, s.fax);
MERGE INTO customers d USING (SELECT 'BERGS' customer_id, 'Berglunds snabbkop' company_name, 'Christina Berglund' contact_name, 'Order Administrator' contact_title, 'Berguvsvagen 8' address, 'Lulea' city, CAST(NULL AS VARCHAR2(15)) region, 'S-958 22' postal_code, 'Sweden' country, '0921-12 34 65' phone, '0921-12 34 67' fax FROM dual) s ON (d.customer_id = s.customer_id) WHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.company_name, s.contact_name, s.contact_title, s.address, s.city, s.region, s.postal_code, s.country, s.phone, s.fax);

MERGE INTO products d USING (SELECT 1 product_id, 'Chai' product_name, 1 supplier_id, 1 category_id, '10 boxes x 20 bags' quantity_per_unit, 18.00 unit_price, 39 units_in_stock, 0 units_on_order, 10 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 2 product_id, 'Chang' product_name, 1 supplier_id, 1 category_id, '24 - 12 oz bottles' quantity_per_unit, 19.00 unit_price, 17 units_in_stock, 40 units_on_order, 25 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 3 product_id, 'Aniseed Syrup' product_name, 1 supplier_id, 2 category_id, '12 - 550 ml bottles' quantity_per_unit, 10.00 unit_price, 13 units_in_stock, 70 units_on_order, 25 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 4 product_id, 'Chef Anton''s Cajun Seasoning' product_name, 2 supplier_id, 2 category_id, '48 - 6 oz jars' quantity_per_unit, 22.00 unit_price, 53 units_in_stock, 0 units_on_order, 0 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 5 product_id, 'Chef Anton''s Gumbo Mix' product_name, 2 supplier_id, 2 category_id, '36 boxes' quantity_per_unit, 21.35 unit_price, 0 units_in_stock, 0 units_on_order, 0 reorder_level, 1 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 6 product_id, 'Grandma''s Boysenberry Spread' product_name, 2 supplier_id, 2 category_id, '12 - 8 oz jars' quantity_per_unit, 25.00 unit_price, 120 units_in_stock, 0 units_on_order, 25 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 7 product_id, 'Uncle Bob''s Organic Dried Pears' product_name, 2 supplier_id, 7 category_id, '12 - 1 lb pkgs.' quantity_per_unit, 30.00 unit_price, 15 units_in_stock, 0 units_on_order, 10 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 8 product_id, 'Northwoods Cranberry Sauce' product_name, 2 supplier_id, 2 category_id, '12 - 12 oz jars' quantity_per_unit, 40.00 unit_price, 6 units_in_stock, 0 units_on_order, 0 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 9 product_id, 'Mishi Kobe Niku' product_name, 2 supplier_id, 6 category_id, '18 - 500 g pkgs.' quantity_per_unit, 97.00 unit_price, 29 units_in_stock, 0 units_on_order, 0 reorder_level, 1 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);
MERGE INTO products d USING (SELECT 10 product_id, 'Ikura' product_name, 2 supplier_id, 8 category_id, '12 - 200 ml jars' quantity_per_unit, 31.00 unit_price, 31 units_in_stock, 0 units_on_order, 0 reorder_level, 0 discontinued FROM dual) s ON (d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.product_id, s.product_name, s.supplier_id, s.category_id, s.quantity_per_unit, s.unit_price, s.units_in_stock, s.units_on_order, s.reorder_level, s.discontinued);

MERGE INTO orders d USING (SELECT 10248 order_id, 'ALFKI' customer_id, 5 employee_id, DATE '1996-07-04' order_date, DATE '1996-08-01' required_date, DATE '1996-07-16' shipped_date, 3 ship_via, 32.38 freight, 'Alfreds Futterkiste' ship_name, 'Obere Str. 57' ship_address, 'Berlin' ship_city, CAST(NULL AS VARCHAR2(15)) ship_region, '12209' ship_postal_code, 'Germany' ship_country FROM dual) s ON (d.order_id = s.order_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.customer_id, s.employee_id, s.order_date, s.required_date, s.shipped_date, s.ship_via, s.freight, s.ship_name, s.ship_address, s.ship_city, s.ship_region, s.ship_postal_code, s.ship_country);
MERGE INTO orders d USING (SELECT 10249 order_id, 'ANATR' customer_id, 6 employee_id, DATE '1996-07-05' order_date, DATE '1996-08-16' required_date, DATE '1996-07-10' shipped_date, 1 ship_via, 11.61 freight, 'Ana Trujillo Emparedados' ship_name, 'Avda. de la Constitucion 2222' ship_address, 'Mexico D.F.' ship_city, CAST(NULL AS VARCHAR2(15)) ship_region, '05021' ship_postal_code, 'Mexico' ship_country FROM dual) s ON (d.order_id = s.order_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.customer_id, s.employee_id, s.order_date, s.required_date, s.shipped_date, s.ship_via, s.freight, s.ship_name, s.ship_address, s.ship_city, s.ship_region, s.ship_postal_code, s.ship_country);
MERGE INTO orders d USING (SELECT 10250 order_id, 'AROUT' customer_id, 4 employee_id, DATE '1996-07-08' order_date, DATE '1996-08-05' required_date, DATE '1996-07-12' shipped_date, 2 ship_via, 65.83 freight, 'Around the Horn' ship_name, '120 Hanover Sq.' ship_address, 'London' ship_city, CAST(NULL AS VARCHAR2(15)) ship_region, 'WA1 1DP' ship_postal_code, 'UK' ship_country FROM dual) s ON (d.order_id = s.order_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.customer_id, s.employee_id, s.order_date, s.required_date, s.shipped_date, s.ship_via, s.freight, s.ship_name, s.ship_address, s.ship_city, s.ship_region, s.ship_postal_code, s.ship_country);
MERGE INTO orders d USING (SELECT 10251 order_id, 'BERGS' customer_id, 3 employee_id, DATE '1996-07-08' order_date, DATE '1996-08-05' required_date, DATE '1996-07-15' shipped_date, 1 ship_via, 41.34 freight, 'Berglunds snabbkop' ship_name, 'Berguvsvagen 8' ship_address, 'Lulea' ship_city, CAST(NULL AS VARCHAR2(15)) ship_region, 'S-958 22' ship_postal_code, 'Sweden' ship_country FROM dual) s ON (d.order_id = s.order_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.customer_id, s.employee_id, s.order_date, s.required_date, s.shipped_date, s.ship_via, s.freight, s.ship_name, s.ship_address, s.ship_city, s.ship_region, s.ship_postal_code, s.ship_country);

MERGE INTO order_details d USING (SELECT 10248 order_id, 1 product_id, 14.00 unit_price, 12 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10248 order_id, 2 product_id, 9.80 unit_price, 10 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10248 order_id, 3 product_id, 34.80 unit_price, 5 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10249 order_id, 4 product_id, 18.60 unit_price, 9 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10249 order_id, 5 product_id, 42.40 unit_price, 40 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10250 order_id, 1 product_id, 18.00 unit_price, 10 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10250 order_id, 6 product_id, 25.00 unit_price, 35 quantity, 0.15 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10250 order_id, 7 product_id, 30.00 unit_price, 15 quantity, 0.0 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10251 order_id, 8 product_id, 40.00 unit_price, 20 quantity, 0.05 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);
MERGE INTO order_details d USING (SELECT 10251 order_id, 9 product_id, 97.00 unit_price, 40 quantity, 0.05 discount FROM dual) s ON (d.order_id = s.order_id AND d.product_id = s.product_id) WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.product_id, s.unit_price, s.quantity, s.discount);

COMMIT;

DECLARE
  l_profile VARCHAR2(128) := USER || '_AI';
  l_attrs   CLOB;
BEGIN
  BEGIN
    DBMS_CLOUD_AI.DROP_PROFILE(profile_name => l_profile, force => TRUE);
  EXCEPTION
    WHEN OTHERS THEN
      NULL;
  END;

  l_attrs := '{
    "provider": "oci",
    "model": "xai.grok-4.3",
    "credential_name": "OCI$RESOURCE_PRINCIPAL",
    "comments": true,
    "object_list": [
      {"owner": "' || USER || '", "name": "CATEGORIES"},
      {"owner": "' || USER || '", "name": "PRODUCTS"},
      {"owner": "' || USER || '", "name": "CUSTOMERS"},
      {"owner": "' || USER || '", "name": "ORDERS"},
      {"owner": "' || USER || '", "name": "ORDER_DETAILS"}
    ]
  }';

  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => l_profile,
    attributes   => l_attrs
  );

  DBMS_OUTPUT.PUT_LINE('CREATED PROFILE ' || l_profile);
END;
/

SELECT 'CATEGORIES' table_name, COUNT(*) row_count FROM categories
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM customers
UNION ALL
SELECT 'PRODUCTS', COUNT(*) FROM products
UNION ALL
SELECT 'ORDERS', COUNT(*) FROM orders
UNION ALL
SELECT 'ORDER_DETAILS', COUNT(*) FROM order_details
ORDER BY table_name;

SELECT profile_name, status
FROM   user_cloud_ai_profiles
WHERE  profile_name = USER || '_AI';

SELECT attribute_name, DBMS_LOB.SUBSTR(attribute_value, 4000, 1) AS attribute_value
FROM   user_cloud_ai_profile_attributes
WHERE  profile_name = USER || '_AI'
AND    attribute_name IN ('provider', 'model', 'credential_name', 'comments')
ORDER  BY attribute_name;
