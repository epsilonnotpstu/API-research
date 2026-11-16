"""Private consumer subscription-mode conflict evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for suffix,method,x,y in [
 ('assignments','doAssign','an assignment request conflicting with an existing topic subscription returns 409 because subscription modes are mutually exclusive','proceed into partition assignment without checking the existing topic subscription'),
 ('subscription','doSubscribe','a subscription request conflicting with an existing partition assignment returns 409 because subscription modes are mutually exclusive','check only simultaneous topics and topic_pattern in the request body and proceed without checking the existing partition assignment')]:
 R['accept']('strimzi-kafka-bridge',33,'POST /consumers/{groupid}/instances/{name}/'+suffix,x,y,
  'IMPL','spec_file','status_code.consumer_subscription_mode_conflict',
  [('src/main/resources/openapi.json',r'"/consumers/\{groupid\}/instances/\{name\}/'+suffix+r'"|Subscriptions to topics, partitions, and patterns are mutually exclusive')],
  [('http/HttpSinkBridgeEndpoint.java',r'void '+method+r'\(|bodyAsJson.containsKey\("topics"\)|this.assign\(false\)|this.subscribe\('),
   ('bridge/SinkBridgeEndpoint.java',r'this.consumer.assign|this.consumer.subscribe|this.topicSubscriptions')],confidence=2)
R['decide']('strimzi-kafka-bridge',33,'ACCEPT','Assignment and subscription contracts require 409 for conflicting modes, but parent handlers do not check existing mode; the patch tracks and rejects both conflicts.')
print('New accepted items:',len(R['accepted']()))
