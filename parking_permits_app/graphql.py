from ariadne import load_schema_from_path, make_executable_schema
from ariadne.contrib.django.views import GraphQLView

from parking_permits_app import resolvers
from project.settings import BASE_DIR

type_defs = load_schema_from_path(BASE_DIR / "parking_permits_app" / "schema.graphql")
schema = make_executable_schema(type_defs, resolvers.query)
view = GraphQLView.as_view(schema=schema)
