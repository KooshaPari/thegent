import pytest
from thegent.security.tenancy import KeyIsolator

from thegent.config import ThegentSettings


@pytest.fixture
def temp_auth_dir(tmp_path):
    return tmp_path / "auth"


@pytest.fixture
def isolator(temp_auth_dir):
    settings = ThegentSettings(cliproxy_auth_dir=temp_auth_dir)
    return KeyIsolator(settings)


def test_key_isolation_lifecycle(isolator):
    owner = "user-1"
    provider = "openai"
    key = "sk-12345"

    # Isolate key
    key_path = isolator.isolate_key(owner, provider, key)
    assert key_path.exists()
    assert key_path.name == "openai.key"
    assert owner in str(key_path)

    # Retrieve key
    retrieved = isolator.get_key(owner, provider)
    assert retrieved == key

    # List tenants
    tenants = isolator.list_tenants()
    assert owner in tenants

    # Delete tenant
    isolator.delete_tenant(owner)
    assert not key_path.exists()
    assert owner not in isolator.list_tenants()


def test_safe_owner_sanitization(isolator):
    unsafe_owner = "../../etc/passwd"
    safe_dir = isolator.get_tenant_dir(unsafe_owner)
    assert ".." not in safe_dir.name
    assert "etcpasswd" in safe_dir.name
