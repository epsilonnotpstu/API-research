"""Private duration-pattern parent evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for endpoint,suffix,x,y in [
 ('code','code/strategy_recovery_admin.go','expires_in consists only of integer duration segments and excludes fractional durations such as 1.5h','parse expires_in with time.ParseDuration and accept a positive fractional duration such as 1.5h'),
 ('link','link/strategy_recovery.go','expires_in consists of exactly one integer duration segment and excludes 1m30s or 1.5h','parse expires_in with time.ParseDuration and accept positive compound and fractional duration strings')]:
 R['accept']('kratos',76,'POST /admin/recovery/'+endpoint,x,y,
  'SPEC','spec_file','request_pattern.recovery_expiration_duration',
  [('spec/api.json',r'"/admin/recovery/'+endpoint+r'"|"createRecovery'+endpoint.title()+r'ForIdentityBody"|"expires_in"|"pattern": "\^')],
  [(suffix,r'func .*createRecovery|decoderx.Decode|time.ParseDuration\(p.ExpiresIn\)|if expiresIn <= 0')],
  [(suffix,r'admin.POST\(RouteAdminCreateRecovery')],confidence=2)
R['decide']('kratos',76,'ACCEPT','Recovery code and link expiration schemas exclude positive fractional durations accepted by their parent time.ParseDuration handlers; the patterns are broadened.')
print('New accepted items:',len(R['accepted']()))
