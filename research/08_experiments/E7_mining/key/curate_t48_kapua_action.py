"""Private event action enum evidence shared by existing operations."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for operation,suffix in [
 ('GET /{scopeId}/devices/{deviceId}/events','deviceEvent-scopeId-deviceId.yaml'),
 ('GET /{scopeId}/devices/{deviceId}/events/{deviceEventId}','deviceEvent-scopeId-deviceId-deviceEventId.yaml'),
 ('POST /{scopeId}/devices/{deviceId}/events/_query','deviceEvent-scopeId-deviceId-_query.yaml')]:
 R['accept']('kapua',102,operation,
  'event action is restricted to READ, CREATE, WRITE, DELETE, OPTIONS and EXECUTE',
  'allow and serialize the additional SUBMIT event action without normalization to any listed value',
  'SPEC','spec_file','response_enum.event_action_submit',
  [(suffix,r'deviceEvent|200:'),
   ('deviceEvent/deviceEvent.yaml',r'deviceEvent:|deviceEventListResult:|device.yaml'),
   ('device/device.yaml',r'action:|READ|CREATE|WRITE|DELETE|OPTIONS|EXECUTE')],
  [('registry/event/DeviceEvent.java',r'XmlElement\(name = "action"\)|KapuaMethod getAction'),
   ('registry/event/internal/DeviceEventImpl.java',r'public KapuaMethod getAction|return action.normalizeAction'),
   ('management/message/KapuaMethod.java',r'SUBMIT,|public KapuaMethod normalizeAction|return this;')],
  [('resources/DeviceEvents.java',r'@Path|public DeviceEventListResult (simpleQuery|query)|public DeviceEvent find')],confidence=2)
R['decide']('kapua',102,'ACCEPT','Three existing event-reading operations exclude SUBMIT in their shared action enum, while parent event models preserve that enum value; documentation adds it.')
print('New accepted items:',len(R['accepted']()))
