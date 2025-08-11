#!/usr/bin/env python3
"""
Test de Autenticación JWT - Pool Banorte API en Vercel
=====================================================

Este archivo contiene tests para verificar el funcionamiento
del sistema de autenticación JWT en el deploy de Vercel.

Ejecutar con: python test_auth_complete.py
"""

import requests
import json
import uuid
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# URL del deploy en Vercel - ACTUALIZAR CON TU URL
VERCEL_URL = "https://pool-b.vercel.app/"

class AuthTester:
    def __init__(self):
        self.base_url = VERCEL_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Pool-Banorte-Auth-Tester/1.0'
        })
        
        self.test_user_data: Optional[Dict] = None
        self.test_token: Optional[str] = None
        self.test_user_id: Optional[str] = None
        self.test_results = []
        
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
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    headers: Dict = None, timeout: int = 45) -> Dict[str, Any]:
        """Hacer petición HTTP optimizada para Vercel con manejo de cold starts"""
        url = f"{self.base_url}{endpoint}"
        
        # Combinar headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            # Timeout extendido para cold starts de Vercel
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=timeout)
            elif method.upper() == "POST":
                if endpoint == "/auth/login":
                    # OAuth2 form data - remover Content-Type para que requests lo configure automáticamente
                    oauth_headers = {k: v for k, v in request_headers.items() if k.lower() != 'content-type'}
                    response = self.session.post(url, data=data, headers=oauth_headers, timeout=timeout)
                else:
                    # JSON data
                    response = self.session.post(url, json=data, headers=request_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers, timeout=timeout)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=request_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
                
            # Manejar respuestas vacías
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
        print(f"\n🔍 Test 0: Verificando API en VERCEL...")
        print(f"URL: {self.base_url}")
        print("⏳ Esperando respuesta (cold start puede tomar 10-15s)...")
        
        timeout = 45  # Timeout extendido para cold start de Vercel
            
        # Intentar varios endpoints para verificar la API
        endpoints_to_test = ["/", "/health", "/docs"]
        api_working = False
        
        for endpoint in endpoints_to_test:
            result = self.make_request("GET", endpoint, timeout=timeout)
            if result["success"]:
                self.log_test(f"Health Check {endpoint}", True, f"Status: {result['status_code']}")
                api_working = True
                break
            else:
                self.log_test(f"Health Check {endpoint}", False, f"Error: {result['data']}")
        
        if not api_working:
            self.log_test("API Health Check", False, "Ningún endpoint responde")
            return False
            
        # Test específico de documentación
        result = self.make_request("GET", "/docs", timeout=timeout)
        if result["success"]:
            self.log_test("Swagger UI Disponible", True, "Documentación accesible")
        else:
            self.log_test("Swagger UI Disponible", False, "Documentación no accesible")
            
        return True

    def test_register_user(self):
        """Test 1: Registro de usuario"""
        print("\n📝 Test 1: Registro de usuario...")
        
        # Datos de usuario válido con timestamp para evitar duplicados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_user_data = {
            "email": f"test_{timestamp}_{uuid.uuid4().hex[:6]}@poolbanorte.com",
            "name": f"Usuario Test {timestamp}",
            "password": "SecurePass123!"
        }
        
        print(f"📧 Email de prueba: {self.test_user_data['email']}")
        result = self.make_request("POST", "/auth/register", self.test_user_data)
        
        if result["success"] and result["status_code"] == 201:
            user_response = result["data"]
            self.test_user_id = user_response["id"]
            self.test_token = user_response.get("access_token")
            
            # Verificar campos requeridos
            required_fields = ["id", "email", "name", "access_token", "token_type"]
            missing_fields = [field for field in required_fields if field not in user_response]
            
            if not missing_fields:
                self.log_test("Registro de Usuario", True, 
                             f"ID: {user_response['id'][:8]}..., Token recibido")
                
                # Verificar que no se devuelva la contraseña
                if "password" not in user_response:
                    self.log_test("Seguridad Password", True, "Contraseña no expuesta")
                else:
                    self.log_test("Seguridad Password", False, "¡Contraseña expuesta!")
                    
                return True
            else:
                self.log_test("Registro de Usuario", False, 
                             f"Campos faltantes: {missing_fields}")
        else:
            error_detail = result["data"].get("detail", result["data"]) if result["data"] else "Unknown error"
            self.log_test("Registro de Usuario", False, 
                         f"Status: {result['status_code']}, Error: {error_detail}")
            
        return False

    def test_register_validations(self):
        """Test 2: Validaciones de registro"""
        print("\n🔍 Test 2: Validaciones de registro...")
        
        # Test email duplicado
        if self.test_user_data:
            result = self.make_request("POST", "/auth/register", self.test_user_data)
            if result["status_code"] == 400:
                self.log_test("Email Duplicado (400)", True, "Validación correcta")
            else:
                self.log_test("Email Duplicado (400)", False, 
                             f"Expected 400, got {result['status_code']}")
        
        # Test email inválido
        invalid_email_data = {
            "email": "email-sin-arroba-ni-dominio",
            "name": "Usuario Test",
            "password": "SecurePass123!"
        }
        
        result = self.make_request("POST", "/auth/register", invalid_email_data)
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
        
        result = self.make_request("POST", "/auth/register", weak_password_data)
        if result["status_code"] in [422, 400]:
            self.log_test("Contraseña Débil", True, f"Validación correcta ({result['status_code']})")
        else:
            self.log_test("Contraseña Débil", False, 
                         f"Expected 422/400, got {result['status_code']}")

    def test_login_oauth2(self):
        """Test 3: Login con OAuth2 (formulario)"""
        print("\n🔐 Test 3: Login OAuth2...")
        
        if not self.test_user_data:
            self.log_test("Login OAuth2", False, "No hay datos de usuario de test")
            return False
            
        # Login con formulario OAuth2 (compatible con Swagger UI)
        login_data = {
            "username": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        
        if result["success"] and result["status_code"] == 200:
            token_response = result["data"]
            
            # Verificar campos del token
            required_fields = ["access_token", "token_type"]
            missing_fields = [field for field in required_fields if field not in token_response]
            
            if not missing_fields:
                self.log_test("Login OAuth2", True, "Token recibido correctamente")
                
                # Verificar tipo de token
                if token_response["token_type"] == "bearer":
                    self.log_test("Token Type Bearer", True, "Tipo correcto")
                else:
                    self.log_test("Token Type Bearer", False, 
                                 f"Expected 'bearer', got '{token_response['token_type']}'")
                    
                return True
            else:
                self.log_test("Login OAuth2", False, 
                             f"Campos faltantes: {missing_fields}")
        else:
            error_detail = result["data"].get("detail", result["data"]) if result["data"] else "Unknown error"
            self.log_test("Login OAuth2", False, 
                         f"Status: {result['status_code']}, Error: {error_detail}")
            
        return False

    def test_login_json(self):
        """Test 4: Login con JSON"""
        print("\n🔐 Test 4: Login JSON...")
        
        if not self.test_user_data:
            self.log_test("Login JSON", False, "No hay datos de usuario de test")
            return False
            
        # Login con JSON
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        result = self.make_request("POST", "/auth/login-json", login_data)
        
        if result["success"] and result["status_code"] == 200:
            token_response = result["data"]
            
            if "access_token" in token_response:
                self.test_token = token_response["access_token"]  # Actualizar token
                self.log_test("Login JSON", True, "Token recibido correctamente")
                return True
            else:
                self.log_test("Login JSON", False, "Token no recibido")
        else:
            error_detail = result["data"].get("detail", result["data"]) if result["data"] else "Unknown error"
            self.log_test("Login JSON", False, 
                         f"Status: {result['status_code']}, Error: {error_detail}")
            
        return False

    def test_login_invalid_credentials(self):
        """Test 5: Login con credenciales inválidas"""
        print("\n🔐 Test 5: Credenciales inválidas...")
        
        if not self.test_user_data:
            self.log_test("Credenciales Inválidas", False, "No hay datos de usuario de test")
            return False
        
        # Test contraseña incorrecta
        invalid_data = {
            "email": self.test_user_data["email"],
            "password": "wrong_password"
        }
        
        result = self.make_request("POST", "/auth/login-json", invalid_data)
        
        if result["status_code"] == 401:
            self.log_test("Contraseña Incorrecta (401)", True, "Error correcto")
        else:
            self.log_test("Contraseña Incorrecta (401)", False, 
                         f"Expected 401, got {result['status_code']}")
        
        # Test usuario inexistente
        nonexistent_data = {
            "email": "noexiste@poolbanorte.com",
            "password": "password123"
        }
        
        result = self.make_request("POST", "/auth/login-json", nonexistent_data)
        
        if result["status_code"] == 401:
            self.log_test("Usuario Inexistente (401)", True, "Error correcto")
        else:
            self.log_test("Usuario Inexistente (401)", False, 
                         f"Expected 401, got {result['status_code']}")

    def test_get_current_user(self):
        """Test 6: Obtener usuario actual con token"""
        print("\n👤 Test 6: Usuario actual...")
        
        if not self.test_token:
            self.log_test("Usuario Actual", False, "No hay token de test")
            return False
            
        # Obtener usuario actual con token válido
        headers = {"Authorization": f"Bearer {self.test_token}"}
        result = self.make_request("GET", "/auth/me", headers=headers)
        
        if result["success"] and result["status_code"] == 200:
            user_data = result["data"]
            
            # Verificar campos esperados
            expected_fields = ["id", "email", "name"]
            missing_fields = [field for field in expected_fields if field not in user_data]
            
            if not missing_fields:
                # Verificar que los datos coincidan
                if (user_data["email"] == self.test_user_data["email"] and
                    user_data["name"] == self.test_user_data["name"]):
                    self.log_test("Usuario Actual", True, "Datos correctos")
                    
                    # Verificar que no se devuelva la contraseña
                    if "password" not in user_data:
                        self.log_test("Seguridad Token", True, "Contraseña no expuesta")
                    else:
                        self.log_test("Seguridad Token", False, "¡Contraseña expuesta!")
                        
                    return True
                else:
                    self.log_test("Usuario Actual", False, "Datos no coinciden")
            else:
                self.log_test("Usuario Actual", False, 
                             f"Campos faltantes: {missing_fields}")
        else:
            error_detail = result["data"].get("detail", result["data"]) if result["data"] else "Unknown error"
            self.log_test("Usuario Actual", False, 
                         f"Status: {result['status_code']}, Error: {error_detail}")
            
        return False

    def test_invalid_tokens(self):
        """Test 7: Tokens inválidos"""
        print("\n🔐 Test 7: Tokens inválidos...")
        
        # Test sin token
        result = self.make_request("GET", "/auth/me")
        if result["status_code"] == 401:
            self.log_test("Sin Token (401)", True, "Error correcto")
        else:
            self.log_test("Sin Token (401)", False, 
                         f"Expected 401, got {result['status_code']}")
        
        # Test token inválido
        headers = {"Authorization": "Bearer token_invalido"}
        result = self.make_request("GET", "/auth/me", headers=headers)
        if result["status_code"] == 401:
            self.log_test("Token Inválido (401)", True, "Error correcto")
        else:
            self.log_test("Token Inválido (401)", False, 
                         f"Expected 401, got {result['status_code']}")
        
        # Test formato de token incorrecto
        headers = {"Authorization": "InvalidFormat token"}
        result = self.make_request("GET", "/auth/me", headers=headers)
        if result["status_code"] == 401:
            self.log_test("Formato Token Incorrecto (401)", True, "Error correcto")
        else:
            self.log_test("Formato Token Incorrecto (401)", False, 
                         f"Expected 401, got {result['status_code']}")

    def test_protected_endpoints(self):
        """Test 8: Endpoints protegidos"""
        print("\n🛡️ Test 8: Endpoints protegidos...")
        
        # Test acceso sin token
        result = self.make_request("GET", "/users/")
        if result["status_code"] == 401:
            self.log_test("Endpoint Protegido Sin Token (401)", True, "Protección correcta")
        else:
            self.log_test("Endpoint Protegido Sin Token (401)", False, 
                         f"Expected 401, got {result['status_code']}")
        
        # Test acceso con token válido
        if self.test_token:
            headers = {"Authorization": f"Bearer {self.test_token}"}
            result = self.make_request("GET", "/users/", headers=headers)
            if result["success"]:
                self.log_test("Endpoint Protegido Con Token", True, "Acceso autorizado")
            else:
                self.log_test("Endpoint Protegido Con Token", False, 
                             f"Status: {result['status_code']}")

    def test_user_profile_access(self):
        """Test 9: Acceso al perfil propio"""
        print("\n👤 Test 9: Acceso al perfil...")
        
        if not self.test_token or not self.test_user_id:
            self.log_test("Acceso Perfil Propio", False, "No hay token o ID de usuario")
            return False
            
        # Acceder al perfil propio
        headers = {"Authorization": f"Bearer {self.test_token}"}
        result = self.make_request("GET", f"/users/{self.test_user_id}", headers=headers)
        
        if result["success"]:
            user_data = result["data"]
            if user_data["email"] == self.test_user_data["email"]:
                self.log_test("Acceso Perfil Propio", True, "Datos correctos")
                return True
            else:
                self.log_test("Acceso Perfil Propio", False, "Datos incorrectos")
        else:
            self.log_test("Acceso Perfil Propio", False, 
                         f"Status: {result['status_code']}")
            
        return False

    def test_full_auth_flow(self):
        """Test 10: Flujo completo de autenticación"""
        print("\n🔄 Test 10: Flujo completo...")
        
        # Crear un segundo usuario para probar el flujo completo
        timestamp = datetime.now().strftime("%H%M%S")
        flow_user_data = {
            "email": f"flow_{timestamp}_{uuid.uuid4().hex[:6]}@poolbanorte.com",
            "name": f"Usuario Flujo {timestamp}",
            "password": "FlowPass123!"
        }
        
        # 1. Registrar
        register_result = self.make_request("POST", "/auth/register", flow_user_data)
        if not register_result["success"]:
            self.log_test("Flujo Completo - Registro", False, "Registro falló")
            return False
            
        register_token = register_result["data"]["access_token"]
        
        # 2. Login
        login_data = {
            "email": flow_user_data["email"],
            "password": flow_user_data["password"]
        }
        login_result = self.make_request("POST", "/auth/login-json", login_data)
        if not login_result["success"]:
            self.log_test("Flujo Completo - Login", False, "Login falló")
            return False
            
        login_token = login_result["data"]["access_token"]
        
        # 3. Usar ambos tokens para acceder a endpoints protegidos
        tokens_valid = 0
        for i, token in enumerate([register_token, login_token], 1):
            headers = {"Authorization": f"Bearer {token}"}
            me_result = self.make_request("GET", "/auth/me", headers=headers)
            if me_result["success"] and me_result["data"]["email"] == flow_user_data["email"]:
                tokens_valid += 1
        
        if tokens_valid == 2:
            self.log_test("Flujo Completo", True, "Registro → Login → Acceso exitoso")
            return True
        else:
            self.log_test("Flujo Completo", False, f"Solo {tokens_valid}/2 tokens válidos")
            
        return False

    def run_all_tests(self):
        """Ejecutar todos los tests de autenticación en Vercel"""
        print("🚀 Tests de Autenticación JWT - Pool Banorte API")
        print("=" * 60)
        print(f"🌐 Entorno: VERCEL")
        print(f"🔗 URL: {self.base_url}")
        print(f"🔐 Sistema: Autenticación JWT + bcrypt")
        print("=" * 60)
        
        # Verificar que la API esté funcionando
        if not self.test_api_health():
            print("\n❌ API no disponible en Vercel. Verificar:")
            print("  - URL de deploy correcta")
            print("  - Variables de entorno en Vercel")
            print("  - Conexión a Supabase")
            print("  - Cold start (primera petición puede tardar)")
            print("  - Deploy exitoso sin errores")
            return
        
        # Ejecutar tests en orden
        tests = [
            self.test_register_user,
            self.test_register_validations,
            self.test_login_oauth2,
            self.test_login_json,
            self.test_login_invalid_credentials,
            self.test_get_current_user,
            self.test_invalid_tokens,
            self.test_protected_endpoints,
            self.test_user_profile_access,
            self.test_full_auth_flow
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Exception: {str(e)}")
        
        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprimir resumen de tests"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS - AUTENTICACIÓN JWT EN VERCEL")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"🌐 Entorno: VERCEL")
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
        
        print(f"\n🎯 Estado de la Autenticación en VERCEL:")
        if failed_tests == 0:
            print("✅ Sistema de autenticación JWT completamente funcional en producción")
            print("🔐 Listo para implementar pools y funcionalidades avanzadas")
        elif failed_tests <= 2:
            print("⚠️ Autenticación mayormente funcional - Revisar fallos menores")
            print("🔧 Posibles problemas de configuración en Vercel")
        else:
            print("❌ Sistema de autenticación necesita correcciones importantes")
            print("🔧 Revisar implementación JWT, variables de entorno y deploy")
        
        print(f"\n📋 Próximos pasos:")
        if failed_tests == 0:
            print("  1. ✅ Autenticación verificada en producción")
            print("  2. 💰 Implementar sistema de pools de dinero")
            print("  3. 👥 Añadir funcionalidades de grupos")
            print("  4. 🚀 Continuar desarrollo con confianza")
        else:
            print("  1. 🔧 Corregir fallos identificados en Vercel")
            print("  2. 🔄 Re-ejecutar tests")
            print("  3. ✅ Verificar variables de entorno y deploy")
            print("  4. 📞 Revisar logs de Vercel si persisten errores")


def main():
    """Ejecutar tests de autenticación en Vercel"""
    print("🏦 Pool Banorte API - Test de Autenticación JWT en Vercel")
    print("=" * 60)
    print("⚠️ IMPORTANTE: Actualizar VERCEL_URL con tu URL de deploy")
    print(f"📍 URL actual configurada: {VERCEL_URL}")
    print("=" * 60)
    
    # Ejecutar tests directamente
    tester = AuthTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()