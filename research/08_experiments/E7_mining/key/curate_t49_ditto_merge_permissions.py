from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('ditto',641,'PATCH /things/{thingId}',
 'updating an existing thing requires WRITE permission on the root resource',
 'also authorize partial-root permission when every affected merge-patch leaf has unrestricted WRITE permission',
 'SPEC','openapi','authorization.merge-affected-leaves',
 [('openapi/ditto-api-2.yml',r'authorized subject needs \*\*WRITE\*\* permission on the thing.s root resource')],
 [('enforcement/ThingCommandEnforcement.java',r'enforceMergeThingCommand|calculateLeaves|hasPartialPermissions\(thingResourceKey|hasUnrestrictedPermissions\(resourceKeys')],
 route=[('routes/things/ThingsRoute.java',r'PATCH /things/<thingId>$|MergeThing.withThing')])
print('Accepted/capped:',R['finish_accept']('Parent PATCH prose demands root WRITE; parent enforcement permits WRITE on all affected leaves; patch corrects that requirement.'))
