"""Private invalid product sort error mapping evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('Iced-Latte',194,'GET /api/v1/products',
 'invalid pagination or sorting parameters return 400',
 'pass arbitrary sort properties to the repository without a PropertyReferenceException response mapping, allowing invalid properties to escape as server errors',
 'IMPL','spec_file','response_status.product_invalid_sort_property',
 [('api-specs/product-openapi.yaml',r'sort_attribute|Invalid parameters provided for pagination or sorting')],
 [('product/api/PageableProductsProvider.java',r'Sort.by\(sortAttribute\)|findAll\(pageable\)'),
  ('product/exception/handler/ProductExceptionHandler.java',r'class ProductExceptionHandler|ExceptionHandler'),
  ('common/exception/handler/GlobalExceptionHandler.java',r'class GlobalExceptionHandler|ExceptionHandler')],
 [('product/endpoint/ProductsEndpoint.java',r'GetMapping|sort_attribute|productApi.getProducts')],confidence=2)
R['decide']('Iced-Latte',194,'ACCEPT','Product listing promises 400 for invalid sorting, but parent repository property errors lack a handler; the patch maps PropertyReferenceException to 400.')
print('New accepted items:',len(R['accepted']()))
