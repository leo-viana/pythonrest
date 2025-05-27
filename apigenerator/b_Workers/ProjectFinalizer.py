import shutil
import yaml
from mergedeep import merge
import os
from shutil import copytree


# def install_sql_route(result, script_absolute_path):
#     copytree(os.path.join(script_absolute_path, 'apigenerator/resources/4 - SQLRoute'),
#              os.path.join(result, 'src', 'a_Presentation', 'b_Custom'), dirs_exist_ok=True)


def install_sql_swagger(result_full_path, script_absolute_path): # Renamed 'result' to 'result_full_path' for clarity
    # Old YAML modification for Swagger - kept as per original function's intent for non-FastAPI parts
    with open(os.path.join(result_full_path, 'config', 'swagger.yaml'), 'r') as yaml_in:
        swagger_dict = yaml.safe_load(yaml_in)
    with open(os.path.join(script_absolute_path, 'apigenerator/resources/2 - Swagger/yaml/sql.yaml'), 'r') as sql_in:
        sql_dict = yaml.safe_load(sql_in)

    if 'tags' not in swagger_dict or not isinstance(swagger_dict['tags'], list):
        swagger_dict['tags'] = []
    swagger_dict['tags'].extend(sql_dict.get('tags', []))

    if 'paths' not in swagger_dict or not isinstance(swagger_dict['paths'], dict):
        swagger_dict['paths'] = {}
    merge(swagger_dict['paths'], sql_dict.get('paths', {}))

    with open(os.path.join(result_full_path, 'config', 'swagger.yaml'), 'w') as yaml_out:
        yaml.dump(swagger_dict, yaml_out, sort_keys=False)

    # Define FastAPI SQLController content
    fastapi_sql_controller_content = """
from typing import Dict, Optional, Any
from fastapi import APIRouter, Query, Body, Request, HTTPException
from pydantic import BaseModel # Import BaseModel

# Service Layer Imports - paths must be valid in the *generated project*
from src.b_Application.b_Service.b_Custom.SQLService import execute_query, execute_post_route_sql_stored_procedure

sql_router = APIRouter(
    prefix="/sql",
    tags=["SQL Execution"],
)

class SQLQueryPayload(BaseModel):
    sql_query: str

class StoredProcedurePayload(BaseModel):
    json_payload: Dict[str, Any]

@sql_router.get("")
async def sql_direct_get_route(request: Request, sql_query: Optional[str] = Query(None, alias="HTTP_QUERY")):
    query_to_execute = sql_query or request.headers.get('HTTP_QUERY')
    if not query_to_execute:
        raise HTTPException(status_code=400, detail="Missing SQL query. Provide 'HTTP_QUERY' as query parameter or header.")
    result = await execute_query(query_to_execute, "GET") 
    return result

@sql_router.post("")
async def sql_direct_post_route(payload: SQLQueryPayload):
    result = await execute_query(payload.sql_query, "POST")
    return result

@sql_router.patch("")
async def sql_direct_patch_route(payload: SQLQueryPayload):
    result = await execute_query(payload.sql_query, "PATCH")
    return result

@sql_router.delete("")
async def sql_direct_delete_route(request: Request, sql_query: Optional[str] = Query(None, alias="HTTP_QUERY")):
    query_to_execute = sql_query or request.headers.get('HTTP_QUERY')
    if not query_to_execute:
        raise HTTPException(status_code=400, detail="Missing SQL query. Provide 'HTTP_QUERY' as query parameter or header.")
    result = await execute_query(query_to_execute, "DELETE")
    return result

@sql_router.post("/storedprocedure")
async def sql_stored_procedure_post_route(payload: StoredProcedurePayload):
    result = await execute_post_route_sql_stored_procedure(payload.json_payload)
    return result
"""

    # Write the new SQLController.py
    sql_controller_path = os.path.join(result_full_path, 'src', 'a_Presentation', 'b_Custom', 'SQLController.py')
    os.makedirs(os.path.dirname(sql_controller_path), exist_ok=True)
    with open(sql_controller_path, 'w') as f:
        f.write(fastapi_sql_controller_content)
    print(f"FastAPI SQLController.py written to {sql_controller_path}")

    # Modify generated app.py to include the SQL router
    generated_app_py_path = os.path.join(result_full_path, 'app.py')
    
    with open(generated_app_py_path, 'r') as f:
        app_py_lines = f.readlines()

    # Prepare lines to add
    import_line = "from src.a_Presentation.b_Custom.SQLController import sql_router\n"
    include_router_line = "app_handler.include_router(sql_router)\n"

    # Add import line: Find the block of controller imports
    # This is a heuristic, might need adjustment if app.py structure varies wildly
    import_insertion_point = -1
    for i, line in enumerate(app_py_lines):
        if "# Controller Imports #" in line:
            import_insertion_point = i + 1 
            # Try to insert after existing controller imports or at the end of the block
            for j in range(i + 1, len(app_py_lines)):
                if not app_py_lines[j].strip().startswith("from src.a_Presentation.b_Custom") and \
                   not app_py_lines[j].strip().startswith("#"):
                    import_insertion_point = j
                    break
                import_insertion_point = j + 1 # Place after the last relevant import
            break
    if import_insertion_point == -1: # Fallback if "# Controller Imports #" not found
        # Find first block of imports
        for i, line in enumerate(app_py_lines):
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                for j in range(i, len(app_py_lines)):
                    if not (app_py_lines[j].strip().startswith("from ") or \
                            app_py_lines[j].strip().startswith("import ") or \
                            app_py_lines[j].strip() == "" or \
                            app_py_lines[j].strip().startswith("#")):
                        import_insertion_point = j
                        break
                    import_insertion_point = j +1
                break
        if import_insertion_point == -1: import_insertion_point = 0 # Add at the beginning as last resort

    # Check if import already exists
    already_imported = any(import_line.strip() == line.strip() for line in app_py_lines)
    if not already_imported:
        app_py_lines.insert(import_insertion_point, import_line)
        print(f"Added SQL router import to {generated_app_py_path}")

    # Add include_router line: Find app_handler definition or end of file
    include_router_insertion_point = -1
    for i, line in enumerate(app_py_lines):
        if "app_handler = FastAPI(" in line: # Assuming app_handler is FastAPI instance
            # Insert after the app_handler instance, typically before run command or end of script
            for j in range(i + 1, len(app_py_lines)):
                if not app_py_lines[j].strip().startswith("app_handler.") and \
                   not app_py_lines[j].strip() == "" and \
                   not app_py_lines[j].strip().startswith("#"):
                    include_router_insertion_point = j
                    break
                include_router_insertion_point = j + 1
            break
            
    if include_router_insertion_point == -1: # Fallback: add before the last non-comment line
        for i in range(len(app_py_lines) -1, -1, -1):
            if app_py_lines[i].strip() and not app_py_lines[i].strip().startswith("#"):
                include_router_insertion_point = i + 1
                break
        if include_router_insertion_point == -1 : include_router_insertion_point = len(app_py_lines)


    # Check if router already included
    already_included = any(include_router_line.strip() == line.strip() for line in app_py_lines)
    if not already_included:
        # Adjust insertion point if import was added before it
        if not already_imported and include_router_insertion_point >= import_insertion_point :
            include_router_insertion_point +=1
        app_py_lines.insert(include_router_insertion_point, include_router_line)
        print(f"Added app_handler.include_router(sql_router) to {generated_app_py_path}")

    if not already_imported or not already_included:
        with open(generated_app_py_path, 'w') as f:
            f.writelines(app_py_lines)
    else:
        print(f"SQL Router import and include statement already exist in {generated_app_py_path}")


def finalize_project(result_full_path, script_absolute_path): # Renamed 'result'
    print('Adding SQL routes and updating Swagger for FastAPI...')
    install_sql_swagger(result_full_path, script_absolute_path) # Call the modified function
    # The old install_sql_route is removed/commented out, its functionality is merged or replaced.
