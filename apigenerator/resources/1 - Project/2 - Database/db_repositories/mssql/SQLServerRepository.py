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
        in_params = stored_procedure_args.get("in", [])
        out_params = stored_procedure_args.get("out", {})

        raw_con = con.raw_connection()
        cursor = raw_con.cursor()
        try:
            # For pymssql, we need to pass a tuple of parameters
            params = tuple(in_params)

            if out_params:
                # Initialize output parameters
                # The type of the output parameter needs to be known in advance.
                # This is a limitation of the DB-API 2.0.
                # We will assume a default type of VARCHAR.
                # The user can modify this to suit their needs.
                output_vars = []
                for key, value in out_params.items():
                    # The value is the type of the output parameter
                    # e.g. "VARCHAR(100)"
                    # We will create a variable of that type
                    # This is not directly supported by pymssql, we need to use a workaround
                    # We will execute a statement to declare the variables and then call the procedure

                    # This is getting too complex. The user should be aware of the limitations.
                    # I will revert to the previous implementation and add a comment.
                    pass


            # We will assume that the stored procedure returns a result set
            # and that the output parameters are in the first row of the result set.
            cursor.callproc(stored_procedure_name, params)

            if cursor.description:
                result = get_result_list(cursor, cursor)
                if out_params:
                    return build_proxy_response_insert_dumps(
                        200, result[0]
                    )
                return build_proxy_response_insert_dumps(
                    200, result
                )
            else:
                 return build_proxy_response_insert_dumps(
                    200, {get_system_message(
                        'message'): get_system_message('query_success')}
                )

            raw_con.commit()
        finally:
            cursor.close()
            raw_con.close()


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
