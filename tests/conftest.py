import warnings

with warnings.catch_warnings():
    # The DeprecationWarning is a issue of passlib
    # https://github.com/fastapi-users/fastapi-users/issues/1301
    warnings.filterwarnings(
        "ignore",
        message="pkg_resources is deprecated as an API",
        category=DeprecationWarning,
        module="passlib",
    )
    from aria2_server.config import reload, schemas

new_config = schemas.Config(
    server=schemas.Server(
        uvicorn_logging_level="info", show=False, sqlite_db=":memory:"
    ),
)
reload(new_config)
