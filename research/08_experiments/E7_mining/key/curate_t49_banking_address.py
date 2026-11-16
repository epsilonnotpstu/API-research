from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for method,controller,dto in [('POST','TppBankingApiPisController','SinglePaymentBody'),('GET','TppBankingApiPisInfoController','PaymentInfoBody')]:
 R['accept']('open-banking-gateway',152,method+' /v1/banking/pis/payments/{payment-product}',
  'creditorAddress includes the townName string',
  ('map creditorAddress without translating townName to the domain city property' if method=='POST' else 'map a domain creditorAddress city without translating it to the response townName property'),
  'IMPL','openapi','property_mapping.payment-creditor-town-name',
  [('static/tpp_banking_api_pis.yml',r'creditorAddress:|/v1/banking/pis/payments/\{payment-product\}'),('static/tpp_banking_api_commons.yml',r'townName:')],
  [('controller/'+controller+'.java',r'SinglePaymentBody map\(PaymentInitiation|PaymentInitiationWithStatusResponse map\(PaymentInfoBody|\.singlePayment\(|paymentInfoResponseMapper'),('result/body/Address.java',r'private String city;')],
  helpers=['request/payments/'+dto+'.java'],confidence=2)
print('Accepted/capped:',R['finish_accept']('Parent address schema uses townName while domain uses city; parent mapper lacks a translation; patch adds both request and response mappings.'))
