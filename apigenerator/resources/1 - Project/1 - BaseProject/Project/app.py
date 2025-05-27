# Infra Imports #
from src.e_Infra.g_Environment.EnvironmentVariables import *
from src.e_Infra.b_Builders.FastAPIBuilder import app_handler

# Controller Imports #
# Imports for SwaggerController, RedocController, OptionsController, BeforeRequestController, ExceptionHandlerController have been removed.
# FlaskAdminPanelController import is also removed.
from src.a_Presentation.b_Custom.SQLController import * # SQLController import remains

# To run this FastAPI application (after generating the project):
# Ensure you are in the root directory of the generated project.
# Run: uvicorn app:app_handler --reload