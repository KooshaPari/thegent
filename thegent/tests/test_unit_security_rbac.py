import pytest

from thegent.security.rbac import Permission, RBACManager, Role


@pytest.fixture
def rbac():
    return RBACManager()


def test_rbac_permission_checks(rbac):
    # Admin has everything
    assert rbac.has_permission(Role.ADMIN, Permission.PURGE_DATA)
    assert rbac.has_permission(Role.ADMIN, Permission.RUN_AGENT)

    # Operator has limited permissions
    assert rbac.has_permission(Role.OPERATOR, Permission.RUN_AGENT)
    assert not rbac.has_permission(Role.OPERATOR, Permission.PURGE_DATA)

    # Auditor is read-only
    assert rbac.has_permission(Role.AUDITOR, Permission.VIEW_LOGS)
    assert not rbac.has_permission(Role.AUDITOR, Permission.RUN_AGENT)


def test_rbac_check_access(rbac):
    # Operator can run agents in standard lane
    res = rbac.check_access(Role.OPERATOR, "run test", lane="standard")
    assert res["allowed"] is True

    # Operator cannot run agents in critical lane
    res = rbac.check_access(Role.OPERATOR, "run test", lane="critical")
    assert res["allowed"] is False
    assert "critical lane" in res["reason"]

    # Auditor cannot run agents
    res = rbac.check_access(Role.AUDITOR, "run test")
    assert res["allowed"] is False
    assert "lacks required permission" in res["reason"]

    # Incident commander can override
    res = rbac.check_access(Role.INCIDENT_COMMANDER, "run test", lane="critical")
    assert res["allowed"] is True


def test_operation_mapping(rbac):
    assert rbac._map_operation_to_permission("orchestrate run") == Permission.RUN_AGENT
    assert rbac._map_operation_to_permission("govern purge") == Permission.PURGE_DATA
    assert rbac._map_operation_to_permission("logs --session X") == Permission.VIEW_LOGS
    assert rbac._map_operation_to_permission("unknown") is None
