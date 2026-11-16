"""Private exact-parent keystore property evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kapua',88,'GET /{scopeId}/devices/{deviceId}/keystore',
 'each deviceKeystore identifies the keystore with a name property',
 'serialize each keystore identifier under the id property',
 'SPEC','spec_file','response_body.keystore_identifier_property',
 [('deviceKeystore-scopeId-deviceId.yaml',r'/\{scopeId\}/devices/\{deviceId\}/keystore:|deviceKeystores'),
  ('deviceKeystore/deviceKeystore.yaml',r'deviceKeystore:|name:|deviceKeystores:')],
 [('keystore/model/DeviceKeystore.java',r'XmlElement\(name = "id"\)|String getId'),
  ('keystore/model/DeviceKeystores.java',r'List<DeviceKeystore> getKeystores|XmlElement'),
  ('keystore/model/internal/DeviceKeystoreImpl.java',r'public String getId|return id;')],
 [('resources/DeviceManagementKeystores.java',r'@Path\("\{scopeId\}/devices/\{deviceId\}/keystore"\)|public DeviceKeystores getKeystores|return DEVICE_KEYSTORE_MANAGEMENT_SERVICE.getKeystores')],confidence=2)
R['decide']('kapua',88,'ACCEPT','Keystore response schema calls the identifier name, while parent JAXB and model getters serialize id; documentation adopts the existing identifier property.')
print('New accepted items:',len(R['accepted']()))
