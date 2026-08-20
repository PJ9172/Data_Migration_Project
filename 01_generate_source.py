import pandas as pd
import numpy as np
np.random.seed(42)

n_customers, n_products, n_orders = 2000, 150, 15000

customers = pd.DataFrame({
    "customer_id": range(1, n_customers+1),
    "full_name": [f"Customer {i}" for i in range(1, n_customers+1)],
    "email": [f"cust{i}@example.com" for i in range(1, n_customers+1)],
    "region_id": np.random.randint(1, 6, n_customers),
})

products = pd.DataFrame({
    "product_id": range(1, n_products+1),
    "product_name": [f"Product {i}" for i in range(1, n_products+1)],
    "category": np.random.choice(["Electronics","Home","Apparel","Sports"], n_products),
    "unit_price": np.round(np.random.uniform(5, 500, n_products), 2),
})

# 80/20 skew: 20% of customers generate 80% of orders
weights = np.random.pareto(2, n_customers) + 1
weights = weights / weights.sum()
order_customers = np.random.choice(customers.customer_id, n_orders, p=weights)

orders = pd.DataFrame({
    "order_id": range(1, n_orders+1),
    "customer_id": order_customers,
    "order_date": pd.date_range("2025-01-01", periods=n_orders, freq="min"),
    "order_status": np.random.choice(
        ["PLACED","SHIPPED","DELIVERED","CANCELLED"], n_orders, p=[0.1,0.2,0.6,0.1]),
    "region_id": np.random.randint(1, 6, n_orders),
})

items = []
item_id = 1
for oid in orders.order_id:
    for _ in range(np.random.randint(1, 4)):
        pid = np.random.randint(1, n_products+1)
        items.append((item_id, oid, pid, np.random.randint(1,5),
                       float(products.loc[products.product_id==pid,"unit_price"].values[0])))
        item_id += 1
order_items = pd.DataFrame(items, columns=["order_item_id","order_id","product_id","quantity","unit_price"])

base = "/Volumes/demo_catalog/bronze/raw_files"
for name, df in [("customers", customers), ("products", products),
                  ("orders", orders), ("order_items", order_items)]:
    dbutils.fs.mkdirs(f"{base}/{name}")
    df.to_csv(f"/tmp/{name}.csv", index=False)
    dbutils.fs.cp(f"file:/tmp/{name}.csv", f"{base}/{name}/{name}.csv")