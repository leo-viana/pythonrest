# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.ControlService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /control route #
@app_handler.route('/control', methods=['GET'])
def control_route_get():
    # Routing request to /control GET method #
    if request.method == 'GET':
        result = get_control_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_GROUPBY': request.environ.get('HTTP_GROUPBY'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /control route #
@app_handler.route('/control', methods=['POST'])
def control_route_post_patch_put():
    # Routing request to /control POST method #
    if request.method == 'POST':
        result = post_control_set(request.json)
        return result


# /control route #
@app_handler.route('/control', methods=['DELETE'])
def control_route_delete_by_full_match():
    # Routing request to /control DELETE method #
    if request.method == 'DELETE':
        result = delete_control_by_full_match(request.json)
        return result
