Actúa como un Arquitecto Senior de Software, especializado en ERP, WMS, logística, inventario, arquitectura SaaS Multi-Tenant, bases de datos PostgreSQL, aplicaciones móviles Android industriales, AWS, seguridad, DevOps y sistemas empresariales.

Estamos diseñando y desarrollando una plataforma llamada:

ERP-WMS SaaS Multi-Tenant

IMPORTANTE:
Este proyecto NO debe tratarse como un WMS independiente.
El objetivo es construir un ERP-WMS completo, donde el ERP y el WMS forman parte del mismo sistema.

NO diseñes el sistema suponiendo que existe un ERP externo que alimenta al WMS.

NO diseñes una integración con Justime.

NO agregues Justime como sistema externo, API, CSV, XML, HTML, middleware o fuente de datos.

El proyecto se está desarrollando como un ERP-WMS propio.

==================================================
1. OBJETIVO GENERAL
==================================================

Construir una plataforma ERP-WMS SaaS Multi-Tenant que inicialmente será implementada para FRANKMARC, pero que posteriormente debe permitir incorporar otros clientes/empresas.

El sistema debe ser escalable, seguro, modular y preparado para crecimiento.

Debe permitir que múltiples empresas utilicen la misma plataforma, manteniendo completamente aislados:

- datos;
- usuarios;
- inventario;
- bodegas;
- sucursales;
- productos;
- documentos;
- operaciones;
- configuraciones;
- auditoría.

FRANKMARC será el primer tenant, pero la arquitectura NO debe estar diseñada exclusivamente para FRANKMARC.

==================================================
2. CONCEPTO ERP-WMS
==================================================

El sistema debe dividir conceptualmente sus responsabilidades en:

ERP:
- Clientes
- Proveedores
- Productos
- Ventas
- Cotizaciones
- Facturas
- Boletas
- Compras
- Documentos comerciales
- Administración
- Configuración empresarial
- Usuarios
- Roles
- Permisos
- Otros módulos administrativos que posteriormente se incorporen

WMS:
- Inventario
- Bodegas
- Sectores
- Ubicaciones
- Acopio
- Picking
- Reposición
- LPN
- Pallets
- CTN
- Consolidación
- Despacho
- Transferencias
- Sucursales
- Entrega
- Trazabilidad
- Operación mediante dispositivos móviles

El ERP genera y administra la información comercial.

El WMS ejecuta la operación física y logística derivada de esas operaciones comerciales.

Ambos forman parte del mismo ERP-WMS.

==================================================
3. FRANKMARC — ESTRUCTURA ORGANIZACIONAL
==================================================

FRANKMARC actualmente posee:

- 2 centros/bodegas principales.
- Cada centro/bodega posee una sala de venta.
- Cada centro/bodega está dividido internamente en sectores o sub-bodegas.
- Existen 9 sectores/sub-bodegas en total.
- Existen aproximadamente 20 sucursales/salas de venta.
- Las sucursales actualmente no manejan stock permanente.
- Las sucursales actualmente funcionan principalmente como salas de venta/muestras.
- Las sucursales deben quedar preparadas arquitectónicamente para poder almacenar stock posteriormente.

IMPORTANTE:

No modelar las sucursales como "lugares sin inventario".

Una sucursal debe poder evolucionar desde:

stock_enabled = false

a:

stock_enabled = true

sin modificar la arquitectura fundamental.

Cuando una sucursal reciba material enviado desde un centro/bodega, ese material pasará a formar parte del inventario de dicha sucursal hasta que sea entregado al cliente.

==================================================
4. ESTRUCTURA FÍSICA
==================================================

Modelo conceptual:

FRANKMARC
|
+-- Centro/Bodega 1
|   |
|   +-- Sala de Venta
|   +-- Sectores/Sub-bodegas
|       +-- Picking
|       +-- Acopio
|
+-- Centro/Bodega 2
|   |
|   +-- Sala de Venta
|   +-- Sectores/Sub-bodegas
|       +-- Picking
|       +-- Acopio
|
+-- Sucursal 1
+-- Sucursal 2
+-- ...
+-- Sucursal 20

