from prisma.models import Post, User

User.create_partial("UserSafe", exclude=["hashed_password"])

Post.create_partial("PostWithAuthor", required=["author"], relations={
    "author": "UserSafe",
})
