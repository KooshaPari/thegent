"""Test isolation module structure and imports."""


def test_isolation_module_importable():
    """Isolation module is importable and has required exports."""
    from thegent import isolation

    assert isolation is not None


def test_isolation_exceptions_importable():
    """Isolation exceptions module exists and is importable."""
    from thegent.isolation import exceptions

    assert hasattr(exceptions, "IsolationError")
    assert hasattr(exceptions, "TenantAllocationError")
    assert hasattr(exceptions, "LeaseConflictError")


def test_isolation_models_importable():
    """Isolation models module exists and has required enums."""
    from thegent.isolation import models

    assert hasattr(models, "TenantContext")
    assert hasattr(models, "IsolationMode")


def test_isolation_base_provider_importable():
    """Base provider interface is importable."""
    from thegent.isolation import base_provider

    assert hasattr(base_provider, "IsolationProvider")


def test_tenant_context_dataclass():
    """TenantContext has required fields."""
    from thegent.isolation.models import TenantContext

    # Should be instantiable with tenant_id
    ctx = TenantContext(tenant_id="test-tenant-1")
    assert ctx.tenant_id == "test-tenant-1"


def test_isolation_mode_enum():
    """IsolationMode enum has required values."""
    from thegent.isolation.models import IsolationMode

    assert hasattr(IsolationMode, "SUB_USER")
    assert hasattr(IsolationMode, "OS_USER")
    assert hasattr(IsolationMode, "DOCKER")
