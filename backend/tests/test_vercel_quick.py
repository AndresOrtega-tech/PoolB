#!/usr/bin/env python3
"""
Test rápido del CRUD en Vercel - Sin confirmaciones
"""

import requests
import json
import uuid
from datetime import datetime

# URL de Vercel
BASE_URL = "https://pool-b.vercel.app"

def test_health():
    """Test básico de health"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_user():
    """Test crear usuario"""
    print("\n👤 Testing create user...")
    
    user_data = {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "name": "Test User",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user_data,
            timeout=30
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"✅ User created: {user['id']}")
            return user['id']
        else:
            print(f"❌ Create user failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Create user error: {e}")
        return None

def test_get_user(user_id):
    """Test obtener usuario"""
    print(f"\n📖 Testing get user {user_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}", timeout=30)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User retrieved: {user['name']}")
            return True
        else:
            print(f"❌ Get user failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return False

def test_list_users():
    """Test listar usuarios"""
    print("\n📋 Testing list users...")
    
    try:
        response = requests.get(f"{BASE_URL}/users/", timeout=30)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users listed: {len(users)} users found")
            return True
        else:
            print(f"❌ List users failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ List users error: {e}")
        return False

def test_delete_user(user_id):
    """Test eliminar usuario"""
    print(f"\n🗑️ Testing delete user {user_id}...")
    
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}", timeout=30)
        
        if response.status_code == 204:
            print("✅ User deleted")
            return True
        else:
            print(f"❌ Delete user failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Delete user error: {e}")
        return False

def main():
    """Ejecutar tests rápidos"""
    print("🚀 Pool Banorte API - Test Rápido en Vercel")
    print("=" * 50)
    print(f"🔗 URL: {BASE_URL}")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ API no disponible. Abortando tests.")
        return
    
    # Test crear usuario
    user_id = test_create_user()
    if not user_id:
        print("\n❌ No se pudo crear usuario. Abortando tests.")
        return
    
    # Test obtener usuario
    test_get_user(user_id)
    
    # Test listar usuarios
    test_list_users()
    
    # Test eliminar usuario
    test_delete_user(user_id)
    
    print("\n🎉 Tests completados!")

if __name__ == "__main__":
    main()