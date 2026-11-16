"""Private payment product propagation evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for path,entry,method in [
 ('/v1/banking/pis/payments/{payment-product}','Xs2aGetPaymentInfoEntrypoint.java','getPaymentInformation'),
 ('/v1/banking/pis/payments/{payment-product}/status','Xs2aGetPaymentStatusEntrypoint.java','getPaymentInitiationStatus')]:
 R['accept']('open-banking-gateway',71,'GET '+path,
  'payment-product selects the requested product, including instant-sepa-credit-transfers and other listed products',
  'discard the supplied product and call the bank using the constant sepa-credit-transfers product',
  'IMPL','spec_file','request_parameter.payment_product_propagation',
  [('static/tpp_banking_api_pis.yml',r'/v1/banking/pis/payments/|PaymentProduct:|instant-sepa-credit-transfers|required: true')],
  [('controller/TppBankingApiPisInfoController.java',r'public CompletableFuture '+method+r'|String paymentProduct|Payment(?:Info|Status)Request.builder'),
   (entry,r'PAYMENT_PRODUCT_SEPA|pis.getSinglePayment'),
   ('xs2a/constant/GlobalConst.java',r'PAYMENT_PRODUCT_SEPA = "sepa-credit-transfers"')],confidence=2)
R['decide']('open-banking-gateway',71,'ACCEPT','Both payment lookup operations document a product path parameter but discard it and call SEPA unconditionally; the patch propagates the selected product.')
print('New accepted items:',len(R['accepted']()))
