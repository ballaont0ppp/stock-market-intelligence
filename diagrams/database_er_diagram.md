# Database Entity-Relationship Diagram

## Metadata
- Generated: 2025-11-19
- Generator: Manual
- Source: Stock Portfolio Platform Models

## Diagram

```mermaid
%%{init: {'theme':'neutral'}}%%
erDiagram
    User ||--|| Wallet : has
    User ||--o{ Holding : owns
    User ||--o{ Order : places
    Company ||--o{ Holding : "held in"
    Company ||--o{ Order : "ordered for"
    Company ||--o{ PriceHistory : "has prices"
    Order ||--o{ Transaction : "creates"
    Wallet ||--o{ Transaction : "records"
    
    User {
        int user_id PK
        string username
        string email
        string role
        datetime created_at
    }
    
    Wallet {
        int wallet_id PK
        int user_id FK
        decimal balance
        datetime updated_at
    }
    
    Company {
        int company_id PK
        string symbol
        string name
        string sector
        decimal current_price
    }
    
    Holding {
        int holding_id PK
        int user_id FK
        int company_id FK
        int quantity
        decimal average_price
        decimal current_value
    }
    
    Order {
        int order_id PK
        int user_id FK
        int company_id FK
        string order_type
        int quantity
        decimal price
        string status
        datetime created_at
    }
    
    Transaction {
        int transaction_id PK
        int user_id FK
        int wallet_id FK
        int order_id FK
        string type
        decimal amount
        datetime created_at
    }
    
    PriceHistory {
        int price_history_id PK
        int company_id FK
        decimal open_price
        decimal close_price
        date price_date
    }
```

## Key Relationships

### User-Centric Relationships
- **User → Wallet**: One-to-Many (A user has one wallet for managing funds)
- **User → Holdings**: One-to-Many (A user can own multiple stock holdings)
- **User → Orders**: One-to-Many (A user can place multiple buy/sell orders)
- **User → Transactions**: One-to-Many (A user has transaction history)
- **User → Notifications**: One-to-Many (A user receives notifications)

### Company-Centric Relationships
- **Company → Holdings**: One-to-Many (A company's stock can be held by multiple users)
- **Company → Orders**: One-to-Many (A company's stock can have multiple orders)
- **Company → PriceHistory**: One-to-Many (A company has historical price data)
- **Company → Dividend**: One-to-Many (A company can pay multiple dividends)
- **Company → Broker**: Many-to-One (Companies are listed with brokers)

### Transaction Flow
- **Order → Transaction**: One-to-One (An executed order creates a transaction)
- **Wallet → Transaction**: One-to-Many (Wallet records all transactions)

## Business Rules

1. **User Management**: Users have roles (admin/user) with different permissions
2. **Portfolio Tracking**: Holdings track quantity, average price, and unrealized gains
3. **Order Processing**: Orders go through states (pending → executed/cancelled)
4. **Wallet Management**: Wallet balance updated with deposits, withdrawals, and trades
5. **Commission Tracking**: Each order includes broker commission
6. **Dividend Processing**: Dividends automatically credited to user wallets
7. **Price Updates**: Background jobs update company prices and price history
8. **Audit Trail**: All critical actions logged for compliance
