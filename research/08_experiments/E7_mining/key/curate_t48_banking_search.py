"""Private bank-search status evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('open-banking-gateway',92,'GET /v1/banking/search/bankSearch',
 'an authorized bank search returns a 200 BankSearchResult response',
 'return 404 with no result object when the matching banks collection is empty',
 'IMPL','spec_file','status_code.bank_search_empty_result',
 [('static/tpp_banking_api_bank_search.yml',r'/v1/banking/search/bankSearch:|200_BankSearchResult|bankDescriptor:|total:')],
 [('controller/TppBankSearchController.java',r'public ResponseEntity<InlineResponse200> bankSearchGET|banks.isEmpty|HttpStatus.NOT_FOUND|HttpStatus.OK')],confidence=2)
R['decide']('open-banking-gateway',92,'ACCEPT','Bank search documents a 200 result object, but parent code returns an undocumented 404 for empty matches; the early 404 branch is removed.')
print('New accepted items:',len(R['accepted']()))
