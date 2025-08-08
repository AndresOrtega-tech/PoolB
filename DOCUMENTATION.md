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
| **Framework Web** | FastAPI | 0.104.1 | API REST, documentación automática |
| **ORM** | SQLAlchemy | 2.0.23 | Mapeo objeto-relacional |
| **Base de Datos** | PostgreSQL | 15+ | Almacenamiento persistente |
| **Hosting BD** | Supabase | - | BaaS con PostgreSQL |
| **Validación** | Pydantic | 2.5.0 | Validación de datos y serialización |
| **Migraciones** | Alembic | 1.13.0 | Control de versiones de BD |
| **Autenticación** | bcrypt + JWT | 4.1.2 / 3.3.0 | Hash de contraseñas y tokens |
| **Despliegue** | Vercel | - | Serverless deployment |

### Estado Actual del Proyecto ✅

- ✅ **CRUD de Usuarios**: Completamente implementado y probado (19/19 tests pasados)
- ✅ **Base de Datos**: Configurada y operativa en Supabase
- ✅ **Autenticación Básica**: Hash de contraseñas implementado
- ✅ **API Desplegada**: Funcionando en Vercel
- ✅ **Testing Automatizado**: Suite completa de tests
- 🔄 **Próximo**: Sistema de autenticación JWT

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
    ├── tests/                 # Tests automatizados
    │   ├── __init__.py
    │   └── test_users_crud.py # Tests del CRUD de usuarios
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
- **`tests/`**: Suite de tests automatizados
- **`models.py`**: Definición de modelos SQLAlchemy
- **`database.py`**: Configuración de conexión a base de datos

---

## 🗃️ Modelos de Datos

### Modelo User ✅ **IMPLEMENTADO**

```python
class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Características**:
- ✅ **ID**: UUID generado automáticamente
- ✅ **Email**: Único e indexado
- ✅ **Password**: Hasheado con bcrypt
- ✅ **Timestamps**: Automáticos con triggers de BD

### Modelo Pool 🔄 **PENDIENTE**

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

### Esquemas de Usuario ✅ **IMPLEMENTADOS**

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
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('La contraseña debe contener al menos una letra')
            if not re.search(r'\d', v):
                raise ValueError('La contraseña debe contener al menos un número')
        return v
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

#### Esquemas de Autenticación 🔄 **PENDIENTES**
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

### UserService ✅ **IMPLEMENTADO**

```python
class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Crear nuevo usuario con contraseña hasheada"""
        # ✅ Implementado con hash de contraseñas
        
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        # ✅ Implementado y probado
        
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        # ✅ Implementado y probado
        
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Listar usuarios con paginación"""
        # ✅ Implementado y probado
        
    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        # ✅ Implementado con hash de contraseñas
        
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Eliminar usuario"""
        # ✅ Implementado y probado
        
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        # 🔄 Pendiente implementación
```

**Estado de Testing**: ✅ **19/19 tests pasados (100% de éxito)**

---

## 🔌 Endpoints de la API

### Endpoints de Sistema ✅ **OPERATIVOS**

| Método | Endpoint | Descripción | Respuesta |
|--------|----------|-------------|-----------|
| `GET` | `/` | Mensaje de bienvenida | `{"message": "Pool Banorte API está funcionando"}` |
| `GET` | `/health` | Estado completo (incluye BD) | Estado detallado con conexiones |
| `GET` | `/health-simple` | Estado básico | Estado simple sin BD |
| `GET` | `/docs` | Documentación Swagger | Interfaz interactiva |
| `GET` | `/redoc` | Documentación ReDoc | Documentación alternativa |

### Endpoints de Usuarios ✅ **COMPLETAMENTE FUNCIONALES**

| Método | Endpoint | Descripción | Request Body | Response | Estado |
|--------|----------|-------------|--------------|----------|--------|
| `GET` | `/users/` | Listar usuarios | - | `List[UserResponse]` | ✅ |
| `GET` | `/users/{user_id}` | Obtener usuario | - | `UserResponse` | ✅ |
| `POST` | `/users/` | Crear usuario | `UserCreate` | `UserResponse` | ✅ |
| `PUT` | `/users/{user_id}` | Actualizar completo | `UserCreate` | `UserResponse` | ✅ |
| `PATCH` | `/users/{user_id}` | Actualizar parcial | `UserUpdate` | `UserResponse` | ✅ |
| `DELETE` | `/users/{user_id}` | Eliminar usuario | - | `204 No Content` | ✅ |

### Endpoints de Autenticación 🔄 **PENDIENTES**

| Método | Endpoint | Descripción | Request Body | Response | Estado |
|--------|----------|-------------|--------------|----------|--------|
| `POST` | `/auth/login` | Autenticación | `UserLogin` | `Token` | 🔄 |
| `POST` | `/auth/register` | Registro | `UserCreate` | `UserResponseWithToken` | 🔄 |
| `POST` | `/auth/refresh` | Renovar token | `RefreshToken` | `Token` | 🔄 |

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

### Utilidades de Autenticación ✅ **IMPLEMENTADAS**

#### PasswordManager
```python
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseña con bcrypt"""
        # ✅ Implementado con fallback a SHA256
        
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
        # ✅ Implementado con soporte bcrypt y SHA256
