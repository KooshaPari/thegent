import sys

import pytest

from byteport_sdk import local
from byteport_sdk.local import LocalDeploymentConfig, LocalDeploymentManager
from byteport_sdk.exceptions import MissingKInfraError


def _clear_kinfra_module():
    sys.modules.pop('kinfra', None)


def test_import_kinfra_missing_raises_helpful_error(monkeypatch):
    monkeypatch.delenv('BYTEPORT_KINFRA_PATH', raising=False)
    _clear_kinfra_module()

    with pytest.raises(MissingKInfraError):
        local._import_kinfra()


def test_start_local_tunnel_uses_stubbed_kinfra(monkeypatch):
    class FakeTunnelManager:
        def __init__(self):
            self.stopped = []

        def stop_tunnel(self, service_name):
            self.stopped.append(service_name)

    class FakeTunnel:
        url = 'https://demo.example'
        tunnel_id = 'tunnel-123'
        hostname = 'demo-host'

    class FakeKInfra:
        def __init__(self, domain):
            self.domain = domain
            self.tunnel_manager = FakeTunnelManager()
            self.allocated = []
            self.started = []

        def allocate_port(self, service_name):
            self.allocated.append(service_name)
            return 4242

        def start_tunnel(self, service_name, port, domain, path='/'):
            self.started.append((service_name, port, domain, path))
            return FakeTunnel()

    monkeypatch.setattr(local, '_import_kinfra', lambda: (FakeKInfra, FakeTunnel))

    manager = LocalDeploymentManager(domain='byteport.dev')
    config = LocalDeploymentConfig(service_name='demo-service')

    with manager.start_local_tunnel(config) as info:
        assert info.service_name == 'demo-service'
        assert info.port == 4242
        assert info.url == 'https://demo.example'
        assert info.tunnel_id == 'tunnel-123'
        assert info.hostname == 'demo-host'

    assert manager._kinfra.allocated == ['demo-service']
    assert manager._kinfra.started == [('demo-service', 4242, None, '/')]
    assert manager._kinfra.tunnel_manager.stopped == ['demo-service']


def test_start_local_tunnel_respects_provided_port(monkeypatch):
    class FakeTunnelManager:
        def __init__(self):
            self.stopped = []

        def stop_tunnel(self, service_name):
            self.stopped.append(service_name)

    class FakeTunnel:
        url = 'https://demo.example'
        tunnel_id = None
        hostname = 'demo-host'

    class FakeKInfra:
        def __init__(self, domain):
            self.domain = domain
            self.tunnel_manager = FakeTunnelManager()
            self.allocated = []
            self.started = []

        def allocate_port(self, service_name):
            raise AssertionError('allocate_port should not be called when local_port is provided')

        def start_tunnel(self, service_name, port, domain, path='/'):
            self.started.append((service_name, port, domain, path))
            return FakeTunnel()

    monkeypatch.setattr(local, '_import_kinfra', lambda: (FakeKInfra, FakeTunnel))

    manager = LocalDeploymentManager(domain='byteport.dev')
    config = LocalDeploymentConfig(service_name='demo', local_port=5001, domain='byteport.dev')

    with manager.start_local_tunnel(config) as info:
        assert info.port == 5001
        assert info.hostname == 'demo-host'

    assert manager._kinfra.started == [('demo', 5001, 'byteport.dev', '/')]
    assert manager._kinfra.tunnel_manager.stopped == ['demo']
