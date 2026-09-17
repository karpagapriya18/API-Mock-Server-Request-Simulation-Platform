import asyncio
import re
import time
from typing import Any

from fastapi import HTTPException, Request, Response
from jsonschema import ValidationError, validate
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.entities import ApiPermission, ApiVersion, ApiVisibility, AuthMode, MockApi, RequestLog, ResponseTemplate, User


def _path_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template).replace(r"\{", "{").replace(r"\}", "}")
    pattern = re.sub(r"{[^/]+}", r"[^/]+", escaped)
    return re.compile(f"^{pattern}$")


def _matches(template: str, actual: str) -> bool:
    return bool(_path_regex(template).match(actual))


def _select_template(templates: list[ResponseTemplate], scenario: str | None) -> ResponseTemplate:
    if scenario:
        match = next((template for template in templates if template.scenario == scenario), None)
        if match:
            return match
    return next((template for template in templates if template.is_default), templates[0])


def _validate_schema(instance: Any, schema: dict | None, label: str) -> None:
    if not schema:
        return
    try:
        validate(instance=instance, schema=schema)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail={"location": label, "message": exc.message})


def _can_access(api: MockApi, user: User | None) -> bool:
    if api.visibility == ApiVisibility.public and api.auth_mode == AuthMode.none:
        return True
    if not user:
        return False
    if api.owner_id == user.id:
        return True
    return any(permission.user_id == user.id and permission.can_invoke for permission in api.permissions)


def find_api(db: Session, method: str, endpoint: str) -> MockApi | None:
    candidates = (
        db.query(MockApi)
        .options(
            selectinload(MockApi.versions).selectinload(ApiVersion.request_schema),
            selectinload(MockApi.versions).selectinload(ApiVersion.response_templates),
            selectinload(MockApi.permissions),
        )
        .filter(MockApi.method == method.upper(), MockApi.is_active.is_(True))
        .all()
    )
    return next((api for api in candidates if _matches(api.path, endpoint)), None)


async def execute_mock(db: Session, request: Request, user: User | None) -> Response:
    started = time.perf_counter()
    endpoint = "/" + request.path_params.get("path", "").strip("/")
    method = request.method.upper()
    api = find_api(db, method, endpoint)
    status_code = 404
    error_message = None
    request_body = None

    try:
        if not api:
            raise HTTPException(status_code=404, detail="Mock API not found")
        if not _can_access(api, user):
            raise HTTPException(status_code=403, detail="You do not have access to this mock API")

        version_name = request.headers.get("x-api-version") or request.query_params.get("version")
        version = next((item for item in api.versions if item.version == version_name), None) if version_name else None
        version = version or next((item for item in api.versions if item.is_default), api.versions[0])
        schema = version.request_schema

        if method in {"POST", "PUT", "PATCH"}:
            try:
                request_body = await request.json()
            except Exception:
                request_body = None

        query = dict(request.query_params)
        headers = {key.lower(): value for key, value in request.headers.items()}
        _validate_schema(query, schema.query_schema if schema else None, "query")
        _validate_schema(headers, schema.headers_schema if schema else None, "headers")
        _validate_schema(request_body, schema.body_schema if schema else None, "body")

        scenario = request.headers.get("x-mock-scenario") or request.query_params.get("scenario")
        template = _select_template(version.response_templates, scenario)
        if version.response_delay_ms:
            await asyncio.sleep(version.response_delay_ms / 1000)
        status_code = template.status_code
        body = template.body if template.body is not None else {}
        headers = template.headers or {}
        return Response(
            content=body if isinstance(body, str) else __import__("json").dumps(body),
            status_code=status_code,
            headers=headers,
            media_type=headers.get("content-type", "application/json"),
        )
    except HTTPException as exc:
        status_code = exc.status_code
        error_message = str(exc.detail)
        raise
    finally:
        elapsed = int((time.perf_counter() - started) * 1000)
        db.add(
            RequestLog(
                api_id=api.id if api else None,
                method=method,
                endpoint=endpoint,
                request_params=dict(request.query_params),
                request_headers={key: value for key, value in request.headers.items()},
                request_body=request_body,
                response_status=status_code,
                response_time_ms=elapsed,
                error_message=error_message,
            )
        )
        db.commit()


def owned_or_permitted_query(db: Session, user: User):
    return db.query(MockApi).outerjoin(ApiPermission).filter(
        or_(MockApi.owner_id == user.id, ApiPermission.user_id == user.id)
    )
