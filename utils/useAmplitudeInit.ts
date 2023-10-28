import { useEffect, useState } from "react";
import { AMPLITUDE_API_KEY } from "./constants";

export let amplitude: {
  init: any;
  Types: any;
  default?: any;
  createInstance?: any;
  add?: any;
  extendSession?: any;
  flush?: any;
  getDeviceId?: any;
  getSessionId?: any;
  getUserId?: any;
  groupIdentify?: any;
  identify?: any;
  logEvent?: any;
  remove?: any;
  reset?: any;
  revenue?: any;
  setDeviceId?: any;
  setGroup?: any;
  setOptOut?: any;
  setSessionId?: any;
  setTransport?: any;
  setUserId?: any;
  track?: any;
  runQueuedFunctions?: any;
  Revenue?: any;
  Identify?: any;
};

const useAmplitudeInit = () => {
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    const initAmplitude = async () => {
      amplitude = await import("@amplitude/analytics-browser");
      amplitude.init(AMPLITUDE_API_KEY, undefined, {
        logLevel: amplitude.Types.LogLevel.Warn,
        defaultTracking: true,
      });
      setLoading(false);
    };
    initAmplitude();
  }, []);

  return isLoading;
};

export default useAmplitudeInit;
