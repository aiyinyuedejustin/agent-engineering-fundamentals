// Original inert fixture. The toolkit never executes it.
checkGate("demo_feature", true);
checkGate("demo_experiment", false);
analytics.track("demo_completed");
registerTool("demo_lookup");
const payload = { event_key: dynamicName };
