# ReviewTap

**Tu cliente toca. Tu negocio escucha.**

ReviewTap conecta negocios con sus clientes mediante NFC y QR, facilitando el acceso a canales oficiales de feedback y proporcionando analytics sobre las interacciones.

## Problema

Los negocios dificultan a sus clientes compartir experiencias. Los clientes no encuentran fácilmente los canales oficiales (Google Reviews, WhatsApp, Instagram, etc.) y los negocios pierden oportunidades de feedback auténtico.

## Solución

ReviewTap ofrece dispositivos NFC/QR que, al ser tocados o escaneados, llevan al cliente a una página personalizada con acceso directo a los canales oficiales del negocio.

## Stack

- **Backend:** Python 3.13, Flask 3.1, SQLAlchemy 2.0
- **Base de datos:** PostgreSQL (producción) / SQLite (testing)
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Auth:** Flask-Login, Flask-WTF (CSRF)
- **Rate Limiting:** Flask-Limiter
- **QR:** qrcode + Pillow
- **Deploy:** Render

## Arquitectura

```
reviewtap/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── config.py            # Config por entornos
│   ├── extensions.py        # Flask extensions (db, migrate, login, csrf, limiter)
│   ├── models/              # SQLAlchemy models (User, Business, Location, NFCDevice, QRCode, AnalyticsEvent, AuditLog)
│   ├── routes/              # Blueprints (auth, business, location, devices, public, dashboard, landing, errors)
│   ├── services/            # Lógica de negocio (authorization, auth, business, location, device, dashboard)
│   ├── templates/           # Jinja2 (auth, dashboard, public, landing)
│   └── static/              # CSS, JS
├── tests/                   # 141 tests (pytest)
├── requirements.txt
├── .env.example
├── render.yaml
└── run.py
```

## Funcionalidades

### Multi-tenancy
- Registro y autenticación de usuarios
- Roles: `admin`, `business_owner`, `staff`
- Aislamiento por `business_id` en todas las queries
- 404 para acceso no autorizado (previene enumeración de tenants)

### Gestión de Negocios
- CRUD completo de negocios con soft delete
- Ubicaciones por negocio
- Dispositivos NFC con códigos únicos de 8 caracteres
- Generación de QR (PNG y SVG) con URL absoluta

### Página Pública
- Perfil público responsive por dispositivo NFC/QR
- Canales configurables (Google, WhatsApp, Instagram, Facebook, TripAdvisor, Sitio web)
- Validación de URLs de canales
- Tracking de interacciones (escaneos, clics)
- Eventos analytics por canal

### Dashboard
- Métricas: negocios, dispositivos, escaneos, clics, clic rate
- Detalle por negocio con event breakdown
- Auditoría de actividad
- Navegación responsive con hamburger menu

### Landing Page
- Hero section, features, benefits, CTA
- SEO optimizado

### Seguridad
- Password hashing con Werkzeug (PBKDF2)
- CSRF protection en todos los formularios
- Sesiones: `HTTPONLY`, `SAMESITE=Lax`, `SECURE` en producción
- Rate limiting: 60/min en `/r/<device_code>`, 30/min en `/track`
- XSS protection (Jinja2 escaping)
- External links: `rel="noopener noreferrer"`
- Auditoría en AuditLog

## Instalación local

```bash
# Clonar repositorio
git clone https://github.com/alvaroberrio23242-eng/reviewtap.git
cd reviewtap

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar migraciones
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Ejecutar la aplicación
python run.py
```

## Configuración

Copia `.env.example` a `.env` y configura:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Flask | (requerida) |
| `DATABASE_URL` | URL de conexión a PostgreSQL | SQLite local |
| `BASE_URL` | URL pública de la app | `http://127.0.0.1:5000` |
| `FLASK_ENV` | Entorno de ejecución | `development` |
| `RATELIMIT_ENABLED` | Habilitar rate limiting | `true` |

## Tests

```bash
# Ejecutar todos los tests
python -m pytest -q

# Ejecutar con verbosidad
python -m pytest -v
```

**141 tests** cubriendo:

| Suite | Tests |
|-------|-------|
| Infraestructura | 7 |
| Auth | 15 |
| Authorization | 8 |
| Business | 15 |
| Location | 14 |
| Device | 17 |
| Public | 34 |
| Dashboard | 14 |
| Landing | 15 |
| **Total** | **141** |

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/register` | No | Registro de usuario |
| POST | `/login` | No | Inicio de sesión |
| POST | `/logout` | Sí | Cierre de sesión |
| GET | `/me` | Sí | Usuario actual |
| GET | `/` | No | Landing page |
| GET | `/r/<device_code>` | No | Página pública del dispositivo |
| POST | `/track` | No | Tracking de clics |
| GET/POST | `/business` | Sí | CRUD de negocios |
| GET/POST | `/business/<id>/locations` | Sí | CRUD de ubicaciones |
| GET/POST | `/business/<id>/devices` | Sí | CRUD de dispositivos |
| GET | `/dashboard` | Sí | Dashboard principal |
| GET | `/dashboard/business/<id>` | Sí | Detalle de negocio |

## Modelo de negocio

| Plan | Negocios | Ubicaciones | Dispositivos | Precio |
|------|----------|-------------|--------------|--------|
| FREE | 1 | 1 | 1 | Gratis |
| STARTER | 1 | 3 | 5 | Configurable |
| PRO | 5 | 10 | 25 | Configurable |
| BUSINESS | Ilimitado | Ilimitado | Ilimitado | Configurable |

## Estado

**Fase 1-6.5 completada.** 141/141 tests passing.

Funcionalidades implementadas: auth, roles, multi-tenancy, business CRUD, location CRUD, device CRUD, QR generation, public profiles, analytics, dashboard, landing page, rate limiting, CSRF, responsive navigation.

## Licencia

MIT License
