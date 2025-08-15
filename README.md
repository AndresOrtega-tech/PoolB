# Pool Banorte API

Una API REST desarrollada con FastAPI para gestionar colectas de dinero (pools) entre usuarios. El sistema permite crear, administrar y participar en colectas de dinero de manera colaborativa.

## 🚀 Estado Actual del Proyecto

✅ **COMPLETADO:**
- Sistema de gestión de usuarios (CRUD completo)
- Base de datos configurada en Supabase
- API desplegada en Vercel
- Sistema de autenticación con contraseñas hasheadas (bcrypt)
- **Sistema de autenticación JWT completo**
- **Endpoints de autenticación (login, register, refresh)**
- **Middleware de autenticación y protección de rutas**
- Tests automatizados (95% de éxito en auth, 76.5% en CRUD con auth)
- Conexión dual a base de datos (SQLAlchemy + psycopg2)
- Optimización para entornos serverless

🔄 **EN DESARROLLO:**
- Endpoints para gestión de pools
- Sistema de participantes y contribuciones
- Integración con APIs de Banorte

## 🛠️ Tecnologías

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Autenticación**: bcrypt + JWT (OAuth2 + Bearer Token)
- **Despliegue**: Vercel
- **Testing**: Requests + pytest
- **Seguridad**: python-jose, passlib, JWT tokens

## 📋 Requisitos

- Python 3.8+
- PostgreSQL (o cuenta de Supabase)
- Node.js (para despliegue en Vercel)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd POOL_BANORTE
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate     # Linux/Mac
```

### 3. Instalar dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo `.env.example` a `.env` y configura las variables:

```env
# Base de datos (usar Transaction Pooler de Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:6543/postgres

# Supabase
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=[ANON-KEY]
SUPABASE_SERVICE_KEY=[SERVICE-KEY]

# Autenticación JWT
JWT_SECRET=tu-clave-secreta-muy-segura-de-al-menos-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
ALLOWED_ORIGINS=http://localhost:3000,https://tu-frontend.vercel.app
ENVIRONMENT=development
DEBUG=true
```

### 5. Ejecutar la aplicación
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## 🗄️ Esquema de Base de Datos

### Usuarios (`users`)
```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hash bcrypt
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Pools (`pools`) - En desarrollo
```sql
CREATE TABLE IF NOT EXISTS pools (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🌐 Endpoints de la API

### Estado de la API
- `GET /` - Mensaje de bienvenida
- `GET /health` - Verificación completa del estado (incluye conexión a BD)
- `GET /health-simple` - Verificación básica del estado

### 🔐 Autenticación
- `POST /auth/register` - Registro de nuevos usuarios
- `POST /auth/login` - Login con OAuth2 (form data)
- `POST /auth/login-json` - Login con JSON
- `POST /auth/refresh` - Renovar token de acceso
- `GET /auth/me` - Obtener información del usuario actual (requiere auth)

### 👥 Usuarios (Protegidos con JWT)
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios (con paginación) 🔒
- `GET /users/{user_id}` - Obtener usuario por ID 🔒
- `PUT /users/{user_id}` - Actualizar usuario completo 🔒
- `PATCH /users/{user_id}` - Actualizar usuario parcial 🔒
- `DELETE /users/{user_id}` - Eliminar usuario 🔒

### 📚 Documentación Interactiva
- `GET /docs` - Swagger UI (documentación interactiva)
- `GET /redoc` - ReDoc (documentación alternativa)

## 🚀 Despliegue en Vercel

### 1. Configurar Supabase
1. Crear proyecto en [Supabase](https://supabase.com)
2. Ejecutar el script SQL para crear la tabla `users`
3. Habilitar **SSL Enforcement** en Settings → Database
4. Obtener la **Connection String del Transaction Pooler** (puerto 6543)

### 2. Configurar Vercel
1. Conectar el repositorio a Vercel
2. Configurar las variables de entorno en Vercel:
   - `DATABASE_URL` (usar la URI del Transaction Pooler)
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `JWT_SECRET` (clave secreta segura de al menos 32 caracteres)
   - `JWT_ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=30`
   - `ALLOWED_ORIGINS`
   - `ENVIRONMENT=production`

### 3. Desplegar
```bash
vercel --prod
```

## ⚙️ Configuración Avanzada

### Optimizaciones para Serverless
La aplicación está optimizada para entornos serverless con:
- `pool_size=0` - Sin pool de conexiones persistente
- `pool_pre_ping=False` - Sin verificación previa de conexiones
- Timeouts de 30 segundos para conexiones
- Configuración SSL optimizada para Supabase
- Forzado de IPv4 para evitar problemas de conectividad

### Conexión Dual a Base de Datos
El sistema implementa dos métodos de conexión:
1. **SQLAlchemy** - Para operaciones normales con ORM
2. **psycopg2 directo** - Como fallback para máxima compatibilidad

## 🧪 Testing

### Ejecutar tests de autenticación
```bash
cd backend
python tests/test_auth_complete.py
```

### Ejecutar tests de CRUD con autenticación
```bash
cd backend
python tests/test_users_crud.py
```

### Ejecutar todos los tests con pytest
```bash
cd backend
python -m pytest tests/ -v
```

### Verificar Estado de la API
```bash
curl https://tu-api.vercel.app/health
```

### Probar autenticación
```bash
# Registrar usuario
curl -X POST "https://tu-api.vercel.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"password123"}'

