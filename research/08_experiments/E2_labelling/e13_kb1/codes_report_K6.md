# K6 কোড রিপোর্ট (kb1)

## Method
প্রতিটি Q আইটেমের proposition আগে implementation/contract ফাইলের সাথে মিলিয়ে দেখা হয়েছে (targeted grep ও ফাইল পড়া, শুধু আইটেমের নিজস্ব path)। এরপর divergence_kind ও contract_specificity কোড করা হয়েছে। কোনো source execute করা হয়নি।

## Difficult items
- Q18: proposition ভুল, handler আসলে flagKeys পড়ে; তাই UNCLEAR।
- Q14, Q20, Q21: কোড explicit হলেও inconsistency সম্ভবত oversight; কোড-লক্ষ্য দেখে DELIBERATE (confidence 2)।
- Q17, Q16: contract-এর prose copy/boilerplate-সদৃশ; SPECIFIC ধরা হয়েছে (confidence 2)।
- Q04, Q10, Q12: status বা default না-সেট করা থেকে ACCIDENTAL।

## Limitations
কোনো runtime data বা history নেই; বড় ফাইল (যেমন StandardNiFiServiceFacade) শুধু প্রাসঙ্গিক অংশ পড়া হয়েছে।

## Boundary incidents
কোনো নেই।
