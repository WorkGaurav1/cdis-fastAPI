# NOTE: there used to be a test_create_user here, asserting
# POST /api/v1/users/ returns 201 -- but that route was never actually
# defined on the users router (only GET "" is), so the test could never
# have passed against the real app. Node has no such endpoint either:
# user creation happens through POST /auth/register (tests/test_register.py),
# which is what this template's own users:write-adjacent flow actually
# is. Removed rather than "fixed" by inventing a non-Node-parity route
# just to make a stale test green.
#
# The health-check test that used to live in this file moved to
# tests/test_health.py, mirroring Node's own separate
# health.controller.test.ts -- it isn't really a "users" test.