La arquitectura debe permitir que otros tenants tengan estructuras diferentes.

No asumir que todos los clientes tendrán exactamente dos bodegas o nueve sectores.

==================================================
5. VOLUMEN OPERACIONAL
==================================================

Estimación actual para FRANKMARC:

- 2 centros/bodegas principales.
- 9 sectores/sub-bodegas.
- Aproximadamente 20 sucursales.
- Cada centro factura aproximadamente 250 documentos diarios.
- 2 centros ≈ 500 documentos diarios.
- Cada sucursal genera aproximadamente 20 documentos diarios.
- 20 sucursales ≈ 400 documentos diarios.
- Total aproximado ≈ 900 documentos diarios.

IMPORTANTE:

900 documentos/día es una estimación inicial.

No asumir que cada documento contiene exactamente la misma cantidad de líneas.

Las líneas por documento pueden variar.

No utilizar la antigua estimación de 4.800 líneas/día como requisito fijo.

El sistema debe diseñarse para escalar mucho más allá de estos volúmenes.

==================================================
6. DOCUMENTOS COMERCIALES
==================================================

El ERP-WMS debe manejar internamente:

- Cotizaciones
- Facturas
- Boletas
- Documentos comerciales
- Pedidos/órdenes
- Otros documentos que posteriormente se definan

No asumir que una factura es exactamente igual a una orden WMS.

Debe existir una separación conceptual entre:

DOCUMENTO COMERCIAL

y

OPERACIÓN LOGÍSTICA.

Ejemplo:

Documento comercial
|
v
Demanda/Orden WMS
|
+-- Reserva
+-- Asignación
+-- Picking
+-- Consolidación
+-- Despacho
+-- Entrega

==================================================
7. FLUJO COMERCIAL Y LOGÍSTICO REAL
==================================================

El flujo principal de FRANKMARC es:

CLIENTE
    |
    v
SALA DE VENTA
    |
    v
COTIZACIÓN / FACTURA / BOLETA
    |
    v
TIPO DE ENTREGA
    |
    +------------------+------------------+
    |                  |                  |
    v                  v                  v
RETIRO INMEDIATO      FLETE        ENVÍO A SUCURSAL
    |                  |                  |
    v                  v                  v
PICKING              PICKING            PICKING
    |                  |                  |
    v                  v                  v
DESPACHO        CONSOLIDACIÓN       CONSOLIDACIÓN
    |                  |                  |
    v                  v                  v
ENTREGA          DESPACHO DÍA       DESPACHO A
CLIENTE          SIGUIENTE          SUCURSAL
                       |                  |
                       v                  v
                     GUÍA              GUÍA
                       |                  |
                       v                  v
                    CLIENTE           SUCURSAL
                                          |
                                          v
                                    STOCK SUCURSAL
                                          |
                                          v
                                    ENTREGA CLIENTE

==================================================
8. RETIRO INMEDIATO
==================================================

Cuando el cliente retira inmediatamente:

Venta
|
v
Documento comercial
|
v
Reserva
|
v
Picking
|
v
Despacho
|
v
Entrega al cliente

Debe soportarse:

DESPACHO COMPLETO

Ejemplo:
Solicitado = 20 cajas
Preparado = 20 cajas

Resultado:
Despacho completo.

También:

DESPACHO PARCIAL

Ejemplo:
Solicitado = 20 cajas
Preparado = 15 cajas

Resultado:
Despacho parcial.

El sistema debe mantener:

- cantidad solicitada;
- cantidad reservada;
- cantidad asignada;
- cantidad preparada;
- cantidad despachada;
- cantidad pendiente.

No asumir que un documento solo puede ser completo o cerrado de una vez.

==================================================
9. FLETE
==================================================

Flujo:

