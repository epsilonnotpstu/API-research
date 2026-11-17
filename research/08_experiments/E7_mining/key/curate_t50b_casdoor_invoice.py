import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('casdoor',23,'POST /api/invoice-payment',
 'the HTTP 200 response is a single controllers.Response JSON object',
 'an invoice-generation error writes an error object and then unconditionally writes a success object',
 'IMPL','openapi','response.double_invoice_write',confidence=2,
 contract=[('swagger/swagger.json',r'"/api/invoice-payment"')],
 implementation=[('controllers/payment.go',r'publicNOTFOUND|func \(c \*ApiController\) InvoicePayment|c.ResponseOk\(invoiceUrl\)'),('controllers/util.go',r'func \(c \*ApiController\) ResponseJsonData|c.ServeJSON\(\)')])
print('Accepted items and exclusions:',R['finish_accept']('Invoice errors fall through to success output, producing two response objects where the parent schema specifies one; the patch adds the missing return.'))
