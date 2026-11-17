import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
R['accept']('traccar',3,'GET /api/commandtypes','the commandtypes path is documented with POST','CommandTypeResource registers GET',
 'SPEC','openapi','route.commandtypes_method',contract=[('swagger.json',r'"/commandtypes":')],implementation=[('CommandTypeResource.java',r'@GET|@Path\("commandtypes"\)')])
R['accept']('traccar',3,'GET /api/users','the successful user list is an array of Position objects','UserResource returns a collection of User objects',
 'SPEC','openapi','schema.user_list_items',contract=[('swagger.json',r'"/users":')],implementation=[('UserResource.java',r'public Collection<User> get')])
print('Accepted items and exclusions:',R['finish_accept']('The parent document gives commandtypes the wrong method and user listings the wrong item schema; existing resource methods disagree.'))
