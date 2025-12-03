from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    user_id: int | None = None


class Login(BaseModel):
    username: EmailStr  # We use email as username
    password: str