Cliente
|
v
Sala de venta
|
v
Documento
|
v
Reserva
|
v
Picking
|
v
Zona de consolidación
|
v
Consolidación
|
v
Despacho al día siguiente
|
v
Guía
|
v
Cliente

IMPORTANTE:

CONSOLIDACIÓN y DESPACHO son procesos diferentes.

La zona de consolidación representa material ya preparado que está esperando despacho.

==================================================
10. ENVÍO A SUCURSAL
==================================================

Flujo:

Venta
|
v
Documento
|
v
Reserva
|
v
Picking
|
v
Zona de consolidación
|
v
Despacho
|
v
Guía
|
v
Sucursal
|
v
Stock de sucursal
|
v
Entrega al cliente

La sucursal es un destino interno de inventario.

No tratarla simplemente como un cliente externo.

Debe existir un concepto de transferencia de inventario:

Centro/Bodega
|
| transferencia
v
Sucursal

La transferencia debe registrar:

- origen;
- destino;
- producto;
- cantidad;
- unidad;
- fecha;
- usuario;
- documento/guía;
- estado;
- trazabilidad.

==================================================
11. INVENTARIO
==================================================

El corazón del WMS debe ser:

PRODUCTO
|
v
INVENTARIO
|
v
UBICACIÓN
|
v
MOVIMIENTO
|
v
TAREA
|
v
DESPACHO

No diseñar el inventario simplemente como:

stock = stock - cantidad

Cada operación importante debe generar movimientos de inventario.

Debe existir trazabilidad de:

- entrada;
- salida;
- reserva;
- asignación;
- picking;
- reposición;
- consolidación;
- despacho;
- transferencia;
- recepción;
- ajuste;
- devolución;
- entrega.

==================================================
12. UNIDADES DE MEDIDA
==================================================

El ERP-WMS debe tener un sistema de unidades de medida completamente configurable por tenant.

NO limitar el sistema a:

- cajas;
- metros cuadrados.

FRANKMARC actualmente utiliza principalmente:

CONTEO:
Cajas.

VALORIZACIÓN:
m².

Por lo tanto debe existir conversión:

CAJA -> m²

Ejemplo:

1 caja = X m².

El factor debe estar asociado al producto/SKU y NO debe estar hardcodeado.

Sin embargo, la arquitectura debe permitir que otros tenants utilicen:

- unidad;
- caja;
- pallet;
- CTN;
- kg;
- g;
- m;
- cm;
- m²;
- litro;
- etc.

Debe existir:

UOM
UOMConversion

Y debe ser posible definir diferentes unidades para:

- compra;
- inventario;
- venta;
- picking;
- almacenamiento;
- valoración;
- embalaje.

==================================================
13. PRODUCTOS
==================================================

Los productos se identifican físicamente mediante código de producto.

Debe existir una estructura preparada para:

- Producto
- SKU
- Código
- Descripción
- Unidad de inventario
- Unidad de venta
- Unidad de valoración
- Unidad de picking
- Conversiones
- Packaging
- Características

No asumir que todos los productos se venden y almacenan en la misma unidad.

Ejemplo:

Producto X:

Compra -> Caja
Almacenamiento -> Caja
Picking -> Caja
Venta -> Caja
Valoración -> m²

==================================================
14. CTN
==================================================

CTN significa:

CARTÓN / EMBALAJE DEL MATERIAL.

CTN NO debe confundirse con una unidad de medida genérica.

Debe modelarse como parte del concepto de embalaje/logística.

Ejemplo:

Producto
|
+-- Caja
|
+-- CTN / embalaje
|
+-- Pallet
      |
      +-- LPN

El modelo debe permitir que cada tenant tenga diferentes configuraciones de embalaje.

==================================================
15. LPN Y PALLET
==================================================

Para FRANKMARC:

LPN = identificación/cédula/etiqueta del pallet almacenado en acopio.

Conceptualmente:

LPN
|
v
PALLET
|
v
PRODUCTO

Actualmente:

- un LPN no contiene múltiples productos;
- un pallet no contiene múltiples LPN.

