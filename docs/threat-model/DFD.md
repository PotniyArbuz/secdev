# DFD — Data Flow Diagram for Habit Tracker

```mermaid
graph TD
    A[External User Client] --> B[BFF - API Gateway]
    B --> C[Habit Tracker API - FastAPI]
    C --> D[SQLite DB]
    C --> E[Auth Service - JWT]
    C --> F[External Monitoring Uptime]
    D --> G[Secure Storage]

    subgraph Trust_Boundary_External
        A
    end

    subgraph Trust_Boundary_Internal
        B
        C
        E
    end

    subgraph Trust_Boundary_Data
        D
        G
    end
