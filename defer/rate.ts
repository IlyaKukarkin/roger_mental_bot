// the `defer()` helper will be used to define a background function
import { defer } from "@defer/client";
// the `defer()` helper will be used to define a background function
import { getCalculatedRates } from "../lib/api/rate";

// the imported function must be wrapped with `defer()` and re-exported as default
export default defer(getCalculatedRates, { concurrency: 1 });
