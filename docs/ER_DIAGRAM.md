# Entity Relationship Diagram (ERD)

The following Mermaid diagram outlines the complete multi-database domain architecture for the Amazon Backend System, encompassing Relational SQL storage, Document MongoDB collections, and Vector ChromaDB stores.

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : assigned_to
    ROLES ||--o{ ROLE_PERMISSIONS : contains
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : granted_to

    USERS ||--o{ ADDRESSES : owns
    USERS ||--o{ ORDERS : places

    CATEGORIES ||--o{ CATEGORIES : parent_of
    CATEGORIES ||--o{ PRODUCTS : categorizes
    PRODUCTS ||--|| INVENTORY : tracks_stock
    WAREHOUSES ||--o{ INVENTORY : stores

    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : purchased_in
    ADDRESSES ||--o{ ORDERS : ships_to
    ORDERS ||--|| PAYMENTS : processed_via
    ORDERS ||--|| INVOICES : generates

    USERS ||..o{ MONGO_CARTS : cart_document
    USERS ||..o{ MONGO_WISHLISTS : wishlist_document
    USERS ||..o{ MONGO_REVIEWS : reviews_document
    USERS ||..o{ MONGO_NOTIFICATIONS : notification_feed

    PRODUCTS ||..|| CHROMADB_VECTORS : semantic_embedding
```

## Storage Engine Mapping

| Entity | Primary Storage System | Responsibilities |
|---|---|---|
| **Users / Roles / Auth** | SQLite / PostgreSQL (SQL) | Identity, Credentials, RBAC, Claims |
| **Products & Catalog** | SQLite / PostgreSQL (SQL) | SKU, Pricing, Branding, Discounts |
| **Inventory & Warehouse**| SQLite / PostgreSQL (SQL) | Stock Levels, Reserved Stock, Warehouses |
| **Orders & Payments** | SQLite / PostgreSQL (SQL) | Transactions, Line Items, Addresses |
| **PDF Invoices & Receipts**| Filesystem (`/uploads/invoice`) | Generated ReportLab PDF Documents |
| **Shopping Cart** | MongoDB | Dynamic user cart state & temporary items |
| **Wishlist & Notifications**| MongoDB | Saved items & async alert feeds |
| **Semantic Search / Vector**| ChromaDB | Vector embeddings, recommendations & similarity |
