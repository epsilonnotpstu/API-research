from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for op in ['GET /things','GET /things/{thingId}']:
 R['accept']('ditto',485,op,
  'the optional _metadata field in a returned Thing has type string',
  'serialize the selected _metadata field as a JSON object',
  'SPEC','openapi','response_schema.thing-metadata-object',
  [('openapi/ditto-api-2.yml',r'^        _metadata:|^          type: string$|^  .*/things')],
  [('model/things/ImmutableThing.java',r'JsonFields.METADATA, metadata.toJson'),('model/things/Thing.java',r'JsonFieldDefinition<JsonObject> METADATA')],
  route=[('routes/things/ThingsRoute.java',r'GET /things|selectedFields|withSelectedFields')],
  helpers=['things/query/RetrieveThingResponse.java'] if '{thingId}' in op else ['things/query/RetrieveThingsResponse.java'])
print('Accepted/capped:',R['finish_accept']('Parent Thing schema declares _metadata string; parent model serializes an object selected by both retrieval routes; patch corrects the type.'))
