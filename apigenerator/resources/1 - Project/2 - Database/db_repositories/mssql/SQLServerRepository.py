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
import pymssql



# Executes a stored procedure on the database #
def execute_sql_stored_procedure(stored_procedure_name, stored_procedure_args):
    try:
        # Connecting to the database and getting the engine
        main_connection_session = get_main_connection_session()
        engine = main_connection_session.bind
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    with engine.connect() as con:
        in_params = stored_procedure_args.get("in", []) or []
        out_count = stored_procedure_args.get("out", 0) or 0

        # Build placeholders for IN params, then append NULL for each OUT slot requested
        placeholders = [f":p{i}" for i in range(len(in_params))]
        try:
            out_n = int(out_count)
        except Exception:
            out_n = 0
        if out_n > 0:
            placeholders.extend(["NULL"] * out_n)

        # Compose SQL and bind parameters safely (EXEC for SQL Server)
        exec_sql = (
            f"EXEC {stored_procedure_name} {', '.join(placeholders)}" if placeholders
            else f"EXEC {stored_procedure_name}"
        )
        bind_params = {f"p{i}": v for i, v in enumerate(in_params)}

        try:
            stored_procedure_result = con.execute(text(exec_sql), bind_params)
            con.commit()
        except Exception as e:
            return handle_custom_exception(e)

        cursor = stored_procedure_result.cursor if hasattr(stored_procedure_result, 'cursor') else None

        if cursor is not None and cursor.description:
            result = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(200, result)
        else:
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message('query_success')}
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
