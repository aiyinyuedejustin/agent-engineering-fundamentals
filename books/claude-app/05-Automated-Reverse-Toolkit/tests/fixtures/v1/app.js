// Original inert fixture. The toolkit never executes it.
checkGate("demo_feature", false);
analytics.track("demo_opened");
registerTool("demo_lookup");
const payload = { event_key: "demo_clicked" };
