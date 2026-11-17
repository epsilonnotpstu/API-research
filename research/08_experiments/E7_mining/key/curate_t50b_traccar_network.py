import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for op,file,pattern in [('GET /api/positions','PositionResource.java',r'public Collection<Position> getJson'),('GET /api/reports/route','ReportResource.java',r'public Collection<Position> getRoute\(')]:
 R['accept']('traccar',18,op,
  'the returned Position network property is a string',
  'Position exposes a Network bean that serializes as a JSON object',
  'SPEC','openapi','schema.position_network',
  contract=[('swagger.json',r'"network":')],
  implementation=[('api/resource/'+file,pattern),('model/Position.java',r'public Network getNetwork'),('model/Network.java',r'public class Network')])
print('Accepted items and exclusions:',R['finish_accept']('Position network is declared as a string, while both JSON endpoints return Position objects exposing a Network bean; the patch corrects its schema.'))
