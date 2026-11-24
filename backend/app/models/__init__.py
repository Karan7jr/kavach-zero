
from datetime import datetime, timezone

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# 1. Campus Departments
class Department(db.Model):

    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 2. Campus Users
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 3. User Roles
class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


# 4. User Role Mapping
class UserRole(db.Model):

    __tablename__ = "user_roles"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        primary_key=True
    )


# 5. Protected Documents
class Document(db.Model):

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    storage_key = db.Column(db.String(255), unique=True, nullable=False)
    classification = db.Column(db.String(30), nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    file_hash = db.Column(db.String(64), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 6. Temporary Access Grants
class AccessGrant(db.Model):

    __tablename__ = "access_grants"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    granted_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    permission = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)

    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=utc_now)


# 7. Server-Side Sessions
class Session(db.Model):

    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 8. Versioned Security Policies
class Policy(db.Model):

    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    version = db.Column(db.Integer, unique=True, nullable=False)

    rules = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default="DRAFT", nullable=False)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=utc_now)


# 9. Global Security State
class SecurityState(db.Model):

    __tablename__ = "security_state"

    id = db.Column(db.Integer, primary_key=True)

    active_policy_id = db.Column(
        db.Integer,
        db.ForeignKey("policies.id"),
        nullable=True
    )

    state_revision = db.Column(db.Integer, default=1, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


# 10. Authorization Decisions
class AccessDecision(db.Model):

    __tablename__ = "access_decisions"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(36), unique=True, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=True
    )

    action = db.Column(db.String(30), nullable=False)
    decision = db.Column(db.String(10), nullable=False)
    reason_code = db.Column(db.String(100), nullable=False)
    policy_version = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)


# 11. TRACE Audit Logs
class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    event_type = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=False)

    previous_hash = db.Column(db.String(64), nullable=False)
    entry_hash = db.Column(db.String(64), nullable=False)

    created_at = db.Column(db.DateTime, default=utc_now)


# 12. PRISM Policy Simulations
class PolicySimulation(db.Model):

    __tablename__ = "policy_simulations"

    id = db.Column(db.Integer, primary_key=True)

    policy_id = db.Column(
        db.Integer,
        db.ForeignKey("policies.id"),
        nullable=False
    )

    candidate_hash = db.Column(db.String(64), nullable=False)
    base_revision = db.Column(db.Integer, nullable=False)

    result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 13. AEGIS Regression Results
class RegressionRun(db.Model):

    __tablename__ = "regression_runs"

    id = db.Column(db.Integer, primary_key=True)

    simulation_id = db.Column(
        db.Integer,
        db.ForeignKey("policy_simulations.id"),
        nullable=False
    )

    total_tests = db.Column(db.Integer, default=0)
    passed_tests = db.Column(db.Integer, default=0)
    failed_tests = db.Column(db.Integer, default=0)

    result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


# 14. PHANTOM Red Team Results
class RedTeamRun(db.Model):

    __tablename__ = "redteam_runs"

    id = db.Column(db.Integer, primary_key=True)

    scenario = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    result = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=utc_now)
