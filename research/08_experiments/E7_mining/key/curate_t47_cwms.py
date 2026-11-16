"""Reviewed CWMS parent propositions and private truth records."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide'];P='cwms-data-api/src/main/java/cwms/cda/'
a('cwms-data-api',73,'POST /projects/{office}/{project-id}/water-user',
  'fail-if-exists defaults to true when omitted',
  'parse the absent query value with Boolean.parseBoolean and pass false to storage',
  'IMPL','annotations','query_default.water_user_fail_if_exists',
  [(P+'api/watersupply/WaterUserCreateController.java',r'already exists. Default: true')],
  [(P+'api/watersupply/WaterUserCreateController.java',r'Boolean.parseBoolean\(ctx.queryParam\(FAIL_IF_EXISTS\)\)|contractDao.storeWaterUser\(user, failIfExists\)')],
  [(P+'api/watersupply/WaterUserCreateController.java',r'path = "/projects/\{office\}/\{project-id\}/water-user"')])
d('cwms-data-api',73,'ACCEPT','Water-user creation explicitly documents a true default; parsing the omitted Boolean query parameter instead supplies false.')
a('cwms-data-api',100,'GET /locations/with-kind',
  'the successful JSON response contains an array of Location objects',
  'serialize an array of CwmsIdLocationKind objects with location identifiers and kind identifiers',
  'SPEC','annotations','response_schema.location_kind_identifiers',
  [(P+'api/LocationKindController.java',r'OpenApiContent\(isArray = true, type = Formats.JSONV2, from = Location.class'),
   (P+'data/dto/Location.java',r'private final String name|private final Double latitude')],
  [(P+'api/LocationKindController.java',r'List<CwmsIdLocationKind> locationKinds|Formats.format\(contentType, locationKinds, CwmsIdLocationKind.class\)'),
   (P+'data/dto/CwmsIdLocationKind.java',r'public CwmsId getLocationId|public String getLocationKindId')],
  [(P+'api/LocationKindController.java',r'path = "/locations/with-kind"')],
  helpers=[P+'formatters/json/JsonV2.java'],confidence=2)
d('cwms-data-api',100,'ACCEPT','Location-kind response annotation names Location, while the parent response serializes identifier-and-kind DTOs.')
a('cwms-data-api',143,'GET /offices',
  'the XML response is described by the comma-separated Office_CSV schema',
  'marshal offices through the XMLv1Office wrapper with an offices root element',
  'SPEC','annotations','response_schema.office_xml_wrapper',
  [(P+'api/OfficeController.java',r'OpenApiContent\(from = CsvV1Office.class, type = Formats.XML\)'),
   (P+'formatters/csv/CsvV1Office.java',r'name = "Office_CSV"|comma separated format')],
  [(P+'api/OfficeController.java',r'Formats.format\(contentType, offices, Office.class\)'),
   (P+'data/dto/Office.java',r'FormattableWith\(contentType = Formats.XML, formatter = XMLv1.class\)'),
   (P+'formatters/xml/XMLv1.java',r'mar.marshal\(new XMLv1Office'),
   (P+'formatters/xml/XMLv1Office.java',r'XmlRootElement\(name = "offices"\)')],
  [(P+'ApiServlet.java',r'cdaCrudCache\("/offices/\{office\}"')],confidence=2)
d('cwms-data-api',143,'ACCEPT','Office XML is annotated with a CSV schema, while the parent XML formatter constructs the offices wrapper.')
a('cwms-data-api',146,'GET /level-refs/',
  'the JSON response is a LocationLevels container whose levels contain full LocationLevel objects',
  'serialize a LocationLevelRefs container whose levels contain identifiers and effective dates',
  'SPEC','annotations','response_schema.location_level_reference_container',
  [(P+'api/LevelRefsController.java',r'OpenApiContent\(from = LocationLevels.class'),
   (P+'data/dto/locationlevel/LocationLevels.java',r'private List<LocationLevel> levels')],
  [(P+'api/LevelRefsController.java',r'LocationLevelRefs levels =|Formats.format\(contentType, levels\)'),
   (P+'data/dto/locationlevel/LocationLevelRefs.java',r'private List<LocationLevelRef> levels|List of retrieved location levels ids and effective dates'),
   (P+'data/dto/locationlevel/LocationLevelRef.java',r'public class|public final class|private final|private .*id|private .*effective')],
  [(P+'ApiServlet.java',r'String levelRefsPath =|get\(levelRefsPath, new LevelRefsController')],
  helpers=[P+'formatters/json/JsonV1.java'],confidence=2)
d('cwms-data-api',146,'ACCEPT','Level-reference annotation describes full levels; parent serialization returns the separate reference DTO container.')
print('Accepted items from this reviewed repository:',4)
