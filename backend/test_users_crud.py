#!/usr/bin/env python3
"""
Test del CRUD de Usuarios - Pool Banorte API
============================================

Este archivo contiene tests para verificar el funcionamiento
completo del CRUD de usuarios en el deploy de Vercel con Supabase.

Ejecutar con: python test_users_crud.py
"""

import requests
import json
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Configuración para diferentes entornos
ENVIRONMENTS = {
    "local": "http://localhost:8000",
    "vercel": "https://pool-banorte-api.vercel.app",  # Cambiar por tu URL de Vercel
    "custom": None  # Se puede especificar manualmente
}

class UserCRUDTester:
    def __init__(self, environment: str = "vercel"):
        if environment in ENVIRONMENTS:
            self.base_url = ENVIRONMENTS[environment]
        else:
            self.base_url = environment  # URL personalizada
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Pool-Banorte-CRUD-Tester/1.0'
        })
        
        self.test_user_id: Optional[str] = None
        self.test_results = []
        self.environment = environment
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registrar resultado de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Hacer petición HTTP con manejo de errores para Vercel/Supabase"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Configurar timeout más largo para cold starts de Vercel
            if method.upper() == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
                
            # Manejar respuestas vacías (como 204 No Content)
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = {"message": "No JSON content"} if response.content else None
                
            return {
                "status_code": response.status_code,
                "data": response_data,
                "success": 200 <= response.status_code < 300,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.Timeout:
            return {
                "status_code": 0,
                "data": {"error": "Request timeout - Vercel cold start?"},
                "success": False
            }
        except requests.exceptions.ConnectionError:
            return {
                "status_code": 0,
                "data": {"error": "Connection error - Check URL and internet"},
                "success": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }

    def test_api_health(self):
        """Test 0: Verificar que la API esté funcionando en Vercel"""
        print(f"\n🔍 Test 0: Verificando API en {self.environment.upper()}...")
        print(f"URL: {self.base_url}")
        
        # Test health check básico con timeout extendido para cold start
        print("⏳ Esperando respuesta (cold start puede tomar 10-15s)...")
        result = self.make_request("GET", "/health-simple", timeout=45)
        
        if result["success"]:
            self.log_test("Health Check Básico", True, f"Status: {result['status_code']}")
        else:
            self.log_test("Health Check Básico", False, f"Error: {result['data']}")
            return False
            
        # Test health check completo
        result = self.make_request("GET", "/health", timeout=30)
        if result["success"]:
            db_status = result["data"].get("database", "unknown") if result["data"] else "unknown"
            supabase_status = "✅ Conectado" if db_status == "connected" else f"⚠️ {db_status}"
            self.log_test("Health Check Completo", True, f"Supabase: {supabase_status}")
        else:
            self.log_test("Health Check Completo", False, f"Error: {result['data']}")
            
        return True

    def test_create_user(self):
        """Test 1: Crear usuario en Supabase"""
        print("\n📝 Test 1: Creando usuario en Supabase...")
        
        # Datos de usuario válido con timestamp para evitar duplicados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_data = {
            "email": f"test_{timestamp}_{uuid.uuid4().hex[:6]}@poolbanorte.com",
            "name": f"Usuario Test {timestamp}",
            "password": "SecurePass123!"
        }
        
        print(f"📧 Email de prueba: {user_data['email']}")
        result = self.make_request("POST", "/users/", user_data)
        
        if result["success"] and result["status_code"] == 201:
            user = result["data"]
            self.test_user_id = user["id"]
            self.log_test("Crear Usuario en Supabase", True, 
                         f"ID: {user['id'][:8]}..., Email: {user['email']}")
            return True
        else:
            error_detail = result["data"].get("detail", result["data"]) if result["data"] else "Unknown error"
            self.log_test("Crear Usuario en Supabase", False, 
                         f"Status: {result['status_code']}, Error: {error_detail}")
            return False

    def test_create_user_validations(self):
        """Test 2: Validaciones con Supabase"""
        print("\n🔍 Test 2: Probando validaciones con Supabase...")
        
        # Test email duplicado
        if self.test_user_id:
            get_result = self.make_request("GET", f"/users/{self.test_user_id}")
            if get_result["success"]:
                existing_email = get_result["data"]["email"]
                
                duplicate_data = {
                    "email": existing_email,
                    "name": "Usuario Duplicado",
                    "password": "SecurePass123!"
                }
                
                result = self.make_request("POST", "/users/", duplicate_data)
                if result["status_code"] == 400:
                    self.log_test("Email Duplicado Supabase (400)", True, "Constraint correcta")
                else:
                    self.log_test("Email Duplicado Supabase (400)", False, 
                                 f"Expected 400, got {result['status_code']}")
        
        # Test email inválido
        invalid_email_data = {
            "email": "email-sin-arroba-ni-dominio",
            "name": "Usuario Test",
            "password": "SecurePass123!"
        }
        
        result = self.make_request("POST", "/users/", invalid_email_data)
        if result["status_code"] == 422:
            self.log_test("Email Inválido (422)", True, "Validación Pydantic correcta")
        else:
            self.log_test("Email Inválido (422)", False, 
                         f"Expected 422, got {result['status_code']}")
        
        # Test contraseña débil
        weak_password_data = {
            "email": f"weak_{uuid.uuid4().hex[:8]}@poolbanorte.com",
            "name": "Usuario Test",
            "password": "123"  # Muy corta
        }
        
        result = self.make_request("POST", "/users/", weak_password_data)
        if result["status_code"] == 422:
            self.log_test("Contraseña Débil (422)", True, "Validación bcrypt correcta")
        else:
            self.log_test("Contraseña Débil (422)", False, 
                         f"Expected 422, got {result['status_code']}")

    def test_get_user(self):
        """Test 3: Obtener usuario desde Supabase"""
        print("\n👤 Test 3: Obteniendo usuario desde Supabase...")
        
        if not self.test_user_id:
            self.log_test("Obtener Usuario Supabase", False, "No hay usuario de test")
            return False
            
        result = self.make_request("GET", f"/users/{self.test_user_id}")
        
        if result["success"]:
            user = result["data"]
            expected_fields = ["id", "email", "name", "created_at"]
            missing_fields = [field for field in expected_fields if field not in user]
            
            if not missing_fields:
                self.log_test("Obtener Usuario Supabase", True, 
                             f"Campos: {', '.join(expected_fields)}")
                
                # Verificar que no se devuelva la contraseña hasheada
                if "password" not in user:
                    self.log_test("Password Hash No Expuesto", True, "Seguridad bcrypt correcta")
                else:
                    self.log_test("Password Hash No Expuesto", False, "¡Hash de contraseña expuesto!")
                
                # Verificar formato UUID de Supabase
                if len(user["id"]) == 36 and user["id"].count("-") == 4:
                    self.log_test("UUID Supabase Válido", True, f"Formato correcto: {user['id'][:8]}...")
                else:
                    self.log_test("UUID Supabase Válido", False, f"Formato incorrecto: {user['id']}")
                    
                return True
            else:
                self.log_test("Obtener Usuario Supabase", False, 
                             f"Campos faltantes: {missing_fields}")
        else:
            self.log_test("Obtener Usuario Supabase", False, 
                         f"Status: {result['status_code']}")
            
        return False

    def test_list_users(self):
        """Test 5: Listar usuarios desde Supabase"""
        print("\n📋 Test 5: Listando usuarios desde Supabase...")
        
        # Test sin parámetros
        result = self.make_request("GET", "/users/")
        
        if result["success"]:
            users = result["data"]
            if isinstance(users, list):
                self.log_test("Listar Usuarios Supabase", True, f"Encontrados: {len(users)} usuarios")
                
                # Verificar que nuestro usuario esté en la lista
                if self.test_user_id:
                    user_found = any(user["id"] == self.test_user_id for user in users)
                    if user_found:
                        self.log_test("Usuario en Lista Supabase", True, "Usuario test encontrado")
                    else:
                        self.log_test("Usuario en Lista Supabase", False, "Usuario test no encontrado")
            else:
                self.log_test("Listar Usuarios Supabase", False, "Respuesta no es una lista")
        else:
            self.log_test("Listar Usuarios Supabase", False, f"Status: {result['status_code']}")
        
        # Test con paginación
        result = self.make_request("GET", "/users/?skip=0&limit=3")
        if result["success"]:
            users = result["data"]
            if len(users) <= 3:
                self.log_test("Paginación Supabase", True, f"Límite respetado: {len(users)}/3")
            else:
                self.log_test("Paginación Supabase", False, f"Límite excedido: {len(users)}/3")

    def test_update_user_partial(self):
        """Test 6: Actualización parcial en Supabase"""
        print("\n✏️ Test 6: Actualización parcial en Supabase...")
        
        if not self.test_user_id:
            self.log_test("Actualización Parcial Supabase", False, "No hay usuario de test")
            return False
            
        # Actualizar solo el nombre
        update_data = {
            "name": f"Nombre Actualizado {datetime.now().strftime('%H:%M:%S')}"
        }
        
        result = self.make_request("PATCH", f"/users/{self.test_user_id}", update_data)
        
        if result["success"]:
            user = result["data"]
            if user["name"] == update_data["name"]:
                self.log_test("Actualización Parcial Supabase", True, "Nombre actualizado en DB")
                return True
            else:
                self.log_test("Actualización Parcial Supabase", False, 
                             f"Nombre no actualizado: {user['name']}")
        else:
            self.log_test("Actualización Parcial Supabase", False, 
                         f"Status: {result['status_code']}")
            
        return False

    def test_update_user_complete(self):
        """Test 7: Actualización completa en Supabase"""
        print("\n🔄 Test 7: Actualización completa en Supabase...")
        
        if not self.test_user_id:
            self.log_test("Actualización Completa Supabase", False, "No hay usuario de test")
            return False
            
        # Actualización completa
        timestamp = datetime.now().strftime("%H%M%S")
        update_data = {
            "email": f"updated_{timestamp}_{uuid.uuid4().hex[:6]}@poolbanorte.com",
            "name": f"Usuario Actualizado {timestamp}",
            "password": "NewSecurePass123!"
        }
        
        result = self.make_request("PUT", f"/users/{self.test_user_id}", update_data)
        
        if result["success"]:
            user = result["data"]
            if (user["name"] == update_data["name"] and 
                user["email"] == update_data["email"]):
                self.log_test("Actualización Completa Supabase", True, "Datos actualizados en DB")
                return True
            else:
                self.log_test("Actualización Completa Supabase", False, "Datos no actualizados")
        else:
            self.log_test("Actualización Completa Supabase", False, 
                         f"Status: {result['status_code']}")
            
        return False

    def test_delete_user(self):
        """Test 9: Eliminar usuario de Supabase"""
        print("\n🗑️ Test 9: Eliminando usuario de Supabase...")
        
        if not self.test_user_id:
            self.log_test("Eliminar Usuario Supabase", False, "No hay usuario de test")
            return False
            
        result = self.make_request("DELETE", f"/users/{self.test_user_id}")
        
        if result["status_code"] == 204:
            self.log_test("Eliminar Usuario Supabase", True, "Usuario eliminado de DB")
            
            # Verificar que realmente se eliminó de Supabase
            get_result = self.make_request("GET", f"/users/{self.test_user_id}")
            if get_result["status_code"] == 404:
                self.log_test("Verificar Eliminación Supabase", True, "Usuario no existe en DB")
                return True
            else:
                self.log_test("Verificar Eliminación Supabase", False, "Usuario aún existe en DB")
        else:
            self.log_test("Eliminar Usuario Supabase", False, 
                         f"Expected 204, got {result['status_code']}")
            
        return False

    def test_error_cases(self):
        """Test de casos de error específicos de Vercel/Supabase"""
        print("\n🔍 Test: Casos de error Vercel/Supabase...")
        
        # Test usuario inexistente
        fake_id = str(uuid.uuid4())
        result = self.make_request("GET", f"/users/{fake_id}")
        
        if result["status_code"] == 404:
            self.log_test("Usuario Inexistente Supabase (404)", True, "Error correcto")
        else:
            self.log_test("Usuario Inexistente Supabase (404)", False, 
                         f"Expected 404, got {result['status_code']}")
        
        # Test actualizar usuario inexistente
        update_data = {"name": "No debería funcionar"}
        result = self.make_request("PATCH", f"/users/{fake_id}", update_data)
        
        if result["status_code"] == 404:
            self.log_test("Actualizar Inexistente Supabase (404)", True, "Error correcto")
        else:
            self.log_test("Actualizar Inexistente Supabase (404)", False, 
                         f"Expected 404, got {result['status_code']}")
        
        # Test eliminar usuario inexistente
        result = self.make_request("DELETE", f"/users/{fake_id}")
        
        if result["status_code"] == 404:
            self.log_test("Eliminar Inexistente Supabase (404)", True, "Error correcto")
        else:
            self.log_test("Eliminar Inexistente Supabase (404)", False, 
                         f"Expected 404, got {result['status_code']}")

    def run_all_tests(self):
        """Ejecutar todos los tests para Vercel/Supabase"""
        print("🚀 Iniciando Tests del CRUD - Vercel + Supabase")
        print("=" * 60)
        print(f"🌐 Entorno: {self.environment.upper()}")
        print(f"🔗 URL: {self.base_url}")
        print(f"🗄️ Base de datos: Supabase PostgreSQL")
        print("=" * 60)
        
        # Verificar que la API esté funcionando
        if not self.test_api_health():
            print("\n❌ API no disponible en Vercel. Verificar:")
            print("  - URL de deploy correcta")
            print("  - Variables de entorno en Vercel")
            print("  - Conexión a Supabase")
            print("  - Cold start (primera petición puede tardar)")
            return
        
        # Ejecutar tests en orden
        tests = [
            self.test_create_user,
            self.test_create_user_validations,
            self.test_get_user,
            self.test_list_users,
            self.test_update_user_partial,
            self.test_update_user_complete,
            self.test_error_cases,
            self.test_delete_user
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Exception: {str(e)}")
        
        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprimir resumen de tests para Vercel/Supabase"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS - VERCEL + SUPABASE")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"🌐 Entorno: {self.environment.upper()}")
        print(f"🔗 URL: {self.base_url}")
        print(f"📊 Total de tests: {total_tests}")
        print(f"✅ Exitosos: {passed_tests}")
        print(f"❌ Fallidos: {failed_tests}")
        print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Tests fallidos ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Estado del CRUD en {self.environment.upper()}:")
        if failed_tests == 0:
            print("✅ CRUD completamente funcional en Vercel + Supabase")
            print("🔐 Listo para implementar autenticación JWT")
        elif failed_tests <= 2:
            print("⚠️ CRUD mayormente funcional - Revisar fallos menores")
            print("🔧 Posibles problemas de configuración en Vercel/Supabase")
        else:
            print("❌ CRUD necesita correcciones importantes")
            print("🔧 Revisar variables de entorno y conexión a Supabase")
        
        print(f"\n📋 Próximos pasos:")
        if failed_tests == 0:
            print("  1. ✅ CRUD verificado - Continuar con autenticación")
            print("  2. 🔐 Implementar endpoints de login/register")
            print("  3. 🛡️ Añadir middleware de autenticación")
        else:
            print("  1. 🔧 Corregir fallos identificados")
            print("  2. 🔄 Re-ejecutar tests")
            print("  3. ✅ Verificar CRUD antes de autenticación")