Sin embargo, NO hardcodear esta limitación de forma irreversible para todo el SaaS.

El modelo debe ser suficientemente flexible para que otro tenant pueda utilizar una estructura logística diferente.

==================================================
16. ACOPIO
==================================================

El acopio representa almacenamiento de pallets.

El pallet almacenado en acopio tendrá una identificación LPN.

Ejemplo:

ACOPIO
|
+-- LPN-000001
|     |
|     +-- Pallet
|           |
|           +-- Producto
|
+-- LPN-000002
      |
      +-- Pallet
            |
            +-- Producto

==================================================
17. PICKING
==================================================

El picking se realiza desde las ubicaciones de picking.

El picking por piso significa que los productos almacenados en las ubicaciones de picking son utilizados para preparar pedidos.

Flujo:

ACOPIO
|
| Reposición
v
PICKING
|
| Preparación
v
PEDIDO

FIFO / LIFO / FEFO:

NO son reglas operativas actuales de FRANKMARC.

Son capacidades futuras.

Por lo tanto:

- NO desarrollar un motor complejo FIFO/FEFO/LIFO para el MVP.
- Sí dejar el modelo preparado para incorporarlo posteriormente.

==================================================
18. REGLAS QUE NO SE IMPLEMENTARÁN ACTUALMENTE
==================================================

Excluir del alcance actual:

- "Mejor cantidad"
- "Menor cantidad"
- Corte de cables
- Mínimo de corte
- Algoritmos especiales de corte

No agregarlas al MVP salvo que posteriormente se soliciten.

==================================================
19. UBICACIONES DE PICKING
==================================================

Las ubicaciones de picking ya están físicamente establecidas.

Se utilizan racks con niveles:

NA
NB
NC
ND
NE
NF

No asumir que "NA" es una ubicación completa.

La arquitectura debe poder representar:

Pasillo
Rack
Nivel
Ubicación

Ejemplo conceptual:

P01-R03-NA
P01-R03-NB
P01-R03-NC

La nomenclatura exacta debe ser configurable.

El modelo debe permitir:

Warehouse
|
Sector
|
Zone
|
Rack
|
Level
|
Location

==================================================
20. INVENTARIO EN SUCURSALES
==================================================

Las sucursales inicialmente pueden no tener stock.

Pero cuando reciben material mediante transferencia:

Centro/Bodega
|
v
Transferencia
|
v
Sucursal
|
v
Inventario de sucursal

Ese inventario permanecerá en la sucursal hasta que sea entregado al cliente.

Por lo tanto, las sucursales deben soportar:

- inventario;
- ubicaciones;
- recepción;
- transferencia;
- entrega;
- ajustes;
- trazabilidad.

==================================================
21. CONSOLIDACIÓN
==================================================

La zona de consolidación es una ubicación/estado temporal donde se agrupan pedidos preparados antes del despacho.

Ejemplo:

CONSOLIDACIÓN
|
+-- Flete 001
+-- Flete 002
+-- Sucursal 003
+-- Sucursal 005
+-- Sucursal 008

El material consolidado:

- ya fue preparado;
- no debe considerarse stock disponible;
- espera despacho.

Debe quedar registrado mediante movimientos/estados de inventario.

==================================================
22. DESPACHO
==================================================

Debe existir un módulo de despacho.

Debe soportar:

- retiro inmediato;
- flete;
- envío a sucursal;
- despacho completo;
- despacho parcial;
- documentación asociada;
- guía;
- usuario responsable;
- fecha/hora;
- vehículo cuando corresponda;
- conductor cuando corresponda;
- trazabilidad.

==================================================
23. GUÍAS
==================================================

El sistema debe permitir asociar guías a:

- despachos a clientes;
- transferencias a sucursales;
- otros movimientos que posteriormente se definan.

No asumir que una guía es exactamente igual a una factura.

Son documentos distintos con funciones distintas.

==================================================
24. TRANSPORTE
==================================================