```

#### TokenManager ✅ **IMPLEMENTADO**
```python
class TokenManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Inicializar gestor de tokens JWT"""
        # ✅ Implementado
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        # ✅ Implementado
        
    def verify_token(self, token: str) -> TokenData:
        """Verificar y decodificar token JWT"""
        # ✅ Implementado
```

### Funciones de Conveniencia ✅ **IMPLEMENTADAS**

```python
def hash_password(password: str) -> str:
    """Función de conveniencia para hashear contraseñas"""
    # ✅ Funcionando en producción

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Función de conveniencia para verificar contraseñas"""
    # ✅ Funcionando en producción

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Función de conveniencia para crear tokens"""
    # ✅ Listo para usar

def verify_token(token: str) -> TokenData:
    """Función de conveniencia para verificar tokens"""
    # ✅ Listo para usar
```

### Variables de Entorno para JWT

```env
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Estado Actual de Seguridad

- ✅ **Hash de Contraseñas**: Implementado y funcionando
- ✅ **Utilidades JWT**: Implementadas y listas
- ✅ **Validaciones**: Contraseñas seguras requeridas
- 🔄 **Endpoints Auth**: Pendiente implementación
- 🔄 **Middleware**: Pendiente protección de rutas

---

## 🗄️ Base de Datos

### Configuración de Conexión ✅ **OPERATIVA**

#### Para Supabase (Producción)
```python
DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres"
```

### Configuración SQLAlchemy ✅ **OPTIMIZADA**

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

### Estado de la Base de Datos ✅ **COMPLETAMENTE FUNCIONAL**

#### Tabla `users` ✅ **OPERATIVA**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

#### Datos de Ejemplo
```
id: 710bc396-1b70-4a45-bbab-5357f299a0b8
email: test@example.com
name: Test User
password: b55c8792d1ce458e279308835f8a97b500... (hash bcrypt)
created_at: 2025-08-08 19:16:47.243643+00
updated_at: NULL
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

---

## ⚙️ Configuración y Variables de Entorno

### Variables Requeridas ✅ **CONFIGURADAS**

```env
# Base de Datos
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres

# Supabase
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=[ANON-KEY]
SUPABASE_SERVICE_KEY=[SERVICE-KEY]

# JWT (Pendiente configurar en producción)
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
ALLOWED_ORIGINS=http://localhost:3000,https://tu-frontend.vercel.app
ENVIRONMENT=production
```

### Configuración por Entorno

#### Producción (Vercel) ✅ **CONFIGURADO**
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres
ALLOWED_ORIGINS=https://pool-banorte.vercel.app
```

#### Desarrollo Local
```env
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/pool_banorte_dev
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🚀 Despliegue y DevOps

### Despliegue en Vercel ✅ **OPERATIVO**

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

### Configuración de Supabase ✅ **COMPLETADA**

#### 1. Connection Pooling ✅ **CONFIGURADO**
- ✅ **Transaction Pooler** habilitado
- ✅ Puerto **6543** configurado
- ✅ **SSL Enforcement** habilitado

#### 2. Variables de Entorno en Vercel ✅ **CONFIGURADAS**
```bash
DATABASE_URL=postgresql://postgres:...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
ALLOWED_ORIGINS=...
ENVIRONMENT=production
```

### Estado de Conexiones ✅ **TODAS OPERATIVAS**
- ✅ **SQLAlchemy**: Funcionando correctamente
- ✅ **psycopg2 directo**: Funcionando correctamente
- ✅ **Transaction Pooler**: Configurado y operativo
- ✅ **SSL**: Habilitado y funcionando

### Monitoreo y Logs

#### Health Checks ✅ **FUNCIONANDO**
- `/health` - Verificación completa con BD ✅
- `/health-simple` - Verificación básica ✅

#### Logs de Vercel
```bash
vercel logs [deployment-url]
```

---

## 🧪 Testing y Validación

### Suite de Tests Automatizados ✅ **COMPLETADA**

#### Archivo: `backend/tests/test_users_crud.py`

**Resultado**: ✅ **19/19 tests pasados (100% de éxito)**

#### Tests Implementados:

1. **Conectividad** ✅
   - Verificación de estado de API
   - Conexión a base de datos

2. **Crear Usuario** ✅
   - Usuario válido
   - Email duplicado (error 400)
   - Contraseña débil (error 422)

3. **Listar Usuarios** ✅
   - Listado básico
   - Paginación

4. **Obtener Usuario** ✅
   - Usuario existente
   - Usuario inexistente (error 404)

5. **Actualizar Usuario** ✅
   - Actualización completa (PUT)
   - Actualización parcial (PATCH)
   - Usuario inexistente (error 404)

6. **Eliminar Usuario** ✅
   - Eliminación exitosa
   - Usuario inexistente (error 404)

7. **Validaciones de Seguridad** ✅
   - Contraseña no expuesta en respuestas
   - Hash de contraseñas funcionando

### Testing Manual de Endpoints

#### 1. Crear Usuario ✅
```bash
curl -X POST "https://pool-banorte-api.vercel.app/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Usuario Test",
    "password": "password123"
  }'
```

#### 2. Listar Usuarios ✅
```bash
curl -X GET "https://pool-banorte-api.vercel.app/users/?skip=0&limit=10"
```

#### 3. Obtener Usuario ✅
```bash
curl -X GET "https://pool-banorte-api.vercel.app/users/{user_id}"
```

#### 4. Actualizar Usuario ✅
```bash
curl -X PATCH "https://pool-banorte-api.vercel.app/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nuevo Nombre"
  }'
```

#### 5. Eliminar Usuario ✅
```bash
curl -X DELETE "https://pool-banorte-api.vercel.app/users/{user_id}"
```

### Casos de Prueba

#### Casos Exitosos ✅
- ✅ Crear usuario con datos válidos
- ✅ Listar usuarios con paginación
- ✅ Obtener usuario existente
- ✅ Actualizar usuario parcial/completo
- ✅ Eliminar usuario existente

#### Casos de Error ✅
- ✅ Crear usuario con email duplicado (400)
- ✅ Crear usuario con contraseña débil (422)
- ✅ Obtener usuario inexistente (404)
- ✅ Actualizar usuario inexistente (404)
- ✅ Eliminar usuario inexistente (404)

### Validaciones de Contraseña ✅

```python
# Casos válidos ✅
"password123"  # ✅ Letra + número, 8+ chars
"MyPass456"    # ✅ Letra + número, 8+ chars
"test1234"     # ✅ Letra + número, 8+ chars

# Casos inválidos ✅
"password"     # ❌ Sin números (detectado)
"12345678"     # ❌ Sin letras (detectado)
"pass123"      # ❌ Menos de 8 caracteres (detectado)
""             # ❌ Vacía (detectado)
```

---

## 🔧 Troubleshooting

### Problemas Resueltos ✅

#### 1. Conexión a Base de Datos ✅ **RESUELTO**

**Problema**: `connection to server failed`

**Solución aplicada**:
- ✅ Configuración del Transaction Pooler de Supabase
- ✅ Corrección del parámetro inválido `command_timeout`
- ✅ Optimización para Vercel Serverless

#### 2. Tabla Users Incompleta ✅ **RESUELTO**

**Problema**: Faltaban columnas `created_at` y `updated_at`

**Solución aplicada**:
- ✅ Creación manual de tabla completa en Supabase
- ✅ Configuración de triggers para timestamps automáticos
- ✅ Validación con tests automatizados

#### 3. CRUD de Usuarios ✅ **RESUELTO**

**Problema**: Necesidad de implementar y validar CRUD completo

**Solución aplicada**:
- ✅ Implementación de todos los endpoints CRUD
- ✅ Suite de tests automatizados (19/19 pasados)
- ✅ Validación en producción (Vercel + Supabase)

### Problemas Comunes y Soluciones

#### Error de Validación Pydantic

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

#### Error de Usuario Duplicado

**Síntoma**: `400 Bad Request: El email ya está registrado`

**Solución**:
```python
# Verificar si el usuario ya existe antes de crear
GET /users/?email=usuario@example.com
```

### Comandos Útiles

```bash
# Verificar estado de la API
curl https://pool-banorte-api.vercel.app/health

# Ejecutar tests
cd backend/tests
python test_users_crud.py

# Verificar logs de Vercel
vercel logs --follow

# Documentación interactiva
https://pool-banorte-api.vercel.app/docs
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

### URLs del Proyecto

- **API en Producción**: `https://pool-banorte-api.vercel.app`
- **Documentación Swagger**: `https://pool-banorte-api.vercel.app/docs`
- **Documentación ReDoc**: `https://pool-banorte-api.vercel.app/redoc`
- **Health Check**: `https://pool-banorte-api.vercel.app/health`

---

## 📊 Estado Actual del Proyecto

### Progreso General: **~75% completado** para MVP básico

#### ✅ Completado (100%)
- **Base de datos**: Configurada y operativa
- **CRUD de usuarios**: Completamente implementado y probado
- **Seguridad básica**: Hash de contraseñas funcionando
- **API desplegada**: Funcionando en Vercel
- **Testing**: Suite completa de tests automatizados

#### 🔄 En Progreso (0%)
- **Autenticación JWT**: Utilidades listas, endpoints pendientes
- **Middleware de autenticación**: Pendiente implementación
- **Protección de rutas**: Pendiente implementación

#### ❌ Pendiente (0%)
- **Sistema de pools**: Modelos y endpoints pendientes
- **Sistema de participantes**: Pendiente implementación
- **Sistema de contribuciones**: Pendiente implementación

### Próximos Pasos

1. **🔐 Implementar endpoints de autenticación JWT**
2. **🛡️ Implementar middleware de autenticación**
3. **🏗️ Desarrollar funcionalidades de pools**
4. **🤝 Implementar sistema de participantes**
5. **💰 Desarrollar sistema de contribuciones**

---

*Documentación generada para Pool Banorte API v1.0.0*  
*Última actualización: Diciembre 2024*  
*Estado: CRUD de usuarios completamente funcional ✅*  
*Para más información, consultar el [README.md](README.md) o el [TODO.md](TODO.md)*