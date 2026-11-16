"""Private instance measurement mapping evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('rhsm-subscriptions',100,'GET /instances/products/{product_id}',
 'each instance measurement corresponds to the unit at the same position in meta.measurements',
 'read the first monthly total for the instance-key unit and fill other requested units with zero, without selecting their stored totals',
 'IMPL','spec_file','response_value.instance_measurement_unit_selection',
 [('api/rhsm-subscriptions-api-spec.yaml',r'/instances/products/|Must be in the same order|instance.measurements\[0\]')],
 [('resource/InstancesResource.java',r'for \(String uom : measurements\)|getKey\(\).getUom|getMonthlyTotals\(\).values|measurementList.add\(0.0\)|String month ='),
  ('db/model/TallyInstanceView.java',r'InstanceMonthlyTotalKey|monthlyTotals'),
  ('InstanceMonthlyTotalKey.java',r'class InstanceMonthlyTotalKey|String monthId|Uom uom|Measurement.Uom')],confidence=2)
R['decide']('rhsm-subscriptions',100,'ACCEPT','Instance measurements promise matching metadata units, but parent mapping chooses a first total or zero; the patch selects totals by month and unit.')
print('New accepted items:',len(R['accepted']()))