def main():
    """Función principal"""
    print("🏦 Pool Banorte API - Test del CRUD en Vercel + Supabase")
    print("=" * 60)
    
    # Seleccionar entorno
    print("Selecciona el entorno a probar:")
    print("1. 🌐 Vercel (Producción)")
    print("2. 💻 Local (Desarrollo)")
    print("3. 🔧 URL personalizada")
    
    choice = input("\nOpción (1-3): ").strip()
    
    if choice == "1":
        environment = "vercel"
        print(f"\n🌐 Probando en Vercel: {ENVIRONMENTS['vercel']}")
        print("⚠️ Asegúrate de actualizar la URL en ENVIRONMENTS['vercel']")
    elif choice == "2":
        environment = "local"
        print(f"\n💻 Probando en Local: {ENVIRONMENTS['local']}")
    elif choice == "3":
        custom_url = input("Ingresa la URL personalizada: ").strip()
        environment = custom_url
        print(f"\n🔧 Probando en: {custom_url}")
    else:
        print("❌ Opción inválida. Usando Vercel por defecto.")
        environment = "vercel"
    
    # Confirmar ejecución
    response = input(f"\n¿Continuar con los tests en {environment}? (y/N): ").lower().strip()
    if response not in ['y', 'yes', 'sí', 'si']:
        print("Tests cancelados.")
        return
    
    # Ejecutar tests
    tester = UserCRUDTester(environment)
    tester.run_all_tests()


if __name__ == "__main__":
    main()