"""Private date representation comparisons, reviewed in frozen rank order."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t47.py'))
a=R['accept'];d=R['decide'];P='fineract-provider/src/main/java/org/apache/fineract/'
a('fineract',65,'POST /loans',
  'submittedOnDate is declared as LocalDate with an array-valued example',
  'read submittedOnDate as scalar text parsed with the request dateFormat and locale',
  'SPEC','annotations','request_date_format.loan_submitted_on_date',
  [(P+'portfolio/loanaccount/api/LoansApiResourceSwagger.java',r'public LocalDate submittedOnDate')],
  [(P+'portfolio/loanaccount/serialization/LoanApplicationCommandFromApiJsonHelper.java',r'extractLocalDateNamed\(submittedOnDateParameterName, element\)'),
   (P+'infrastructure/core/serialization/JsonParserHelper.java',r'final String valueAsString = primitive.getAsString|value = convertFrom\(valueAsString, parameterName, dateFormat')],
  [(P+'portfolio/loanaccount/api/LoansApiResource.java',r'@Path\("/loans"\)|LoansApiResourceSwagger.PostLoansRequest.class')],
  helpers=[P+'infrastructure/core/serialization/FromJsonHelper.java'],confidence=2)
d('fineract',65,'ACCEPT','Loan submission schema declares a LocalDate array example, while the parent parser consumes scalar dates in the supplied format.')
a('fineract',75,'POST /loans',
  'repaymentsStartingFromDate is declared as LocalDate with an array-valued example',
  'parse repaymentsStartingFromDate from scalar text in the supplied dateFormat and locale',
  'SPEC','annotations','request_date_format.loan_repayments_starting',
  [(P+'portfolio/loanaccount/api/LoansApiResourceSwagger.java',r'public LocalDate repaymentsStartingFromDate')],
  [(P+'portfolio/loanaccount/loanschedule/service/LoanScheduleAssembler.java',r'extractLocalDateNamed\("repaymentsStartingFromDate", element\)'),
   ('fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/JsonParserHelper.java',r'primitive.getAsString|convertFrom\(valueAsString, parameterName, dateFormat')],
  [(P+'portfolio/loanaccount/api/LoansApiResource.java',r'@Path\("/loans"\)|LoansApiResourceSwagger.PostLoansRequest.class')],
  helpers=['fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/FromJsonHelper.java'],confidence=2)
a('fineract',75,'POST /loans/{loanId}',
  'nested disbursementData.expectedDisbursementDate is declared as LocalDate with an array-valued example',
  'parse each nested expectedDisbursementDate from scalar text using the request dateFormat and locale',
  'SPEC','annotations','request_date_format.loan_nested_disbursement',
  [(P+'portfolio/loanaccount/api/LoansApiResourceSwagger.java',r'class PostLoansLoanIdDisbursementData|public LocalDate expectedDisbursementDate')],
  [(P+'portfolio/loanaccount/service/LoanDisbursementDetailsAssembler.java',r'extractLocalDateNamed\(LoanApiConstants.expectedDisbursementDateParameterName, jsonElement, dateFormat, locale\)'),
   ('fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/JsonParserHelper.java',r'primitive.getAsString|convertFrom\(valueAsString, parameterName, dateFormat')],
  [(P+'portfolio/loanaccount/api/LoansApiResource.java',r'PostLoansLoanIdRequest.class|@Path\("\{loanId\}"\)')],
  helpers=['fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/FromJsonHelper.java'],confidence=2)
d('fineract',75,'ACCEPT','Repayment-start and nested disbursement date fields declare LocalDate array examples; both parent paths parse request-formatted scalar text.')
for operation in ['GET /businessdate','GET /businessdate/{type}']:
    a('fineract',80,operation,
      'BusinessDateResponse.date has string type',
      'serialize the LocalDate date as an array containing year, month and day',
      'SPEC','annotations','response_value_type.business_date_array',
      [(P+'infrastructure/businessdate/api/BusinessDateApiResourceSwagger.java',r'public String date;')],
      [(P+'infrastructure/businessdate/api/BusinessDateApiResource.java',r'jsonSerializer.serialize\(settings, (?:businessDate|foundBusinessDates)\)'),
       (P+'infrastructure/businessdate/data/BusinessDateData.java',r'private LocalDate date'),
       (P+'infrastructure/core/api/LocalDateAdapter.java',r'array = new JsonArray|array.add\(new JsonPrimitive'),
       (P+'infrastructure/core/serialization/GoogleGsonSerializerHelper.java',r'registerTypeAdapter\(LocalDate.class, new LocalDateAdapter\(\)\)')],
      [(P+'infrastructure/businessdate/api/BusinessDateApiResource.java',r'@Path\("businessdate"\)|@Path\("\{type\}"\)|BusinessDateResponse.class')],
      helpers=[P+'infrastructure/core/serialization/DefaultToApiJsonSerializer.java'],confidence=2)
d('fineract',80,'ACCEPT','Business-date responses declare a string date; the parent registered LocalDate adapter emits a year-month-day array for both retrieval operations.')
print('Accepted items from this reviewed repository:',5)
