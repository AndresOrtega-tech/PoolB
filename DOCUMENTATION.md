# 📚 Pool Banorte API - Documentación Técnica

## 📋 Índice

1. [Arquitectura del Sistema](#-arquitectura-del-sistema)
2. [Estructura del Proyecto](#-estructura-del-proyecto)
3. [Modelos de Datos](#-modelos-de-datos)
4. [Esquemas Pydantic](#-esquemas-pydantic)
5. [Servicios y Lógica de Negocio](#-servicios-y-lógica-de-negocio)
6. [Endpoints de la API](#-endpoints-de-la-api)
7. [Sistema de Autenticación](#-sistema-de-autenticación)
8. [Base de Datos](#-base-de-datos)
9. [Configuración y Variables de Entorno](#-configuración-y-variables-de-entorno)
10. [Despliegue y DevOps](#-despliegue-y-devops)
11. [Testing y Validación](#-testing-y-validación)
12. [Troubleshooting](#-troubleshooting)

---

## 🏗️ Arquitectura del Sistema

### Patrón de Arquitectura
El proyecto sigue una **arquitectura en capas** con separación clara de responsabilidades:

```
┌─────────────────────────────────────┐
│           Frontend (React)          │
├─────────────────────────────────────┤
│              API Layer              │
│            (FastAPI)                │
├─────────────────────────────────────┤
│           Business Logic            │
│            (Services)               │
├─────────────────────────────────────┤
│           Data Access               │
│          (SQLAlchemy)               │
├─────────────────────────────────────┤
│            Database                 │
│         (PostgreSQL/Supabase)       │
└─────────────────────────────────────┘
```

### Tecnologías Principales

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Framework Web** | FastAPI | Latest | API REST, documentación automática |
| **ORM** | SQLAlchemy | Latest | Mapeo objeto-relacional |
| **Base de Datos** | PostgreSQL | 15+ | Almacenamiento persistente |
| **Hosting BD** | Supabase | - | BaaS con PostgreSQL |
| **Validación** | Pydantic | Latest | Validación de datos y serialización |
| **Migraciones** | Alembic | Latest | Control de versiones de BD |
| **Autenticación** | bcrypt + JWT | Latest | Hash de contraseñas y tokens |
| **Despliegue** | Vercel | - | Serverless deployment |

---

## 📁 Estructura del Proyecto

```
POOL_BANORTE/
├── README.md                    # Documentación de usuario
├── DOCUMENTATION.md            # Documentación técnica (este archivo)
├── TODO.md                     # Lista de tareas y progreso
├── .gitignore                  # Archivos ignorados por Git
└── backend/                    # Código del backend
    ├── main.py                 # Punto de entrada de la aplicación
    ├── index.py                # Punto de entrada para Vercel
    ├── config.py               # Configuración de la aplicación
    ├── database.py             # Configuración de base de datos
    ├── models.py               # Modelos SQLAlchemy
    ├── requirements.txt        # Dependencias Python
    ├── .env.example           # Plantilla de variables de entorno
    ├── vercel.json            # Configuración de Vercel
    ├── routers/               # Endpoints de la API
    │   ├── __init__.py
    │   └── users.py           # Endpoints de usuarios
    ├── schemas/               # Esquemas Pydantic
    │   ├── __init__.py
    │   └── user_schemas.py    # Esquemas de usuarios
    ├── services/              # Lógica de negocio
    │   ├── __init__.py
    │   └── user_services.py   # Servicios de usuarios
    └── utils/                 # Utilidades
        ├── __init__.py
        └── auth.py            # Utilidades de autenticación
```

### Descripción de Directorios

- **`routers/`**: Contiene los endpoints de la API organizados por dominio
- **`schemas/`**: Esquemas Pydantic para validación y serialización
- **`services/`**: Lógica de negocio y operaciones CRUD
- **`utils/`**: Funciones auxiliares y utilidades compartidas
- **`models.py`**: Definición de modelos SQLAlchemy
- **`database.py`**: Configuración de conexión a base de datos

---

## 🗃️ Modelos de Datos

### Modelo User

```python
class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Modelo Pool (Futuro)

```python
class Pool(BaseModel):
    __tablename__ = "pools"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    organizer_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0.00)
    deadline = Column(DateTime(timezone=True))
    visibility = Column(String(50), default="private")
    allow_partial_contributions = Column(Boolean, default=True)
    allow_anonymous_contributions = Column(Boolean, default=False)
    comments_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

---

## 📝 Esquemas Pydantic

### Esquemas de Usuario

#### UserBase
```python
class UserBase(BaseModel):
    email: EmailStr
    name: str
```

#### UserCreate
```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
```

#### UserCreateDB
```python
class UserCreateDB(UserBase):
    """Esquema para crear usuario en BD con contraseña hasheada"""
    password: str  # Hash bcrypt
```

#### UserUpdate
```python
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
```

#### UserResponse
```python
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### Esquemas de Autenticación
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserResponseWithToken(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str
```

---

## ⚙️ Servicios y Lógica de Negocio

### UserService

```python
class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Crear nuevo usuario con contraseña hasheada"""
        
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Listar usuarios con paginación"""
        
    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Eliminar usuario"""
        
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuario (pendiente implementación)"""
```

---

## 🔌 Endpoints de la API

### Endpoints de Sistema

| Método | Endpoint | Descripción | Respuesta |
|--------|----------|-------------|-----------|
| `GET` | `/` | Mensaje de bienvenida | `{"message": "Pool Banorte API está funcionando"}` |
| `GET` | `/health` | Estado completo (incluye BD) | Estado detallado con conexiones |
| `GET` | `/health-simple` | Estado básico | Estado simple sin BD |
| `GET` | `/debug-env` | Variables de entorno | Info de configuración |
| `GET` | `/docs` | Documentación Swagger | Interfaz interactiva |
| `GET` | `/redoc` | Documentación ReDoc | Documentación alternativa |

### Endpoints de Usuarios

| Método | Endpoint | Descripción | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/users/` | Listar usuarios | - | `List[UserResponse]` |
| `GET` | `/users/{user_id}` | Obtener usuario | - | `UserResponse` |
| `POST` | `/users/` | Crear usuario | `UserCreate` | `UserResponse` |
| `PUT` | `/users/{user_id}` | Actualizar completo | `UserCreate` | `UserResponse` |
| `PATCH` | `/users/{user_id}` | Actualizar parcial | `UserUpdate` | `UserResponse` |
| `DELETE` | `/users/{user_id}` | Eliminar usuario | - | `204 No Content` |

### Parámetros de Query

#### GET /users/
- `skip` (int, default=0): Número de registros a omitir
- `limit` (int, default=100): Número máximo de registros a retornar

### Códigos de Estado HTTP

| Código | Descripción | Cuándo se usa |
|--------|-------------|---------------|
| `200` | OK | Operación exitosa |
| `201` | Created | Usuario creado exitosamente |
| `204` | No Content | Usuario eliminado exitosamente |
| `400` | Bad Request | Datos inválidos o email duplicado |
| `404` | Not Found | Usuario no encontrado |
| `422` | Unprocessable Entity | Error de validación Pydantic |
| `500` | Internal Server Error | Error interno del servidor |

---

## 🔐 Sistema de Autenticación

### Utilidades de Autenticación

#### PasswordManager
```python
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseña con bcrypt"""
        
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
```

#### TokenManager
```python
class TokenManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Inicializar gestor de tokens JWT"""
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        
    def verify_token(self, token: str) -> TokenData:
        """Verificar y decodificar token JWT"""
```

### Funciones de Conveniencia

```python
def hash_password(password: str) -> str:
    """Función de conveniencia para hashear contraseñas"""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Función de conveniencia para verificar contraseñas"""

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Función de conveniencia para crear tokens"""

def verify_token(token: str) -> TokenData:
    """Función de conveniencia para verificar tokens"""
```

### Variables de Entorno para JWT

```env
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🗄️ Base de Datos

### Configuración de Conexión

#### Para Desarrollo Local
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/pool_banorte"
```

#### Para Supabase (Producción)
```python
DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres"
```

### Configuración SQLAlchemy

```python
# Optimizado para Vercel Serverless
engine = create_engine(
    DATABASE_URL,
    pool_size=0,  # Sin pool para serverless
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=False,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
        "application_name": "pool_banorte_api"
    }
)
```

### Migraciones con Alembic

#### Comandos Básicos
```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history

# Revertir migración
alembic downgrade -1
```

#### Estructura de Migración
```python
"""Agregar campo password a usuarios

Revision ID: abc123
Revises: def456
Create Date: 2024-08-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('password', sa.String(255), nullable=False))

def downgrade():
    op.drop_column('users', 'password')
```

---

## ⚙️ Configuración y Variables de Entorno

### Variables Requeridas

```env
# Base de Datos
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres

# Supabase
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=[ANON-KEY]
SUPABASE_SERVICE_KEY=[SERVICE-KEY]

# JWT
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
ALLOWED_ORIGINS=http://localhost:3000,https://tu-frontend.vercel.app
ENVIRONMENT=production
DEBUG=false
```

### Variables Opcionales

```env
# Configuración adicional
PYTHONPATH=/var/task
LOG_LEVEL=INFO
MAX_CONNECTIONS=20
```

### Configuración por Entorno

#### Desarrollo
```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://user:password@localhost:5432/pool_banorte_dev
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Producción
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres
ALLOWED_ORIGINS=https://pool-banorte.vercel.app
```

---

## 🚀 Despliegue y DevOps

### Despliegue en Vercel

#### Configuración vercel.json
```json
{
  "functions": {
    "backend/index.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/index.py"
    }
  ]
}
```

#### Punto de Entrada (index.py)
```python
from main import app

# Vercel requiere que la aplicación se exporte como 'app'
# El archivo main.py contiene la aplicación FastAPI
```

### Configuración de Supabase

#### 1. Configurar Connection Pooling
- Habilitar **Transaction Pooler** en Settings → Database
- Usar puerto **6543** en lugar de 5432
- Configurar **SSL Enforcement**

#### 2. Configurar Variables de Entorno en Vercel
```bash
vercel env add DATABASE_URL
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_KEY
vercel env add JWT_SECRET_KEY
vercel env add ALLOWED_ORIGINS
```

#### 3. Desplegar
```bash
vercel --prod
```

### Monitoreo y Logs

#### Logs de Vercel
```bash
vercel logs [deployment-url]
```

#### Health Checks
- `/health` - Verificación completa con BD
- `/health-simple` - Verificación básica
- `/debug-env` - Variables de entorno (desarrollo)

---

## 🧪 Testing y Validación

### Testing Manual de Endpoints

#### 1. Crear Usuario
```bash
curl -X POST "https://tu-api.vercel.app/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Usuario Test",
    "password": "password123"
  }'
```

#### 2. Listar Usuarios
```bash
curl -X GET "https://tu-api.vercel.app/users/?skip=0&limit=10"
```

#### 3. Obtener Usuario
```bash
curl -X GET "https://tu-api.vercel.app/users/{user_id}"
```

#### 4. Actualizar Usuario
```bash
curl -X PATCH "https://tu-api.vercel.app/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nuevo Nombre"
  }'
```

#### 5. Eliminar Usuario
```bash
curl -X DELETE "https://tu-api.vercel.app/users/{user_id}"
```

### Casos de Prueba

#### Casos Exitosos
- ✅ Crear usuario con datos válidos
- ✅ Listar usuarios con paginación
- ✅ Obtener usuario existente
- ✅ Actualizar usuario parcial/completo
- ✅ Eliminar usuario existente

#### Casos de Error
- ❌ Crear usuario con email duplicado (400)
- ❌ Crear usuario con contraseña débil (422)
- ❌ Obtener usuario inexistente (404)
- ❌ Actualizar usuario inexistente (404)
- ❌ Eliminar usuario inexistente (404)

### Validaciones de Contraseña

```python
# Casos válidos
"password123"  # ✅ Letra + número, 8+ chars
"MyPass456"    # ✅ Letra + número, 8+ chars
"test1234"     # ✅ Letra + número, 8+ chars

# Casos inválidos
"password"     # ❌ Sin números
"12345678"     # ❌ Sin letras
"pass123"      # ❌ Menos de 8 caracteres
""             # ❌ Vacía
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos

**Síntoma**: `connection to server failed`

**Soluciones**:
```bash
# Verificar variables de entorno
curl https://tu-api.vercel.app/debug-env

# Verificar health check
curl https://tu-api.vercel.app/health

# Verificar configuración de Supabase
# - SSL Enforcement habilitado
# - Transaction Pooler configurado (puerto 6543)
# - IP allowlist configurado si es necesario
```

#### 2. Error de Validación Pydantic

**Síntoma**: `422 Unprocessable Entity`

**Soluciones**:
```python
# Verificar formato de email
"email": "usuario@example.com"  # ✅ Válido
"email": "usuario-invalid"      # ❌ Inválido

# Verificar contraseña
"password": "password123"  # ✅ Válido (letra + número, 8+ chars)
"password": "pass123"      # ❌ Inválido (menos de 8 chars)
```

#### 3. Error de Usuario Duplicado

**Síntoma**: `400 Bad Request: El email ya está registrado`

**Solución**:
```python
# Verificar si el usuario ya existe antes de crear
GET /users/?email=usuario@example.com
```

#### 4. Error de Token JWT

**Síntoma**: `401 Unauthorized` o `Invalid token`

**Soluciones**:
```bash
# Verificar variables de entorno JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Verificar formato del token en headers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Logs y Debugging

#### Habilitar Logs Detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Estado de la Aplicación
```bash
# Health check completo
curl https://tu-api.vercel.app/health

# Variables de entorno
curl https://tu-api.vercel.app/debug-env

# Documentación interactiva
https://tu-api.vercel.app/docs
```

### Comandos Útiles

```bash
# Verificar dependencias
pip list

# Verificar migraciones
alembic current
alembic history

# Verificar conexión a BD local
psql -h localhost -U usuario -d pool_banorte

# Verificar logs de Vercel
vercel logs --follow
```

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Documentation](https://vercel.com/docs)

### Herramientas de Desarrollo
- [Swagger UI](https://swagger.io/tools/swagger-ui/) - Documentación interactiva
- [ReDoc](https://redocly.github.io/redoc/) - Documentación alternativa
- [Postman](https://www.postman.com/) - Testing de APIs
- [pgAdmin](https://www.pgadmin.org/) - Administración de PostgreSQL

---

*Documentación generada para Pool Banorte API v1.0.0*  
*Última actualización: Agosto 2024*  
*Para más información, consultar el [README.md](README.md) o el [TODO.md](TODO.md)*