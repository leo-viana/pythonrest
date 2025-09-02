# Repository Imports #
from src.d_Repository.b_Transactions.GenericDatabaseTransaction import *

# Validator Imports #
from src.e_Infra.d_Validators.SqlAlchemyDataValidator import validate_request_data_object, validate_header_args
from src.e_Infra.d_Validators.RequestJSONValidator import *

# Handler Imports #
from src.e_Infra.a_Handlers.SystemMessagesHandler import *
from src.e_Infra.a_Handlers.ExceptionsHandler import *

# Builder Imports #
from src.e_Infra.b_Builders.DomainObjectBuilder import build_domain_object_from_dict, build_object_error_message
from src.e_Infra.b_Builders.ProxyResponseBuilder import *

# Resolver Imports #
from src.e_Infra.c_Resolvers.MainConnectionResolver import *

# SqlAlchemy Imports #
from sqlalchemy.sql import text


# Executes a stored procedure on the database #
def execute_sql_stored_procedure(stored_procedure_name, stored_procedure_args):
    try:
        # Connecting to the database and getting the engine
        main_connection_session = get_main_connection_session()
        engine = main_connection_session.bind
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    with engine.connect() as con:
        # Set OUT parameters as variables in the SQL session
        out_params = stored_procedure_args.get("out", {})
        for key, value in out_params.items():
            con.execute(text(f"SET @{key} = {value}"))

        in_values = ', '.join(
            [f"'{value}'" for value in stored_procedure_args.get("in", [])])
        call_proc = text(
            f"CALL {stored_procedure_name}({in_values}"
            f"{', ' if (out_params and in_values) else ''}"
            f"{', '.join([f'@{key}' for key in out_params])})"
        )

        try:
            stored_procedure_result = con.execute(call_proc)
            con.commit()
        except Exception as e:
            return handle_custom_exception(e)

        cursor = stored_procedure_result.cursor

        if out_params:
            # Fetch the OUT parameters
            fetched_out_params = {}
            for key in out_params:
                result = con.execute(text(f"SELECT @{key}"))
                fetched_out_params[key] = result.scalar()
            return build_proxy_response_insert_dumps(
                200, fetched_out_params
            )

        if cursor is not None:
            result = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(
                200, result
            )
        else:
            return build_proxy_response_insert_dumps(
                200, {get_system_message(
                    'message'): get_system_message('query_success')}
            )


# Method that retrieves a result list from database
def get_result_list(result, cursor):
    # Retrieving list of fields name #
    field_names = [i[0] for i in cursor.description]

    # Initializing result list #
    result_list = list()

    # Iterating over result #
    for result_object in result:
        # Creating new column dictionary #
        new_object = dict()
        # Iterating over field names #
        for i in range(len(field_names)):
            # Constructing column dict with field name #
            new_object[field_names[i]] = result_object[i]
        # Appending column dict in result list #
        result_list.append(new_object)
    # Returning result list #
    return result_list
