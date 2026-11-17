import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('halo',36,'GET /sitemap.html',
 'the declared response media type is text/plain',
 'the handler resolves an HTML template through a view resolver configured to emit text/html',
 'SPEC','jvm_annotation','response.sitemap_media_type',confidence=2,
 contract=[('ContentFeedController.java',r'@GetMapping\(value = "sitemap.html", produces = MediaType.TEXT_PLAIN_VALUE\)')],
 implementation=[('ContentFeedController.java',r'return "common/web/sitemap_html"'),('WebMvcAutoConfiguration.java',r'resolver.setContentType\("text/html; charset=UTF-8"\)')])
print('Accepted items and exclusions:',R['finish_accept']('Sitemap annotation declares plain text while the handler selects an HTML view with explicit HTML content type; the patch removes the conflicting declaration.'))
