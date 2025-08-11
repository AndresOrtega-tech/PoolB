"""
Dependencias de la aplicación

Este paquete contiene las dependencias que se usan en toda la aplicación,
especialmente para autenticación y autorización.
"""

from .auth import get_current_user, get_current_active_user

__all__ = ["get_current_user", "get_current_active_user"]