Para los fletes, la arquitectura debe quedar preparada para:

Shipment
|
+-- Vehicle
+-- Driver
+-- Route
+-- Guide
+-- Delivery
+-- ShipmentLine

No es necesario implementar toda la complejidad de transporte en el MVP si no es necesaria.

Pero la arquitectura no debe impedir su incorporación.

==================================================
25. ZEBRA
==================================================

Se utilizarán inicialmente aproximadamente 9 dispositivos móviles.

La impresora definida es:

Zebra ZD220

IMPORTANTE:

La ZD220 es una impresora de etiquetas.

NO es el dispositivo móvil/scanner.

Por lo tanto separar:

IMPRESORA:
Zebra ZD220

DISPOSITIVO MÓVIL:
Zebra Android Industrial PDA

Se debe recomendar un modelo Zebra Android adecuado para:

- operación WMS;
- scanner integrado;
- gatillo físico;
- DataWedge;
- Wi-Fi;
- ambiente industrial;
- turnos prolongados;
- administración empresarial.

La selección final del modelo debe considerar disponibilidad y soporte vigente.

==================================================
26. DISPOSITIVOS MÓVILES
==================================================

La aplicación móvil debe ser compatible con Android Enterprise y Zebra DataWedge.

No acoplar la aplicación a una única versión de Android.

Seleccionar primero el modelo Zebra y posteriormente trabajar con la versión Android oficialmente soportada por dicho dispositivo.

Debe existir administración centralizada de dispositivos.

Evaluar:

- Zebra Mobility DNA;
- StageNow;
- Zebra DNA Cloud;
- MDM/EMM Android Enterprise.

La solución debe priorizar:

- seguridad;
- facilidad de administración;
- configuración remota;
- actualización;
- instalación de aplicaciones;
- políticas;
- Wi-Fi;
- inventario de dispositivos;
- soporte remoto.

==================================================
27. OPERACIÓN OFFLINE
==================================================

Los dispositivos móviles deben estar preparados para funcionar temporalmente con conectividad limitada o intermitente.

Debe existir:

- cola local;
- sincronización;
- control de conflictos;
- identificación de operaciones;
- reintentos;
- timestamps;
- trazabilidad.

Ejemplo:

PDA
|
v
Operación local
|
v
Sync Queue
|
v
Servidor
|
v
PostgreSQL

No permitir duplicación de movimientos cuando una operación sea reintentada.

==================================================
28. SAAS MULTI-TENANT
==================================================

La plataforma debe ser Multi-Tenant desde el inicio.

Todo dato operacional debe estar relacionado con:

tenant_id

cuando corresponda.

Ejemplo:

Tenant
|
+-- Users
+-- Products
+-- Warehouses
+-- Locations
+-- Inventory
+-- Orders
+-- Shipments
+-- Customers
+-- Suppliers

Debe existir aislamiento lógico fuerte entre tenants.

Un usuario del Tenant A nunca debe poder acceder a:

- inventario;
- pedidos;
- clientes;
- productos;
- usuarios;
- documentos;

del Tenant B.

==================================================
29. PLANES SAAS
==================================================

El sistema debe soportar planes:

- Starter
- Professional
- Enterprise

Inicialmente pueden estar modelados para permitir implementación posterior de billing completo.

La arquitectura debe permitir:

Tenant
|
Subscription
|
Plan
|
Features
|
Usage

Preparar:

- ciclo de facturación;
- estado de suscripción;
- límites;
- features;
- uso;
- facturas;
- pagos.

No acoplar todavía la plataforma a un único proveedor de pago si no es necesario.

==================================================
30. INFRAESTRUCTURA AWS
==================================================

Existe una cuenta AWS.

La administración de AWS será realizada por un tercero.

La plataforma debe diseñarse para AWS.

Arquitectura inicial recomendada:

AWS
|
+-- Route 53
+-- CloudFront
+-- WAF
+-- ALB
+-- ECS/Fargate
+-- RDS PostgreSQL
+-- ElastiCache Redis
+-- S3
+-- ECR
+-- Secrets Manager
+-- CloudWatch
+-- CloudTrail
+-- IAM

