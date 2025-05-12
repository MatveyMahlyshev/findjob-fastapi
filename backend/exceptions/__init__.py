from fastapi import HTTPException, status


class UnauthorizedException:
    INVALID_LOGIN_DATA = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )
    INVALID_TOKEN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token.",
    )
    ERROR_TOKEN_TYPE = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error type of token.",
    )
    NO_EMAIL = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token does not contain email",
    )


class AccessDeniesException:
    ACCESS_DENIED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Aсcess denied."
    )


class NotFoundException:
    PROFILE_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Profile not found for this user.",
    )
    SKILL_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Skill not found.",
    )
    VACANCY_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Vacancy not found.",
    )


class ConflictException:
    SKILL_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Skill already exists.",
    )
    EMAIL_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already exists.",
    )


class UnprocessableEntityException:
    NO_TITLE_KEY = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No 'title' key."
    )