# Login
curl -X POST "https://tu-api.vercel.app/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

### Respuesta esperada:
```json
{
    "status": "healthy",
    "database": "connected",
    "sqlalchemy_status": true,
    "direct_connection_status": true,
    "environment": "production"
}
```

## 📁 Estructura del Proyecto

```
POOL_BANORTE/
├── backend/
│   ├── main.py                     # Aplicación principal FastAPI
│   ├── database.py                 # Configuración de base de datos
│   ├── models.py                   # Modelos SQLAlchemy
│   ├── config.py                   # Configuración de la aplicación
│   ├── index.py                    # Punto de entrada para Vercel
│   ├── requirements.txt            # Dependencias Python
│   ├── vercel.json                 # Configuración de Vercel
│   ├── pytest.ini                 # Configuración de pytest
│   ├── .env.example                # Ejemplo de variables de entorno
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py                 # Dependencias de autenticación JWT
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Endpoints de autenticación JWT
│   │   └── users.py                # Endpoints de usuarios
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user_schemas.py         # Esquemas Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_services.py        # Lógica de negocio
│   ├── utils/
│   │   ├── __init__.py
│   │   └── auth.py                 # Utilidades de autenticación
│   └── tests/
│       ├── README.md               # Documentación de tests
│       ├── test_auth_complete.py   # Tests completos de autenticación
│       └── test_users_crud.py      # Tests del CRUD de usuarios
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Este archivo
├── TODO.md                         # Lista de tareas
└── DOCUMENTATION.md                # Documentación técnica
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación en `/docs` de la API
2. Verifica el estado de la API en `/health`
3. Revisa los logs de Vercel para errores de despliegue
4. Asegúrate de que la configuración de Supabase sea correcta

## 📊 Estado del Proyecto

- ✅ **API Base**: Configuración inicial completa
- ✅ **Base de Datos**: Esquema implementado y optimizado
- ✅ **Despliegue**: Configurado para Vercel serverless
- ✅ **Sistema de Usuarios**: CRUD completo y funcional
- ✅ **Autenticación JWT**: Sistema completo implementado
- ✅ **Middleware de Seguridad**: Protección de rutas implementada
- ✅ **Testing**: Suite de tests automatizados (95% auth, 76.5% CRUD)
- 🔄 **En Desarrollo**: Endpoints CRUD para pools y participantes
- 📋 **Próximo**: Sistema de pools y transacciones

### 🎯 Progreso General: **~80% completado** para MVP básico

### 🚀 Últimos Cambios Implementados:
- ✅ **Sistema de autenticación JWT completo**
- ✅ **Endpoints de registro, login y refresh**
- ✅ **Middleware de autenticación con Bearer tokens**
- ✅ **Protección de rutas sensibles**
- ✅ **Tests automatizados de autenticación**
- ✅ **Integración OAuth2 con FastAPI**

---

**Pool Banorte API** - Sistema de gestión de colectas colaborativas