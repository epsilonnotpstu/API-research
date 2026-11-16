from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
base='management/rest/resource/'
route=[(base+'organization/OrganizationsResource.java',r'@Path\("/organizations"\)|@Path\("/\{orgId\}"\)'),(base+'organization/OrganizationResource.java',r'@Path\("environments"\)'),(base+'EnvironmentsResource.java',r'@Path\("\{envId\}"\)|description = "The ID of the environment"'),(base+'EnvironmentResource.java',r'@Path\("configuration"\)'),(base+'EnvironmentConfigurationResource.java',r'@Path\("categories"\)'),(base+'CategoriesResource.java',r'@Path\("\{categoryId\}"\)|categoryService.update')]
root='/organizations/{orgId}/environments/{envId}/configuration/categories'
ops=[('DELETE',root+'/{categoryId}'),('GET',root+'/{categoryId}'),('GET',root+'/{categoryId}/background'),('GET',root+'/{categoryId}/picture'),('PUT',root),('PUT',root+'/{categoryId}')]
for method,path in ops:
 R['accept']('gravitee-api-management',179,method+' '+path,
  'the category operation is scoped by the envId path identifying the environment',
  'look up categoryId globally without checking the returned category environment before '+('deleting it' if method=='DELETE' else 'returning it' if method=='GET' else 'updating it'),
  'IMPL','annotations','resource_scope.category-environment',
  [(base+'EnvironmentsResource.java',r'description = "The ID of the environment"'),(base+'CategoryResource.java',r'@Operation\(summary = "(Get|Update|Delete) the category|@Path\("(picture|background)"\)')],
  [('service/impl/CategoryServiceImpl.java',r'findById\(final String id, final String environmentId\)|categoryRepository.findById|categoryToUpdate = optCategoryToUpdate.get')],
  route=route+[(base+'CategoryResource.java',r'categoryService.findById|categoryService.update|categoryService.delete')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Environment-scoped category routes call global identifier lookups without ownership checks; patch constrains reads, updates and deletion to the current environment.'))
