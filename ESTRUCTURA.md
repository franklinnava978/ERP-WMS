src/
├── core/                        # Utilidades globales de la infraestructura
│   ├── config.py                # Variables de entorno y ajustes
│   ├── database.py              # Conexiones PostgreSQL (Engine/Session)
│   ├── security.py              # JWT, Hashing de contraseñas, RLS Context
│   └── middleware/              # Interceptor Multi-Tenant (Inyección de tenant_id)
│
├── modules/                     # Módulos del Dominio ERP-WMS
│   ├── tenants/                 # Administración SaaS (Empresas, Subscripciones)
│   ├── auth/                    # Usuarios, Roles, Permisos
│   ├── catalog/                 # Productos, SKU, UOM, Conversiones, CTN
│   ├── topology/                # Bodegas, Sectores, Ubicaciones, Sucursales
│   ├── inventory/               # Stock, LPN, Movimientos, Logs, Trazabilidad
│   ├── commercial/              # Facturas, Boletas, Cotizaciones, Ventas
│   ├── wms/                     # Demandas WMS, Tareas, Picking, Despacho
│   └── mobile/                  # API optimizada para PDAs Zebra (Sync Offline/ZPL)
│
├── shared/                      # DTOs, Excepciones y Enums compartidos
│   ├── enums.py                 # Estados de stock, tipos de documento, etc.
│   └── exceptions.py            # Manejo unificado de errores HTTP
│
└── main.py                      # Punto de entrada de FastAPI


ERP-WMS-SaaS/
├── database/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql        <-- GUARDA AQUÍ EL SQL COMPLETO
│   │   └── 002_rls_and_indexes.sql       <-- Índices y políticas RLS
│   └── seeds/
│       └── 001_initial_seed.sql          <-- Unidades de medida y permisos base
│
├── alembic/                              # Si usas Alembic para controlar versiones en Python
│   └── versions/
│
└── src/
    └── modules/                          # Los ORMs (Python) reflejan este SQL
        ├── tenants/models.py             # Clase Tenant
        ├── auth/models.py                # Clase User
        ├── catalog/models.py             # Clases UnitOfMeasure, Product, UOMConversion
        ├── topology/models.py            # Clase Location
        ├── inventory/models.py           # Clases LPN, InventoryLevel, InventoryLog
        └── commercial/models.py          # Clases CommercialDocument, WMSDemand, WMSTask