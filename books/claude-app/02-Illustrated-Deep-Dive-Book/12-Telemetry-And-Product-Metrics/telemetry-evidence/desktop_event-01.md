# desktop_event 完整有界字典

[返回索引](README.md)

位置数是语法计数。字段并集不是必填 schema；`?` 表示至少一处条件加入，`~` 表示至少一处可能 undefined。所有值仍可能被未知 spread 或后置清理改变。这里的记录数包含已提取字段的条件 spread 与未解析形式；直接字面量对象展开会被内联，不计入此列。它不是未知字段集合数。源码位置与每处类型详见 index.json 的 sites/field_forms/shapes 分片。

| 名称 | 位置数 | 字段并集 | 已记录 spread 数 | 位置编号 |
|---|---:|---|---:|---|
| `builtin_m365_call` | 1 |  | 0 | call-03568 |
| `builtin_websearch_call` | 1 | `duration_ms`~, `http_status`?~, `provider`~, `query_length`~, `result_count`~, `status`~ | 1 | call-03808 |
| `ccd_simulator_access_toggle` | 1 | `device_platform`~, `enabled`~ | 0 | call-03137 |
| `ccd_simulator_annotate` | 1 | `device_platform`~, `success`~ | 0 | call-03127 |
| `ccd_simulator_approval_decision` | 1 | `action`~, `decision`~, `device_platform`~, `latency_ms`~, `session_id`~ | 0 | call-03132 |
| `ccd_simulator_attach` | 1 | `attach_reason`?~, `attachment_seq`?~, `cold_boot`~, `detected_by`?~, `device_platform`~, `duration_ms`~, `error_type`?~, `source`~, `success`~ | 4 | call-03115 |
| `ccd_simulator_capture_thumbnail_action` | 1 | `action`~, `device_platform`~, `remote`~, `success`~ | 0 | call-03113 |
| `ccd_simulator_consent_decision` | 1 | `decision`~, `device_platform`~, `duration_ms`~, `explainer_shown`?~, `origin`~ | 1 | call-03133 |
| `ccd_simulator_consent_waived` | 1 | `device_platform`~, `session_id`~ | 0 | call-03134 |
| `ccd_simulator_detach` | 1 | `attached_duration_ms`~, `attachment_seq`?~, `device_platform`~, `source`~, `timed_out_here`?~ | 5 | call-03117 |
| `ccd_simulator_device_action` | 1 | `action`~, `device_platform`~, `outcome`~ | 0 | call-03136 |
| `ccd_simulator_helper_end` | 1 | `app_stall`?~, `attached_devices`~, `first_timeout_op`?~, `helper_quiet_ms`?~, `helper_uptime_ms`~, `last_frame_age_ms`?~, `last_timeout_op`?~, `pending_requests`~, `xcode_change`?~ | 6 | call-03119 |
| `ccd_simulator_impression` | 1 | `device_platform`~, `opened_via`~, `promoted_by_ios_intent`?~ | 2 | call-03110 |
| `ccd_simulator_input_broken` | 1 | `dtuhidd_state`~, `helper_run`~ | 0 | call-03120 |
| `ccd_simulator_input_connect_failed` | 1 | `connect_error_kind`~, `connect_trigger`~, `helper_run`~ | 0 | call-03121 |
| `ccd_simulator_inspect` | 1 | `backend`~, `device_platform`~, `duration_ms`~, `query_kind`~, `success`~, `truncated`?~ | 1 | call-03128 |
| `ccd_simulator_manual_gesture` | 1 | `device_platform`~, `gesture_type`~, `origin`~ | 0 | call-03123 |
| `ccd_simulator_native_fold` | 1 | `arriving_frame_ms`?~, `confirm_requests`?~, `confirmed_screens`?~, `device_platform`, `direction`~, `duration_ms`?~, `end_reason`?~, `followed_hinge`?~, `ready_ms`?~, `refusal_reason`?~, `result`~, `settled`?~, `stage`?~, `turn_ms`?~ | 5 | call-03126 |
| `ccd_simulator_repin_decision` | 1 | `decision`~, `device_platform`, `duration_ms`~ | 0 | call-03135 |
| `ccd_simulator_screenshot` | 1 | `device_platform`~, `success`~, `trigger`~ | 0 | call-03124 |
| `ccd_simulator_session_summary` | 1 | `device_platform`~ | 1 | call-03118 |
| `ccd_simulator_setup_cta` | 1 | `cta`~, `device_platform`~ | 0 | call-03112 |
| `ccd_simulator_setup_probe_failed` | 1 | `device_platform`, `exit_code`?~, `failure`~, `probe`~, `xcode_on_disk`?~ | 2 | call-03114 |
| `ccd_simulator_setup_step` | 1 | `device_platform`~, `status`~, `step`~, `studio_installed`?~ | 1 | call-03111 |
| `ccd_simulator_shutdown` | 1 | `ccd_booted`~, `device_platform`~, `outcome`~, `trigger`~ | 0 | call-03130 |
| `ccd_simulator_stream_settings` | 1 | `device_platform`~, `fps`~, `scale`~ | 0 | call-03131 |
| `ccd_simulator_tool_call` | 1 | `action`~, `airplane_mode`?~, `device_id_kind`~, `device_platform`~, `device_specified`~, `duration_ms`~, `error_type`?~, `launch_timeout_stage`?~, `permission_mode`~, `point_count`?~, `session_id`~, `success`~, `text_length`?~, `url_scheme`?~ | 8 | call-03122 |
| `ccd_simulator_tool_load_timing` | 1 | `deferred_at_start`~, `device_platform`~, `from_project_scan`~, `gap_ms`~, `intent_before_initialized`~, `intent_saved_at_start`~, `session_id`~ | 0 | call-03125 |
| `ccd_simulator_video_recording` | 1 | `device_platform`~, `duration_ms`?~, `phase`~, `success`~, `trigger`?~ | 2 | call-03129 |
| `ccd_simulator_xcode_session` | 1 | `outcome`~, `start_tool`~ | 0 | call-03116 |
| `chrome_bridge_transport_selected` | 1 | `bridge_url_present`~, `is_nest_build`~, `platform`~, `transport`~ | 0 | call-03784 |
| `cic_proxy_stale_deny` | 1 | `ext_saw`~, `once_approved`~, `session_allowed`~ | 0 | call-03195 |
| `cowork_artifacts_auto_publish_failed` | 2 | `artifact_id`~, `error_class`~ | 0 | call-03975, call-03977 |
| `cowork_artifacts_auto_published` | 1 | `artifact_id`~, `shared_artifact_uuid`~ | 0 | call-03976 |
| `cowork_artifacts_bridge_call` | 1 | `duration_ms`~, `host_kind`~, `method`~, `outcome`~, `tool_name`?~ | 1 | call-03985 |
| `cowork_artifacts_created` | 1 | `artifact_id`~, `creator_session_id`?~, `html_size_bytes`~, `mcp_tool_count`~ | 1 | call-03973 |
| `cowork_artifacts_deleted` | 1 | `age_ms`~, `artifact_id`~, `files_removed`~ | 0 | call-03979 |
| `cowork_artifacts_imported` | 1 | `artifact_id`~, `html_size_bytes`~, `pending_mcp_tool_count`~, `shared_artifact_uuid`?~ | 1 | call-03980 |
| `cowork_artifacts_network_close_failed` | 1 | `arm`~, `surface`~ | 0 | call-03862 |
| `cowork_artifacts_screenshot` | 1 | `bytes`~, `height`~, `outcome`~, `target`~, `wait_ms`~, `width`~ | 0 | call-03575 |
| `cowork_artifacts_share_pulled` | 1 | `artifact_id`~, `html_size_bytes`~, `shared_artifact_uuid`~ | 0 | call-03983 |
| `cowork_artifacts_shared` | 1 | `artifact_id`~, `html_size_bytes`~, `is_reshare`~, `shared_artifact_uuid`~ | 0 | call-03981 |
| `cowork_artifacts_unshared` | 1 | `artifact_id`~, `shared_artifact_uuid`~ | 0 | call-03982 |
| `cowork_artifacts_updated` | 1 | `artifact_id`~, `html_size_bytes`~, `mcp_tool_count`~, `version_count`~ | 0 | call-03974 |
| `cowork_artifacts_verified` | 1 | `artifact_id`~, `log_entry_count`~ | 0 | call-03574 |
| `cowork_artifacts_version_restored` | 1 | `artifact_id`~, `version_age_ms`~ | 0 | call-03978 |
| `cowork_remote_attestation` | 1 | `attestation_form`~, `clock_offset_decision`~, `clock_offset_ms`~, `duration_ms`~, `hw_attestation`~, `hw_unavailable_reason`~, `outcome`~, `proof_kind`~, `row_pk_resolved`~, `sign_error_code`~, `sign_error_probe_code`~, `surface`~ | 1 | call-03920 |
| `cowork_scheduled_task_migration_reverted` | 1 | `days_since_migration`?~, `lane`?~, `outcome`~, `scheduled_task_id`~, `trigger_id`~ | 2 | call-03965 |
| `cowork_scheduled_tasks_inventory` | 1 | `blocked_chrome`~, `blocked_count`~, `blocked_custom_cron`~, `blocked_cwd`~, `blocked_dispatch_hook`~, `blocked_local_files_only`~, `blocked_local_folders`~, `blocked_no_prompt`~, `blocked_pattern_approvals`~, `blocked_projects`~, `blocked_projects_multi_or_malformed`~, `blocked_space`~, `blocked_sub_hourly`~, `cadence_daily`~, `cadence_hourly`~, `cadence_manual`~, `cadence_one_shot`~, `cadence_other`~, `cadence_sub_hourly`~, `cadence_weekdays`~, `cadence_weekly`~, `disabled_count`~, `disabled_migratable_count`~, `dispatch_origin_blocked_chrome`~, `dispatch_origin_blocked_count`~, `dispatch_origin_blocked_custom_cron`~, `dispatch_origin_blocked_cwd`~, `dispatch_origin_blocked_dispatch_hook`~, `dispatch_origin_blocked_local_folders`~, `dispatch_origin_blocked_no_prompt`~, `dispatch_origin_blocked_pattern_approvals`~, `dispatch_origin_blocked_projects`~, `dispatch_origin_blocked_space`~, `dispatch_origin_blocked_sub_hourly`~, `dispatch_origin_cadence_daily`~, `dispatch_origin_cadence_hourly`~, `dispatch_origin_cadence_manual`~, `dispatch_origin_cadence_one_shot`~, `dispatch_origin_cadence_other`~, `dispatch_origin_cadence_sub_hourly`~, `dispatch_origin_cadence_weekdays`~, `dispatch_origin_cadence_weekly`~, `dispatch_origin_count`~, `dispatch_origin_last_run_age_bucket`~, `dispatch_origin_migratable_count`~, `dispatch_origin_unreadable_count`~, `emit_reason`~, `enabled_count`~, `migratable_count`~, `observed_built_in_browser`~, `observed_chrome`~, `observed_computer_use`~, `observed_device_free_count`~, `observed_local_mcp`~, `observed_request_folder_access`~, `observed_task_count`~, `origin_notify_none_count`~, `origin_unresolvable_count`~, `remote_scheduled_tasks_enabled`~, `routines_enabled`~, `space_empty`~, `space_folders_0`~, `space_folders_1`~, `space_folders_2_plus`~, `space_tied_enabled_count`~, `space_unresolvable`~, `space_with_drive_links`~, `space_with_instructions`~, `space_with_links`~, `space_with_projects`~, `task_count`~, `total_observed_runs`~, `unreadable_count`~ | 0 | call-03967 |
| `cowork_skill_saved` | 1 | `created`~, `session_id`~, `skill_name`~, `skill_name_hash`~ | 0 | call-03572 |
| `cowork_space_migration_outcome` | 1 | `attempts`~, `dry_run`~, `memory_copy_error`~, `memory_copy_keyless`~, `memory_copy_state`~, `memory_files_copied`~, `memory_files_total`~, `outcome`~, `reason`~, `space_id`~, `stage`~, `task_wait_seconds`~, `tasks_already_remote`~, `tasks_failed`~, `tasks_remote`~, `tasks_repointed`~, `tasks_total`~, `wave`~ | 0 | call-04087 |
| `cu_app_dispatch` | 1 | `app_category`~, `ax_op`~, `front_check_scheduled`~, `intent`~, `is_system_app`~, `outcome`~, `path`~, `reason_code`~, `role`~, `session_id`~, `session_type`~, `subrole`~ | 0 | call-03049 |
| `cu_app_front_check_held_back` | 1 |  | 0 | call-03804 |
| `cu_app_helper_crash` | 1 | `exit_code`~, `last_method`~, `restart_count`~, `signal`~, `uptime_ms`~ | 0 | call-03806 |
| `cu_app_helper_probe` | 1 | `auth_envelope`~, `ax_get_window`~, `ax_trusted`~, `focus_without_raise`~, `skylight`~, `skylight_verified`~ | 0 | call-03805 |
| `cu_app_target_took_front` | 1 | `cursor_in_prior_app`~, `cursor_in_target`~, `front_after_restore`~, `had_click_since_action`~, `is_first_for_action`~, `press_to_activation_ms`~, `release_to_activation_ms`~ | 1 | call-03803 |
| `cu_lock_acquired` | 1 | `is_hub_chat`~, `session_id`~, `session_type` | 0 | call-03191 |
| `cu_lock_released` | 1 | `held_duration_ms`~, `is_hub_chat`~, `release_trigger`~, `session_id`~, `session_type`, `was_teach_mode`~ | 0 | call-03190 |
| `cu_session_config` | 2 | `chicago_enabled`~, `is_hub_chat`~, `session_id`~, `session_type`~ | 2 | call-03050, call-03192 |
| `cu_setting_changed` | 1 | `new_value`~, `previous_value`~, `setting`~ | 0 | call-04140 |
| `cu_takeover_approved` | 1 | `session_id`~, `via`~ | 0 | call-03781 |
| `cu_tool_call` | 4 | `coordinate_mode`~, `denied_browser_count`~, `denied_count`~, `denied_terminal_count`~, `duration_ms`~, `error_detail`~, `error_kind`~, `granted_count`~, `is_error`~, `is_hub_chat`~, `is_teach_mode`~, `lock_released`~, `session_id`~, `session_type`~, `tool_name`~, `user_message_uuid`~ | 4 | call-03051, call-03052, call-03053, call-03194 |
| `cu_watch_record_choice` | 1 | `choice`~, `purpose`~, `resumed`~ | 1 | call-04102 |
| `cu_watch_record_chooser_shown` | 1 |  | 1 | call-04101 |
| `cu_watch_record_ended` | 8 | `duration_ms`~, `event_count`~, `exit_trigger`~, `image_count`~, `output_mode`~, `purpose`~ | 8 | call-04100, call-04106, call-04108, call-04109, call-04110, call-04111, call-04113, call-04115 |
| `cu_watch_record_held_dropped` | 3 | `held`, `image_count`~, `purpose`, `reason`?~ | 4 | call-04096, call-04112, call-04114 |
| `cu_watch_record_narration_failed` | 1 | `at_ms`~ | 1 | call-04097 |
| `cu_watch_record_permission_blocked` | 5 | `check`~, `flow` | 5 | call-04095, call-04098, call-04099, call-04103, call-04104 |
| `cu_watch_record_pill_hold_timeout` | 1 |  | 1 | call-04107 |
| `cu_watch_record_started` | 1 | `output_mode`~, `purpose`~ | 1 | call-04105 |
| `custom3p_config_relaunch_auto_restart` | 1 | `enforcement_hours`~, `pending_hours`~ | 0 | call-03644 |
| `custom3p_config_relaunch_enforced` | 1 | `enforcement_hours`~, `pending_hours`~ | 0 | call-03643 |
| `custom3p_idp_silent_reauthorize` | 1 | `bearer_token_type`~, `deployment_kind`, `outcome`~ | 0 | call-03184 |
| `desktop_accessibility_support_changed` | 1 | `accessibility_features`~, `enabled`~ | 0 | call-03657 |
| `desktop_artifact_popup_gate` | 1 | `dropped_since_last`~ | 1 | call-03679 |
| `desktop_browser_env_bridge_open` | 1 | `outcome`~ | 0 | call-03594 |
| `desktop_ccd_activity_context` | 1 | `chars`~, `held_back`~, `lane`~, `lines`~, `session_id`~ | 1 | call-03471 |
| `desktop_ccd_agent_remote_control` | 5 | `enabled`~, `outcome`~, `reason`~, `session_id`~, `target`~ | 0 | call-03062, call-03063, call-03064, call-03065, call-03066 |
| `desktop_ccd_archive_session_auto_mode` | 1 | `outcome`~, `session_id`~, `target`~ | 0 | call-03292 |
| `desktop_ccd_artifact_publish_preview` | 1 | `session_id`~, `source_was_previewed`~, `tabs_closed`~ | 0 | call-03938 |
| `desktop_ccd_artifacts_reset` | 1 | `after_clear_or_rewind`~, `frames_after`~, `frames_before`~, `messages_after`~, `messages_before`~, `session_id`~, `session_scope`~, `trigger`~ | 0 | call-03684 |
| `desktop_ccd_aside` | 1 | `backend_kind`~, `cancel_reason`?~, `history_shim`~, `latency_ms`~, `message_uuid`~, `outcome`~, `prior_asides`~, `reply_chars`~, `session_id`~, `tool_running_at_send`~ | 1 | call-03349 |
| `desktop_ccd_attention_mislabel` | 1 | `backend_kind`~, `is_ssh`~, `renderer_surface`~, `session_id`~ | 1 | call-03274 |
| `desktop_ccd_auth_error_result` | 1 | `backend_kind`~, `bearer_state`~, `cli_session_id`~, `ended_turn`?~, `session_age_ms`~, `session_id`~, `signal`~ | 1 | call-03550 |
| `desktop_ccd_auto_archive` | 3 | `held_ms`?~, `hold_reason`~, `kicked`~, `losable_kind`?~, `outcome`, `pr_state`?~, `rule`~, `session_id`~, `tasks_stopped`~, `untracked_discard_requested`?~, `worktree_cleanup_requested`~, `worktree_kept_dirty`~ | 4 | call-03141, call-03142, call-03143 |
| `desktop_ccd_auto_update_check` | 1 | `from_version`~, `gate_reason`~, `result`~, `spread_hours`~, `target_from_flag`~, `to_version`~ | 0 | call-03799 |
| `desktop_ccd_autofix_own_pr_arm` | 1 | `change_key`~, `outcome`~, `session_id`~ | 0 | call-03354 |
| `desktop_ccd_autofix_settled` | 1 | `auto_merge_seen`~, `change_key`~, `check_count`~, `clean_read_banked`~, `episode_ms`~, `episode_outcome`~, `first_wake_message_uuid`~, `head_changed_since_first_wake`~, `heads_in_episode`~, `last_read_verdict`~, `ms_since_last_read`~, `session_id`~, `text_variant`~, `wakes_in_episode`~ | 0 | call-03176 |
| `desktop_ccd_background_task_killed_by_teardown` | 1 | `session_id`~, `settle_reason`~, `task_type`~ | 0 | call-03492 |
| `desktop_ccd_background_task_resolved` | 1 | `age_ms`~, `dismissed_by_model`?~, `expired`?~, `launched`~, `remaining`~, `session_id`~, `started_by_model`?~, `was_cross_repo`~ | 4 | call-03411 |
| `desktop_ccd_background_task_suggested` | 1 | `evicted_count`~, `has_target_cwd`~, `offer`?~, `proposal`?~, `proposed_context`~, `queue_length`~, `session_id`~ | 2 | call-03389 |
| `desktop_ccd_base_branch_merge` | 2 | `conflicted_count`~, `fast_forward`~, `ms`~, `outcome`~, `protected_taken_count`~, `reason`~, `session_id`~, `trigger`~ | 0 | call-03405, call-03547 |
| `desktop_ccd_base_fast_forward` | 17 | `ms`~, `outcome`~, `reason`~ | 0 | call-03158, call-03159, call-03160, call-03161, call-03162, call-03163, call-03164, call-03165, call-03166, call-03167, call-03168, call-03169, call-03170, call-03171, call-03172, call-03173, call-03174 |
| `desktop_ccd_bash_foreground_active` | 1 | `uninterruptible`~ | 0 | call-03589 |
| `desktop_ccd_bash_interrupt` | 1 |  | 0 | call-03583 |
| `desktop_ccd_bash_shell_reset` | 1 |  | 0 | call-03588 |
| `desktop_ccd_bash_stale_interrupted` | 4 | `cleared_by`~ | 0 | call-03584, call-03585, call-03586, call-03587 |
| `desktop_ccd_below_boundary_symlink_refused` | 1 |  | 0 | call-03651 |
| `desktop_ccd_binary_cache_invalid` | 4 | `detail`~, `platform`~, `reason`~, `version`~ | 0 | call-03791, call-03792, call-03793, call-03798 |
| `desktop_ccd_binary_prepare_failed` | 1 | `attempt`~, `background`?~, `error_code`~, `final`~, `kind`~, `step`~, `target`~, `version`~ | 1 | call-03794 |
| `desktop_ccd_binary_resolved` | 7 | `awaited_ms`~, `awaited_outcome`~, `awaited_reason`~, `required_version`~, `resolution`~, `resolved_version`~ | 0 | call-03360, call-03361, call-03362, call-03363, call-03795, call-03796, call-03797 |
| `desktop_ccd_browser_navigated` | 1 | `is_localhost`~, `session_id`~, `session_type`~, `via`~ | 0 | call-03870 |
| `desktop_ccd_btw_child_close` | 1 | `already_archived`~, `archived`~, `completed_turns`~, `parent_session_id`~, `session_id`~, `working`~ | 1 | call-03187 |
| `desktop_ccd_btw_child_open` | 1 | `fork_ms`~, `opened_by`~, `outcome`~, `parent_session_id`~, `refusal_reason`?~, `session_id`?~ | 2 | call-03186 |
| `desktop_ccd_btw_child_shown` | 1 | `already_archived`~, `parent_session_id`~, `session_id`~ | 1 | call-03188 |
| `desktop_ccd_change_cwd` | 2 | `new_cwd`~, `previous_cwd`~, `record_synced`~, `scratch_offer_folder`~, `session_id`~, `transcript_relocated`~, `unstarted`~ | 0 | call-03454, call-03456 |
| `desktop_ccd_chip_level_change_failed` | 1 | `backend_kind`~, `error_message`~, `from_level`~, `requested_level`~, `session_id`~ | 0 | call-03396 |
| `desktop_ccd_chip_level_changed` | 2 | `backend_kind`~, `from_level`~, `permission_mode`~, `session_id`~, `source`~, `to_level`~ | 0 | call-03395, call-03556 |
| `desktop_ccd_chrome_import` | 8 | `browser`~, `cookies`~, `failed`~, `failure`~, `persist_enabled`~, `session_id`~, `session_type`~, `sites`~, `stage`~, `storage_budget_hit`~, `storage_carried`~, `storage_concurrency`~, `storage_failed`~, `storage_keys`~, `storage_ms`~, `storage_origins`~, `storage_pending`~, `storage_timeouts`~ | 4 | call-03027, call-03028, call-03029, call-03030, call-03031, call-03032, call-03033, call-03034 |
| `desktop_ccd_cli_install` | 1 |  | 0 | call-04130 |
| `desktop_ccd_cli_install_failed` | 6 | `reason` | 0 | call-04126, call-04127, call-04128, call-04129, call-04131, call-04132 |
| `desktop_ccd_cli_outdated_refusal` | 1 | `backend_kind`~, `cli_version`~, `decision`~, `reason`~, `refusal`~, `resolved_version`~, `session_id`~, `site` | 0 | call-03357 |
| `desktop_ccd_cli_resume_refused` | 1 | `reason`~ | 0 | call-03557 |
| `desktop_ccd_cli_session_imported` | 1 | `import_source`~, `is_large_import`~, `session_id`~, `transcript_line_count`~, `transcript_size_bytes`~ | 0 | call-03559 |
| `desktop_ccd_cli_started_turn_result` | 1 | `backend_kind`~, `cache_creation_1h_input_tokens`?~, `cache_creation_5m_input_tokens`?~, `cache_creation_input_tokens`?~, `cache_read_input_tokens`?~, `cli_session_id`~, `had_pending_cycle`~, `input_tokens`?~, `model`~, `output_tokens`?~, `session_id`~, `turn_origin`~ | 6 | call-03444 |
| `desktop_ccd_cli_teardown_outcome` | 1 |  | 2 | call-03493 |
| `desktop_ccd_cli_uninstall` | 1 |  | 0 | call-04136 |
| `desktop_ccd_cli_uninstall_failed` | 5 | `reason` | 0 | call-04133, call-04134, call-04135, call-04137, call-04138 |
| `desktop_ccd_composer_inp` | 1 | `active_session_count`~, `draft_len`~, `in_popout`~, `inp_ms`~, `input_delay_ms`~, `interaction_type`~, `key_class`~, `loaf_entry_count`~, `loaf_script_char_pos`~, `loaf_script_duration_ms`~, `loaf_script_forced_layout_ms`~, `loaf_script_function`~, `loaf_script_invoker`~, `loaf_script_invoker_type`~, `loaf_script_source`~, `loaf_total_blocking_ms`~, `loaf_total_forced_layout_ms`~, `low_memory_posture`~, `message_count`~, `presentation_delay_ms`~, `processing_ms`~, `renderer_surface`~, `running_session_count`~, `session_id`~, `was_submit`~ | 2 | call-03402 |
| `desktop_ccd_connector_switch_auto_mode` | 1 | `enabled`~, `outcome`~, `session_id`~ | 0 | call-03289 |
| `desktop_ccd_context_auto_compact` | 1 | `attempt_number`~, `backend_kind`~, `compact_error`~, `continuation`~, `continue_message_uuid`~, `duration_ms`~, `outcome`~, `session_id`~, `slept`~, `trigger`~, `user_message_uuid`~ | 0 | call-03446 |
| `desktop_ccd_context_exceeded` | 1 | `active_mcp_server_count`~, `attempt_number`~, `auto_compact`~, `auto_compact_attempts`~, `backend_kind`~, `cli_session_id`~, `enabled_mcp_tool_count`~, `had_pending_cycle`~, `image_count_in_buffer`~, `is_repeat`~, `is_resume`~, `is_ssh`~, `message_buffer_size`~, `model`~, `session_id`~, `transcript_size_bytes`~, `turns_before_ptl`~, `user_message_uuid`~ | 0 | call-03445 |
| `desktop_ccd_context_recovered` | 1 | `attempts_before_recovery`~, `auto_compact_attempts`~, `auto_compact_recovered`~, `session_id`~ | 0 | call-03549 |
| `desktop_ccd_delegated_ask_allowed` | 1 | `delegated_tool`~, `session_id`~ | 0 | call-03317 |
| `desktop_ccd_env_vars_read_failed` | 1 | `reason`~, `scoped`~ | 0 | call-04086 |
| `desktop_ccd_folder_worktrees` | 1 | `created`~, `dropped_untrusted`~, `failed`~, `has_worktree`~, `in_place`~, `is_remote`?~, `requested`~, `session_id`~, `shared`~ | 1 | call-03460 |
| `desktop_ccd_fork_timing` | 1 | `fresh_start`~, `per_message`~, `pool_ms`~, `pool_outcome`~, `pool_wait_ms`~, `prep_ms`~, `session_id`~, `total_ms`~, `transcript_bytes`~, `transcript_ms`~, `worktree`~, `worktree_ms`~, `wt_add_ms`~, `wt_fetch_outcome`~, `wt_prep_ms`~ | 0 | call-03373 |
| `desktop_ccd_github_pr_checks_summary` | 1 | `graphql_read_by_caller`~, `ratelimit_remaining`~, `ratelimit_used`~, `rest_304_by_endpoint`~, `rest_ratelimit_remaining`~, `rest_ratelimit_used`~, `rest_read_by_endpoint`~, `window_ms`~ | 1 | call-03351 |
| `desktop_ccd_github_rate_limited` | 1 | `held`~, `kind`~, `path`~, `ratelimit_remaining`~, `ratelimit_reset_seconds`~, `ratelimit_used`~, `suppressed_count`~ | 0 | call-03350 |
| `desktop_ccd_governor_throttled` | 1 | `bypassed`?~, `deferred_for_ms`?~, `level`, `source`, `total_mem_gb`~, `trigger`~ | 1 | call-03481 |
| `desktop_ccd_hardlinked_file_read` | 1 |  | 0 | call-03652 |
| `desktop_ccd_helper_fork_empty_text` | 2 | `kind`~, `session_id`~ | 0 | call-03468, call-03470 |
| `desktop_ccd_helper_fork_usage` | 1 | `aborted`~, `cache_creation_1h_input_tokens`~, `cache_creation_5m_input_tokens`~, `cache_creation_input_tokens`~, `cache_read_input_tokens`~, `delivered`~, `input_tokens`~, `kind`~, `output_tokens`~, `session_id`~, `transcript_size_bytes`~ | 0 | call-03463 |
| `desktop_ccd_host_handoff` | 1 | `handoff_tool`~, `outcome`~, `remote`~, `session_id`~ | 0 | call-03061 |
| `desktop_ccd_host_keep_awake` | 5 | `action`~, `held_ms`~, `release_reason`~, `session_id`~, `until`~ | 0 | call-03055, call-03056, call-03057, call-03058, call-03059 |
| `desktop_ccd_host_storage` | 1 | `outcome`~, `session_id`~, `storage_tool`~ | 1 | call-03060 |
| `desktop_ccd_hotpath_cwd_gone_detected` | 3 | `backend_kind`~, `can_recover`~, `cwd`~, `had_live_query`~, `is_worktree`~, `probe_ms`~, `session_id`~, `trigger` | 0 | call-03508, call-03509, call-03530 |
| `desktop_ccd_inline_pastes` | 1 | `backend_kind`~, `renderer_surface`~, `session_id`~ | 1 | call-03377 |
| `desktop_ccd_interrupt_no_query` | 1 | `backend_kind`~, `has_input_stream`~, `is_running`~, `session_exists`~, `session_id`~, `start_in_flight`~ | 0 | call-03514 |
| `desktop_ccd_keep_awake_held` | 1 | `on_battery`~, `reason`~, `session_count`~ | 0 | call-03728 |
| `desktop_ccd_keep_awake_manual_held` | 1 | `on_battery`~, `while_working_held`~ | 0 | call-03730 |
| `desktop_ccd_keep_awake_manual_released` | 1 | `held_ms`~, `keep_awake_release`~, `on_battery`~ | 0 | call-03731 |
| `desktop_ccd_keep_awake_released` | 1 | `held_ms`~, `keep_awake_release`~, `max_session_count`~, `max_system_idle_ms`~, `notice_requested`~, `on_battery`~ | 0 | call-03729 |
| `desktop_ccd_lazy_worktree_provided` | 4 | `error_kind`~, `git_isolation_errno`?~, `git_isolation_stage`?~, `prepare_ms`?~, `session_id`~, `wait_ms`~, `worktree_refusal`~, `worktree_source`~ | 4 | call-03285, call-03286, call-03287, call-03288 |
| `desktop_ccd_local_policy_unreadable` | 1 | `cause`~ | 0 | call-03807 |
| `desktop_ccd_logs_handoff_outcome` | 5 | `outcome`~ | 0 | call-03913, call-03914, call-03915, call-03916, call-03917 |
| `desktop_ccd_mcp_internal_name_claimed` | 1 | `internal_server_name`~, `session_id`~, `source`~ | 0 | call-03545 |
| `desktop_ccd_mcp_own_server_handshake_failed` | 1 | `internal_server_name`~, `session_id`~ | 0 | call-03544 |
| `desktop_ccd_message_cycle_outcome` | 1 | `app_quit_trigger`?~, `assistant_narration_block_count`?~, `assistant_narration_char_count`?~, `assistant_text_block_count`?~, `assistant_text_char_count`?~, `assistant_tool_group_count`?~, `assistant_tool_use_count`?~, `backend_kind`~, `cache_creation_input_tokens`?~, `cache_read_input_tokens`?~, `cli_binary_choice`?~, `cli_session_id`~, `cli_stderr_tail`?~, `cli_version`?~, `closing_message_char_count`?~, `cycle_health`~, `error_category`?~, `error_message`?~, `first_turn_since_spawn`?~, `had_first_response`~, `http_status`?~, `init_arrived`?~, `input_origin`~, `input_tokens`?~, `is_first_turn`~, `is_resume`?~, `is_ssh`~, `model`~, `ms_to_first_token`?~, `no_response_category`?~, `output_tokens`?~, `permission_mode`~, `plan_call_count`?~, `plan_call_count_since_compaction`?~, `plan_open_step_count`?~, `prompt_append_source`?~, `prompt_lifecycle`?~, `renderer_surface`~, `result_subtype`?~, `resume_reason`?~, `resume_stop_trigger`?~, `rewind_target_miss_reason`?~, `scheduled_task_id`?~, `seconds_to_outcome`~, `session_id`~, `session_presets`?~, `side_sessions_available`~, `spawn_source`?~, `spawn_to_init_ms`?~, `spawn_to_outcome_ms`?~, `start_stage_reached`?~, `steered_send_count`?~, `system_prompt_snapshot`?~, `tool_calls`?~, `tool_use_count_since_plan_call`?~, `transcript_size_bytes`?~, `turn_box_mounted`~, `unhealthy_reason`?~, `user_message_uuid`~ | 38 | call-03277 |
| `desktop_ccd_message_cycle_start` | 1 | `backend_kind`~, `cli_session_id`~, `input_origin`~, `is_ssh`~, `remote_cwd_probe_ms`?~, `renderer_surface`~, `session_id`~, `user_message_uuid`~ | 2 | call-03276 |
| `desktop_ccd_midturn_send` | 7 | `at_turn_boundary`?~, `auto_reason`?~, `backend_kind`~, `ccd_steering`~, `initiator`~, `input_origin`~, `is_ssh`~, `message_uuid`~, `mode`~, `queued_message_bar`~, `renderer_surface`~, `session_id`~, `tool_running_at_send`~, `window_parked`~ | 10 | call-03384, call-03385, call-03386, call-03510, call-03511, call-03512, call-03513 |
| `desktop_ccd_model_change_failed` | 1 | `backend_kind`~, `cli_version`~, `error_message`~, `model`~, `path`~, `reason`~, `recorded`~, `rejected_model`~, `restored`~, `session_id`~, `superseded`~ | 0 | call-03414 |
| `desktop_ccd_model_selection_fallback` | 1 | `reason`~, `rejected_model`~, `session_id`~, `source`~ | 0 | call-04085 |
| `desktop_ccd_move_to_cloud` | 1 | `duration_ms`~, `environment_source`~, `environments`?~, `git`?~, `outcome`~, `reason`?~, `session_id`~, `skip_push`~ | 2 | call-03570 |
| `desktop_ccd_move_to_cloud_auto_mode` | 1 | `outcome`~, `session_id`~ | 0 | call-03296 |
| `desktop_ccd_oauth_refresh_declined` | 1 | `backend_kind`~, `elapsed_ms`~, `failure_type`~, `fence_detail`~, `reason`~, `session_id`~, `source`~, `status`~, `suppressed_count`~ | 0 | call-03364 |
| `desktop_ccd_oauth_token_renewal` | 4 | `failure_type`~, `live_sessions`~, `outcome`~, `sessions_pushed`~, `trigger`~ | 0 | call-03365, call-03366, call-03367, call-03368 |
| `desktop_ccd_path_floor_homebrew_added` | 1 | `addedDirs`~ | 0 | call-03841 |
| `desktop_ccd_peer_send_undelivered` | 2 | `backend_kind`~, `is_ssh`~, `ms_since_write`~, `owned_cycle`~, `session_id`~, `stage` | 0 | call-03372, call-03515 |
| `desktop_ccd_permission_auto_allowed` | 2 | `permission_mode`~, `reason`~, `session_id`~, `tool_name`~ | 0 | call-03300, call-03307 |
| `desktop_ccd_permission_auto_denied` | 39 | `reason`~, `session_id`~, `tool_name`~ | 0 | call-03091, call-03273, call-03299, call-03303, call-03304, call-03305, call-03306, call-03308, call-03309, call-03310, call-03311, call-03312, call-03313, call-03314, call-03315, call-03316, call-03318, call-03320, call-03321, call-03322, call-03324, call-03325, call-03326, call-03327, call-03328, call-03329, call-03330, call-03331, call-03332, call-03333, call-03334, call-03335, call-03336, call-03337, call-03338, call-03339, call-03341, call-03342, call-03344 |
| `desktop_ccd_permission_decisionreason_cache_hit` | 1 | `session_id`~, `tool_name`~ | 0 | call-03340 |
| `desktop_ccd_permission_mode_change_failed` | 1 | `backend_kind`~, `error_message`~, `from_mode`~, `model`~, `requested_mode`~, `session_id`~ | 0 | call-03393 |
| `desktop_ccd_permission_mode_changed` | 6 | `backend_kind`~, `cli_informed`~, `from_mode`~, `session_id`~, `source`~, `to_mode`~ | 0 | call-03390, call-03391, call-03392, call-03394, call-03397, call-03555 |
| `desktop_ccd_pr_auto_merge_auto_mode` | 1 | `enabled`~, `outcome`~, `session_id`~ | 0 | call-03294 |
| `desktop_ccd_pr_bar_bind` | 1 | `ahead_of_read`~, `change_key`~, `created`~, `error_kind`~, `outcome`~, `provider`~, `session_id`~, `source`~ | 0 | call-03353 |
| `desktop_ccd_pr_bar_confirm` | 1 | `change_key`~, `outcome`~, `provider`~, `session_id`~ | 0 | call-03352 |
| `desktop_ccd_pr_bar_dismiss` | 1 | `change_key`~, `live_bindings`~, `provider`~, `session_id`~, `source`~, `state`~ | 0 | call-03355 |
| `desktop_ccd_pr_bind_auto_mode` | 1 | `outcome`~, `session_id`~ | 0 | call-03295 |
| `desktop_ccd_pr_mcp_call` | 1 | `auto_archive_on_close`~, `auto_fix`~, `auto_merge`~, `bind_outcome`~, `outcome`~, `pr_tool`~, `session_id`~, `target`~ | 0 | call-03067 |
| `desktop_ccd_preview_idle_teardown` | 1 | `outcome`~, `session_id`~ | 0 | call-03475 |
| `desktop_ccd_proxy_unreachable` | 1 | `proxy_key`~, `session_id`~, `settings_tier`~ | 0 | call-03552 |
| `desktop_ccd_quit_auto_resume` | 1 | `interrupted_age_seconds`~, `outcome`~, `renderer_surface`~, `session_id`~, `trigger`~ | 1 | call-03479 |
| `desktop_ccd_quit_auto_resume_launch_pass` | 1 | `left_awaiting_person_count`~, `marked_count`~, `outcome`~, `planned_count`~, `warmed_count`~ | 0 | call-03482 |
| `desktop_ccd_rc_serve_register` | 1 | `attempts`~, `duration_ms`~, `error_class`~, `folder_hash`~, `outcome`, `target`~, `trigger`~ | 0 | call-03602 |
| `desktop_ccd_rc_serve_session_end` | 1 | `duration_bucket`~, `end_reason`~, `local_session_id`~, `session_id`~, `target`~, `turns_bucket`~, `unarchive`~ | 0 | call-03604 |
| `desktop_ccd_rc_serve_stall` | 1 | `cleared_by`~, `heartbeats`~, `quiet_bucket`~, `session_id`~, `target`~, `tool`?~, `tool_builtin`?~, `waiting_in`~ | 2 | call-03605 |
| `desktop_ccd_rc_serve_state` | 1 | `folders_excluded`~, `folders_limited`~, `folders_missing`~, `folders_served`~, `intent`~, `last_error_code`?~, `prev_reason`~, `reason`~, `reason_detail`?~, `trigger`~ | 2 | call-03612 |
| `desktop_ccd_rc_serve_summary` | 1 |  | 0 | call-03614 |
| `desktop_ccd_rc_serve_ui` | 24 | `action`~, `folder_count`~, `folder_reason`?~, `refusal`~, `spawn_mode`~ | 2 | call-03595, call-03596, call-03597, call-03598, call-03599, call-03600, call-03601, call-03608, call-03609, call-03610, call-03611, call-03613, call-04067, call-04068, call-04069, call-04070, call-04071, call-04072, call-04073, call-04074, call-04075, call-04076, call-04077, call-04078 |
| `desktop_ccd_rc_serve_work` | 1 | `environment_id`~, `folder_hash`~, `intent`~, `session_id`~, `target`~ | 1 | call-03603 |
| `desktop_ccd_rc_toolhost_end` | 1 | `duration_bucket`~, `folder_hash`~, `reason`~ | 0 | call-03606 |
| `desktop_ccd_rc_toolhost_work` | 1 | `action`~, `capacity`~, `folder_hash`~, `leases`~, `reason`?~, `tool_host_sessions`~ | 1 | call-03607 |
| `desktop_ccd_recap_capped` | 1 | `recap_chars_raw`~, `session_id`~ | 0 | call-03469 |
| `desktop_ccd_recap_generated` | 1 | `recap_chars`~, `session_id`~, `trigger`~ | 0 | call-03449 |
| `desktop_ccd_recap_started` | 1 | `session_id`~, `trigger`~ | 0 | call-03448 |
| `desktop_ccd_remote_attachment_write` | 1 | `bailed`~, `connection_failed`~, `dropped_overcap`~, `dropped_oversized`~, `dropped_unreadable`~, `duration_ms`~, `failed_writes`~, `requested`~, `session_id`~, `written`~ | 0 | call-03189 |
| `desktop_ccd_remote_control_auto_enable` | 1 | `backend_kind`~, `duration_ms`~, `error_message`?~, `outcome`~, `route`~, `session_id`~, `suppressed_count`~, `trigger`~, `verdict`~, `verdict_detail`~, `verdict_source`~, `will_retry`~ | 1 | call-03399 |
| `desktop_ccd_remote_control_bridge_failed` | 1 | `auto_enabled`~, `auto_source`~, `backend_kind`~, `error_message`?~, `last_oauth_decline_reason`~, `seconds_since_last_activity`~, `seconds_since_last_oauth_decline`~, `session_id`~ | 1 | call-03400 |
| `desktop_ccd_remote_control_update_restore` | 1 | `same_session`~, `session_id`~ | 0 | call-03484 |
| `desktop_ccd_remote_control_update_restore_pass` | 1 |  | 0 | call-03483 |
| `desktop_ccd_remote_managed_settings_fetch` | 1 | `duration_ms`~, `http_status`~, `key_count`~, `organization_id`~, `outcome`~ | 0 | call-03571 |
| `desktop_ccd_remote_restart_auto_resume` | 1 | `backend_kind`~, `interrupted_age_seconds`~, `outcome`~, `session_id`~, `trigger`~ | 1 | call-03480 |
| `desktop_ccd_repository_review` | 1 | `initiator`~, `kind`~, `session_id`~, `site`~ | 1 | call-03252 |
| `desktop_ccd_resume_bring_home_timing` | 1 | `cli_session_id`~, `copy_ms`~, `outcome`~, `resolve_ms`~, `scan_ms`~, `session_id`~, `stat_ms`~, `timed_out_phase`~, `total_ms`~ | 0 | call-03498 |
| `desktop_ccd_run_follow_up` | 1 | `active_session_count`~, `has_local_disk`~, `outcome`~, `probed`~, `renderer_surface`~, `running_session_count`~, `session_id`~ | 0 | call-03404 |
| `desktop_ccd_scheduled_task_tool_auto_mode` | 1 | `outcome`~, `scheduled_task_tool`~, `session_id`~ | 0 | call-03298 |
| `desktop_ccd_scheduled_tasks_permission_auto_approved` | 1 | `scheduled_task_id`~, `tool_name`~ | 0 | call-03343 |
| `desktop_ccd_scheduled_tasks_permission_stall_released` | 1 | `denied_count`~, `scheduled_task_id`~, `seconds_since_activity`~, `session_id`~, `turn_interrupted`~, `unattended`~ | 0 | call-03477 |
| `desktop_ccd_scheduled_tasks_run_completed` | 2 | `duration_seconds`~, `live_cli_count`~, `live_scheduled_cli_count`~, `num_turns`~, `scheduled_task_id`~, `session_id`~, `status`~ | 0 | call-03485, call-03548 |
| `desktop_ccd_scratch_files_carried` | 1 | `already_there`~, `claude_settings`~, `copied`~, `dependency_folders`~, `duration_ms`~, `held_back`~, `not_copied`~, `outcome`~, `session_id`~ | 0 | call-03455 |
| `desktop_ccd_send_swallowed` | 1 | `recovered`~, `session_id`~ | 0 | call-03551 |
| `desktop_ccd_send_uuid_reused` | 1 | `had_live_query`~, `matched`~, `path`~, `session_id`~ | 0 | call-03378 |
| `desktop_ccd_session_cleared` | 1 | `backend_kind`~, `had_cli_session`~, `is_ssh`~, `message_count`~, `remote_control_user_owned`~, `remote_control_was_on`~, `session_id`~ | 0 | call-03410 |
| `desktop_ccd_session_crash_loop_parked` | 1 | `check_source`?~, `consecutive_failures`~, `error_category`~, `expected_cli_version`?~, `reported_cli_kind`?~, `reported_cli_version`?~, `session_id`~, `spawn_source`~, `total_failures`~ | 2 | call-03554 |
| `desktop_ccd_session_dead_end` | 1 | `deeplink_age_ms`~, `episode_index`~, `ever_connected`~, `from_deeplink`~, `kind`~, `ms_since_open`~, `session_id`~, `session_scope`~, `session_type`~ | 0 | call-03683 |
| `desktop_ccd_session_detached` | 1 | `initiator`~, `kind`~ | 0 | call-03542 |
| `desktop_ccd_session_discard_pending` | 2 | `first_turn`~, `session_id`~ | 0 | call-03516, call-03517 |
| `desktop_ccd_session_file_access` | 1 | `lane`~, `outcome`~, `root_is_unc`~, `spelled_in`?~ | 2 | call-04119 |
| `desktop_ccd_session_idle_paused` | 1 |  | 2 | call-03494 |
| `desktop_ccd_session_idle_warm_complete` | 1 | `backend_kind`~, `cli_binary_choice`~, `cli_current_version`~, `cli_pinned_version`~, `had_scheduled_task`~, `idle_timeout_ms`~, `is_resume`?~, `is_ssh`~, `prefix_parity`~, `prompt_append_source`~, `prompt_suggestions_requested`~, `resume_reason`?~, `resume_stop_trigger`?~, `session_id`~, `system_prompt_snapshot`?~, `warm_duration_ms`~, `warm_trigger`?~ | 5 | call-03527 |
| `desktop_ccd_session_idle_warm_failed` | 1 | `backend_kind`~, `error_category`~, `error_message`~, `git_isolation_errno`?~, `git_isolation_stage`?~, `has_worktree`~, `is_ssh`~, `session_id`~, `warm_duration_ms`~, `warm_trigger`?~, `worktree_refusal`~ | 5 | call-03528 |
| `desktop_ccd_session_idle_warm_start` | 1 | `backend_kind`~, `idle_timeout_ms`~, `is_ssh`~, `session_id`~, `warm_trigger`?~ | 2 | call-03526 |
| `desktop_ccd_session_initialization_failed` | 3 | `backend_kind`~, `error_category`~, `error_message`~, `fault_class`~, `git_isolation_errno`?~, `git_isolation_stage`?~, `has_worktree`~, `input_origin`?~, `is_resume`~, `is_ssh`~, `is_violin_bow`?~, `oversize_option`?~, `session_id`~, `spawn_argv_chars`?~, `tcc_folder_kind`?~, `worktree_refusal`~, `wsl_error_code`?~ | 11 | call-03504, call-03506, call-03558 |
| `desktop_ccd_session_initialized` | 2 | `backend_kind`~, `had_scheduled_task`~, `has_launch_tools`~, `has_worktree`~, `idle_timeout_ms`~, `is_git_repo`~, `is_scratch`~, `is_ssh`~, `managed_launcher`?~, `mcp_server_count`~, `model`~, `os_entry`~, `permission_mode`~, `prewarm`?~, `prompt_suggestions_requested`~, `renderer_surface`~, `scratch_offer_folder`~, `session_id`~, `shell_env_failed_reads`~, `side_sessions_available`~, `thinking_forced`~, `turn_box_mounted`~, `user_message_uuid`~ | 8 | call-03503, call-03505 |
| `desktop_ccd_session_list_load_failed` | 3 | `attempt_id`~, `error_category`~, `list_source` | 2 | call-03279, call-03281, call-03282 |
| `desktop_ccd_session_list_loaded` | 1 | `active_phase_ms`?~, `archive_index_state`?~, `archived_phase_ms`?~, `archived_phase_trigger`?~, `archived_with_bridge_count`?~, `cached`~, `deferred_archived_count`?~, `head_unknown_count`?~, `index_deferred_count`?~, `index_stale_active_count`?~, `load_phase`?~, `session_bytes_read`?~, `session_count`~, `skipped_count`~, `store_state`~ | 2 | call-03280 |
| `desktop_ccd_session_path_gone` | 1 | `ask_took`~, `verdict`~ | 0 | call-04118 |
| `desktop_ccd_session_pause_blocked_by_cron` | 1 | `active_cron_count`~, `session_id`~ | 0 | call-03519 |
| `desktop_ccd_session_pause_blocked_by_lanyard` | 1 | `seconds_since_last_activity`~, `session_id`~ | 0 | call-03523 |
| `desktop_ccd_session_pause_blocked_by_rc` | 1 | `auto_enabled`~, `auto_source`~, `is_scheduled_task_session`~, `seconds_since_last_activity`~, `session_id`~ | 0 | call-03522 |
| `desktop_ccd_session_pause_blocked_by_wakeup` | 1 | `session_id`~, `wakeup_in_ms`~ | 0 | call-03520 |
| `desktop_ccd_session_pause_blocked_by_workflow` | 1 | `active_background_task_count`~, `active_workflow_count`~, `session_id`~ | 0 | call-03521 |
| `desktop_ccd_session_pause_skipped_remote` | 1 | `backend_kind`~, `session_id`~, `trigger`~ | 0 | call-03524 |
| `desktop_ccd_session_query_error` | 1 | `backend_kind`~, `error_category`~, `exit_code`?~, `fatal_startup_result`~, `had_pending_turn`~, `has_worktree`~, `is_resume`~, `is_ssh`~, `is_startup_error`~, `is_violin_bow`?~, `last_message_model`?~, `last_message_type`?~, `last_tool_name`?~, `launcher_version_check`?~, `managed_launcher`?~, `ntstatus_name`~, `quiet_recovery`?~, `rewind_active_chain_length`?~, `rewind_target_miss_reason`?~, `rewind_transcript_has_compact_boundary`?~, `rewind_transcript_length`?~, `sandbox_cascade`?~, `session_id`~, `tcc_folder_kind`?~, `was_recovered`?~ | 13 | call-03553 |
| `desktop_ccd_session_resume_pre_clear` | 1 | `backend_kind`~, `cli_session_id`~, `is_ssh`~, `message_count`~, `session_id`~ | 0 | call-03518 |
| `desktop_ccd_session_rewind_files` | 1 | `can_rewind`~, `dry_run`~, `files_changed_count`~, `in_flight`~, `mid_turn`~, `session_id`~, `timed_out`~ | 0 | call-03407 |
| `desktop_ccd_session_rewind_rejected_dead_branch` | 1 | `active_chain_length`~, `session_id`~, `target_message_uuid`~, `transcript_length`~ | 0 | call-03416 |
| `desktop_ccd_session_rewind_switch_refused` | 3 | `direction`~, `refusal`~, `session_id`~ | 0 | call-03419, call-03420, call-03421 |
| `desktop_ccd_session_rewind_undone` | 2 | `backend_kind`~, `direction`~, `phase`, `seconds_since_rewind`~, `session_id`~ | 0 | call-03418, call-03422 |
| `desktop_ccd_session_rewound` | 1 | `marker_offered`~, `session_id`~, `target_message_uuid`~, `unwound_refusal_fallback`~ | 0 | call-03417 |
| `desktop_ccd_session_start_timing` | 1 | `anchor_source`~, `base_config_cache_hit`~, `ccd_overhead_ms`~, `checkout_barrier`~, `checkout_overlap_mode`~, `context_tokens`~, `deferred_startup_reads`~, `enqueue_ms`~, `estimated_cache_write_usd`~, `first_assistant_ms`~, `full_checkout_wait_ms`~, `include_overlay_wait_ms`~, `init_awake_ms`~, `init_mcp_connected_count`~, `init_mcp_disabled_count`~, `init_mcp_failed_count`~, `init_mcp_needs_auth_count`~, `init_mcp_other_count`~, `init_mcp_pending_count`~, `init_mcp_total_count`~, `init_ms`~, `init_plugin_count`~, `is_first_turn`~, `is_ssh`~, `mcp_config_http_count`~, `mcp_config_sdk_count`~, `mcp_config_stdio_count`~, `mcp_ms`~, `mcp_server_count`~, `needs_tree_before_spawn_reason`~, `online`~, `org_skills_off`~, `overlay_spawn_wait_ms`~, `overlay_wait_ms`~, `plugin_delivery`~, `plugin_dir_count`~, `plugin_mcp_connector_twin_by_name_count`~, `plugin_mcp_connector_twin_count`~, `pool_busy_skips`~, `pool_cached_unclean`~, `pool_candidates`~, `pool_deferred`~, `pool_indeterminate`~, `pool_ms`~, `pool_outcome`~, `pool_probes`~, `pool_rebind_attempts`~, `pool_rebind_ms`~, `pool_refused`~, `pool_trusted`~, `pool_wait_ms`~, `post_checkout_wait_ms`~, `preflight_ms`~, `prewarm`~, `prewarm_kind`~, `prewarm_lead_ms`~, `prompt_cache_likely_expired`~, `query_ms`~, `registry_plugin_count`~, `resume_cost_source`~, `resume_reason`~, `resume_seed`~, `resume_stop_trigger`~, `rpm_enabled_state_age_ms`~, `rpm_enabled_state_ms`~, `rpm_enabled_state_source`~, `rpm_fs_scan_ms`~, `seconds_since_last_response`~, `seconds_since_last_turn`~, `session_id`~, `session_repo_entry_base_missing`~, `session_repo_missing`~, `session_repo_not_a_tree`~, `session_repo_not_session_scoped`~, `session_repo_tree_not_anchored`~, `session_repo_unbound`~, `session_repo_would_refuse_base`~, `session_repo_would_refuse_tree`~, `spare_claim_ms`~, `spare_mcp_settled`~, `spare_miss_reason`~, `spare_parked_ms`~, `spare_wait_ms`~, `total_to_assistant_ms`~, `total_to_init_ms`~, `worktree_created`~, `worktree_lazy`~, `worktree_ms`~, `worktree_pool_enabled`~, `worktree_reused`~, `wt_add_ms`~, `wt_checkout_workers`~, `wt_config_copied`~, `wt_config_deferred`~, `wt_config_overlay_ms`~, `wt_config_overlay_outcome`~, `wt_fetch_ms`~, `wt_fetch_outcome`~, `wt_fetch_settled`~, `wt_filter_refresh_ms`~, `wt_filter_refresh_no_space`~, `wt_full_checkout_ms`~, `wt_git_crypt_binary`~, `wt_git_crypt_keys`~, `wt_git_crypt_left`~, `wt_git_spawns`~, `wt_hooks_config_ms`~, `wt_include_matched`~, `wt_include_patterns_dropped`~, `wt_include_scan_mode`~, `wt_include_scan_ms`~, `wt_include_scan_outcome`~, `wt_include_unsearched_dirs`~, `wt_lfs_hydrate_ms`~, `wt_lfs_hydrated`~, `wt_lfs_not_local`~, `wt_lfs_rejected`~, `wt_lfs_skipped`~, `wt_load_avg_1m`~, `wt_overlay_settled_ms`~, `wt_post_checkout_hook_ms`~, `wt_post_checkout_hook_ran`~, `wt_prep_ms`~, `wt_stage1_ms`~, `wt_status_cache_prime`~, `wt_tracked_files`~ | 0 | call-03275 |
| `desktop_ccd_session_stopped` | 1 |  | 2 | call-03495 |
| `desktop_ccd_session_switch_abandoned` | 1 | `elapsed_ms`~, `nav_temp`~, `reason`~, `session_id`~, `session_type`~, `switch_id`~, `was_hidden`~ | 0 | call-03284 |
| `desktop_ccd_session_switch_initiated` | 1 | `backend_kind`~, `entry_point`~, `input_delay_ms`~, `is_new_session`~, `low_memory_posture`~, `renderer_build_id`~, `renderer_surface`~, `session_id`~, `session_type`~, `switch_id`~ | 3 | call-03283 |
| `desktop_ccd_session_switch_timing` | 1 | `active_session_count`~, `after_paint_ms`~, `backend_kind`~, `cache_hit`~, `defer_ms`~, `entry_point`~, `first_content_source`~, `first_paint_ms`~, `host_mount_ms`~, `input_delay_ms`~, `intent_lead_ms`~, `ipc_bytes`~, `ipc_ms`~, `is_new_session`~, `loaf_in_delay_ms`~, `low_memory_posture`~, `mount_commit_ms`~, `mount_composer_ms`~, `mount_layout_ms`~, `mount_list_ms`~, `mount_ms`~, `mount_panel_ms`~, `nav_temp`~, `parse_input_len`~, `parse_ms`~, `press_lead_ms`~, `renderer_build_id`~, `renderer_surface`~, `route_ms`~, `running_session_count`~, `seeded_from_tail`~, `session_id`~, `session_type`~, `since_app_focus_ms`~, `since_input_ms`~, `since_page_hidden_ms`~, `since_page_visible_ms`~, `switch_id`~, `tail_drain_overlap`~, `tail_file_bytes`~, `tail_handler_ms`~, `tail_ipc_ms`~, `tail_parse_ms`~, `tail_parse_self_ms`~, `tail_queue_ms`~, `tail_read_bytes`~, `tail_read_ms`~, `tail_rows_kept`~, `tail_rows_parsed`~, `tail_rungs`~, `tail_session_wait_ms`~, `tail_source`~, `transcript_fill_rows`~, `transcript_ms`~, `transcript_page_fallback`~, `transcript_page_source`~, `transcript_result`~, `transcript_total_rows`~, `was_hidden`~ | 6 | call-03401 |
| `desktop_ccd_session_timeout` | 1 | `probe_result`~ | 1 | call-03478 |
| `desktop_ccd_session_title_check` | 1 | `latency_ms`~, `proposed_title_chars`~, `title_check_outcome`~, `title_overlap_pct`~, `would_offer`~ | 1 | call-03423 |
| `desktop_ccd_session_title_from_pr` | 1 | `previous_title_source`~, `seconds_since_create`~, `session_id`~ | 0 | call-03424 |
| `desktop_ccd_session_title_offer` | 1 | `action`~, `check_ordinal`~, `current_title_chars`~, `proposed_title_chars`~, `seconds_since_offer`~, `session_id`~, `title_source`~ | 0 | call-03426 |
| `desktop_ccd_session_title_via_cli` | 1 | `cli_version`~, `latency_ms`~, `session_id`~, `title_via_cli_outcome`~ | 0 | call-03425 |
| `desktop_ccd_session_tool_auto_mode` | 1 | `outcome`~, `session_id`~, `session_tool`~ | 0 | call-03293 |
| `desktop_ccd_session_visibility_changed` | 1 | `backend_kind`~, `has_active_query`~, `is_ssh`~, `is_visible`~, `session_id`~ | 0 | call-03529 |
| `desktop_ccd_sessions_recovered` | 1 |  | 0 | call-03560 |
| `desktop_ccd_set_model_mid_turn` | 1 | `deferred_sends`~, `had_first_response`~, `session_id`~ | 0 | call-03415 |
| `desktop_ccd_setting_change_auto_mode` | 1 | `outcome`~, `session_id`~, `setting_key`~ | 0 | call-03290 |
| `desktop_ccd_settings_tool` | 2 | `outcome`~, `session_id`~, `setting_key`~, `settings_tool` | 0 | call-03068, call-03069 |
| `desktop_ccd_shell_env_extraction_failed` | 1 | `attempt`~, `errorMessage`~, `willRetry`~ | 0 | call-03840 |
| `desktop_ccd_shell_env_extraction_recovered` | 1 | `attempt`~ | 0 | call-03839 |
| `desktop_ccd_shell_env_tls_trust_adopted` | 1 | `vars_adopted`~ | 0 | call-03838 |
| `desktop_ccd_side_chat_guard_breach` | 1 | `session_id`~, `tool`~ | 0 | call-03467 |
| `desktop_ccd_side_chat_started` | 1 | `declares_parent_tools`~, `session_id`~ | 0 | call-03466 |
| `desktop_ccd_side_chat_tool_refused` | 1 | `session_id`~, `tool`~ | 0 | call-03464 |
| `desktop_ccd_side_chat_tools_narrowed` | 1 | `session_id`~ | 0 | call-03465 |
| `desktop_ccd_side_session_hand_off` | 1 | `parent_session_id`~, `session_id`~ | 0 | call-03543 |
| `desktop_ccd_side_session_offer` | 5 | `child_session_id`?~, `outcome`~, `session_id`~ | 2 | call-03408, call-03535, call-03536, call-03537, call-03538 |
| `desktop_ccd_side_session_start_gated` | 1 | `outcome`~, `session_id`~, `start_gate`~, `started`~, `tool`~ | 0 | call-03319 |
| `desktop_ccd_side_session_started` | 2 | `context`~, `from_preset`~, `live_children`~, `model_downgraded`~, `parent_is_side_session`~, `parent_session_id`~, `proposal_id_present`~, `session_id`~, `target_kind`~, `wake_when_done`~, `worktree_mode`~ | 1 | call-03540, call-03541 |
| `desktop_ccd_side_session_wake` | 1 | `children`~, `parent_session_id`~, `waiting_children`~, `wakes_since_user_message`~ | 0 | call-03409 |
| `desktop_ccd_sleep_auto_resume` | 1 | `last_buffered_message_type`~, `outcome`~, `renderer_surface`~, `session_id`~, `silence_ms`~, `sleep_duration_seconds`~ | 1 | call-03452 |
| `desktop_ccd_sleep_interruption_cleared` | 1 | `cleared_by`~, `renderer_surface`~, `session_id`~, `time_visible_ms`~, `wake_at`~ | 0 | call-03451 |
| `desktop_ccd_sleep_interruption_shown` | 1 | `last_buffered_message_type`~, `renderer_surface`~, `session_id`~, `sleep_duration_seconds`~, `trigger`~, `wake_at`~ | 0 | call-03450 |
| `desktop_ccd_spare` | 2 | `age_ms`~, `ready`~, `ready_ms`~, `reason`~, `session_id`~, `spare_event`~, `spare_fail_code`~ | 0 | call-03501, call-03502 |
| `desktop_ccd_spawn_tool_parity` | 1 |  | 0 | call-03359 |
| `desktop_ccd_start_lock_broken` | 1 | `automatic`~, `backend_kind`~, `held_ms`~, `host_work`?~, `is_warm`~, `reason`~, `session_id`~ | 1 | call-03358 |
| `desktop_ccd_steer_delivered` | 1 | `backend_kind`~, `is_ssh`~, `message_uuid`~, `mode`~, `ms_to_echo`~, `renderer_surface`~, `session_id`~, `tool_running_at_send`~, `was_held`~ | 0 | call-03453 |
| `desktop_ccd_steer_detach` | 2 | `backend_kind`~, `backgrounded`?~, `is_ssh`~, `message_uuid`~, `mode`~, `renderer_surface`~, `session_id`~, `tool_age_ms`~, `tool_name`~, `unread_steers`~ | 2 | call-03387, call-03388 |
| `desktop_ccd_storage_cleanup` | 1 | `bytes`~, `cancelled`~, `candidate_count`~, `delete_sessions`~, `deleted_count`~, `failed_count`~, `include_uncommitted`~, `older_than_days`~, `removed_count`~, `skipped_count`~, `trigger`? | 1 | call-04088 |
| `desktop_ccd_storage_cleanup_auto_mode` | 1 | `outcome`~, `session_id`~ | 0 | call-03297 |
| `desktop_ccd_stream_ended_diagnostic` | 1 | `cli_session_id`~, `cli_stderr_tail`?~, `had_first_response`~, `is_ssh`~, `is_stopping`~, `seconds_since_stderr`?~, `seconds_to_outcome`~, `session_id`~, `user_message_uuid`~ | 2 | call-03278 |
| `desktop_ccd_stream_render` | 1 | `active_session_count`~, `blocks_committed`~, `chunk_count`~, `ended_by_unmount`~, `frontier_renders`~, `hidden_at_emit`~, `long_frame_ms_max`~, `long_frame_ms_total`~, `low_memory_posture`~, `renderer`~, `renderer_surface`~, `running_session_count`~, `session_id`~, `single_ingest`~, `stream_ms`~, `tail_reparse_count`~, `text_len`~, `update_count`~, `via_fallback`~, `was_hidden_any`~ | 0 | call-03403 |
| `desktop_ccd_task_backlog_dismissed` | 1 | `age_days`~, `source`~, `taken`~ | 0 | call-03539 |
| `desktop_ccd_task_backlog_filed` | 1 | `filed_count`~, `session_id`~, `source`~ | 0 | call-03412 |
| `desktop_ccd_teleport_snapshot` | 1 | `duration_ms`~, `session_id`~ | 1 | call-03180 |
| `desktop_ccd_terminal_auto_mode` | 1 | `outcome`~, `session_id`~, `tool`~ | 0 | call-03291 |
| `desktop_ccd_terminal_pty_closed` | 1 | `bytes_dropped`~, `bytes_received`~, `cap_bytes`~, `close_reason`~, `command_marks`~, `commands_run`~, `had_input`?~, `lifetime_ms`~, `log_reads`?~, `pool`~, `reads`~, `reads_cap_limited`~, `replays`?~, `replays_after_drop`?~, `scrollback_log`?~, `shell_integration`?~, `spawn_reason`?~ | 3 | call-03576 |
| `desktop_ccd_terminal_pty_evicted` | 2 | `pool`, `size`~ | 0 | call-03580, call-03582 |
| `desktop_ccd_terminal_shared_unavailable` | 2 | `reason` | 0 | call-03578, call-03581 |
| `desktop_ccd_terminal_spawned` | 1 | `carrier`~, `sessionId`~, `shell`~, `spawn_reason`~ | 0 | call-03579 |
| `desktop_ccd_terminal_typed` | 1 | `carrier`~, `closed`~, `hooked`~, `into_open_tab`~, `outcome`~, `slow_shell_wait`~, `waited_ms`~ | 0 | call-03179 |
| `desktop_ccd_thinking_display_flip` | 1 | `is_ssh`~, `mid_turn`~, `session_id`~, `to_display`~, `trigger`~ | 0 | call-03413 |
| `desktop_ccd_transcript_kept_on_delete` | 1 | `idle_gated`~, `reason`~ | 0 | call-03443 |
| `desktop_ccd_transcript_lease_pass` | 1 | `candidates`~, `errors`~, `fresh`~, `missing`~, `renewed`~, `retention_days`?~, `retention_source`?~, `skipped`?~ | 3 | call-03476 |
| `desktop_ccd_transcript_load_earlier` | 1 | `has_more`~, `ok`~, `page_note`~, `rows`~, `session_id`~, `session_type`~, `trigger`~ | 0 | call-03532 |
| `desktop_ccd_transcript_newest_page` | 1 | `page_source`~, `read_ms`~, `remote`~, `session_id`~, `via`~, `window_fallback`?~, `window_probe_error`?~ | 2 | call-03440 |
| `desktop_ccd_transcript_read_failed` | 1 | `reason`~, `session_id`~ | 0 | call-03438 |
| `desktop_ccd_transcript_unavailable_marked` | 2 | `dormant_days`?~, `missing_kind`~, `session_id`~, `site` | 2 | call-03439, call-03525 |
| `desktop_ccd_transcript_window_backfill` | 1 | `backfill_outcome`~, `differed`~, `fill_rows`~, `ok`~, `session_id`~ | 0 | call-03533 |
| `desktop_ccd_trust_check_miss` | 1 | `trust_check_cause`~, `trust_total_ms`~ | 0 | call-03457 |
| `desktop_ccd_turn_result_wait_expired` | 1 | `backend_kind`~, `cli_provably_idle`~, `deferred_sends`~, `disposition`~, `had_interrupt_carrier`~, `had_pending_cycle`~, `held_steers`~, `is_ssh`~, `renderer_surface`~, `session_id`~ | 0 | call-03447 |
| `desktop_ccd_turn_scope` | 1 | `session_id`~, `turn_scope`~ | 0 | call-03048 |
| `desktop_ccd_window_tool` | 1 | `outcome`~, `reason`?~, `session_id`~, `target`?~, `tool`~ | 2 | call-03070 |
| `desktop_ccd_work_lost_at_relaunch` | 1 | `backend_kind`~, `is_scheduled_task_session`~, `session_id`~, `turn_interrupted`~ | 1 | call-03398 |
| `desktop_ccd_workflow_consent_policy_wait_ms` | 1 | `wait_ms`~ | 0 | call-03087 |
| `desktop_ccd_workflow_consent_write_failed` | 1 | `session_id`~ | 0 | call-03347 |
| `desktop_ccd_workflow_usage_consented` | 1 | `decision`~, `session_id`~ | 0 | call-03348 |
| `desktop_ccd_worktree_deps_seeded` | 1 | `duration_ms`~, `install_state_seeded`~, `outcome`~, `root_ms`~, `session_id`~, `workspaces_seeded`~ | 0 | call-03145 |
| `desktop_ccd_worktree_fallback` | 4 | `backend_kind`~, `branch_reattached`?~, `fallback_cwd`~, `folder_tree`~, `fresh_worktree_created`?~, `is_ssh`~, `own_worktree_reattached`~, `re_leased_from_pool`~, `recreate_cause`~, `recreate_outcome`~, `session_id`~, `worktree_path`~ | 2 | call-03458, call-03459, call-03461, call-03462 |
| `desktop_ccd_worktree_fetch_degraded` | 8 | `blocking`~, `reason`~ | 0 | call-03147, call-03151, call-03152, call-03153, call-03154, call-03155, call-03156, call-03157 |
| `desktop_ccd_worktree_kept_dirty` | 4 | `changed_count`~, `folder_tree`~, `force_cleanup_explicit_false`~, `has_live_sibling`~, `is_remote`~, `reason`~, `session_id`~ | 0 | call-03370, call-03371, call-03496, call-03497 |
| `desktop_ccd_worktree_lease_violation` | 1 | `cwd`~, `holder`~, `session_id`~ | 0 | call-03534 |
| `desktop_ccd_worktree_leftovers` | 1 | `bytes`~, `file_count`~, `folder_tree`?~, `outcome`~, `reason`?~, `session_id`~, `source` | 2 | call-03369 |
| `desktop_ccd_worktree_probe_timeout` | 1 | `elapsed_ms`~, `remote`~, `session_id`~, `timeout_ms`~ | 0 | call-03406 |
| `desktop_ccd_worktree_recycle` | 1 | `hidden_count`?~, `ms`~, `outcome`~, `source`~ | 1 | call-04161 |
| `desktop_ccd_worktree_removed` | 1 | `admin_removed`?~, `caller`~, `detach_ms`?~, `fs_error_code`?~, `git_remove_ms`?~, `had_node_modules`?~, `lane`~, `removed`~, `status_ms`~, `total_ms`~ | 5 | call-03149 |
| `desktop_ccd_worktree_source_ref_fetch` | 1 | `outcome`~, `wait_ms`~ | 0 | call-03148 |
| `desktop_ccd_worktree_tombstone_reaped` | 1 | `age_ms`~, `attempts`~, `duration_ms`~, `outcome`~ | 0 | call-03150 |
| `desktop_ccd_worktree_transcript_migrated` | 2 | `cli_session_id`~, `session_id`~ | 0 | call-03441, call-03442 |
| `desktop_ccd_worktree_write_guard_blocked` | 1 | `session_id`~, `target`~, `tool_name`~ | 0 | call-03323 |
| `desktop_chat_upload_no_reply` | 1 | `upload_net_error_name`~ | 1 | call-04143 |
| `desktop_claude_ai_import` | 1 | `conversations`~, `files`~, `import_source`~, `projects`~, `skipped`~, `source_organization_uuid`~ | 0 | call-04139 |
| `desktop_claude_auth_url_withheld` | 10 | `host`~ | 0 | call-03623, call-03630, call-03631, call-03632, call-03633, call-03640, call-03984, call-04145, call-04146, call-04147 |
| `desktop_code_deeplink_received` | 1 |  | 0 | call-03703 |
| `desktop_code_deeplink_resume_failed` | 1 | `category`~, `is_repeat`~ | 0 | call-03686 |
| `desktop_code_deeplink_session_received` | 1 | `cold_start`~, `link_host`~, `resolved`~ | 0 | call-03705 |
| `desktop_code_project_link_opened` | 3 | `cold_start`~, `entry`, `has_message`~, `has_thread`~, `link_host`~ | 0 | call-03706, call-03707, call-03708 |
| `desktop_cowork_feedback_logs_left_out` | 1 | `reason`~ | 0 | call-03937 |
| `desktop_deeplink_handler_unregistered` | 1 | `cause`~, `generated_entry`~, `os_entry_points`~, `trigger`~ | 0 | call-03727 |
| `desktop_design_pdf_export` | 3 | `ok`~ | 0 | call-03900, call-03901, call-03902 |
| `desktop_design_window_closed_before_load` | 1 | `open_ms`~ | 0 | call-03906 |
| `desktop_design_window_http_error` | 1 | `first_load`~, `http_status`~, `http_status_text`~ | 0 | call-03905 |
| `desktop_design_window_load` | 1 | `load_ms`~ | 0 | call-03903 |
| `desktop_design_window_load_failed` | 1 | `error_code`~, `error_description`~, `first_load`~ | 0 | call-03904 |
| `desktop_download_checksum_mismatch` | 1 | `actual_sha256`~, `attempts`~, `bytes_downloaded`~, `expected_sha256`~, `key`~, `resumed_from_byte`~ | 0 | call-03628 |
| `desktop_download_retry` | 2 | `attempt_num`~, `bytes_at_failure`~, `discarded_partial`~, `error_code`~, `key`~, `resume_from_byte`~ | 0 | call-03627, call-03825 |
| `desktop_download_verified` | 1 | `attempts`~, `bytes_downloaded`~, `expected_sha256`~, `key`~, `resumed_from_byte`~ | 0 | call-03629 |
| `desktop_dxt_install_failed` | 1 | `error_code`~, `extension_id`~, `is_internal`~ | 0 | call-03861 |
| `desktop_dxt_installed` | 1 | `extension_author`~, `extension_id`~, `extension_name`~, `extension_version`~, `is_internal`~, `total_extensions_installed`~ | 0 | call-03860 |
| `desktop_dxt_policy_enforced` | 1 | `denied`~, `fallback`~, `store_unreadable`~, `unrecorded`~ | 0 | call-03858 |
| `desktop_dxt_uninstalled` | 1 | `extension_author`~, `extension_id`~, `extension_name`~, `extension_version`~, `total_extensions_installed`~ | 0 | call-03859 |
| `desktop_enterprise_host_mode_changed` | 1 | `new_value`~, `previous_value`~ | 0 | call-03800 |
| `desktop_feature_exposure` | 1 | `feature_hash`~, `feature_source`~, `in_experiment`~, `on`~ | 0 | call-03626 |
| `desktop_file_save_destination` | 1 | `destination`~, `source`~ | 0 | call-03842 |
| `desktop_git_confined_install` | 1 | `at_launch`~, `confined`~, `cowork_folder`~, `fleet_override`~, `folders_unread`~, `launcher_marked`~, `no_off_read`~, `relocated_config`~, `remote_folder`~, `sandbox_env`~, `sandbox_on`~, `sandbox_settings`~, `saved_other`~, `status_unknown`~, `store_reset`~, `third_party`~, `unreadable_settings`~, `unreadable_store`~ | 0 | call-04089 |
| `desktop_gpu_crash_loop_terminal` | 1 | `action`~, `gpu_deaths`, `hw_accel_disabled_at_launch`~, `last_exit_code_decoded`~, `last_reason`~, `relaunch_marker_present`~, `window_span_ms`~ | 0 | call-03786 |
| `desktop_gpu_hw_accel_auto_disable` | 1 |  | 0 | call-03785 |
| `desktop_gpu_hw_accel_user_toggle` | 1 | `disabled`~, `was_auto_disabled`~ | 0 | call-03918 |
| `desktop_gpu_process_gone` | 1 | `exit_code`~, `exit_code_decoded`~, `reason`~, `surface`~, `third_party_gpu_modules_allowed`~, `web_commit_hash`~ | 0 | call-03788 |
| `desktop_gpu_state` | 1 | `trigger`~ | 1 | call-03787 |
| `desktop_hardware_buddy_status` | 1 | `paired_device_count`~ | 0 | call-03138 |
| `desktop_heavy_work_failed` | 7 | `error_category`~, `heavy_work_task`~ | 0 | call-03086, call-03089, call-03146, call-03175, call-03185, call-03593, call-03642 |
| `desktop_hybrid_growthbook_fetch` | 1 | `host`~, `outcome`~ | 1 | call-03625 |
| `desktop_inactive_service_paused` | 1 | `reason`, `service` | 0 | call-03616 |
| `desktop_inference_routing_skip` | 1 | `reason`~ | 0 | call-03090 |
| `desktop_initial_activation` | 1 | `app_version`~, `platform`~ | 0 | call-04152 |
| `desktop_launch_button_clicked` | 1 | `has_config`~ | 0 | call-03961 |
| `desktop_launch_model_nav_refused` | 2 | `reason`~, `source` | 0 | call-03235, call-03940 |
| `desktop_launch_preview_allowed_origin_added` | 1 | `result`~ | 0 | call-03957 |
| `desktop_launch_preview_allowed_origin_removed` | 1 |  | 0 | call-03955 |
| `desktop_launch_preview_allowed_origins_cleared` | 1 |  | 0 | call-03956 |
| `desktop_launch_preview_artifact_fullscreen` | 1 | `phase`~, `reason`?~ | 1 | call-03886 |
| `desktop_launch_preview_blocklist_consult_failed` | 1 | `hard_deny_served`~, `reason`~, `status`?~ | 1 | call-03658 |
| `desktop_launch_preview_chat_pane_bound` | 1 | `pane_open`~ | 0 | call-03887 |
| `desktop_launch_preview_chat_pane_created` | 1 |  | 0 | call-03953 |
| `desktop_launch_preview_clipboard_write` | 1 | `kind`~, `origin_class`~, `phase`~ | 0 | call-03896 |
| `desktop_launch_preview_config_url` | 4 | `outcome`~, `source`, `url_class`~ | 0 | call-03234, call-03239, call-03240, call-03944 |
| `desktop_launch_preview_credentialed_nav` | 11 | `action`, `source`~ | 0 | call-03236, call-03237, call-03238, call-03874, call-03890, call-03898, call-03899, call-03939, call-03941, call-03942, call-03943 |
| `desktop_launch_preview_exported` | 1 | `kind`~ | 0 | call-03895 |
| `desktop_launch_preview_external_nav_policy_blocked` | 4 | `arm`, `source`~ | 0 | call-03879, call-03880, call-03881, call-03888 |
| `desktop_launch_preview_external_only_site` | 3 | `action`, `source`~ | 0 | call-03875, call-03876, call-03947 |
| `desktop_launch_preview_file_access_prompt` | 4 | `card_reason`~, `decision`~, `missing`~ | 4 | call-03661, call-03662, call-03663, call-03664 |
| `desktop_launch_preview_first_frame_fallback` | 1 | `expected_height`~, `expected_width`~, `probed_height`~, `probed_width`~, `reason`~ | 0 | call-03884 |
| `desktop_launch_preview_gdrive_view_created` | 1 |  | 0 | call-03954 |
| `desktop_launch_preview_governed_held_blocked` | 1 | `resource_type`~, `why`~ | 0 | call-03867 |
| `desktop_launch_preview_hide_refused` | 2 | `reason`, `session_id`~ | 0 | call-03891, call-03892 |
| `desktop_launch_preview_link_routed` | 2 | `outcome`, `surface`~ | 0 | call-03872, call-03873 |
| `desktop_launch_preview_link_routed_external` | 2 | `outcome` | 0 | call-03959, call-03960 |
| `desktop_launch_preview_load_failed` | 2 | `error_code`~, `retry_count`~ | 0 | call-03882, call-03883 |
| `desktop_launch_preview_media_permission_denied` | 1 | `kinds`~ | 0 | call-03868 |
| `desktop_launch_preview_nav_redirect_blocked` | 1 | `source`~ | 0 | call-03878 |
| `desktop_launch_preview_open_in_browser` | 1 |  | 0 | call-03958 |
| `desktop_launch_preview_origin_prompt` | 6 | `decision`~, `is_financial`~, `is_high_risk`~, `is_local`~, `org_browser_allowed`~, `phase` | 4 | call-03660, call-03665, call-03666, call-03667, call-03668, call-03669 |
| `desktop_launch_preview_overlap_healed` | 1 | `basis`~, `host_window`~, `session_id`?~, `stale_claimed`~, `stale_cowork_owned`~, `stale_shown_age_ms`~, `survivor_claimed`~, `survivor_cowork_owned`~, `survivor_shown_age_ms`~ | 2 | call-03894 |
| `desktop_launch_preview_pdf_file_tab` | 2 |  | 0 | call-03951, call-03952 |
| `desktop_launch_preview_pdf_nav_download` | 1 |  | 0 | call-03869 |
| `desktop_launch_preview_ssrf_blocked` | 1 | `initiator`~, `own_address`~, `resource_type`~, `target`~, `why`~ | 0 | call-03866 |
| `desktop_launch_preview_subframe_click_gate` | 3 | `decision`~, `frame_depth`, `via_oopif`~ | 0 | call-03231, call-03232, call-03885 |
| `desktop_launch_preview_transcript_link_opened` | 7 | `clicked_in`~, `expired`~, `handed_off`~, `surface`, `tab`~ | 0 | call-03877, call-03889, call-03945, call-03946, call-03948, call-03949, call-03950 |
| `desktop_launch_preview_trust_grant_minted` | 1 | `from_card`?~, `http_sibling`~, `lan_name`~, `structural`~, `upgraded_existing`~ | 1 | call-03659 |
| `desktop_launch_preview_viewport_emulation` | 1 | `action`~, `pane_visible`~, `source`~, `tabs`~, `viewport_size_bucket`~ | 0 | call-03897 |
| `desktop_launch_preview_visible_overlap` | 1 |  | 0 | call-03893 |
| `desktop_launch_tool_used` | 1 | `session_id`~, `tool_name`~ | 0 | call-03233 |
| `desktop_login_callback_duplicate_suppressed` | 1 |  | 0 | call-03685 |
| `desktop_login_callback_evicted` | 2 | `method`, `reason`~ | 0 | call-03691, call-03692 |
| `desktop_login_callback_received` | 3 | `method` | 0 | call-03690, call-03694, call-03698 |
| `desktop_login_failed` | 4 | `load_error_code`~, `method`~, `reason` | 0 | call-03687, call-03693, call-03695, call-03696 |
| `desktop_main_event_loop_stall` | 1 | `emit_delay_ms`~, `gc_cumulative_ms`~, `gc_in_stall_max_ms`~, `gc_in_stall_ms`~, `sampler_frames`~, `sampler_start_lag_ms`~ | 2 | call-03928 |
| `desktop_main_process_crash_reported` | 1 | `crashed_app_version`~ | 0 | call-04093 |
| `desktop_main_view_http_error` | 1 | `http_status`~, `http_status_text`~, `is_claude_host`~ | 0 | call-03673 |
| `desktop_main_view_load_failed` | 1 | `error_code`~, `error_description`~, `is_claude_host`~ | 0 | call-03672 |
| `desktop_main_view_load_recovered` | 1 |  | 0 | call-03674 |
| `desktop_main_view_load_retry_exhausted` | 1 |  | 0 | call-03670 |
| `desktop_main_view_redirect_blocked` | 1 | `attempt`~, `first_load`~, `redirect_vendor`~ | 0 | call-03671 |
| `desktop_main_view_render_process_gone` | 1 | `exit_code`~, `main_rss_bytes`~, `reason`~, `reload_attempt`~, `surface`~, `web_commit_hash`~ | 1 | call-03678 |
| `desktop_main_view_unresponsive` | 1 | `main_rss_bytes`~, `print_call`~, `surface`~, `web_commit_hash`~ | 3 | call-03675 |
| `desktop_main_view_unresponsive_kill_skipped` | 1 | `print_call_age_ms`~, `surface`~, `web_commit_hash`~ | 0 | call-03676 |
| `desktop_managed_config_unreadable` | 1 | `fs_error_code`~, `plist_scope`~ | 0 | call-03802 |
| `desktop_mcp_tool_call_gate` | 1 | `basis`~, `session_id`~, `tool_name`~ | 0 | call-03078 |
| `desktop_mcp_unexpected_close` | 1 | `extension_id`~, `extension_name`~, `extension_version`~, `mcp_cmd`~ | 0 | call-03856 |
| `desktop_mdm_config_detected` | 1 | `keys_set`~ | 0 | call-03801 |
| `desktop_media_permission_probe` | 1 | `capture_kind`~, `is_main_frame`~, `occurrence`~, `requesting_site`~, `result`~, `via`~ | 0 | call-04090 |
| `desktop_notification_displayed` | 2 | `backend`~ | 2 | call-03744, call-03747 |
| `desktop_notification_failed` | 3 | `backend`~, `error_kind`~ | 3 | call-03745, call-03746, call-03775 |
| `desktop_notification_interaction` | 10 | `action`~, `backend`~, `notification_type`~, `product`~, `session_grouping_id`~, `session_id`~, `tool_name`~ | 4 | call-03749, call-03750, call-03751, call-03752, call-03753, call-03760, call-03766, call-03773, call-03778, call-03780 |
| `desktop_notification_reachability` | 1 | `authorization`~, `backend`~, `supported`~, `trigger`~ | 0 | call-03748 |
| `desktop_notification_shown` | 8 | `backend`~, `has_action_buttons`~, `tool_name`~ | 18 | call-03759, call-03761, call-03765, call-03767, call-03772, call-03774, call-03777, call-03779 |
| `desktop_notification_suppressed` | 18 | `notification_type`~, `product`~, `reason`~, `session_grouping_id`~, `session_id`~ | 3 | call-03754, call-03755, call-03756, call-03757, call-03758, call-03762, call-03763, call-03764, call-03768, call-03769, call-03770, call-03771, call-03776, call-04121, call-04122, call-04123, call-04124, call-04125 |
| `desktop_oauth_return_navigate` | 3 | `surface`~ | 0 | call-03699, call-03700, call-03701 |
| `desktop_os_open_handlers_ready` | 1 | `acked`~, `ms_after_commit`~, `ms_after_load`~ | 0 | call-03682 |
| `desktop_os_surface_invoked` | 5 | `cold_start`~, `os_entry`~, `verb`~ | 0 | call-03688, call-03689, call-03697, call-03702, call-03704 |
| `desktop_preview_jitless_kill_switch_transition` | 3 | `contexts_destroyed`~, `reason`~, `state` | 0 | call-03863, call-03864, call-03865 |
| `desktop_process_memory_high_water` | 3 | `bucket_gb`~, `bucket_pct_of_ram`~, `reason` | 8 | call-03924, call-03925, call-03926 |
| `desktop_process_memory_over_ram` | 1 | `ccd_live_cli_count`~ | 1 | call-03927 |
| `desktop_process_memory_sample` | 1 | `launch_sample_rate`~, `main_view_footprint_bytes`~, `main_view_rss_bytes`~, `sample_index`~, `top1_footprint_bytes`~, `top2_footprint_bytes`~, `top3_footprint_bytes`~ | 4 | call-03923 |
| `desktop_project_detection_failed` | 1 | `duration_ms`~, `error_message`~, `trigger` | 0 | call-03036 |
| `desktop_quick_entry_dictation_start` | 1 |  | 0 | call-03742 |
| `desktop_quick_entry_show` | 2 |  | 0 | call-03741, call-03845 |
| `desktop_quick_entry_submit` | 1 | `quick_entry_images`~, `quick_entry_length`~ | 0 | call-03846 |
| `desktop_quit_cleanup_summary` | 1 |  | 0 | call-03653 |
| `desktop_quit_guard_prompt` | 1 | `choice`~, `context`~, `open_seconds`~, `running_sessions`~, `still_running_sessions`~ | 1 | call-03634 |
| `desktop_quit_handler_timeout` | 1 | `pending_handlers`~ | 0 | call-03655 |
| `desktop_quit_watchdog_fired` | 1 | `timeout_ms`~ | 0 | call-03656 |
| `desktop_sable_otter` | 1 |  | 0 | call-03139 |
| `desktop_sable_otter_kept` | 1 | `action`~ | 0 | call-03140 |
| `desktop_secure_storage_unavailable` | 1 | `backend`~ | 0 | call-04091 |
| `desktop_session_title_set` | 1 | `cli_session_id`~, `had_title`?~, `previous_title_source`?~, `seconds_since_create`~, `session_id`~, `session_title`~, `session_type`~, `title_source`~, `trigger`~ | 1 | call-03047 |
| `desktop_show_in_folder` | 2 | `outcome`~, `tcc_folder_kind`~ | 0 | call-03843, call-03844 |
| `desktop_ssh_admin_mcp_held_back` | 1 | `clash`~, `held_count`~, `held_ms`~, `lock_known_locked`~, `remote_control_on`~, `session_id`~ | 0 | call-03546 |
| `desktop_ssh_adoptable_redial` | 1 | `attempts`~, `held_ms`~, `phase`~, `redial_seq`~ | 0 | call-03435 |
| `desktop_ssh_auto_reconnected` | 2 | `attempts`~, `backend_kind`~, `close_trigger`~, `duration_ms`~, `ended_by`, `preprobe_via`?~, `repair_shown`~, `ssh_transport`~, `ssh_transport_flag_state`~, `woken_by`~ | 1 | call-03225, call-03229 |
| `desktop_ssh_background_readopt` | 1 | `adopted`~, `attempted`~, `candidates`~, `declined`~, `gone`~, `host_count`~, `policy_gate_passed`~, `skipped`~ | 0 | call-03433 |
| `desktop_ssh_cold_send_held` | 2 | `attachment_bytes`~, `attachments`~, `backend_kind`~, `error_class`~, `failure_reason`~, `first_turn`?~, `held_count`~, `session_id`~ | 3 | call-03379, call-03380 |
| `desktop_ssh_cold_send_rearmed` | 1 | `backend_kind`~, `first_turn`?~, `held_count`~, `origin`~, `session_id`~ | 2 | call-03381 |
| `desktop_ssh_cold_send_released` | 1 | `attempts`~, `backend_kind`~, `failure_reason`?~, `first_turn`?~, `held_ms`~, `outcome`~, `resumed_after_attention`?~, `session_id`~, `sign_in_waits`?~ | 5 | call-03376 |
| `desktop_ssh_cold_send_sign_in_redelivery` | 1 | `hosts`, `late`~, `sessions` | 0 | call-03375 |
| `desktop_ssh_cold_send_stalled` | 1 | `backend_kind`~, `error_category`~, `session_id`~ | 0 | call-03374 |
| `desktop_ssh_connect_awaiting_person` | 1 | `backend_kind`~, `cause`~, `connect_attempt`~, `disposition`~, `duration_ms`~, `legacy_user_waiting`~, `prompt_asker`?~, `prompt_kind`~, `prompt_origin`~, `prompt_rendered`~, `ssh_transport`~, `ssh_transport_flag_state`~, `ssh_transport_flag_wait_ms`~, `trigger`~, `unattended`~, `user_waiting`~, `waited_ms`~ | 3 | call-03212 |
| `desktop_ssh_connect_interrupted` | 1 | `backend_kind`~, `dial_context_version`, `disposition`~, `elapsed_ms`~, `fired_by`~, `generation_age_ms`~, `interrupt_seq`~, `legacy_user_waiting`~, `overdue_ms`~, `ssh_transport`~, `ssh_transport_flag_state`~, `step`~, `step_budget_ms`~, `trigger`~, `unattended`~, `user_waiting`~ | 2 | call-03214 |
| `desktop_ssh_connected` | 1 | `abandoned_processes`~, `adopted_first_attempt`?~, `auth_auto_retry`?, `auth_method`~, `backend_kind`~, `cli_fetch_bytes`?~, `cli_fetch_failure`?~, `cli_fetch_fell_back`?~, `cli_fetch_longest_pause_ms`?~, `cli_fetch_ms`?~, `cli_install_source`?~, `cli_upload_bytes`?~, `cli_upload_folder_not_plain`?~, `cli_upload_longest_pause_ms`?~, `cli_upload_ms`?~, `cli_upload_pauses`?~, `cli_upload_restarted_after_reject`?~, `cli_upload_resumed_from_bytes`?~, `client_run_id_source`~, `connect_attempt`~, `connection_generation`~, `daemon_instance_changed`?~, `daemon_instance_known`~, `daemon_upgrade`~, `duration_ms`~, `helper_peer_check`~, `launcher_status`?~, `legacy_user_waiting`~, `needed_deploy`~, `reattach_auth`~, `reattach_failed_reason`?~, `reattach_silent_retries`?~, `resolved_person_holds`?~, `reused_server`~, `ssh_client_launch_error_code`~, `ssh_transport`~, `ssh_transport_flag_state`~, `ssh_transport_flag_wait_ms`~, `ssh_transport_source`~, `ssh_windows_client_unusable_reason`~, `stop_outcome`?~, `tracked_processes`~, `trigger`~, `user_waiting`~, `windows_host_jobs`?~ | 20 | call-03217 |
| `desktop_ssh_connection_failed` | 1 | `adopted_first_attempt`?~, `auth_auto_retry`?, `auth_method`~, `backend_kind`~, `connect_attempt`~, `deploy_bytes_total`?~, `deploy_bytes_transferred`?~, `duration_ms`~, `error_class`~, `error_message`~, `failed_phase`?~, `failure_reason`~, `legacy_user_waiting`~, `prompt_origin`~, `prompt_outcome`~, `prompt_rendered`~, `proxy_diagnostic`~, `reattach_silent_retries`?~, `ssh_client_launch_error_code`~, `ssh_transport`~, `ssh_transport_flag_state`~, `ssh_transport_flag_wait_ms`~, `ssh_transport_source`~, `ssh_windows_client_unusable_reason`~, `trigger`~, `unattended`~, `user_waiting`~, `will_hold`?~, `will_retry`~, `wsl_error_code`?~ | 14 | call-03218 |
| `desktop_ssh_connection_skipped` | 2 | `backend_kind`~, `consecutive_failures`~, `last_error_class`~, `retry_in_ms`~, `trigger`~ | 0 | call-03210, call-03211 |
| `desktop_ssh_disconnected` | 2 | `auto_reconnect_attempts`~, `backend_kind`~, `connection_duration_ms`~, `error_class`~, `failure_reason`?~, `ssh_transport`~, `ssh_transport_flag_state`~, `trigger`~ | 1 | call-03219, call-03230 |
| `desktop_ssh_git_settings_control` | 1 | `backend_kind`~, `connection_generation`~, `daemon_version`~, `git_settings_control`~, `ssh_platform`~ | 0 | call-03209 |
| `desktop_ssh_host_mcp_failed_start_read` | 1 | `session_id`~ | 1 | call-03472 |
| `desktop_ssh_host_mcp_self_heal` | 2 | `attempt`~, `dialed`~, `reconnected`~, `session_id`~ | 0 | call-03382, call-03383 |
| `desktop_ssh_host_write_checks` | 1 | `adopts`~, `root_fenced`~, `root_named`~, `session_id`~ | 1 | call-03436 |
| `desktop_ssh_host_write_refused` | 1 | `permission_mode`~, `session_id`~, `target`~, `tool_name`~, `tool_use_id`~ | 0 | call-03437 |
| `desktop_ssh_identity_hold_ended` | 1 | `backend_kind`~, `ended_by`~, `failures`~, `held_ms`~, `hold_cause`~, `present_failures`~, `sign_in_reason`?~, `ssh_transport`~, `ssh_transport_flag_state`~ | 1 | call-03215 |
| `desktop_ssh_input_kept_across_loss` | 1 | `backend_kind`~, `cause`, `count`, `session_id`~, `written_unacked` | 0 | call-03500 |
| `desktop_ssh_kept_input_verdict` | 1 | `backend_kind`~, `ends_mid_turn`?~, `ms`~, `reason`?~, `session_id`~, `taken`?~, `trigger`~, `verdict`~ | 3 | call-03428 |
| `desktop_ssh_mcp_hook_servers_uncovered` | 1 | `hosted_count`~, `session_id`~, `uncovered_count`~ | 0 | call-03499 |
| `desktop_ssh_mirror_removed` | 2 | `failed`~, `folders`~, `kept_claimed_elsewhere`~, `newly_unclaimed`~, `reason`, `stood_down`~ | 0 | call-03432, call-03531 |
| `desktop_ssh_orphan_kill` | 1 | `abandoned_ms_ago`~, `already_exited`~, `daemon_instance`~, `daemon_version`~, `died`~, `duration_ms`~, `escalated`~, `found`~, `legacy_kill`~, `orphan_process_id`~, `retained`~, `rpc_error`~, `session_id`~, `ssh_platform`~ | 0 | call-03488 |
| `desktop_ssh_password_remembered` | 3 | `action`~, `backend_kind`~, `ssh_transport`~ | 0 | call-03177, call-03178, call-03213 |
| `desktop_ssh_plugin_sync_failed` | 2 | `backend_kind`, `error_message`~, `plugin_count`~, `stage`~, `synced_count`~ | 0 | call-03490, call-03491 |
| `desktop_ssh_process_dormant` | 1 | `backend_kind`~, `cause`?~, `cli_stderr_tail`?~, `dropped_ms_ago`~, `error_message`~, `exit_killed_by`?~, `exit_signal`?~, `has_cli_session_id`~, `is_resume`~, `message_buffer_size`~, `session_id`~ | 4 | call-03429 |
| `desktop_ssh_process_loss` | 1 | `backend_kind`~, `brake_rule`~, `cause`~, `chain_continues`~, `chain_starts`~, `connection_generation`~, `daemon_instance_known`~, `daemon_version`~, `decision`~, `exit_killed_by`?~, `exit_signal`?~, `first_block_streaming`~, `host_slot`~, `how`~, `link_up`~, `losses_this_round`~, `lost_input`~, `ms_since_first_cut`~, `ms_since_prior_loss`~, `orphan_process_id`~, `prior_loss_how`~, `process_instance_known`~, `recovery_granted_ms_ago`~, `rounds_last_day`~, `rounds_last_hour`~, `same_category_as_prior_loss`?~, `session_id`~, `spawn_confirmed`~, `stop_outcome`~, `verified_since_recovery`~, `was_mid_turn`~ | 4 | call-03434 |
| `desktop_ssh_process_reattached` | 1 | `backend_kind`~, `connection_generation`~, `daemon_version`~, `detached_ms`~, `is_fork`~, `outcome`~, `reattach_ms`~, `replayed_bytes`~, `replayed_frames`~, `running`~, `session_id`~, `was_mid_turn`~ | 0 | call-03486 |
| `desktop_ssh_reachability_watch` | 1 | `acts`~, `armed_by`~, `backend_kind`~, `duration_ms`~, `failed_acts`~, `outcome`~, `probes`~, `saw_unreachable`~, `ssh_transport`~, `ssh_transport_flag_state`~, `start_reason`~, `transitions_seen`~, `unknown_answers`~, `via`~ | 0 | call-03222 |
| `desktop_ssh_reattach_gap` | 1 | `abandon_reason`~, `backend_kind`~, `detached_ms`~, `first_seq`~, `from_seq`~, `is_fork`~, `outcome`~, `session_id`~, `was_mid_turn`~ | 0 | call-03487 |
| `desktop_ssh_reconnect_attempt` | 3 | `attempt`~, `backend_kind`~, `close_trigger`~, `dial_context_version`, `elapsed_ms`~, `error_class`~, `has_live_processes`~, `interrupted`~, `preprobe_hurried`?~, `presence`?~, `signals_ignored`~, `silent_reattach`~, `ssh_transport`~, `ssh_transport_flag_state`~, `unattended`~, `woken_by`~ | 9 | call-03226, call-03227, call-03228 |
| `desktop_ssh_reconnect_flapping` | 2 | `backend_kind`~, `backoff_ms`~, `close_count`~, `link_late_pongs`?~, `link_queued_pongs`?~, `link_srtt_ms`?~, `trigger`~ | 6 | call-03220, call-03221 |
| `desktop_ssh_reconnect_held` | 1 | `attempt`~, `away_at_failure`~, `backend_kind`~, `claims`~, `close_trigger`~, `failures`~, `live_processes`~, `present_failures`~, `reason`~, `sign_in_reason`?~, `skipped_offline`~, `ssh_transport`~, `ssh_transport_flag_state`~ | 1 | call-03216 |
| `desktop_ssh_reconnect_needs_attention` | 1 | `backend_kind`~, `error_class`~, `failure_reason`?~, `live_processes`~, `reason`~, `ssh_transport`~ | 1 | call-03223 |
| `desktop_ssh_reconnect_prolonged` | 1 | `attempts`~, `backend_kind`~, `close_trigger`~, `elapsed_ms`~, `error_class`~, `live_processes`~, `ssh_transport`~ | 0 | call-03224 |
| `desktop_ssh_relaunch_reattach` | 2 | `away_ms`~, `backend_kind`~, `daemon_version`~, `decide_ms`~, `gap`~, `hook_sig_match`~, `hooks_applied`~, `init_ms`~, `mcp_kind_followed`~, `outcome`~, `rc_intent`~, `rc_reconciled`~, `rc_recorded`~, `rc_roundtrip_ms`~, `rc_wait_ms`~, `reattach_answer_ms`~, `replay`~, `replayed_frames`~, `session_id`~, `settle_ms`~, `slot_wait_ms`~, `total_ms`~, `trigger`~, `was_mid_turn`~ | 0 | call-03356, call-03489 |
| `desktop_ssh_sandbox_check_failed` | 1 | `backend_kind`, `reason`~, `sandbox_on`~, `session_id`~ | 0 | call-03427 |
| `desktop_ssh_scheduled_run_released` | 1 | `failures`~, `reason`~, `released_by`~, `waited_minutes`~ | 0 | call-03963 |
| `desktop_ssh_scheduled_run_wait` | 1 | `failures`~, `one_time`~ | 1 | call-03962 |
| `desktop_ssh_send_answered_from_last_failure` | 1 | `backend_kind`~, `error_class`~, `failure_age_ms`~, `failure_reason`~, `has_origin`~ | 0 | call-03507 |
| `desktop_ssh_tool_grant_changed` | 2 | `action`~, `count`~ | 0 | call-03430, call-03431 |
| `desktop_ssh_wake_probe` | 1 | `backend_kind`~, `busy`~, `decided_by`~, `decision_ms`~, `frozen_ms`?~, `kept`~, `link_age_ms`?~, `ping_ms`?~, `probe_trigger`~, `replaced_by`?~, `slept_ms`?~, `ssh_transport`?~ | 6 | call-03208 |
| `desktop_startup_sign_in_state` | 1 |  | 0 | call-04092 |
| `desktop_stealth_update_triggered` | 1 | `pending_hours`~ | 0 | call-04141 |
| `desktop_third_party_history_import` | 1 |  | 0 | call-03591 |
| `desktop_universal_link_bounced` | 1 | `bounce_reason`~, `route_prefix`~ | 0 | call-03709 |
| `desktop_universal_link_received` | 1 | `route_prefix`~ | 0 | call-03710 |
| `desktop_update_applied` | 1 | `from_version`~, `is_downgrade`~, `payload_arch`~, `payload_kind`~, `to_version`~ | 0 | call-03853 |
| `desktop_update_available` | 2 | `current_version`~, `target_version`~, `update_channel`~ | 0 | call-03850, call-03854 |
| `desktop_update_check_started` | 1 | `current_version`~, `is_manual`~, `update_channel`~ | 0 | call-03849 |
| `desktop_update_disabled` | 1 | `reason` | 0 | call-03855 |
| `desktop_update_downloaded` | 1 | `current_version`~, `duration_ms`~, `feed_arch`~, `payload_arch`~, `payload_kind`~, `update_version`~ | 0 | call-03852 |
| `desktop_update_error` | 1 | `current_version`~, `duration_ms`~, `payload_kind`~, `phase`~, `target_version`~, `update_channel`~ | 1 | call-03848 |
| `desktop_update_install_failed` | 1 | `attempt`~, `from_version`~, `payload_arch`~, `payload_kind`~, `shipit_stderr_tail`~, `to_version`~, `update_channel`~ | 0 | call-03847 |
| `desktop_update_manual_install` | 1 | `pending_hours`~, `source`~, `update_version`~ | 0 | call-03654 |
| `desktop_update_not_available` | 1 | `current_version`~, `is_manual`~, `update_channel`~ | 0 | call-03851 |
| `desktop_update_relaunch_marker_read` | 1 | `marker_age_ms`~, `nav_only`~, `stale`~ | 0 | call-03711 |
| `desktop_update_required` | 1 | `auto_updates_disabled`~, `refused_route`~ | 0 | call-03144 |
| `desktop_update_stealth_install` | 1 | `pending_hours`~, `update_version`~ | 0 | call-04142 |
| `desktop_wake_scheduler_darkwake_detected` | 1 | `chain_active`~, `jump_ms`~, `on_battery`~ | 0 | call-03732 |
| `desktop_wake_scheduler_disabled` | 2 | `reason`~, `status_before`~ | 0 | call-03737, call-03738 |
| `desktop_wake_scheduler_resume_correlation` | 1 | `delta_ms`~, `likely_ours`~, `on_battery`~ | 0 | call-03736 |
| `desktop_wake_scheduler_schedule_failed` | 1 | `io_return`~, `on_battery`~ | 0 | call-03734 |
| `desktop_wake_scheduler_scheduled` | 1 | `claim_count`~, `clamped`~, `lead_time_ms`~, `on_battery`~, `requested_lead_time_ms`~ | 0 | call-03733 |
| `desktop_wake_scheduler_wake_duration` | 1 | `on_battery`~, `resume_was_ours`~, `wake_duration_ms`~ | 0 | call-03735 |
| `desktop_window_open_passthrough` | 1 | `dropped_since_last`~ | 1 | call-03680 |
| `desktop_windows_app_job_check` | 1 | `first_child_in_job`~ | 0 | call-04144 |
| `device_registry_no_tpm_probe_code` | 1 | `no_tpm_probe_code`~ | 0 | call-03921 |
| `device_registry_unavailable_probe_code` | 1 | `unavailable_probe_code`~, `unavailable_probe_reason`~ | 0 | call-03922 |
| `dispatch_memory_migration_declined` | 2 | `decline_failure`~, `decline_outcome`~ | 0 | call-03249, call-03250 |
| `dispatch_memory_migration_export_folder` | 1 | `duration_ms`~, `failure_stage`~, `migration_status`~, `refusal_reason`?, `scheduled_tasks_outcome`?~ | 2 | call-03242 |
| `dispatch_memory_migration_preview` | 3 | `already_migrated`~, `excluded_count`~, `failure_stage`~, `file_count`~, `has_local_data`?~, `history_available`~, `refusal_reason`?~, `total_bytes`~ | 3 | call-03246, call-03247, call-03248 |
| `dispatch_memory_migration_run` | 1 | `duration_ms`~, `first_completion`~, `history_included`~, `memory_complete`?~, `memory_outcome`?~, `migration_status`~, `mode`~, `refusal_reason`?~, `server_contacted`~, `status`~, `trigger`~ | 5 | call-03245 |
| `dispatch_memory_migration_run_started` | 1 | `engine_version`, `history_requested`~, `mode`~, `trigger`~ | 0 | call-03244 |
| `grand_prix_code_prompt_outcome` | 1 | `duration_ms`~, `partner_id`~, `session_id`~, `status`~ | 0 | call-03724 |
| `grand_prix_credential_request_outcome` | 1 | `channel_error`?~, `channel_ms`?~, `channel_recreate_ms`?~, `channel_retry`?~, `channel_retry_code`?~, `duration_ms`~, `entry_count`?~, `first_attempt_ms`?~, `has_address`?~, `has_card`?~, `has_login`?~, `leg`?~, `partner_code`?~, `partner_id`?~, `reason`?~, `relay_error`?~, `reply_key_count`?~, `reply_shape`?~, `result_key_count`?~, `result_shape`?~, `second_attempt_ms`?~, `session_id`~, `source`~, `status`~ | 5 | call-03716 |
| `grand_prix_disconnect` | 1 | `had_entry`~, `partner_id`~ | 0 | call-03714 |
| `grand_prix_nudge` | 1 | `partner_id`~, `renewed`~ | 0 | call-03712 |
| `grand_prix_pair_outcome` | 1 | `duration_ms`~, `error`?~, `paired`~, `partner_app_running`?~, `partner_id`~, `previously_paired`~, `source`?~, `unrecognized_partner_code`?~ | 4 | call-03713 |
| `grand_prix_stub_response` | 5 | `downgrade`~, `partner_id`~, `reason`, `waited`~ | 0 | call-03717, call-03718, call-03719, call-03720, call-03721 |
| `grand_prix_teardown` | 1 | `releases_sent`, `scoped`~, `seeds`~, `trigger`~ | 0 | call-03715 |
| `grand_prix_tool_refused` | 2 | `partner_id`~, `reason`, `role`~ | 0 | call-03722, call-03723 |
| `lam_auto_mode_always_allow_overridden` | 3 | `request_id`~, `session_id`~, `session_type`, `source`, `tool_name`~ | 0 | call-03268, call-04028, call-04030 |
| `lam_bridge_abandon_deregister` | 1 | `duration_ms`~, `outcome`~ | 1 | call-03988 |
| `lam_bridge_call_refused` | 1 | `refusal_reason`~, `refused_by`~, `tool_group`~ | 1 | call-03930 |
| `lam_bridge_call_refused_identity_moved` | 1 | `phase`~ | 0 | call-03929 |
| `lam_bridge_call_wait_capped` | 1 | `capped_lookups`~, `lookups`~, `tool_group`~, `waited_ms_bucket`~ | 1 | call-03931 |
| `lam_bridge_device_reload` | 1 | `cause`~, `drain_wait_ms`~ | 0 | call-03934 |
| `lam_bridge_dispatch_seed_skipped` | 2 | `reason`, `session_id`~ | 0 | call-04007, call-04008 |
| `lam_bridge_dispatch_seed_written` | 1 | `seed_count`~, `session_id`~ | 0 | call-04009 |
| `lam_bridge_event_attestation` | 1 | `action`~, `enforce`~, `payload_type`~, `status`~ | 0 | call-03592 |
| `lam_bridge_followup_fast_path` | 2 | `local_session_id`~, `message_uuid`~, `outcome`, `session_id`~ | 0 | call-04015, call-04016 |
| `lam_bridge_ingress_token_refresh` | 1 | `outcome`?~, `session_id`~, `trigger`~ | 1 | call-04011 |
| `lam_bridge_interrupt_received` | 3 | `local_session_id`~, `outcome`, `request_id`~, `session_id`~ | 0 | call-04018, call-04019, call-04020 |
| `lam_bridge_local_mcp_retry` | 1 | `attempt`~, `duration_ms`~, `failure_class`~, `phase`~, `server_name`~, `server_source`~, `success`~ | 0 | call-03251 |
| `lam_bridge_message_forwarded` | 1 | `duration_ms`~, `is_error`~, `local_session_id`~, `message_type`~, `message_uuid`~, `session_id`~, `user_message_uuid`~ | 0 | call-04038 |
| `lam_bridge_permission_auto_denied` | 9 | `local_session_id`~, `preflight_outcome`~, `reason`~, `session_id`~, `tool_name`~ | 0 | call-04026, call-04029, call-04031, call-04032, call-04033, call-04034, call-04036, call-04037, call-04039 |
| `lam_bridge_permission_posted` | 1 | `local_session_id`~, `preflight_outcome`~, `session_id`~, `tool_name`~ | 0 | call-04035 |
| `lam_bridge_permission_resolved` | 1 | `behavior`~, `latency_ms`~, `local_session_id`~, `session_id`~, `tool_name`~ | 0 | call-04017 |
| `lam_bridge_poll_gave_up` | 1 | `attempts`~, `environment_id`~, `status`~ | 0 | call-03999 |
| `lam_bridge_poll_reregister` | 1 | `attempt`~, `environment_id`~, `status`~ | 0 | call-04000 |
| `lam_bridge_reconnect_persisted_session` | 2 | `environment_id`~, `outcome`~, `session_id`~ | 0 | call-04040, call-04041 |
| `lam_bridge_registration_completed` | 1 | `duration_ms`~, `environment_id`~, `reused_environment`~ | 0 | call-03989 |
| `lam_bridge_registration_failed` | 9 | `attempt`~, `attempts`~, `error_kind`~, `status`~, `will_retry`~ | 0 | call-03990, call-03991, call-03992, call-03993, call-03994, call-03995, call-03996, call-03997, call-03998 |
| `lam_bridge_session_bound` | 1 | `is_resumed_session`~, `local_session_id`~, `session_id`~, `work_id`~ | 0 | call-04004 |
| `lam_bridge_session_collision` | 1 | `displaced_pending_turns`~, `displaced_session_id`~, `local_session_id`~, `session_id`~ | 0 | call-04003 |
| `lam_bridge_session_created` | 2 | `duration_ms`~, `environment_id`~, `outcome`, `session_id`~, `trigger`~ | 0 | call-04042, call-04043 |
| `lam_bridge_stale_turn_rearm` | 1 | `local_session_id`~, `pending_turns`~, `session_id`~ | 0 | call-04024 |
| `lam_bridge_stale_turn_reset` | 1 | `local_session_id`~, `pending_turns`~, `reconnect_triggered`~, `session_id`~, `stranded_messages`~ | 0 | call-04025 |
| `lam_bridge_stop_task_received` | 3 | `local_session_id`~, `outcome`, `request_id`~, `session_id`~ | 0 | call-04021, call-04022, call-04023 |
| `lam_bridge_system_resumed` | 1 | `active_session_count`~, `bridge_was_dead`~ | 0 | call-04027 |
| `lam_bridge_transport_cap_redispatch` | 1 | `attempt`~, `local_session_id`~, `outcome`~, `session_id`~ | 0 | call-04013 |
| `lam_bridge_transport_closed` | 1 | `close_code`~, `local_session_id`~, `pending_turns`~, `session_id`~, `uptime_ms`~ | 0 | call-04005 |
| `lam_bridge_transport_connected` | 1 | `attempt`~, `duration_ms`~, `is_reconnect`~, `local_session_id`~, `session_id`~ | 0 | call-04006 |
| `lam_bridge_transport_dead` | 1 | `local_session_id`~, `redispatch_attempts`~, `session_id`~ | 0 | call-04012 |
| `lam_bridge_transport_reconnect_capped` | 1 | `attempts`~, `local_session_id`~, `redispatch_attempt`~, `session_id`~ | 0 | call-04010 |
| `lam_bridge_unexpected_v1_work` | 2 | `session_id`~, `work_id`~ | 0 | call-04001, call-04002 |
| `lam_bridge_user_message_received` | 1 | `local_session_id`~, `message_uuid`~, `session_id`~ | 0 | call-04014 |
| `lam_cli_plugin_oauth` | 4 | `cli_hash`~, `duration_ms`~, `error_code`~, `phase`~, `plugin_id`~, `purpose`?~ | 1 | call-03637, call-03638, call-03639, call-03641 |
| `lam_cli_plugin_stub_provision` | 1 | `duration_ms`~, `error_code`~, `expected_count`~, `fast_path`~, `plugin_id`~, `source`~, `status`~, `written_count`~ | 0 | call-03912 |
| `lam_cowork_managed_dirs_migration` | 1 | `adopted`~, `bytes`~, `dry_run`~, `elapsed_ms`~, `error_class`?~, `files`~, `outcome`~, `still_live`~ | 1 | call-03986 |
| `lam_dispatch_list_projects` | 1 | `parent_session_id`~, `project_count`~ | 0 | call-03207 |
| `lam_dispatch_send_message` | 3 | `error_message`~, `parent_session_id`~, `success`~, `target_is_child`~, `target_kind`~, `target_session_id`~ | 0 | call-03204, call-03205, call-03206 |
| `lam_dispatch_start_code_task` | 3 | `child_session_id`~, `error_message`~, `error_name`~, `parent_session_id`~, `success`~ | 0 | call-03201, call-03202, call-03203 |
| `lam_dispatch_start_task` | 5 | `child_session_id`~, `error_message`~, `parent_session_id`~, `space_id`~, `success`~ | 0 | call-03196, call-03197, call-03198, call-03199, call-03200 |
| `lam_escalated_tool_ask` | 1 | `outcome`~, `session_id`~, `session_type`, `tool_family`, `tool_name`~ | 0 | call-03243 |
| `lam_feature_support_evaluated` | 1 | `feature`, `status`~, `unsupported_code`~ | 0 | call-03739 |
| `lam_folder_grant_refused_protected` | 1 | `refused_kind`?~, `refused_other`~, `root_kind`~, `surface`~ | 1 | call-03573 |
| `lam_held_routine_release` | 1 |  | 0 | call-04116 |
| `lam_hipaa_gate_blocked` | 13 | `reason`?~, `surface`~ | 1 | call-03035, call-03054, call-03071, call-03072, call-03096, call-03098, call-03260, call-03615, call-03648, call-03725, call-03782, call-03972, call-04094 |
| `lam_hipaa_log_retention_pass` | 1 |  | 0 | call-03590 |
| `lam_hipaa_pref_synced` | 1 | `ms_since_app_ready`~, `value_at_ready`~, `value_on_sync`~ | 0 | call-03624 |
| `lam_hipaa_session_retention_pass` | 1 |  | 0 | call-03561 |
| `lam_host_loop_spawn_settings_swept` | 1 |  | 0 | call-03264 |
| `lam_internal_mcp_server_created` | 1 | `always_load_tool_count`~, `chrome_cu_inlined`~, `server_name`~, `server_uuid`~, `session_type`~, `tool_count`~ | 0 | call-03077 |
| `lam_mcp_server_connected` | 2 | `duration_ms`~, `server_name`~, `server_source`~, `server_type`, `session_id`~, `tool_count`~ | 1 | call-03038, call-03103 |
| `lam_mcp_server_connection_failed` | 5 | `declared_tools_capability`~, `duration_ms`~, `error_category`~, `error_message`~, `error_type`, `server_name`~, `server_source`~, `server_type`, `session_id`~ | 2 | call-03037, call-03039, call-03099, call-03102, call-03104 |
| `lam_mcp_server_disconnected` | 2 | `error_message`~, `reason`, `server_name`~, `server_source`~, `server_type`, `session_id`~ | 0 | call-03100, call-03101 |
| `lam_mcp_servers_setup_summary` | 1 | `duration_ms`~, `internal_server_count`~, `local_server_count`~, `local_servers_filtered`~, `remote_server_count`~, `reserved_names_dropped`~, `session_id`~, `session_type`~, `total_server_count`~ | 0 | call-03085 |
| `lam_mcp_tool_call_completed` | 23 | `duration_ms`~, `error_code`~, `error_type`?~, `http_status`~, `internal_server_name`~, `is_error`~, `is_hub_chat`~, `needed_reconnect`~, `output_schema_unchecked`?~, `request_id`~, `result_byte_size`~, `server_name`~, `server_type`~, `server_uuid`~, `session_id`~, `session_type`~, `tool_name`~, `user_message_uuid`~ | 23 | call-03026, call-03040, call-03041, call-03042, call-03073, call-03075, call-03076, call-03079, call-03080, call-03081, call-03082, call-03083, call-03084, call-03088, call-03095, call-03105, call-03106, call-03108, call-03109, call-03193, call-03241, call-03261, call-03569 |
| `lam_mcp_tool_call_stalled` | 2 | `seconds_waiting`~, `server_name`~, `server_type`, `server_uuid`~, `session_id`~, `session_type`~, `tool_name`~, `user_message_uuid`~ | 1 | call-03074, call-03107 |
| `lam_model_selection_fallback` | 1 | `reason`~, `rejected_model`~, `session_id`~, `source`~ | 0 | call-03987 |
| `lam_plugin_binary_asset_provision` | 1 | `already_present_count`~, `cache_hit_count`~, `download_count`~, `duration_ms`~, `error_code`~, `expected_count`~, `placed_count`~, `plugin_id`~, `source`~, `status`~ | 0 | call-03253 |
| `lam_porter_handoff_claim_binding` | 1 | `outcome`~, `sealed`~ | 0 | call-03097 |
| `lam_project_sync_failed` | 1 | `error_message`~, `project_uuid`~, `session_id`~ | 0 | call-04117 |
| `lam_remote_auto_save` | 1 | `by_path_count`~, `duration_ms`~, `file_count`~, `parent_session_id`~ | 1 | call-04157 |
| `lam_remote_commit` | 1 | `duration_ms`~, `error_message`~, `mount_alias_count`?~, `parent_session_id`~, `rejected_count`~, `success`~, `wall_clock_ms`~, `written_count`~ | 4 | call-04156 |
| `lam_remote_create_artifact` | 1 | `error_message`~, `parent_session_id`~, `success`~ | 1 | call-04158 |
| `lam_remote_files_api_attachment_staged` | 2 | `arm`, `elevated_auth_code`?~, `failed_count`~, `retry_429_count`~, `staged_count`~, `total_bytes`~ | 3 | call-03269, call-03270 |
| `lam_remote_folder_consent_outcome` | 1 | `parent_session_digest`?~ | 2 | call-03263 |
| `lam_remote_folder_grant_changed` | 1 | `action`~, `folder_count_after`~, `parent_session_id`~, `principal_kind`~, `row_pk_resolved`~ | 0 | call-04153 |
| `lam_remote_folder_markers` | 1 | `already_granted`~, `folders_in_batch`~, `has_claude_dir`?~, `has_claude_local_md`?~, `has_claude_md`?~, `has_claude_memory`?~, `has_dot_claude_claude_md`?~, `has_memory_md`?~, `n_skills`?~, `n_skills_capped`?~, `not_present_error_code`?~, `not_present_reason`?~, `parent_session_id`~, `root_readable`?~, `scan_outcome`~, `stage_failure_reason`?~, `staged_claude_md`~, `staged_reason`~ | 6 | call-03271 |
| `lam_remote_folder_skills_staged` | 1 | `anchor_staged`?~, `bytes_staged_bucket`?~, `duration_ms`?~, `files_push_failed`?~, `files_upload_failed`?~, `folders_in_batch`~, `has_skills_dir`?~, `mode`~, `parent_session_id`~, `scan_outcome`~, `skills_found`?~, `skills_staged`?~, `skipped_count_capped`?~, `skipped_file_count`?~, `skipped_folder_budget`?~, `skipped_fs_error`?~, `skipped_hygiene`?~, `skipped_oversize_file`?~, `skipped_path_depth`?~, `skipped_placeholder_suspect`?~ | 2 | call-03272 |
| `lam_remote_get_device_info` | 1 | `connected_folders_count`~, `home_dir_count`?~, `local_mcp_truncated`?~, `parent_session_id`~, `platform`~ | 5 | call-03933 |
| `lam_remote_list_artifacts` | 1 | `error_message`~, `parent_session_id`~, `success`~ | 1 | call-04160 |
| `lam_remote_list_dir` | 1 | `entry_count`~, `error_message`~, `mount_alias`?~, `parent_session_id`~, `skeleton`?~, `success`~ | 3 | call-04154 |
| `lam_remote_stage` | 1 | `artifact_count`~, `cloud_hydrated_count`?~, `cloud_placeholder_count`?~, `dispatched_count`~, `duration_ms`~, `elevated_auth_code`~, `error_message`~, `fail_count`~, `file_count`~, `mount_alias_count`?~, `ok_count`~, `parent_session_id`~, `path_count`~, `save_back_denied_count`?~, `save_back_locked_count`?~, `success`~, `total_bytes`~, `wall_clock_ms`~ | 8 | call-04155 |
| `lam_remote_tools_device_state` | 1 |  | 0 | call-03932 |
| `lam_remote_update_artifact` | 1 | `error_message`~, `parent_session_id`~, `success`~ | 1 | call-04159 |
| `lam_session_deletion_failed` | 1 | `session_id`~ | 0 | call-03267 |
| `lam_sessions_cache_prune` | 1 | `error_count`~, `free_bytes`~, `freed_bytes`~, `pruned_session_count`~, `skipped_session_count`~, `trigger`~ | 0 | call-03907 |
| `lam_sessions_disk_cleanup` | 3 | `deleted_count`~, `error_count`~, `kind`, `orphan_dir_count`~, `outcome` | 0 | call-03909, call-03910, call-03911 |
| `lam_sessions_disk_low` | 1 | `free_bytes`~, `orphan_bytes`~, `orphan_dir_count`~, `session_dir_count`~, `total_bytes`~ | 0 | call-03908 |
| `lam_site_access_request_completed` | 1 | `had_standing_grant`~, `is_financial`~, `is_high_risk`~, `outcome`~, `served_over_bridge`~, `wait_ms`?~ | 2 | call-03262 |
| `lam_space_memory_tool_call` | 1 | `has_session`~, `ok`~, `tool`~ | 1 | call-04162 |
| `lam_stop_button_completed` | 1 | `duration_ms`~, `error_message`~, `ok`~, `session_id`~ | 0 | call-03266 |
| `lam_stop_button_received` | 1 | `cli_session_id`~, `session_id`~, `was_running`~ | 0 | call-03265 |
| `lam_storage_cleanup` | 1 | `bytes`~, `cancelled`~, `candidate_count`~, `deleted_count`~, `failed_count`~, `failed_in_use_count`~, `older_than_days`~, `skipped_count`~, `trigger`?~ | 1 | call-04044 |
| `lam_tool_permission_renotify` | 1 | `context_tokens`~, `outcome`~, `pending_ms`~, `permission_mode`~, `request_id`~, `session_id`~, `session_type`, `tool_name`~ | 0 | call-03302 |
| `lam_tool_permission_requested` | 1 | `agent_id`~, `decision_reason`~, `force_ask_cause`~, `permission_mode`~, `permission_surface`~, `request_id`~, `session_id`~, `session_type`, `tool_name`~, `user_message_uuid` | 0 | call-03345 |
| `lam_tool_permission_responded` | 1 | `always_scope`?~, `context_tokens`~, `decision`~, `latency_bucket`~, `latency_ms`~, `permission_mode`~, `permission_surface`~, `request_id`~, `session_id`~, `session_type`, `tool_name`~, `user_message_uuid` | 1 | call-03301 |
| `lam_tool_permission_stalled` | 1 | `permission_mode`~, `permission_surface`~, `request_id`~, `seconds_waiting`, `session_id`~, `session_type`, `tool_name`~, `user_message_uuid` | 0 | call-03346 |
| `lam_vm_auto_reinstall_triggered` | 1 | `bundle_version`~, `error_message`~, `vm_instance_id`~ | 0 | call-03835 |
| `lam_vm_bundle_delta_applied` | 1 | `bundle_version`~, `cache_written`~, `delta_size_bytes`~, `duration_ms`~, `file_name`~, `from_bundle_version`~, `full_size_bytes`~ | 0 | call-03814 |
| `lam_vm_bundle_delta_failed` | 1 | `bundle_version`~, `duration_ms`~, `error_message`~, `failure_reason`~, `file_name`~, `from_bundle_version`~ | 0 | call-03813 |
| `lam_vm_bundle_download_completed` | 2 | `bundle_version`~, `download_reason`~, `download_size_bytes`~, `duration_ms`~, `resumed_from_byte`~, `via_delta`~ | 0 | call-03827, call-03828 |
| `lam_vm_bundle_download_failed` | 1 | `bundle_version`~, `download_reason`~, `download_size_bytes`~, `duration_ms`~, `error_message`~, `resumed_from_byte`~ | 0 | call-03829 |
| `lam_vm_bundle_sweep` | 1 | `bundle_version`~, `leftovers`~, `preserved_partials`~, `reclaimed_bytes`~, `stale_partials`~, `trigger`~ | 0 | call-03821 |
| `lam_vm_cache_decompress_completed` | 1 | `bundle_version`~, `duration_ms`~, `file_name`~ | 0 | call-03823 |
| `lam_vm_cache_decompress_failed` | 2 | `bundle_version`~, `duration_ms`~, `error_message`~, `failure_reason`~, `file_name`~ | 0 | call-03822, call-03824 |
| `lam_vm_download_skipped_nospace` | 1 | `arch`~, `available_disk_space_bytes`~, `bundle_version`~, `platform`~, `reclaimable_bytes`~, `required_disk_space_bytes`~ | 0 | call-03826 |
| `lam_vm_edr_extension_install_completed` | 1 |  | 0 | call-03935 |
| `lam_vm_edr_extension_install_failed` | 1 |  | 0 | call-03936 |
| `lam_vm_heartbeat_failure` | 1 | `bundle_version`~, `consecutive_failures`~, `interval_ms`~, `timeout_ms`~, `trigger`~, `vm_instance_id`~ | 0 | call-03815 |
| `lam_vm_kernel_bug_detected` | 1 | `bug_type`~, `error_line`~, `jetsam_pressure_level`~, `kernel_context`~, `vm_instance_id`~, `vz_footprint_bytes`~ | 0 | call-03810 |
| `lam_vm_oneshot_exited` | 1 | `kind`~, `spawn_ack_ms`?~, `timed_out`~ | 2 | call-03816 |
| `lam_vm_oneshot_spawn_failed` | 1 | `kind`~, `reason`~, `vm_instance_id`~, `waited_ms`~ | 0 | call-03817 |
| `lam_vm_oom_kill_detected` | 1 | `duration_ms`~, `oom_kill_count`~, `process_name`~, `session_id`~, `vm_instance_id`~ | 0 | call-03809 |
| `lam_vm_process_exited` | 1 | `session_id`~ | 1 | call-03811 |
| `lam_vm_process_spawned` | 1 | `failed_mount_count`~, `is_resume`~, `mount_count`~, `session_id`~, `spawn_duration_ms`~, `vm_instance_id`~ | 0 | call-03818 |
| `lam_vm_service_pipe_wait` | 1 | `attempts`~, `duration_ms`~, `outcome`~ | 0 | call-03647 |
| `lam_vm_shutdown_completed` | 2 | `bundle_version`~, `duration_ms`~, `trigger`~, `vm_instance_id`~ | 0 | call-03831, call-03836 |
| `lam_vm_shutdown_failed` | 2 | `bundle_version`~, `duration_ms`~, `trigger`~, `vm_instance_id`~ | 0 | call-03832, call-03837 |
| `lam_vm_startup_completed` | 1 | `bundle_version`~, `duration_ms`~, `is_fresh_download`~, `retry_reason`~, `vm_instance_id`~, `vm_ipv6`~, `vm_memory_gb`~ | 2 | call-03833 |
| `lam_vm_startup_failed` | 2 | `available_disk_space_bytes`~, `bootpd_running`~, `bridge_interfaces`~, `bundle_version`~, `connected_vpns`~, `console_tail`~, `diagnostic_error`~, `duration_ms`~, `error_message`~, `error_type`~, `failed_step`~, `is_fresh_download`~, `kernel_console_tail`~, `last_completed_step`~, `last_step_seen`~, `retry_reason`~, `service_log_tail`~, `vm_instance_id`~, `vpn_active`~, `vpn_interfaces`~ | 3 | call-03830, call-03834 |
| `lam_vm_startup_step` | 2 | `bundle_version`~, `duration_ms`~, `error_message`~, `status`, `step`~, `vm_instance_id`~ | 0 | call-03819, call-03820 |
| `lam_vm_warm_promote_completed` | 1 | `bundle_version`~, `duration_ms`~, `file_name`~ | 0 | call-03045 |
| `lam_vm_warm_promote_failed` | 2 | `bundle_version`~, `duration_ms`~, `error_message`~, `failure_reason`~, `file_name`~ | 0 | call-03044, call-03046 |
| `lam_vm_warm_promote_skipped_nospace` | 1 | `available_disk_space_bytes`~, `bundle_version`~, `compressed_size_bytes`~, `file_name`~, `required_disk_space_bytes`~ | 0 | call-03043 |
| `marketplace_plugin_account_sync_result` | 2 | `duration_ms`~, `error_code`~, `pass_trigger`~, `status`~ | 2 | call-03257, call-03258 |
| `marketplace_plugin_cli_error` | 9 | `error_category`~, `error_message`~, `exit_code`~, `operation`~, `raw_output`~, `target_id`~ | 0 | call-04045, call-04046, call-04047, call-04048, call-04049, call-04050, call-04051, call-04052, call-04053 |
| `marketplace_plugin_ipc_error` | 11 | `error_code`~, `error_message`~, `operation`, `plugin_id`~ | 0 | call-04054, call-04055, call-04056, call-04057, call-04058, call-04059, call-04060, call-04061, call-04062, call-04063, call-04064 |
| `marketplace_plugin_migration_done` | 1 | `posted_count`~, `skipped_count`~ | 0 | call-03182 |
| `marketplace_plugin_migration_retry` | 1 | `deferred_count`~, `failed_count`~ | 0 | call-03183 |
| `marketplace_plugin_op_result` | 3 | `attempt`~, `code_cli_running`~, `code_session_active`~, `cowork_session_active`~, `duration_ms`~, `error_code`?~, `implementation`~, `marketplace_uuid`~, `operation`~, `plugin_uuid`~, `stale_reason`?~, `status`~, `trigger`~, `vm_guest_connected`?~ | 10 | call-03256, call-04065, call-04066 |
| `marketplace_plugin_stub_manifest_detected` | 1 | `action`~, `plugin_uid`~, `plugin_updated_at`~ | 0 | call-03255 |
| `remote_plugin_enabled_migration_superseded` | 1 | `local_enabled`~, `server_enabled`~ | 0 | call-03254 |
| `remote_plugin_enabled_put_outcome` | 1 | `caller`~, `enabled`~, `outcome`~ | 1 | call-03181 |
| `remote_plugin_entry_pruned` | 1 | `caller`, `marketplace_uuid`?~, `plugin_uuid`~ | 1 | call-03259 |
| `ssh_terminal_sentinel_timeout` | 1 | `is_windows`~ | 0 | call-03577 |
| `unattended_serving_consent` | 6 | `action`, `surface` | 0 | call-03562, call-03563, call-03564, call-03565, call-03566, call-03567 |