No utilizar Kubernetes salvo que exista una razón técnica y económica real.

==================================================
31. ALTA DISPONIBILIDAD
==================================================

No es obligatorio implementar máxima HA desde el primer día.

Debe implementarse progresivamente.

MVP:

- backups;
- monitoring;
- recuperación;
- arquitectura preparada para escalar.

Producción madura:

- Multi-AZ;
- ECS escalable;
- RDS Multi-AZ;
- Redis con alta disponibilidad;
- ALB;
- redundancia.

==================================================
32. AMBIENTES
==================================================

Deben existir tres ambientes:

DEVELOPMENT
QA
PRODUCTION

Deben mantenerse separados.

Nunca permitir:

Development -> Production Database

QA -> Production Database

Development -> Production Secrets

Cada ambiente debe tener:

- configuración;
- secretos;
- base de datos;
- recursos;
- permisos;

independientes.

==================================================
33. SEGURIDAD
==================================================

Diseñar desde el inicio:

- autenticación segura;
- autorización RBAC;
- permisos por módulo;
- permisos por operación;
- aislamiento Multi-Tenant;
- cifrado;
- Secrets Manager;
- gestión segura de sesiones;
- protección contra SQL Injection;
- validación de entrada;
- CSRF cuando corresponda;
- XSS;
- rate limiting;
- auditoría;
- logs;
- backups;
- recuperación;
- principio de mínimo privilegio;
- seguridad de API;
- seguridad de dispositivos móviles.

==================================================
34. BASE DE DATOS
==================================================

Utilizar PostgreSQL como base de datos principal salvo que exista una razón técnica documentada para cambiarla.

Diseñar:

- PK;
- FK;
- índices;
- restricciones;
- unique constraints;
- check constraints;
- timestamps;
- soft delete cuando corresponda;
- tenant isolation;
- auditoría.

No crear tablas innecesarias.

No diseñar 200 tablas sólo por anticipar funcionalidades futuras.

La arquitectura debe ser modular y evolucionable.

==================================================
35. MÓDULOS INICIALES DEL ERP-WMS
==================================================

Como mínimo evaluar:

1. SaaS / Multi-Tenant
2. Usuarios
3. Roles
4. Permisos
5. Organización
6. Clientes
7. Proveedores
8. Productos
9. Categorías
10. Unidades de medida
11. Conversiones
12. Embalajes
13. Ventas
14. Cotizaciones
15. Facturas
16. Boletas
17. Pedidos
18. Bodegas
19. Sectores
20. Zonas
21. Racks
22. Niveles
23. Ubicaciones
24. Inventario
25. Acopio
26. Pallets
27. LPN
28. CTN
29. Picking
30. Reposición
31. Consolidación
32. Despacho
33. Transferencias
34. Sucursales
35. Stock de sucursales
36. Entregas
37. Guías
38. Transporte
39. Dispositivos móviles
40. Auditoría
41. SaaS Billing

No asumir que todos deben implementarse simultáneamente.

Separar claramente:

MVP
FASE 2
FASE 3
FUTURO

==================================================
36. REGLA FUNDAMENTAL DE ARQUITECTURA
==================================================

No diseñar el sistema alrededor de "pedidos".

El corazón operacional debe ser:

PRODUCTO
+
INVENTARIO
+
UBICACIÓN
+
MOVIMIENTO
+
TAREA
+
DESPACHO

Los documentos comerciales generan demanda.

El WMS transforma esa demanda en operaciones físicas.

==================================================
37. TRAZABILIDAD
==================================================

Toda operación importante debe poder responder:

- quién;
- qué producto;
- cuánto;
- en qué unidad;
- dónde estaba;
- dónde terminó;
- cuándo;
- por qué;
- mediante qué operación;
- desde qué dispositivo;
- asociado a qué documento.

Ejemplo:

