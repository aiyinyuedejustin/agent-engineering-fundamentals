# 动态或未解析名称

[返回索引](README.md)

下面保留无法静态确定的名称及参数转发，不把它们当不存在，也不补造完整事件名。Sentry 捕获是独立类别，不列入产品事件命名。

| 位置编号 | sink | 名称表达式类型 | 静态模板片段（若有） | 显式字段 |
|---|---|---|---|---|
| payload-00001 | analytics_track | MemberExpression | [] | `event_key`, `reason`, `entry` |
| payload-00002 | analytics_track | MemberExpression | [] | `event_key`, `reason`, `cta`, `entry` |
| payload-00003 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `tab`, `status_bucket`, `server_uuid`, `initial` |
| payload-00004 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `server_uuid` |
| payload-00005 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `server_uuid`, `status_bucket` |
| payload-00006 | analytics_track | MemberExpression | [] | `event_key`, `status`, `status_bucket`, `server_uuid`, `submissions_mount` |
| payload-00007 | analytics_track | MemberExpression | [] | `event_key`, `placement`, `submission_count_bucket` |
| payload-00008 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `submission_count_bucket`, `connector_count_bucket`, `plugin_count_bucket`, `has_needs_changes`, `has_approved_unpublished` |
| payload-00009 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `placement` |
| payload-00010 | analytics_track | MemberExpression | [] | `event_key`, `route_kind` |
| payload-00011 | analytics_track | MemberExpression | [] | `event_key`, `kind` |
| payload-00012 | analytics_track | MemberExpression | [] | `event_key`, `route_kind`, `kind`, `entry`, `access` |
| payload-00020 | analytics_track | Identifier | [] | `event_key` |
| payload-00032 | unresolved_payload | Identifier | [] | `event_key`, `ephemeral` |
| payload-00074 | unresolved_payload | MemberExpression | [] | `event_key`, `message_uuid`, `tool_use_id`, `tool_name`, `copy_version` |
| payload-00129 | analytics_track | MemberExpression | [] | `event_key`, `mount` |
| payload-00130 | analytics_track | MemberExpression | [] | `event_key`, `mount` |
| payload-00133 | analytics_track | Identifier | [] | `event_key`, `menu_surface`, `file_extension`, `file_size_bucket` |
| payload-00139 | analytics_track | Identifier | [] | `event_key`, `session_id` |
| payload-00174 | unresolved_payload | Identifier | [] | `event_key`, `offer_check`, `offer_count`, `draw_point` |
| payload-00175 | unresolved_payload | MemberExpression | [] | `event_key`, `experiment_variant`, `branch`, `chat_host`, `branch_settled`, `offer_check`, `offer_count`, `draw_point` |
| payload-00176 | unresolved_payload | MemberExpression | [] | `event_key`, `surface`, `chat_host`, `experiment_variant`, `branch_settled`, `error_name` |
| payload-00177 | unresolved_payload | MemberExpression | [] | `event_key`, `surface`, `chat_host`, `experiment_variant`, `branch_settled`, `error_name` |
| payload-00178 | unresolved_payload | MemberExpression | [] | `event_key`, `surface`, `chat_host`, `session_id`, `variant_honored`, `experiment_variant`, `branch_settled` |
| payload-00179 | unresolved_payload | MemberExpression | [] | `event_key`, `surface`, `chat_host`, `guided_mode`, `conversation_uuid`, `experiment_variant`, `branch_settled`, `cowork_refused` |
| payload-00180 | unresolved_payload | MemberExpression | [] | `event_key`, `surface`, `chat_host`, `experiment_variant`, `branch_settled`, `error_name`, `cowork_refused` |
| payload-00195 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| payload-00196 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.completed'] | `event_key` |
| payload-00197 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.command_copied'] | `event_key` |
| payload-00198 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.link_clicked'] | `event_key`, `destination` |
| payload-00211 | analytics_track | Identifier | [] | `event_key` |
| payload-00225 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| payload-00226 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.completed'] | `event_key` |
| payload-00227 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.install_clicked'] | `event_key`, `product` |
| payload-00236 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| payload-00237 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.command_copied'] | `event_key` |
| payload-00238 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.link_clicked'] | `event_key`, `destination` |
| payload-00240 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.documentation_clicked'] | `event_key` |
| payload-00253 | analytics_track | Identifier | [] | `event_key`, `arm` |
| payload-00279 | unresolved_payload | Identifier | [] |  |
| payload-00360 | analytics_track | Identifier | [] | `event_key`, `copy_surface`, `kind`, `item_id` |
| payload-00367 | analytics_track | Identifier | [] | `event_key`, `enabled`, `source` |
| payload-00383 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-00384 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-00385 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-00386 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-00450 | analytics_track | Identifier | [] | `event_key`, `host`, `family`, `utm_campaign`, `impression` |
| payload-00469 | analytics_track | MemberExpression | [] | `event_key` |
| payload-00484 | analytics_track | MemberExpression | [] | `event_key`, `action`, `target` |
| payload-00504 | analytics_track | Identifier | [] | `event_key`, `placement` |
| payload-00588 | analytics_track | Identifier | [] | `event_key`, `surface`, `count` |
| payload-00590 | analytics_track | MemberExpression | [] | `event_key`, `surface` |
| payload-00600 | analytics_track | Identifier | [] | `event_key` |
| payload-00621 | analytics_track | Identifier | [] | `event_key`, `session_id`, `hook_type`, `tool_use_id`, `tool_name`, `document_kind` |
| payload-00721 | analytics_track | MemberExpression | [] | `event_key`, `placement`, `signed_in` |
| payload-00722 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| payload-00723 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| payload-00724 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| payload-00748 | analytics_track | template_dynamic | ['', '.shown'] | `event_key` |
| payload-00749 | analytics_track | template_dynamic | ['', '.link_copied'] | `event_key` |
| payload-00768 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `coverage_ready`, `unavailable_reason`, `unavailable_reason_id`, `reach_count`, `total_count`, `managed_count`, `is_everyone`, `faces_shown`, `load_ms` |
| payload-00769 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `can_edit`, `roles_error` |
| payload-00770 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `entry_point`, `from_edit_button`, `can_edit`, `roles_loading`, `custom_role_count`, `editable_role_count`, `coverage_ready` |
| payload-00771 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `outcome`, `outcome_id`, `had_unsaved_changes`, `unsaved_change_count`, `picks_made`, `open_ms` |
| payload-00772 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `from_level`, `to_level`, `from_level_id`, `to_level_id`, `reverted`, `grants_access`, `removes_access`, `role_member_count`, `draft_change_count` |
| payload-00773 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `outcome`, `outcome_id`, `roles_attempted`, `roles_failed`, `to_allow_count`, `to_ask_count`, `to_blocked_count`, `access_granted_count`, `access_removed_count`, `members_affected_estimate`, `error_kind`, `error_kind_id`, `save_ms` |
| payload-00826 | analytics_track | template_dynamic | ['', '.shown'] | `event_key` |
| payload-00827 | analytics_track | template_dynamic | ['', '.copy_clicked'] | `event_key` |
| payload-00828 | analytics_track | template_dynamic | ['', '.dismissed'] | `event_key` |
| payload-00898 | analytics_track | Identifier | [] | `event_key` |
| payload-00899 | analytics_track | Identifier | [] | `event_key` |
| payload-00900 | analytics_track | Identifier | [] | `event_key`, `sentiment`, `category`, `has_text` |
| payload-00901 | analytics_track | Identifier | [] | `event_key`, `reminder_surface` |
| payload-00902 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds` |
| payload-00903 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds`, `artifacts`, `hasPagesArtifact` |
| payload-00923 | analytics_track | template_dynamic | ['', '.connect_clicked'] | `event_key`, `connector_name` |
| payload-00924 | analytics_track | template_dynamic | ['', '.continue_clicked'] | `event_key`, `connected_count`, `connector_names_connected` |
| payload-00925 | analytics_track | template_dynamic | ['', '.skipped'] | `event_key` |
| payload-01063 | analytics_track | template_dynamic | ['claudeai.admin_settings.member_feature_off_confirm.', ''] | `event_key`, `toggle_key`, `toggle_id` |
| payload-01064 | analytics_track | Identifier | [] | `event_key`, `new_state` |
| payload-01195 | unresolved_payload | Identifier | [] | `event_key`, `screen`, `mount`, `entry`, `listing_uuid`, `item_kind`, `connectors_configured`, `connectors_connected`, `connectors_needs_reauth`, `connectors_settled` |
| payload-01388 | unresolved_payload | Identifier | [] |  |
| payload-01390 | unresolved_payload | Identifier | [] |  |
| payload-01392 | unresolved_payload | Identifier | [] |  |
| payload-01394 | unresolved_payload | Identifier | [] |  |
| payload-01411 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01462 | unresolved_payload | template_dynamic | ['payment_state_', ''] | `event_key`, `product_capability`, `rate_limit_tier`, `invoice_created_ts`, `subscription_kind` |
| payload-01487 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| payload-01488 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `trigger`, `trigger_id`, `outcome_id`, `failure_kind_id` |
| payload-01489 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `layout`, `layout_id`, `waiting`, `tool_count`, `missing_count`, `review_state`, `review_state_id` |
| payload-01490 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `layout`, `layout_id`, `waiting` |
| payload-01491 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `entry_point`, `entry_point_id`, `step`, `step_id`, `failing_tool_count`, `missing_count`, `waiting`, `partial` |
| payload-01492 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `step`, `step_id`, `link_sent`, `open_ms` |
| payload-01493 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `via`, `via_id`, `blocked_count`, `other_change_count`, `failed_count`, `kept_tool_count`, `save_ms` |
| payload-01494 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `action`, `action_id`, `step`, `step_id`, `kept_tool_count` |
| payload-01495 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `outcome_id`, `tools_covered`, `wait_ms` |
| payload-01496 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `approved`, `error_code`, `resumed` |
| payload-01502 | analytics_track | Identifier | [] | `event_key` |
| payload-01550 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01551 | analytics_track | MemberExpression | [] | `event_key`, `error_code`, `status_code` |
| payload-01571 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01572 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01675 | analytics_track | Identifier | [] | `event_key`, `host`, `dwell_ms`, `sample_rate` |
| payload-01795 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01806 | unresolved_payload | Identifier | [] |  |
| payload-01807 | unresolved_payload | Identifier | [] | `event_key`, `connector_count`, `row_index`, `was_installed`, `server_says_installed`, `connected_count`, `was_connected`, `had_auth_error`, `other_connector_count`, `origin`, `reason`, `via`, `placement`, `chin_redesign` |
| payload-01836 | analytics_track | Identifier | [] | `event_key` |
| payload-01854 | analytics_track | template_dynamic | ['claudeai.subscription.cancel_modal.', ''] | `event_key`, `variant` |
| payload-01891 | analytics_track | MemberExpression | [] | `event_key`, `client_surface` |
| payload-01892 | analytics_track | MemberExpression | [] | `event_key`, `client_surface` |
| payload-01893 | analytics_track | MemberExpression | [] | `event_key`, `client_surface`, `open_method` |
| payload-01918 | analytics_track | Identifier | [] | `event_key` |
| payload-01919 | analytics_track | Identifier | [] | `event_key` |
| payload-01927 | analytics_track | Identifier | [] | `event_key` |
| payload-01928 | analytics_track | Identifier | [] | `event_key` |
| payload-01929 | analytics_track | Identifier | [] | `event_key` |
| payload-01941 | analytics_track | MemberExpression | [] | `event_key` |
| payload-01942 | analytics_track | Identifier | [] | `event_key` |
| payload-02070 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `managed_enabled`, `has_config`, `can_enable`, `sso_connection_type` |
| payload-02071 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `initial_step`, `has_existing_config`, `entry_point` |
| payload-02072 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `step` |
| payload-02073 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| payload-02074 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `failed_hop` |
| payload-02075 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `last_step`, `connection_test_ok` |
| payload-02076 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `default_roles_managed`, `custom_role_count`, `scope_ceiling`, `had_existing_config` |
| payload-02077 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `error_kind` |
| payload-02078 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `enabled` |
| payload-02079 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `health`, `banner_shown`, `top_cause` |
| payload-02080 | analytics_track | MemberExpression | [] | `event_key`, `connector_count`, `ema_capable_count`, `ema_managed_count`, `rows_resolved` |
| payload-02081 | analytics_track | MemberExpression | [] | `event_key`, `host_surface`, `row_state` |
| payload-02082 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| payload-02083 | analytics_track | conditional | [] | `event_key`, `server_uuid` |
| payload-02084 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02085 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02086 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02087 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02088 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02089 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02104 | analytics_track | template_dynamic | ['onboarding.phone_verification.', ''] | `event_key`, `surface`, `flow`, `version` |
| payload-02111 | analytics_track | template_dynamic | ['claudeai.cowork.skill_proposal.', ''] | `event_key`, `proposal_kind` |
| payload-02114 | unresolved_payload | Identifier | [] | `event_key` |
| payload-02120 | analytics_track | Identifier | [] | `event_key`, `plugin_id`, `plugin_id_hash`, `plugin_name`, `is_official_plugin`, `plugin_context`, `surface`, `skill_name` |
| payload-02133 | analytics_track | Identifier | [] | `event_key`, `plan_type_tab`, `recommended_plan`, `pro_card_label` |
| payload-02143 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-02144 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-02145 | analytics_track | Identifier | [] | `event_key`, `action` |
| payload-02180 | analytics_track | MemberExpression | [] | `event_key`, `status`, `posture`, `registration`, `refused_status`, `discovery_timed_out`, `prefilled` |
| payload-02181 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02182 | analytics_track | MemberExpression | [] | `event_key`, `duration_ms`, `output_chars`, `verdict` |
| payload-02183 | analytics_track | MemberExpression | [] | `event_key`, `error_type`, `duration_ms` |
| payload-02184 | analytics_track | MemberExpression | [] | `event_key`, `capture_surface`, `status`, `tool_count`, `prompt_count`, `prompts_adopted`, `submissions_mount`, `server_uuid`, `kind` |
| payload-02185 | analytics_track | MemberExpression | [] | `event_key`, `capture_surface`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| payload-02186 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| payload-02187 | analytics_track | MemberExpression | [] | `event_key`, `is_resubmit`, `status`, `tool_count`, `submissions_mount`, `server_uuid`, `kind` |
| payload-02188 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| payload-02189 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `submission_count_bucket`, `connector_count_bucket`, `plugin_count_bucket`, `has_needs_changes`, `has_approved_unpublished` |
| payload-02190 | analytics_track | MemberExpression | [] | `event_key`, `outcome`, `reason` |
| payload-02191 | analytics_track | MemberExpression | [] | `event_key`, `outcome`, `reason` |
| payload-02192 | analytics_track | MemberExpression | [] | `event_key`, `total_steps`, `resuming`, `entry_point` |
| payload-02193 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `furthest_step_index` |
| payload-02194 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `furthest_step_index` |
| payload-02195 | unresolved_payload | MemberExpression | [] | `event_key`, `step`, `step_index`, `error_count`, `error_fields` |
| payload-02196 | unresolved_payload | MemberExpression | [] | `event_key`, `step`, `step_index` |
| payload-02197 | unresolved_payload | MemberExpression | [] | `event_key`, `step`, `step_index`, `error_count`, `error_fields` |
| payload-02198 | unresolved_payload | MemberExpression | [] | `event_key`, `phase`, `error_type` |
| payload-02199 | unresolved_payload | MemberExpression | [] | `event_key`, `phase`, `error_type` |
| payload-02200 | unresolved_payload | MemberExpression | [] | `event_key`, `validation_fields` |
| payload-02201 | unresolved_payload | MemberExpression | [] | `event_key`, `phase`, `error_type` |
| payload-02202 | unresolved_payload | MemberExpression | [] | `event_key`, `phase`, `error_type` |
| payload-02203 | unresolved_payload | MemberExpression | [] | `event_key`, `phase`, `error_type` |
| payload-02204 | unresolved_payload | MemberExpression | [] | `event_key`, `server_uuid`, `is_resubmit`, `elapsed_ms` |
| payload-02205 | analytics_track | MemberExpression | [] | `event_key`, `total_steps`, `resuming` |
| payload-02206 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `total_steps` |
| payload-02207 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `total_steps` |
| payload-02208 | unresolved_payload | MemberExpression | [] | `event_key`, `step`, `step_index`, `error_count` |
| payload-02209 | unresolved_payload | MemberExpression | [] | `event_key`, `step`, `step_index`, `error_count`, `error_fields` |
| payload-02210 | unresolved_payload | MemberExpression | [] | `event_key`, `submission_uuid`, `elapsed_ms`, `platform_count`, `has_homepage`, `has_privacy_policy` |
| payload-02211 | unresolved_payload | MemberExpression | [] | `event_key`, `error_type` |
| payload-02222 | unresolved_payload | Identifier | [] | `event_key` |
| payload-02223 | unresolved_payload | conditional | [] | `event_key` |
| payload-02224 | unresolved_payload | Identifier | [] | `event_key` |
| payload-02227 | unresolved_payload | template_dynamic | ['mcp_app.', ''] | `event_key`, `at_ms` |
| payload-02245 | unresolved_payload | Identifier | [] | `session_id`, `tool_name`, `event_key`, `phase` |
| payload-02250 | analytics_track | Identifier | [] | `event_key` |
| payload-02275 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `static_headers_enabled`, `prefilled`, `entry_point` |
| payload-02276 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `step_id` |
| payload-02277 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `error_kind` |
| payload-02278 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `static_headers_enabled`, `outcome`, `last_step_id`, `create_error_count`, `entry_point` |
| payload-02279 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02280 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02281 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02303 | analytics_track | template_dynamic | ['claudeai.billing.stripe_elements.', ''] | `event_key` |
| payload-02316 | analytics_track | Identifier | [] | `event_key`, `placement` |
| payload-02377 | analytics_track | Identifier | [] | `event_key` |
| payload-02417 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount` |
| payload-02418 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount` |
| payload-02470 | analytics_track | Identifier | [] | `event_key`, `banner_id` |
| payload-02534 | analytics_track | template_dynamic | ['claudeai.admin_settings.requests_off_confirm.', ''] | `event_key`, `setting_label`, `blocked_count_shown`, `blocked_count` |
| payload-02584 | analytics_track | template_dynamic | ['claudeai.upgrade.', '_page_viewed'] | `event_key`, `referral_campaign`, `referral_source`, `entry_referral_source` |
| payload-02614 | unresolved_payload | Identifier | [] | `event_key`, `custom_properties`, `custom_properties.suspended_at`, `custom_properties.resume` |
| payload-02705 | analytics_track | MemberExpression | [] | `event_key` |
| payload-02730 | unresolved_payload | Identifier | [] | `event_key`, `scope`, `period`, `write`, `action`, `limit_minor`, `is_unlimited`, `previous_limit_minor`, `previous_known`, `source`, `currency`, `arm`, `recommendation_available`, `prefill_minor`, `prefill_source`, `picked_option` |
| payload-02759 | unresolved_payload | Identifier | [] | `event_key` |
| payload-02808 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| payload-02809 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| payload-02810 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key` |
| payload-02837 | analytics_track | Identifier | [] | `event_key` |
| payload-02845 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| payload-02846 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| payload-02868 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.item_id` |
| payload-02897 | analytics_track | Identifier | [] | `event_key`, `session_type` |
| payload-02906 | analytics_track | Identifier | [] | `event_key`, `platform` |
| payload-02924 | analytics_track | Identifier | [] | `event_key`, `phase`, `episode_id`, `page_kind`, `trigger`, `project_uuid`, `conversation_uuid`, `is_creator`, `open_age_s`, `outcome`, `decline_reason`, `resolve_ms` |
| payload-02980 | unresolved_payload | template_dynamic | ['claudeai.amber_lynx_glade.', ''] | `event_key`, `data`, `data.arm` |
| payload-03004 | unresolved_payload | Identifier | [] | `event_key` |
| payload-03005 | unresolved_payload | conditional | [] | `event_key`, `reason`, `upload_source`, `file_size_bytes`, `uploads_in_flight`, `auto_retry_count`, `duration_ms`, `pick_to_attach_ms`, `queue_wait_ms`, `upload_body_bytes`, `upload_media_type`, `prepare_ms`, `request_ms`, `body_written_ms` |
| payload-03007 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `message_uuid`, `content_kind` |
| payload-03008 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `new_chat` |
| payload-03027 | unresolved_payload | Identifier | [] |  |
| payload-03029 | unresolved_payload | Identifier | [] |  |
| payload-03059 | unresolved_payload | Identifier | [] |  |
| payload-03060 | analytics_track | Identifier | [] | `event_key`, `result` |
| payload-03061 | analytics_track | Identifier | [] | `event_key`, `result`, `failure_reason` |
| payload-03062 | analytics_track | Identifier | [] | `event_key` |
| payload-03080 | analytics_track | Identifier | [] | `event_key`, `entry_surface`, `conversation_uuid`, `original_model`, `fallback_model` |
| payload-03107 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key`, `variant` |
| payload-03108 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key`, `variant` |
| payload-03109 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key`, `variant` |
| payload-03143 | unresolved_payload | Identifier | [] | `event_key`, `key`, `category`, `rank`, `registry_revision` |
| payload-03145 | analytics_track | template_dynamic | ['claudeai.', '.entitlement_suppressed'] | `event_key`, `model_id`, `reason` |
| payload-03146 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| payload-03147 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| payload-03148 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key` |
| payload-03157 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key`, `update_available` |
| payload-03158 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| payload-03176 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds`, `artifacts`, `hasPagesArtifact`, `artifactKind` |
| payload-03178 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `original_model`, `fallback_model` |
| payload-03181 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.arm`, `data.mode`, `data.fallback_reason`, `data.window`, `data.hours_until_reset`, `data.host`, `data.fresh`, `data.reconciled` |
| payload-03182 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.arm`, `data.origin`, `data.window`, `data.destination` |
| payload-03183 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.arm`, `data.origin`, `data.pricing` |
| payload-03184 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.arm`, `data.origin`, `data.action`, `data.interval` |
| payload-03185 | unresolved_payload | MemberExpression | [] | `event_key`, `data`, `data.path` |
| payload-03199 | analytics_track | Identifier | [] | `event_key`, `renderer_surface`, `is_mobile_web` |
| payload-03247 | analytics_track | template_dynamic | ['claudeai.cowork.cache_miss.warning_modal.', ''] | `event_key`, `session_id`, `session_type`, `from_model` |
| payload-03268 | unresolved_payload | template_dynamic | ['', '.threshold_crossed'] | `event_key`, `data`, `data.threshold`, `data.rendered`, `data.prev_utilization_pct`, `data.at_wall` |
| payload-03269 | unresolved_payload | template_dynamic | ['', '.shown'] | `event_key`, `data` |
| payload-03270 | unresolved_payload | template_dynamic | ['', '.popover_opened'] | `event_key`, `data`, `data.resets_held` |
| payload-03271 | unresolved_payload | template_dynamic | ['', '.cta_clicked'] | `event_key`, `data`, `data.cta` |
| call-00001 | analytics_track | MemberExpression | [] | `event_key`, `reason`, `entry` |
| call-00002 | analytics_track | MemberExpression | [] | `event_key`, `reason`, `cta`, `entry` |
| call-00003 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `tab`, `status_bucket`, `server_uuid`, `initial` |
| call-00004 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `server_uuid` |
| call-00005 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `server_uuid`, `status_bucket` |
| call-00006 | analytics_track | MemberExpression | [] | `event_key`, `status`, `status_bucket`, `server_uuid`, `submissions_mount` |
| call-00007 | analytics_track | MemberExpression | [] | `event_key`, `placement`, `submission_count_bucket` |
| call-00008 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `submission_count_bucket`, `connector_count_bucket`, `plugin_count_bucket`, `has_needs_changes`, `has_approved_unpublished` |
| call-00009 | analytics_track | MemberExpression | [] | `event_key`, `kind`, `placement` |
| call-00010 | analytics_track | MemberExpression | [] | `event_key`, `route_kind` |
| call-00011 | analytics_track | MemberExpression | [] | `event_key`, `kind` |
| call-00012 | analytics_track | MemberExpression | [] | `event_key`, `route_kind`, `kind`, `entry`, `access` |
| call-00020 | analytics_track | Identifier | [] | `event_key` |
| call-00120 | analytics_track | MemberExpression | [] | `event_key`, `mount` |
| call-00121 | analytics_track | missing | [] |  |
| call-00122 | analytics_track | MemberExpression | [] | `event_key`, `mount` |
| call-00125 | analytics_track | Identifier | [] | `event_key`, `menu_surface`, `file_extension`, `file_size_bucket` |
| call-00131 | analytics_track | Identifier | [] | `event_key`, `session_id` |
| call-00136 | analytics_track | missing | [] |  |
| call-00164 | analytics_track | missing | [] | `client_platform`, `org_type` |
| call-00179 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| call-00180 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.completed'] | `event_key` |
| call-00181 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.command_copied'] | `event_key` |
| call-00182 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.link_clicked'] | `event_key`, `destination` |
| call-00195 | analytics_track | Identifier | [] | `event_key` |
| call-00209 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| call-00210 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.completed'] | `event_key` |
| call-00211 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.install_clicked'] | `event_key`, `product` |
| call-00220 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.shown'] | `event_key` |
| call-00221 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.command_copied'] | `event_key` |
| call-00222 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.link_clicked'] | `event_key`, `destination` |
| call-00224 | analytics_track | template_dynamic | ['claudeai.onboarding.', '.documentation_clicked'] | `event_key` |
| call-00237 | analytics_track | Identifier | [] | `event_key`, `arm` |
| call-00250 | analytics_track | missing | [] | `layout`, `session_id`, `origin` |
| call-00257 | analytics_track | missing | [] |  |
| call-00279 | analytics_track | missing | [] |  |
| call-00280 | analytics_track | missing | [] |  |
| call-00288 | analytics_track | Identifier | [] | `event_key`, `copy_surface`, `kind`, `item_id` |
| call-00295 | analytics_track | Identifier | [] | `event_key`, `enabled`, `source` |
| call-00311 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-00312 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-00313 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-00314 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-00373 | analytics_track | Identifier | [] | `event_key`, `host`, `family`, `utm_campaign`, `impression` |
| call-00391 | analytics_track | MemberExpression | [] | `event_key` |
| call-00406 | analytics_track | MemberExpression | [] | `event_key`, `action`, `target` |
| call-00416 | analytics_track | missing | [] |  |
| call-00423 | analytics_track | Identifier | [] | `event_key`, `placement` |
| call-00502 | analytics_track | missing | [] |  |
| call-00505 | analytics_track | Identifier | [] | `event_key`, `surface`, `count` |
| call-00507 | analytics_track | MemberExpression | [] | `event_key`, `surface` |
| call-00515 | analytics_track | missing | [] |  |
| call-00517 | analytics_track | Identifier | [] | `event_key` |
| call-00528 | analytics_track | Identifier | [] | `event_key`, `session_id`, `hook_type`, `tool_use_id`, `tool_name`, `document_kind` |
| call-00535 | analytics_track | missing | [] |  |
| call-00540 | analytics_track | missing | [] |  |
| call-00571 | analytics_track | missing | [] |  |
| call-00620 | analytics_visibility | MemberExpression | [] | `placement`, `signed_in` |
| call-00621 | analytics_track | MemberExpression | [] | `event_key`, `placement`, `signed_in` |
| call-00622 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| call-00623 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| call-00624 | analytics_track | MemberExpression | [] | `event_key`, `<computed>` |
| call-00625 | analytics_track | missing | [] |  |
| call-00648 | analytics_track | template_dynamic | ['', '.shown'] | `event_key` |
| call-00649 | analytics_track | template_dynamic | ['', '.link_copied'] | `event_key` |
| call-00663 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `coverage_ready`, `unavailable_reason`, `unavailable_reason_id`, `reach_count`, `total_count`, `managed_count`, `is_everyone`, `faces_shown`, `load_ms` |
| call-00664 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `can_edit`, `roles_error` |
| call-00665 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `in_directory`, `entry_point`, `from_edit_button`, `can_edit`, `roles_loading`, `custom_role_count`, `editable_role_count`, `coverage_ready` |
| call-00666 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `outcome`, `outcome_id`, `had_unsaved_changes`, `unsaved_change_count`, `picks_made`, `open_ms` |
| call-00667 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `from_level`, `to_level`, `from_level_id`, `to_level_id`, `reverted`, `grants_access`, `removes_access`, `role_member_count`, `draft_change_count` |
| call-00668 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `host`, `outcome`, `outcome_id`, `roles_attempted`, `roles_failed`, `to_allow_count`, `to_ask_count`, `to_blocked_count`, `access_granted_count`, `access_removed_count`, `members_affected_estimate`, `error_kind`, `error_kind_id`, `save_ms` |
| call-00670 | analytics_track | missing | [] | `variant` |
| call-00708 | analytics_track | template_dynamic | ['', '.shown'] | `event_key` |
| call-00709 | analytics_track | template_dynamic | ['', '.copy_clicked'] | `event_key` |
| call-00710 | analytics_track | template_dynamic | ['', '.dismissed'] | `event_key` |
| call-00774 | analytics_track | missing | [] |  |
| call-00780 | analytics_track | Identifier | [] | `event_key` |
| call-00781 | analytics_track | Identifier | [] | `event_key` |
| call-00782 | analytics_track | Identifier | [] | `event_key`, `sentiment`, `category`, `has_text` |
| call-00783 | analytics_track | Identifier | [] | `event_key`, `reminder_surface` |
| call-00784 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds` |
| call-00785 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds`, `artifacts`, `hasPagesArtifact` |
| call-00810 | analytics_track | template_dynamic | ['', '.connect_clicked'] | `event_key`, `connector_name` |
| call-00811 | analytics_track | template_dynamic | ['', '.continue_clicked'] | `event_key`, `connected_count`, `connector_names_connected` |
| call-00812 | analytics_track | template_dynamic | ['', '.skipped'] | `event_key` |
| call-00858 | analytics_track | missing | [] |  |
| call-00882 | analytics_track | missing | [] |  |
| call-00902 | analytics_track | missing | [] |  |
| call-00916 | analytics_track | missing | [] |  |
| call-00930 | analytics_track | missing | [] |  |
| call-00931 | analytics_track | missing | [] |  |
| call-00937 | analytics_track | template_dynamic | ['claudeai.admin_settings.member_feature_off_confirm.', ''] | `event_key`, `toggle_key`, `toggle_id` |
| call-00938 | analytics_track | Identifier | [] | `event_key`, `new_state` |
| call-01065 | analytics_track | missing | [] |  |
| call-01077 | analytics_track | missing | [] | `plugin_version` |
| call-01078 | analytics_track | missing | [] | `plugin_version` |
| call-01084 | analytics_track | missing | [] |  |
| call-01260 | analytics_track | missing | [] |  |
| call-01261 | analytics_track | missing | [] |  |
| call-01262 | analytics_track | missing | [] |  |
| call-01263 | analytics_track | missing | [] |  |
| call-01280 | analytics_track | MemberExpression | [] | `event_key` |
| call-01304 | analytics_track | missing | [] |  |
| call-01305 | analytics_track | missing | [] |  |
| call-01320 | analytics_track | missing | [] |  |
| call-01349 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| call-01350 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `trigger`, `trigger_id`, `outcome_id`, `failure_kind_id` |
| call-01351 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `layout`, `layout_id`, `waiting`, `tool_count`, `missing_count`, `review_state`, `review_state_id` |
| call-01352 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `layout`, `layout_id`, `waiting` |
| call-01353 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `entry_point`, `entry_point_id`, `step`, `step_id`, `failing_tool_count`, `missing_count`, `waiting`, `partial` |
| call-01354 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `step`, `step_id`, `link_sent`, `open_ms` |
| call-01355 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `via`, `via_id`, `blocked_count`, `other_change_count`, `failed_count`, `kept_tool_count`, `save_ms` |
| call-01356 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `action`, `action_id`, `step`, `step_id`, `kept_tool_count` |
| call-01357 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `outcome_id`, `tools_covered`, `wait_ms` |
| call-01358 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `approved`, `error_code`, `resumed` |
| call-01361 | analytics_track | Identifier | [] | `event_key` |
| call-01403 | analytics_track | MemberExpression | [] | `event_key` |
| call-01404 | analytics_track | MemberExpression | [] | `event_key`, `error_code`, `status_code` |
| call-01420 | analytics_visibility | MemberExpression | [] |  |
| call-01421 | analytics_track | MemberExpression | [] | `event_key` |
| call-01422 | analytics_track | MemberExpression | [] | `event_key` |
| call-01436 | analytics_track | missing | [] |  |
| call-01439 | analytics_track | missing | [] |  |
| call-01440 | analytics_track | missing | [] |  |
| call-01482 | analytics_track | missing | [] |  |
| call-01483 | analytics_track | missing | [] |  |
| call-01496 | analytics_track | missing | [] | `client_platform` |
| call-01518 | analytics_track | Identifier | [] | `event_key`, `host`, `dwell_ms`, `sample_rate` |
| call-01547 | analytics_track | missing | [] |  |
| call-01548 | analytics_track | missing | [] | `session_id_digest` |
| call-01555 | analytics_track | missing | [] | `session_id_digest` |
| call-01614 | analytics_track | missing | [] |  |
| call-01621 | analytics_track | MemberExpression | [] | `event_key` |
| call-01632 | analytics_track | missing | [] |  |
| call-01652 | analytics_track | Identifier | [] | `event_key` |
| call-01670 | analytics_track | template_dynamic | ['claudeai.subscription.cancel_modal.', ''] | `event_key`, `variant` |
| call-01707 | analytics_track | MemberExpression | [] | `event_key`, `client_surface` |
| call-01708 | analytics_track | MemberExpression | [] | `event_key`, `client_surface` |
| call-01709 | analytics_track | MemberExpression | [] | `event_key`, `client_surface`, `open_method` |
| call-01733 | analytics_track | Identifier | [] | `event_key` |
| call-01734 | analytics_track | Identifier | [] | `event_key` |
| call-01742 | analytics_track | Identifier | [] | `event_key` |
| call-01743 | analytics_track | Identifier | [] | `event_key` |
| call-01744 | analytics_track | Identifier | [] | `event_key` |
| call-01756 | analytics_track | MemberExpression | [] | `event_key` |
| call-01757 | analytics_track | Identifier | [] | `event_key` |
| call-01774 | analytics_track | missing | [] |  |
| call-01855 | analytics_track | missing | [] | `outcome` |
| call-01856 | analytics_track | missing | [] |  |
| call-01857 | analytics_track | missing | [] | `outcome`, `latency_ms`, `sdk_cold` |
| call-01858 | analytics_track | missing | [] | `outcome`, `latency_ms` |
| call-01867 | analytics_track | missing | [] | `session_id` |
| call-01875 | analytics_track | missing | [] |  |
| call-01876 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `managed_enabled`, `has_config`, `can_enable`, `sso_connection_type` |
| call-01877 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `initial_step`, `has_existing_config`, `entry_point` |
| call-01878 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `step` |
| call-01879 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| call-01880 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `failed_hop` |
| call-01881 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `outcome`, `last_step`, `connection_test_ok` |
| call-01882 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `default_roles_managed`, `custom_role_count`, `scope_ceiling`, `had_existing_config` |
| call-01883 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `error_kind` |
| call-01884 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `enabled` |
| call-01885 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid`, `health`, `banner_shown`, `top_cause` |
| call-01886 | analytics_track | MemberExpression | [] | `event_key`, `connector_count`, `ema_capable_count`, `ema_managed_count`, `rows_resolved` |
| call-01887 | analytics_track | MemberExpression | [] | `event_key`, `host_surface`, `row_state` |
| call-01888 | analytics_track | MemberExpression | [] | `event_key`, `server_uuid` |
| call-01889 | analytics_track | conditional | [] | `event_key`, `server_uuid` |
| call-01890 | analytics_track | MemberExpression | [] | `event_key` |
| call-01891 | analytics_track | MemberExpression | [] | `event_key` |
| call-01892 | analytics_track | MemberExpression | [] | `event_key` |
| call-01893 | analytics_track | MemberExpression | [] | `event_key` |
| call-01894 | analytics_track | MemberExpression | [] | `event_key` |
| call-01895 | analytics_track | MemberExpression | [] | `event_key` |
| call-01911 | analytics_track | template_dynamic | ['onboarding.phone_verification.', ''] | `event_key`, `surface`, `flow`, `version` |
| call-01918 | analytics_track | template_dynamic | ['claudeai.cowork.skill_proposal.', ''] | `event_key`, `proposal_kind` |
| call-01923 | analytics_track | Identifier | [] | `event_key`, `plugin_id`, `plugin_id_hash`, `plugin_name`, `is_official_plugin`, `plugin_context`, `surface`, `skill_name` |
| call-01934 | analytics_track | Identifier | [] | `event_key`, `plan_type_tab`, `recommended_plan`, `pro_card_label` |
| call-01939 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-01940 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-01941 | analytics_track | Identifier | [] | `event_key`, `action` |
| call-01942 | analytics_track | missing | [] |  |
| call-01976 | analytics_track | MemberExpression | [] | `event_key`, `status`, `posture`, `registration`, `refused_status`, `discovery_timed_out`, `prefilled` |
| call-01977 | analytics_track | MemberExpression | [] | `event_key` |
| call-01978 | analytics_track | MemberExpression | [] | `event_key`, `duration_ms`, `output_chars`, `verdict` |
| call-01979 | analytics_track | MemberExpression | [] | `event_key`, `error_type`, `duration_ms` |
| call-01980 | analytics_track | MemberExpression | [] | `event_key`, `capture_surface`, `status`, `tool_count`, `prompt_count`, `prompts_adopted`, `submissions_mount`, `server_uuid`, `kind` |
| call-01981 | analytics_track | MemberExpression | [] | `event_key`, `capture_surface`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| call-01982 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| call-01983 | analytics_track | MemberExpression | [] | `event_key`, `is_resubmit`, `status`, `tool_count`, `submissions_mount`, `server_uuid`, `kind` |
| call-01984 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount`, `server_uuid`, `kind` |
| call-01985 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount`, `submission_count_bucket`, `connector_count_bucket`, `plugin_count_bucket`, `has_needs_changes`, `has_approved_unpublished` |
| call-01986 | analytics_track | MemberExpression | [] | `event_key`, `outcome`, `reason` |
| call-01987 | analytics_track | MemberExpression | [] | `event_key`, `outcome`, `reason` |
| call-01988 | analytics_track | missing | [] |  |
| call-01989 | analytics_track | MemberExpression | [] | `event_key`, `total_steps`, `resuming`, `entry_point` |
| call-01990 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `furthest_step_index` |
| call-01991 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `furthest_step_index` |
| call-01992 | analytics_track | missing | [] |  |
| call-01993 | analytics_track | MemberExpression | [] | `event_key`, `total_steps`, `resuming` |
| call-01994 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `total_steps` |
| call-01995 | analytics_track | MemberExpression | [] | `event_key`, `step`, `step_index`, `total_steps` |
| call-02006 | analytics_track | missing | [] |  |
| call-02030 | analytics_track | Identifier | [] | `event_key` |
| call-02032 | analytics_track | missing | [] |  |
| call-02033 | analytics_track | missing | [] |  |
| call-02052 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `static_headers_enabled`, `prefilled`, `entry_point` |
| call-02053 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `step_id` |
| call-02054 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `error_kind` |
| call-02055 | analytics_track | MemberExpression | [] | `event_key`, `form_variant`, `static_headers_enabled`, `outcome`, `last_step_id`, `create_error_count`, `entry_point` |
| call-02056 | analytics_track | MemberExpression | [] | `event_key` |
| call-02057 | analytics_track | MemberExpression | [] | `event_key` |
| call-02058 | analytics_track | MemberExpression | [] | `event_key` |
| call-02080 | analytics_track | template_dynamic | ['claudeai.billing.stripe_elements.', ''] | `event_key` |
| call-02093 | analytics_track | missing | [] |  |
| call-02094 | analytics_track | Identifier | [] | `event_key`, `placement` |
| call-02101 | analytics_track | missing | [] |  |
| call-02150 | analytics_track | Identifier | [] | `event_key` |
| call-02160 | analytics_track | missing | [] |  |
| call-02179 | analytics_track | missing | [] |  |
| call-02186 | analytics_track | missing | [] |  |
| call-02191 | analytics_track | MemberExpression | [] | `event_key`, `status`, `submissions_mount` |
| call-02192 | analytics_track | MemberExpression | [] | `event_key`, `submissions_mount` |
| call-02241 | analytics_track | Identifier | [] | `event_key`, `banner_id` |
| call-02267 | analytics_track | missing | [] |  |
| call-02298 | analytics_track | missing | [] |  |
| call-02304 | analytics_track | missing | [] |  |
| call-02308 | analytics_track | template_dynamic | ['claudeai.admin_settings.requests_off_confirm.', ''] | `event_key`, `setting_label`, `blocked_count_shown`, `blocked_count` |
| call-02319 | analytics_track | missing | [] | `source`, `route`, `client_platform` |
| call-02353 | analytics_track | template_dynamic | ['claudeai.upgrade.', '_page_viewed'] | `event_key`, `referral_campaign`, `referral_source`, `entry_referral_source` |
| call-02383 | analytics_track | missing | [] |  |
| call-02452 | analytics_track | missing | [] |  |
| call-02453 | analytics_track | missing | [] |  |
| call-02459 | analytics_track | MemberExpression | [] | `event_key` |
| call-02466 | analytics_track | missing | [] |  |
| call-02467 | analytics_track | missing | [] |  |
| call-02488 | analytics_track | missing | [] |  |
| call-02490 | analytics_track | missing | [] | `panel_load_id`, `extension_version` |
| call-02531 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| call-02532 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| call-02533 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key` |
| call-02557 | health_outcome | Identifier | [] |  |
| call-02565 | analytics_track | Identifier | [] | `event_key` |
| call-02573 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| call-02574 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| call-02617 | analytics_track | missing | [] | `destination` |
| call-02618 | analytics_track | Identifier | [] | `event_key`, `session_type` |
| call-02624 | analytics_track | missing | [] | `destination` |
| call-02625 | analytics_track | missing | [] | `destination` |
| call-02626 | analytics_track | missing | [] |  |
| call-02627 | analytics_track | missing | [] | `destination` |
| call-02628 | analytics_track | Identifier | [] | `event_key`, `platform` |
| call-02640 | analytics_track | missing | [] |  |
| call-02641 | analytics_track | missing | [] |  |
| call-02651 | analytics_track | Identifier | [] | `event_key`, `phase`, `episode_id`, `page_kind`, `trigger`, `project_uuid`, `conversation_uuid`, `is_creator`, `open_age_s`, `outcome`, `decline_reason`, `resolve_ms` |
| call-02672 | analytics_track | missing | [] |  |
| call-02675 | analytics_track | missing | [] |  |
| call-02678 | analytics_track | missing | [] |  |
| call-02683 | analytics_track | missing | [] |  |
| call-02686 | analytics_track | missing | [] |  |
| call-02721 | analytics_track | missing | [] |  |
| call-02722 | analytics_track | missing | [] |  |
| call-02723 | analytics_track | missing | [] |  |
| call-02724 | analytics_track | missing | [] |  |
| call-02725 | analytics_track | missing | [] |  |
| call-02726 | analytics_track | missing | [] |  |
| call-02728 | analytics_track | missing | [] |  |
| call-02729 | analytics_track | missing | [] |  |
| call-02730 | analytics_track | missing | [] |  |
| call-02731 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `message_uuid`, `content_kind` |
| call-02732 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `new_chat` |
| call-02743 | analytics_track | missing | [] | `data`, `data.credits_explainer_arm`, `data.umber_lark_arm` |
| call-02744 | analytics_track | missing | [] |  |
| call-02745 | analytics_track | missing | [] |  |
| call-02746 | analytics_track | missing | [] |  |
| call-02747 | analytics_track | missing | [] |  |
| call-02752 | analytics_track | missing | [] |  |
| call-02753 | analytics_track | missing | [] |  |
| call-02757 | analytics_track | missing | [] | `client_platform` |
| call-02778 | health_outcome | Identifier | [] |  |
| call-02812 | health_outcome | MemberExpression | [] |  |
| call-02813 | health_outcome | MemberExpression | [] |  |
| call-02842 | analytics_track | Identifier | [] | `event_key`, `result` |
| call-02843 | analytics_track | Identifier | [] | `event_key`, `result`, `failure_reason` |
| call-02844 | analytics_track | Identifier | [] | `event_key` |
| call-02854 | analytics_track | missing | [] |  |
| call-02857 | analytics_track | Identifier | [] | `event_key`, `entry_surface`, `conversation_uuid`, `original_model`, `fallback_model` |
| call-02884 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key`, `variant` |
| call-02885 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key`, `variant` |
| call-02886 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key`, `variant` |
| call-02907 | analytics_track | missing | [] |  |
| call-02909 | analytics_track | template_dynamic | ['claudeai.', '.entitlement_suppressed'] | `event_key`, `model_id`, `reason` |
| call-02910 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key` |
| call-02911 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| call-02912 | analytics_track | template_dynamic | ['claudeai.', '.dismissed'] | `event_key` |
| call-02915 | analytics_track | missing | [] |  |
| call-02921 | analytics_track | template_dynamic | ['claudeai.', '.displayed'] | `event_key`, `update_available` |
| call-02922 | analytics_track | template_dynamic | ['claudeai.', '.cta_clicked'] | `event_key` |
| call-02940 | analytics_track | Identifier | [] | `event_key`, `sessionId`, `cliSessionId`, `type`, `thumbs`, `message`, `messageId`, `apiMessageIds`, `failedApiMessageIds`, `artifacts`, `hasPagesArtifact`, `artifactKind` |
| call-02942 | analytics_track | Identifier | [] | `event_key`, `conversation_uuid`, `original_model`, `fallback_model` |
| call-02945 | analytics_track | missing | [] |  |
| call-02946 | analytics_track | missing | [] |  |
| call-02947 | analytics_track | missing | [] |  |
| call-02961 | analytics_track | Identifier | [] | `event_key`, `renderer_surface`, `is_mobile_web` |
| call-03008 | analytics_track | template_dynamic | ['claudeai.cowork.cache_miss.warning_modal.', ''] | `event_key`, `session_id`, `session_type`, `from_model` |
| call-03013 | analytics_track | missing | [] |  |
| call-03014 | analytics_track | missing | [] |  |
| call-03015 | analytics_track | missing | [] |  |
| call-03092 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `has_title`, `has_cron`, `has_fire_at`, `has_notify_on_completion`, `mcp_tool`, `creator_session_id`, `creator_session_type`, `carry_row`, `saved_in_manual` |
| call-03093 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `updated_display_name`, `updated_prompt`, `updated_description`, `updated_cron`, `updated_fire_at`, `updated_enabled`, `updated_notify_on_completion`, `mcp_tool`, `creator_session_id`, `creator_session_type`, `notify_on_completion_after` |
| call-03094 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `mcp_tool`, `sessions_archived`, `creator_session_id`, `creator_session_type` |
| call-03473 | desktop_event | Identifier | [] |  |
| call-03474 | desktop_event | Identifier | [] |  |
| call-03650 | desktop_event | Identifier | [] | `active_process_count`, `vm_network_mode` |
| call-03740 | desktop_event | Identifier | [] |  |
| call-03783 | desktop_event | Identifier | [] |  |
| call-03812 | cowork_event | LogicalExpression | [] | `vm_instance_id`, `error_message` |
| call-03871 | desktop_event | Identifier | [] | `delta_ms` |
| call-03964 | desktop_event | template_dynamic | ['', '_scheduled_tasks_dispatch_skipped'] | `scheduled_task_id`, `reason`, `active_count`, `limit` |
| call-03966 | desktop_event | template_dynamic | ['', '_scheduled_tasks_run'] | `scheduled_task_id`, `on_ssh_host`, `trigger`, `mcp_tool`, `retry_attempt`, `jitter_seconds`, `disable_jitter`, `permission_mode`, `interval_minutes`, `missed_by_minutes` |
| call-03968 | desktop_event | template_dynamic | ['', '_scheduled_tasks_run'] | `scheduled_task_id`, `on_ssh_host`, `trigger`, `mcp_tool`, `retry_attempt`, `jitter_seconds`, `disable_jitter`, `permission_mode`, `interval_minutes`, `missed_by_minutes` |
| call-03969 | desktop_event | template_dynamic | ['', '_scheduled_tasks_dispatch_stale'] | `scheduled_task_id`, `pending_minutes`, `slot_consumed`, `interval_minutes` |
| call-03970 | desktop_event | template_dynamic | ['', '_scheduled_tasks_offline'] | `consecutive_ticks` |
| call-03971 | desktop_event | template_dynamic | ['', '_scheduled_tasks_not_ready'] | `consecutive_ticks` |
| call-04079 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `mcp_tool` |
| call-04080 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `mcp_tool` |
| call-04081 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `mcp_tool`, `sessions_archived`, `files_removed` |
| call-04082 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `on_ssh_host`, `has_cron`, `has_fire_at`, `mcp_tool`, `disable_jitter`, `jitter_seconds` |
| call-04083 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `updated_prompt`, `updated_description`, `updated_display_name`, `updated_cron`, `updated_fire_at`, `updated_enabled`, `updated_disable_jitter`, `updated_project_uuids`, `stamped_migrated_from_space`, `disable_jitter`, `jitter_seconds`, `mcp_tool` |
| call-04084 | desktop_event | MemberExpression | [] | `scheduled_task_id`, `mcp_tool` |
