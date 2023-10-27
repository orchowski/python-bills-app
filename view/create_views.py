from __future__ import annotations

from flask import Flask
from flask.blueprints import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

from application.factory import ApplicationFactory
from view.authentication.auth_router import auth_router
from view.commitments.commitments_router import commitments_router
from view.dashboards.dashboards_router import dashboard_router
from view.payments.accounting_documents_router import accounting_documents_router


class CreateViewsFor:
    def __init__(self, app: Flask, factory: ApplicationFactory):
        self._factory = factory
        self.register_blueprints(app)

    def register_blueprints(self, app):
        def prepare_blueprints():
            setattr(auth_router, 'app', self._factory)
            setattr(dashboard_router, 'app', self._factory)
            setattr(commitments_router, 'app', self._factory)
            setattr(accounting_documents_router, 'app', self._factory)

        prepare_blueprints()
        app.register_blueprint(auth_router, url_prefix="/api")
        app.register_blueprint(dashboard_router, url_prefix="/api")
        app.register_blueprint(commitments_router, url_prefix="/api")
        app.register_blueprint(accounting_documents_router, url_prefix="/api")
        app.register_blueprint(self.__configure_swagger_blueprint())

    def __configure_swagger_blueprint(self) -> Blueprint:
        SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
        API_URL = '/assets/swagger.yaml'  # Our API url (can of course be a local resource)
        return get_swaggerui_blueprint(
            SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
            API_URL,
            config={  # Swagger UI config overrides
                'app_name': "Test application"
            },
            # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
            #    'clientId': "your-client-id",
            #    'clientSecret': "your-client-secret-if-required",
            #    'realm': "your-realms",
            #    'appName': "your-app-name",
            #    'scopeSeparator': " ",
            #    'additionalQueryStringParams': {'test': "hello"}
            # }
        )