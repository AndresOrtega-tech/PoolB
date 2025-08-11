# Tests Pool Banorte API - Vercel

Tests para verificar el funcionamiento de la API en el deploy de Vercel con Supabase.

## 📁 Archivos de Tests

### `test_auth_complete.py`
Test completo de autenticación JWT en Vercel:
- ✅ Salud de la API
- 🔐 Registro de usuarios
- 🔑 Login (OAuth2)
- 🛡️ Validaciones de seguridad
- 👤 Acceso a endpoints protegidos

### `test_users_crud.py`
Test completo del CRUD de usuarios en Vercel:
- ✅ Salud de la API
- 👤 Crear usuarios
- 📋 Listar usuarios
- 🔍 Obtener usuario específico
- ✏️ Actualizar usuarios
- 🗑️ Eliminar usuarios
- ❌ Casos de error

## 🚀 Ejecutar Tests

### Configuración Previa
1. Actualizar las URLs de Vercel en los archivos:
   ```python
   # En test_auth_complete.py
   VERCEL_URL = "https://tu-app.vercel.app/"
   
   # En test_users_crud.py
   VERCEL_URL = "https://tu-app.vercel.app/"
   ```

### Ejecutar Tests de Autenticación
```bash
cd backend/tests
python test_auth_complete.py
```

### Ejecutar Tests de CRUD
```bash
cd backend/tests
python test_users_crud.py
```

## 🔧 Configuración de Vercel

Asegúrate de que tu deploy en Vercel tenga configuradas las variables de entorno:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`
- `ALGORITHM`

## 📊 Interpretación de Resultados

### ✅ Tests Exitosos
- API funcionando correctamente
- Base de datos conectada
- Endpoints respondiendo

### ❌ Tests Fallidos
- Verificar URL de Vercel
- Revisar variables de entorno
- Comprobar conexión a Supabase
- Cold start puede causar timeouts

## ⚠️ Notas Importantes

- **Cold Start**: La primera petición puede tardar hasta 45 segundos
- **Timeout**: Los tests usan timeout de 45s para manejar cold starts
- **Base de Datos**: Los tests crean y eliminan datos reales en Supabase
- **Limpieza**: Los tests limpian los datos de prueba automáticamente