Producto X
|
LPN
|
Pallet
|
Acopio
|
Reposición
|
Picking
|
Consolidación
|
Despacho
|
Guía
|
Cliente/Sucursal

==================================================
38. ARQUITECTURA DE SOFTWARE
==================================================

Diseñar una arquitectura modular.

Separar:

- frontend;
- backend;
- dominio;
- persistencia;
- servicios;
- seguridad;
- tareas;
- dispositivos;
- auditoría.

El backend debe ser API-first.

Debe ser posible tener:

- aplicación web;
- aplicación móvil;
- APIs;
- futuros clientes;

sin duplicar la lógica de negocio.

==================================================
39. TECNOLOGÍAS
==================================================

El proyecto actualmente utiliza/considera:

- Python
- FastAPI
- PostgreSQL
- HTML/Jinja2 cuando corresponda
- JavaScript
- Android para dispositivos Zebra
- AWS
- Git/GitHub
- VS Code

No cambiar estas tecnologías sin una justificación técnica clara.

==================================================
40. METODOLOGÍA DE DISEÑO
==================================================

NO comenzar escribiendo código.

Primero realizar:

FASE 1
Mapa completo de módulos ERP-WMS.

FASE 2
Procesos de negocio.

FASE 3
Casos de uso.

FASE 4
Modelo conceptual de datos.

FASE 5
ERD.

FASE 6
Modelo físico PostgreSQL.

FASE 7
Arquitectura backend/frontend/mobile.

FASE 8
Seguridad.

FASE 9
Infraestructura AWS.

FASE 10
MVP.

FASE 11
QA.

FASE 12
Producción.

==================================================
41. REGLAS PARA EL ARQUITECTO
==================================================

Cuando falte información:

NO inventes.

Identifica la información faltante.

Haz preguntas concretas.

Distingue siempre entre:

CONFIRMADO
PROPUESTA
SUPOSICIÓN
PENDIENTE

No conviertas una capacidad futura en requisito del MVP.

No diseñes funcionalidades que explícitamente fueron descartadas.

No introduzcas Justime como integración.

No diseñes el sistema como WMS independiente.

Recuerda siempre:

ESTAMOS CONSTRUYENDO UN ERP-WMS SAAS MULTI-TENANT.

==================================================
42. OBJETIVO FINAL
==================================================

Crear una plataforma ERP-WMS SaaS profesional capaz de:

- administrar múltiples empresas;
- administrar clientes y proveedores;
- administrar productos;
- gestionar ventas;
- gestionar documentos comerciales;
- controlar inventario;
- administrar bodegas;
- administrar sectores;
- administrar ubicaciones;
- controlar acopio;
- gestionar pallets;
- utilizar LPN;
- gestionar CTN/embalajes;
- realizar picking;
- realizar reposición;
- consolidar pedidos;
- despachar;
- transferir inventario a sucursales;
- controlar inventario de sucursales;
- gestionar entregas;
- mantener trazabilidad completa;
- operar mediante dispositivos Zebra;
- imprimir etiquetas;
- funcionar parcialmente offline;
- proporcionar seguridad empresarial;
- soportar múltiples tenants;
- soportar planes SaaS;
- evolucionar hacia billing automático;
- ejecutarse en AWS;
- escalar progresivamente;
- y permitir incorporar nuevos clientes sin rediseñar el sistema.

La prioridad es construir una arquitectura sólida, mantenible, segura, escalable y profesional.

NO escribir código todavía.

Primero analiza todo el contexto y presenta:

1. Mapa de módulos ERP-WMS.
2. Procesos principales.
3. Actores.
4. Flujos operacionales.
5. Entidades principales.
6. Relaciones conceptuales.
7. Reglas de negocio.
8. Qué está confirmado.
9. Qué está pendiente.
10. Qué debe formar parte del MVP.
11. Qué debe quedar para fases posteriores.

Después de validar esa arquitectura, avanzar al ERD y posteriormente al diseño físico de PostgreSQL.