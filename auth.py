from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., examples=["dev@example.com"])
    password: str = Field(..., min_length=6, examples=["secret123"])
    name: str = Field(..., examples=["Developer"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "dev@example.com",
                "password": "secret123",
                "name": "Developer",
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["dev@example.com"])
    password: str = Field(..., examples=["secret123"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "dev@example.com",
                "password": "secret123",
            }
        }
    }


class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "paste-this-token-into-swagger-authorize",
                "token_type": "bearer",
            }
        }
    }


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "dev@example.com",
                "name": "Developer",
                "is_active": True,
            }
        },
    }
