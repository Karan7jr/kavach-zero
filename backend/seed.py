
import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from getpass import getpass

from argon2 import PasswordHasher

from app import create_app
from app.extensions import db

from app.models import (
    Department,
    User,
    Role,
    UserRole,
    Document,
    AccessGrant,
    Policy,
    SecurityState
)


app = create_app()
password_hasher = PasswordHasher()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def seed_database():

    with app.app_context():

        # Prevent accidental duplicate seeding
        if User.query.first() is not None:
            print("Database already contains users.")
            print("Seeding stopped to prevent duplicates.")
            return

        password = getpass("Create demo user password: ")
        confirm_password = getpass("Confirm demo password: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return

        if len(password) < 12:
            print("Password must contain at least 12 characters.")
            return

        try:

            # 1. Create departments

            department_names = [
                "Administration",
                "Examination",
                "Computer Science",
                "Finance",
                "Student Affairs"
            ]

            departments = {}

            for name in department_names:
                department = Department(name=name)
                db.session.add(department)
                departments[name] = department

            db.session.flush()

            print("[OK] 5 departments created")


            # 2. Create roles

            role_names = [
                "ADMIN",
                "DEPARTMENT_HEAD",
                "FACULTY",
                "STAFF",
                "STUDENT"
            ]

            roles = {}

            for name in role_names:
                role = Role(name=name)
                db.session.add(role)
                roles[name] = role

            db.session.flush()

            print("[OK] 5 roles created")


            # 3. Create synthetic users

            user_data = [
                ("admin01", "Administration", "ADMIN"),
                ("exam_head", "Examination", "DEPARTMENT_HEAD"),
                ("cs_head", "Computer Science", "DEPARTMENT_HEAD"),
                ("finance_head", "Finance", "DEPARTMENT_HEAD"),
                ("student_head", "Student Affairs", "DEPARTMENT_HEAD"),

                ("faculty01", "Examination", "FACULTY"),
                ("faculty02", "Computer Science", "FACULTY"),
                ("faculty03", "Computer Science", "FACULTY"),
                ("faculty04", "Examination", "FACULTY"),
                ("faculty05", "Computer Science", "FACULTY"),

                ("staff01", "Administration", "STAFF"),
                ("staff02", "Examination", "STAFF"),
                ("staff03", "Finance", "STAFF"),
                ("staff04", "Student Affairs", "STAFF"),
                ("staff05", "Computer Science", "STAFF"),

                ("student01", "Computer Science", "STUDENT"),
                ("student02", "Computer Science", "STUDENT"),
                ("student03", "Student Affairs", "STUDENT"),
                ("student04", "Computer Science", "STUDENT"),
                ("student05", "Student Affairs", "STUDENT")
            ]

            users = {}

            for username, department_name, role_name in user_data:

                user = User(
                    username=username,
                    email=f"{username}@campus.example",
                    password_hash=password_hasher.hash(password),
                    department_id=departments[department_name].id,
                    is_active=True
                )

                db.session.add(user)
                db.session.flush()

                mapping = UserRole(
                    user_id=user.id,
                    role_id=roles[role_name].id
                )

                db.session.add(mapping)
                users[username] = user

            db.session.flush()

            print("[OK] 20 synthetic users created")


            # 4. Create document metadata

            document_data = [
                ("Campus Guidelines", "Administration", "PUBLIC"),
                ("Staff Directory", "Administration", "INTERNAL"),
                ("Administrative Records", "Administration", "CONFIDENTIAL"),
                ("Management Meeting", "Administration", "RESTRICTED"),
                ("Campus Notice", "Administration", "PUBLIC"),
                ("Internal Circular", "Administration", "INTERNAL"),

                ("Exam Schedule", "Examination", "PUBLIC"),
                ("Exam Instructions", "Examination", "INTERNAL"),
                ("Exam Question Paper", "Examination", "RESTRICTED"),
                ("Answer Key", "Examination", "RESTRICTED"),
                ("Student Results", "Examination", "CONFIDENTIAL"),
                ("Evaluation Records", "Examination", "CONFIDENTIAL"),

                ("Course Syllabus", "Computer Science", "PUBLIC"),
                ("Faculty Timetable", "Computer Science", "INTERNAL"),
                ("Research Proposal", "Computer Science", "CONFIDENTIAL"),
                ("Project Evaluation", "Computer Science", "CONFIDENTIAL"),
                ("Lab Guidelines", "Computer Science", "PUBLIC"),
                ("Internal Assessment", "Computer Science", "RESTRICTED"),

                ("Fee Structure", "Finance", "PUBLIC"),
                ("Budget Summary", "Finance", "INTERNAL"),
                ("Salary Records", "Finance", "RESTRICTED"),
                ("Financial Audit", "Finance", "CONFIDENTIAL"),
                ("Purchase Records", "Finance", "INTERNAL"),
                ("Annual Budget", "Finance", "CONFIDENTIAL"),

                ("Student Handbook", "Student Affairs", "PUBLIC"),
                ("Activity Schedule", "Student Affairs", "PUBLIC"),
                ("Scholarship Records", "Student Affairs", "CONFIDENTIAL"),
                ("Disciplinary Records", "Student Affairs", "RESTRICTED"),
                ("Student Requests", "Student Affairs", "INTERNAL"),
                ("Counselling Records", "Student Affairs", "RESTRICTED")
            ]

            documents = []

            for title, department_name, classification in document_data:

                synthetic_content = (
                    f"KAVACH ZERO DEMO DOCUMENT: {title}"
                )

                document = Document(
                    title=title,
                    original_filename=title.replace(" ", "_") + ".pdf",
                    storage_key=secrets.token_hex(32),
                    classification=classification,
                    department_id=departments[department_name].id,
                    uploaded_by=users["admin01"].id,
                    file_hash=hashlib.sha256(
                        synthetic_content.encode()
                    ).hexdigest(),
                    is_active=True
                )

                db.session.add(document)
                documents.append(document)

            db.session.flush()

            print("[OK] 30 synthetic document records created")


            # 5. Create temporary access grants

            now = utc_now()

            eligible_pairs = []

            for username, department_name, role_name in user_data:

                if role_name in ("ADMIN", "STUDENT"):
                    continue

                for document in documents:

                    if document.department_id != users[username].department_id:
                        continue

                    if document.classification == "RESTRICTED":
                        continue

                    eligible_pairs.append(
                        (users[username], document)
                    )

            for index, (user, document) in enumerate(eligible_pairs[:50]):

                status = "ACTIVE"
                expires_at = now + timedelta(days=7)
                revoked_at = None

                if index % 10 == 0:
                    expires_at = now - timedelta(days=1)

                elif index % 10 == 1:
                    status = "REVOKED"
                    revoked_at = now - timedelta(minutes=5)

                grant = AccessGrant(
                    user_id=user.id,
                    document_id=document.id,
                    granted_by=users["admin01"].id,
                    permission="READ",
                    status=status,
                    expires_at=expires_at,
                    revoked_at=revoked_at
                )

                db.session.add(grant)

            print(f"[OK] {len(eligible_pairs[:50])} access grants created")


            # 6. Create initial security policy

            policy = Policy(
                name="KAVACH Default Zero Trust Policy",
                version=1,
                status="ACTIVE",
                created_by=users["admin01"].id,

                rules={
                    "default_decision": "DENY",

                    "require_active_user": True,
                    "require_active_session": True,
                    "enforce_grant_expiry": True,
                    "enforce_grant_revocation": True,

                    "classification_rules": {

                        "PUBLIC": {
                            "allowed_roles": role_names,
                            "require_same_department": False,
                            "require_grant": False
                        },

                        "INTERNAL": {
                            "allowed_roles": [
                                "ADMIN",
                                "DEPARTMENT_HEAD",
                                "FACULTY",
                                "STAFF"
                            ],
                            "require_same_department": True,
                            "require_grant": False
                        },

                        "CONFIDENTIAL": {
                            "allowed_roles": [
                                "ADMIN",
                                "DEPARTMENT_HEAD",
                                "FACULTY",
                                "STAFF"
                            ],
                            "require_same_department": True,
                            "require_grant": True
                        },

                        "RESTRICTED": {
                            "allowed_roles": [
                                "ADMIN",
                                "DEPARTMENT_HEAD"
                            ],
                            "require_same_department": True,
                            "require_grant": True
                        }
                    }
                }
            )

            db.session.add(policy)
            db.session.flush()

            print("[OK] Initial security policy created")


            # 7. Initialize global security state

            security_state = SecurityState(
                id=1,
                active_policy_id=policy.id,
                state_revision=1
            )

            db.session.add(security_state)

            db.session.commit()

            print("[OK] Global security state initialized")

            print("\n" + "=" * 50)
            print("KAVACH ZERO 2.0")
            print("DATABASE SEEDING COMPLETED")
            print("=" * 50)

            print("Departments:", Department.query.count())
            print("Roles:", Role.query.count())
            print("Users:", User.query.count())
            print("Documents:", Document.query.count())
            print("Access Grants:", AccessGrant.query.count())
            print("Policies:", Policy.query.count())
            print("Security States:", SecurityState.query.count())

        except Exception:
            db.session.rollback()
            print("[ERROR] Database seeding failed.")
            raise


if __name__ == "__main__":
    seed_database()
