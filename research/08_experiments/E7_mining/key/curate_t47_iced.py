"""Explicit reviewed parent evidence; private truth metadata."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept']; d=R['decide']
P='src/main/java/com/zufar/icedlatte/'
S='src/main/resources/api-specs/'
a('Iced-Latte',80,'GET /api/v1/products',
  'min_price and max_price independently filter the lower and upper product price limits',
  'disable the price predicate whenever either bound is absent',
  'IMPL','spec_file','query_filter.product_one_sided_price',
  [(S+'product-openapi.yaml',r'Filter products by the (lower|upper) limit')],
  [(P+'product/repository/ProductInfoRepository.java',r'WHERE \(:minPrice IS NULL OR :maxPrice IS NULL OR'),
   (P+'product/api/PageableProductsProvider.java',r'findAllProducts\(minPrice, maxPrice')],
  [(P+'product/endpoint/ProductsEndpoint.java',r'PRODUCTS_URL =|name = "min_price"|name = "max_price"|productsProvider.getProducts')])
d('Iced-Latte',80,'ACCEPT','Independent optional price bounds are documented; the parent query disables filtering when either bound is null.')
a('Iced-Latte',101,'GET /api/v1/products',
  'sorting and filtering parameters use camelCase names including sortAttribute, minPrice and brandNames',
  'bind those parameters only through snake_case names including sort_attribute, min_price and brand_names',
  'SPEC','spec_file','query_parameter_name.product_sort_and_filters',
  [(S+'product-openapi.yaml',r'name: "(?:sortAttribute|sortDirection|minPrice|maxPrice|minimumAverageRating|brandNames|sellerNames)"')],
  [(P+'product/endpoint/ProductsEndpoint.java',r'PRODUCTS_URL =|RequestParam\(name = "(?:sort_attribute|sort_direction|min_price|max_price|minimum_average_rating|brand_names|seller_names)"')])
d('Iced-Latte',101,'ACCEPT','Product query names differ between parent specification and explicit controller bindings; the patch aligns all seven names.')
a('Iced-Latte',145,'GET /api/v1/products/{productId}/reviews',
  'omitted size and sort_direction default to 50 and asc',
  'default omitted size and sort_direction to configured values 10 and desc',
  'SPEC','spec_file','query_default.product_review_pagination',
  [(S+'product-review-openapi.yaml',r'default: 50|default: "asc"')],
  [(P+'review/service/ProductReviewsProvider.java',r'paginationConfig.reviews\(\).defaultPageSize|paginationConfig.reviews\(\).defaultSortDirection'),
   (P+'common/config/PaginationConfig.java',r'public record Reviews|@DefaultValue\("10"\)|@DefaultValue\("desc"\)'),
   ('src/main/resources/application.yaml',r'^  reviews:|default-page-size: 10|default-sort-direction: "desc"')],
  [(P+'review/endpoint/ProductReviewEndpoint.java',r'GetMapping\(ApiPaths.PRODUCTS \+ "/\{productId\}/reviews"\)|productReviewsProvider.getProductReviews'),
   (P+'common/http/ApiPaths.java',r'PRODUCTS =')],confidence=2)
a('Iced-Latte',145,'GET /api/v1/products/{productId}/reviews',
  'a missing product is described under the 400 response',
  'raise a NotFoundException mapped to 404 when that product does not exist',
  'SPEC','spec_file','response_status.product_review_missing_product',
  [(S+'product-review-openapi.yaml',r'Bad request, e.g. the query parameters are invalid or product not found')],
  [(P+'review/service/ProductReviewsProvider.java',r'productReviewValidator.validateProductExists\(productId\)'),
   (P+'review/service/validator/ProductReviewValidator.java',r'public void validateProductExists|throw new NotFoundException'),
   (P+'common/exception/NotFoundException.java',r'ResponseStatus\(HttpStatus.NOT_FOUND\)'),
   (P+'common/exception/handler/GlobalExceptionHandler.java',r'resolveHttpStatus|ResponseStatus.class')],
  [(P+'review/endpoint/ProductReviewEndpoint.java',r'GetMapping\(ApiPaths.PRODUCTS \+ "/\{productId\}/reviews"\)'),
   (P+'common/http/ApiPaths.java',r'PRODUCTS =')],confidence=2)
a('Iced-Latte',145,'GET /api/v1/products/{productId}/review',
  'a user without a review receives 200 with all review fields null',
  'throw a NotFoundException mapped to 404 when the user has no review',
  'SPEC','spec_file','response_status.user_review_absent',
  [(S+'product-review-openapi.yaml',r'All fields are null, if user left no review')],
  [(P+'review/service/ProductReviewsProvider.java',r'getProductReviewForUser|findByUserIdAndProductId|orElseThrow\(\(\) -> new NotFoundException'),
   (P+'common/exception/NotFoundException.java',r'ResponseStatus\(HttpStatus.NOT_FOUND\)'),
   (P+'common/exception/handler/GlobalExceptionHandler.java',r'resolveHttpStatus|ResponseStatus.class')],
  [(P+'review/endpoint/ProductReviewEndpoint.java',r'GetMapping\(ApiPaths.PRODUCTS \+ "/\{productId\}/review"\)'),
   (P+'common/http/ApiPaths.java',r'PRODUCTS =')],confidence=2)
d('Iced-Latte',145,'ACCEPT','Review defaults and missing-resource responses disagree with explicit parent configuration, guards and exception mapping; three distinct propositions verified.')
print('Accepted items from this reviewed repository:',5)
