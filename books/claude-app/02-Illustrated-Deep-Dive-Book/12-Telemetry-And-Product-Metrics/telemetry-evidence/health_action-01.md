# health_action 完整有界字典

[返回索引](README.md)

位置数是语法计数。字段并集不是必填 schema；`?` 表示至少一处条件加入，`~` 表示至少一处可能 undefined。所有值仍可能被未知 spread 或后置清理改变。这里的记录数包含已提取字段的条件 spread 与未解析形式；直接字面量对象展开会被内联，不计入此列。它不是未知字段集合数。源码位置与每处类型详见 index.json 的 sites/field_forms/shapes 分片。

| 名称 | 位置数 | 字段并集 | 已记录 spread 数 | 位置编号 |
|---|---:|---|---:|---|
| `app.bootstrap` | 3 | `early_fetch`?~, `variant` | 4 | call-02648, call-02649, call-02650 |
| `app.crash` | 17 | `boot_reload_counted_ms`~, `contained_in`~, `error_code`~, `error_subcode`?~, `error_type`, `hold_reason`~, `inline_mode`, `marked_entry_route`?~, `marked_only`?~, `reload_decision`?~, `reload_ordinal`~, `stack_origin`~, `variant`?~ | 37 | call-02783, call-02784, call-02785, call-02786, call-02787, call-02788, call-02789, call-02790, call-02791, call-02792, call-02793, call-02794, call-02795, call-02796, call-02797, call-02798, call-02799 |
| `app.gated_page_failure_shown` | 1 | `error_code`~, `error_type`~, `variant`~ | 0 | call-02800 |
| `artifacts.screenshot_capture` | 1 | `error_code`?~, `error_type`?, `variant`~ | 2 | call-01862 |
| `auth.account_add` | 1 |  | 0 | call-02406 |
| `auth.account_mismatch_409` | 1 | `variant`~ | 0 | call-02407 |
| `auth.account_overlay_shown` | 1 | `variant`~ | 0 | call-02408 |
| `auth.account_switch` | 1 |  | 0 | call-02404 |
| `auth.account_switch_ready` | 1 |  | 0 | call-02405 |
| `auth.login` | 2 | `variant`~ | 1 | call-02423, call-02424 |
| `auth.logout` | 1 | `error_code`?~, `error_type`?, `variant`~ | 2 | call-02426 |
| `auth.phone_code_send` | 1 | `variant`~ | 1 | call-01909 |
| `auth.session_expired` | 1 | `variant`~ | 0 | call-02409 |
| `auth.signup` | 1 | `variant`~ | 1 | call-02425 |
| `auth.sso_callback_error` | 1 | `error_code`~, `error_type`, `variant`~ | 0 | call-02427 |
| `billing.plan_upgrade` | 1 |  | 0 | call-02804 |
| `billing.subscription_cancel` | 1 | `error_code`?~, `variant`~ | 2 | call-02805 |
| `chat.connector_add` | 1 | `product_surface`~, `variant`~ | 1 | call-02839 |
| `chat.conversation_create` | 1 | `variant`~ | 3 | call-02773 |
| `chat.conversation_open` | 1 | `chat_kind`?~, `conversation_age_bucket`?~, `empty_reason`?~, `product_surface`~, `variant`?~ | 7 | call-02775 |
| `chat.conversation_search` | 2 | `error_code`~, `variant`~ | 1 | call-02781, call-02782 |
| `chat.file_upload` | 1 |  | 2 | call-02779 |
| `chat.incognito_conversation_create` | 1 | `variant` | 3 | call-02774 |
| `chat.message_send` | 1 |  | 0 | call-02776 |
| `chat.message_stream_complete` | 1 |  | 0 | call-02777 |
| `chat.model_switch` | 1 | `initiator`~, `model`~, `variant`~ | 1 | call-02840 |
| `chat.project_create` | 1 | `variant`~ | 1 | call-02801 |
| `chat.project_file_upload` | 1 |  | 0 | call-02780 |
| `client.navigation_loop` | 1 | `error_code`, `error_type`, `loop_count`~, `path_template`~, `variant`~ | 0 | call-02401 |
| `client.render_loop` | 1 | `error_code`, `error_type`, `loop_count`~, `path_template`~ | 0 | call-02403 |
| `code.artifact_render` | 1 |  | 0 | call-01348 |
| `code.channel_artifact_open` | 1 | `error_code`?~, `error_type`?, `variant`~ | 1 | call-01248 |
| `code.channel_create` | 1 | `create_open`?~, `press_to_created_ms`?~, `source_count`?~, `variant`~ | 4 | call-02837 |
| `code.channel_dialog_open` | 1 | `variant`~ | 0 | call-01250 |
| `code.channel_file_attach` | 1 | `error_code`?, `file_category`~, `file_count`~, `picked_via`~, `preprocess_ms`?~, `press_to_paint_ms`?~, `ready_ms`?~, `result_kind`?~, `size_bucket`~, `staged_to_request_ms`?~, `variant`~, `was_hidden`~ | 7 | call-01253 |
| `code.channel_home_open` | 1 | `bound_sessions`?~, `done_rows`?~, `error_code`?~, `error_type`?, `gated_by`?~, `home_mounted_ms`~, `initial_tab`?~, `live_rows`?~, `needs_you_bucket`?~, `needs_you_rows`?~, `overview_layout`?, `pane_open_cause`?~, `pane_opened_by`?~, `pane_shown`?~, `prefs_ready_ms`?~, `press_age_ms`?~, `press_span`?~, `press_to_paint_ms`?~, `resolved_rows`?~, `rows_bucket`?~, `rows_source`?~, `rows_total`?~, `rows_truncated`?~, `start_failed_rows`?~, `tab_age_ms`~, `tasks_reader`~, `threads_ready_ms`?~, `unread_rows`?~, `v2_at_mount`?~, `variant`~, `was_hidden`?~ | 19 | call-01240 |
| `code.channel_message_send` | 1 | `file_count`?~, `send_surface`?~, `variant`~ | 3 | call-01237 |
| `code.channel_overview_tab_switch` | 1 | `variant`~ | 0 | call-01249 |
| `code.channel_pane_render` | 1 | `error_code`?, `error_type`?, `variant`~ | 1 | call-01247 |
| `code.channel_panel_crash` | 1 | `error_code`~, `error_type`~, `variant`~ | 0 | call-01242 |
| `code.channel_stream_open` | 1 | `variant`~ | 1 | call-01238 |
| `code.channel_stream_reconnect` | 1 | `error_code`~, `variant`~, `was_hidden`~ | 0 | call-01243 |
| `code.channel_thread_open` | 1 | `channel_kind`?~, `home_section`?~, `opened_from`?~, `page_full`?~, `phase`~, `press_to_paint_ms`?~, `restore_path`?~, `rows_bucket`?~, `source`~, `thread_host`?~, `variant`~, `was_hidden`?~ | 10 | call-01239 |
| `code.channel_thread_resolve` | 1 | `variant`~, `was_hidden`~ | 1 | call-01252 |
| `code.channel_thread_walk` | 1 | `rows_bucket`?~, `rows_total`?~, `rows_truncated`?~, `variant`~, `walk_kind`~, `walk_pages`~, `walk_stopped_early`?~ | 4 | call-01241 |
| `code.channel_turn_stop` | 1 | `error_code`?~, `error_type`?, `press_to_paint_ms`?~, `variant`~, `was_hidden`~ | 3 | call-01251 |
| `code.channel_working_state` | 3 | `error_code`~, `error_type`, `variant`~ | 0 | call-01244, call-01245, call-01246 |
| `code.message_send` | 3 | `error_code`~, `error_type`, `variant`~ | 1 | call-02815, call-02816, call-02817 |
| `code.session_create` | 1 | `error_code`?~, `error_type`?, `variant`~ | 2 | call-02831 |
| `code.session_durability` | 1 | `error_code`?, `error_type`?, `variant`~ | 1 | call-02833 |
| `code.session_resume` | 1 | `error_code`?~, `error_type`?, `variant`~ | 2 | call-02832 |
| `code.tab_load` | 1 | `variant`~ | 1 | call-02836 |
| `cowork.artifact_open` | 1 | `variant`~ | 1 | call-02834 |
| `cowork.artifact_render` | 1 |  | 0 | call-01348 |
| `cowork.conversation_create` | 4 | `error_code`~, `error_type`~, `variant`~ | 1 | call-02819, call-02820, call-02821, call-02822 |
| `cowork.conversation_open` | 1 | `error_shape`?~, `variant`~ | 3 | call-02827 |
| `cowork.elevated_auth_step_up` | 1 | `error_code`?~, `error_type`?, `variant`~ | 1 | call-02823 |
| `cowork.file_attach` | 3 | `error_code`?~, `error_subcode`?~, `error_type`?~, `variant`~ | 4 | call-00384, call-02742, call-02835 |
| `cowork.mcp_tool_call` | 1 | `error_code`?~, `error_type`?~ | 2 | call-02828 |
| `cowork.message_send` | 4 | `error_code`~, `error_subcode`~, `error_type`~, `session_id`?~, `variant`~ | 4 | call-00383, call-02741, call-02811, call-02818 |
| `cowork.passkey_enroll_offer` | 1 | `error_code`?~, `error_subcode`?~, `error_type`?, `variant`~ | 4 | call-02825 |
| `cowork.project_create` | 1 | `variant`~ | 1 | call-02830 |
| `cowork.projects_load` | 1 |  | 1 | call-02829 |
| `cowork.session_start` | 1 |  | 0 | call-02814 |
| `cowork.stale_login_return` | 1 | `error_code`?, `error_type`?, `variant`~ | 2 | call-02824 |
| `cowork.tab_load` | 1 | `error_code`?~, `variant`~ | 2 | call-02826 |
| `enterprise.org_create` | 2 | `error_code`?~, `error_subcode`?~, `error_type`~, `variant`~ | 2 | call-02808, call-02809 |
| `mcp.connector_connect` | 1 |  | 0 | call-02546 |
| `mcp.connector_tools_list` | 1 |  | 0 | call-02545 |
| `mcp_app.widget_render` | 1 | `product_surface`~, `variant`~ | 1 | call-01149 |
| `page.onboarding_complete` | 1 |  | 0 | call-01908 |
| `page.onboarding_start` | 2 | `error_code`~, `error_type`~ | 1 | call-01906, call-01907 |
| `page.paid_conversion` | 3 | `error_code`?~, `error_subcode`?~, `error_type`?~, `variant`~ | 6 | call-02349, call-02350, call-02838 |
| `page.projects_load` | 1 |  | 0 | call-02802 |
| `page.security_load` | 1 | `variant`~ | 0 | call-00791 |
| `page.security_settings_load` | 4 | `error_type`~, `variant`~ | 0 | call-00792, call-00793, call-00794, call-00795 |
| `page.site_test_load` | 1 | `variant`~ | 1 | call-01998 |
| `page.upgrade_load` | 1 | `error_code`?~, `error_type`?~, `variant`~ | 2 | call-02803 |
| `security.finding_triage` | 1 | `variant`~ | 1 | call-00800 |
| `security.findings_load` | 1 | `variant`~ | 1 | call-00798 |
| `security.fix_create` | 1 | `variant`~ | 1 | call-00799 |
| `security.github_access_issue` | 1 | `variant`~ | 0 | call-00796 |
| `security.scan_create` | 1 | `variant`~ | 1 | call-00797 |
| `site_test.run_dispatch` | 2 |  | 0 | call-01999, call-02000 |
| `site_test.spec_save` | 2 | `error_code`, `error_type`, `variant`~ | 1 | call-02001, call-02002 |
| `site_test.target_create` | 1 |  | 0 | call-02005 |
| `site_test.target_verify` | 2 | `variant`~ | 0 | call-02003, call-02004 |
| `team.invite_send` | 1 | `variant`~ | 1 | call-02810 |
| `team.org_create` | 2 | `error_code`, `error_type`, `variant`~ | 1 | call-02806, call-02807 |
| `voice.dictation` | 1 | `attempt_count`?~, `variant`~ | 3 | call-02558 |
| `voice.read_aloud` | 1 | `error_subcode`?~, `variant`~, `was_hidden`?~ | 4 | call-02559 |
| `voice.session_end` | 1 | `variant`~ | 1 | call-02556 |
| `voice.session_start` | 1 | `attempt_count`?~, `media_plane`?~, `variant`~ | 4 | call-02555 |
