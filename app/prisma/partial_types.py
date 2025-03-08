from prisma.models import User

User.create_partial("UserSafe", exclude=["hashed_password"])
