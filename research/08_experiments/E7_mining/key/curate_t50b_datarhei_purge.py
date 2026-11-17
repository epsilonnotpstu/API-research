import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for path in ['/api/v3/process','/api/v3/process/{id}','/api/v3/process/{id}/config']:
 R['accept']('datarhei-core',39,'GET '+path,
  'returned process configuration reflects the configuration supplied by Add or Update, including purge_on_delete',
  'output cleanup conversion omits PurgeOnDelete, returning false even when the stored value is true',
  'IMPL','openapi','response.purge_configuration_roundtrip',confidence=2,
  contract=[('docs/swagger.yaml',r'This is the configuration as|provided by Add or Update|purge_on_delete:')],
  implementation=[('http/api/process.go',r'func \(cfg \*ProcessConfig\) Unmarshal|io.Cleanup = append\(io.Cleanup|PurgeOnDelete: c.PurgeOnDelete'),('http/handler/api/restream.go',r'config.Unmarshal\(p.Config\)|info.Config.Unmarshal\(process.Config\)|func \(h \*RestreamHandler\) GetAll|func \(h \*RestreamHandler\) Get\(')])
print('Accepted items and exclusions:',R['finish_accept']('Returned process configuration drops stored purge_on_delete values during cleanup conversion; the patch copies the missing field into API output.'))
