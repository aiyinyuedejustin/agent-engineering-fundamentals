# analytics_payload 完整有界字典

[返回索引](README.md)

位置数是语法计数。字段并集不是必填 schema；`?` 表示至少一处条件加入，`~` 表示至少一处可能 undefined。所有值仍可能被未知 spread 或后置清理改变。这里的记录数包含已提取字段的条件 spread 与未解析形式；直接字面量对象展开会被内联，不计入此列。它不是未知字段集合数。源码位置与每处类型详见 index.json 的 sites/field_forms/shapes 分片。

| 名称 | 位置数 | 字段并集 | 已记录 spread 数 | 位置编号 |
|---|---:|---|---:|---|
| `claudeai.desktop.sidebar.nav_item_clicked` | 1 | `item_id`~, `location`~, `sidebar_state`~ | 0 | payload-03209 |
| `claudeai.desktop.sidebar.peek_changed` | 2 | `end_reason`~, `interacted`~, `lab_tuned`?~, `open_ms`~, `peeking`~, `source`~ | 3 | payload-03202, payload-03203 |
| `claudeai.desktop.sidebar.product_entry_clicked` | 1 | `frame_mode`~, `product_id`~ | 0 | payload-02856 |
| `claudeai.desktop.sidebar.profile_menu_opened` | 1 | `sidebar_state`~ | 0 | payload-03221 |
| `claudeai.desktop.sidebar.scheduled_row_clicked` | 1 | `kind`~, `placement`~, `sidebar_state`~ | 0 | payload-03210 |
| `claudeai.desktop.sidebar.session_cycled` | 1 | `sidebar_state`~ | 1 | payload-03213 |
| `claudeai.desktop.sidebar.state_set` | 2 | `is_expanded`~, `other_tab_activity`~, `source`~ | 2 | payload-03200, payload-03201 |
| `claudeai.desktop.sidebar.tab_activity_changed` | 1 | `cause`~, `frame_mode`~, `initial`~, `previous_state`~, `sidebar_state`~, `since_dotable_ms`~, `state`~, `switcher`~, `tab`~ | 0 | payload-01151 |
| `claudeai.desktop.sidebar_settings.changed` | 5 | `filter`~, `from`~, `source`, `to`~, `value`~ | 0 | payload-02859, payload-02860, payload-02862, payload-02894, payload-03211 |
| `claudeai.desktop.sidebar_settings.opened` | 1 | `group_by`~, `metadata_off`?~, `mode`~, `theme` | 1 | payload-02863 |
| `claudeai.desktop.stale_session_banner.logout_enforced` | 1 | `source`~ | 0 | payload-02754 |
| `claudeai.desktop.stale_session_banner.relogin_clicked` | 1 | `destination`~, `source`~ | 0 | payload-02753 |
| `claudeai.desktop.stale_session_banner.relogin_returned` | 1 | `seconds_since_click`~, `session_marker_changed`~, `source`~ | 0 | payload-02755 |
| `claudeai.desktop.stale_session_banner.shown` | 1 | `source`~ | 0 | payload-02752 |
| `claudeai.desktop.switch_models_on_flag_toggled` | 3 | `enabled`~, `scope`, `source` | 0 | payload-01120, payload-01121, payload-02608 |
| `claudeai.desktop.topbar.navigation_clicked` | 2 | `direction`, `placement`?~ | 2 | payload-02834, payload-02835 |
| `claudeai.desktop.wake_scheduler_toggled` | 2 | `enabled`~ | 0 | payload-00135, payload-00136 |
| `claudeai.desktop.workflow_toggled` | 1 | `prop` | 0 | payload-02137 |
| `claudeai.desktop_install_modal.dismissed` | 1 | `platform`~, `surface`~ | 0 | payload-03053 |
| `claudeai.desktop_install_modal.download_clicked` | 1 | `platform`~, `surface`~ | 0 | payload-03052 |
| `claudeai.desktop_install_modal.shown` | 1 | `platform`~, `surface`~ | 0 | payload-03051 |
| `claudeai.desktop_landing.skipped` | 1 | `platform`~ | 0 | payload-01116 |
| `claudeai.dictation.attempted` | 1 | `dictation_session_id`~, `language`~ | 1 | payload-02920 |
| `claudeai.dictation.drain_ended` | 1 | `dictation_session_id`~, `drain_ms`~, `drain_outcome`~, `final_transcript_missing`~, `speech_lost`~, `superseded`~, `transcript_chars`~ | 2 | payload-02918 |
| `claudeai.dictation.session_ended` | 1 | `activation`~, `backend`~, `connect_dial_count`~, `connected`~, `dictation_session_id`~, `duration_ms`~, `error_type`~, `fast_start`~, `had_audio_ms`~, `had_audio_peak_rms`~, `language`~, `mic_retry`~, `outcome`~, `peak_input_rms`~, `stop_reason`~, `track_ended_ms`~, `track_muted_ms`~, `transcript_chars`~ | 2 | payload-02921 |
| `claudeai.dictation.session_started` | 1 | `backend`~, `capture_start_ms`~, `connect_dial_count`~, `connect_duration_ms`~, `dictation_session_id`~, `language`~, `mic_retry`~ | 1 | payload-02919 |
| `claudeai.direct_share.access_changed` | 2 | `change`~, `item_id`~, `kind`~, `target`~ | 1 | payload-00113, payload-00114 |
| `claudeai.direct_share.link_copied` | 2 | `item_id`~, `kind`~, `only_you`~, `viewer` | 1 | payload-00112, payload-02636 |
| `claudeai.direct_share.opened` | 2 | `item_id`~, `kind`~, `layout`?~, `share_surface`~, `viewer` | 2 | payload-00111, payload-02635 |
| `claudeai.directory.bundle_try_clicked` | 1 | `kind`, `properties`~, `properties.bundle_id`~, `properties.skill`~, `properties.via`~ | 0 | payload-00287 |
| `claudeai.directory.bundle_viewed` | 1 | `kind`, `properties`~, `properties.bundle_id`~ | 0 | payload-00290 |
| `claudeai.directory.card_click` | 1 | `kind`, `properties`~, `properties.bundle_id`?~, `properties.slug`~, `properties.slug_hash`~ | 1 | payload-00294 |
| `claudeai.directory.connect_intent_confirm_shown` | 1 | `kind`, `properties`~, `properties.slug`~ | 0 | payload-00292 |
| `claudeai.directory.connect_intent_dropped` | 5 | `kind`, `properties`~, `properties.guard`~, `properties.slug`~ | 0 | payload-00288, payload-00291, payload-00305, payload-00307, payload-00310 |
| `claudeai.directory.connect_intent_resumed` | 2 | `kind`, `properties`~, `properties.slug`~ | 0 | payload-00293, payload-00306 |
| `claudeai.directory.connect_intent_stashed` | 1 | `kind`, `properties`~, `properties.slug`~ | 0 | payload-00311 |
| `claudeai.directory.connect_intent_taken` | 1 | `kind`, `properties`~, `properties.slug`~ | 0 | payload-00309 |
| `claudeai.directory.detail_not_found` | 1 | `kind` | 0 | payload-00289 |
| `claudeai.directory.filter` | 10 | `kind`, `properties`~, `properties.keys`~, `properties.source` | 0 | payload-00295, payload-00296, payload-00297, payload-00298, payload-00299, payload-00300, payload-00301, payload-00302, payload-00303, payload-00308 |
| `claudeai.directory.local_org_plugins.install_clicked` | 1 | `referrer`~ | 0 | payload-01358 |
| `claudeai.directory.local_org_plugins.sort_changed` | 1 | `sort_by`~ | 0 | payload-01359 |
| `claudeai.directory.local_org_plugins.viewed` | 1 | `load_duration_ms`~, `load_error`~, `plugins_shown_count`~ | 0 | payload-01357 |
| `claudeai.directory.opened` | 2 | `kind`, `opened_via_route`~, `properties`~, `properties.opened_via_route`~, `properties.requested_section`, `properties.section`, `properties.source`, `requested_section`~, `section`~, `source`~ | 0 | payload-00286, payload-01375 |
| `claudeai.directory.page_view` | 1 | `kind` | 0 | payload-00304 |
| `claudeai.directory.section_changed` | 2 | `from_section`~, `search_active`?~, `to_section`~ | 2 | payload-01376, payload-01377 |
| `claudeai.directory.share_link_copied` | 1 | `section`~ | 0 | payload-01167 |
| `claudeai.directory.unified_search.back_clicked` | 2 | `crumb_surface`~, `target`~ | 0 | payload-01379, payload-01380 |
| `claudeai.directory.unified_search.category_item_clicked` | 1 | `query_length`~, `rank`~, `section`~, `source_feed`~ | 0 | payload-01371 |
| `claudeai.directory.unified_search.category_page_viewed` | 1 | `query_length`~, `section`~ | 0 | payload-01378 |
| `claudeai.directory.unified_search.item_clicked` | 2 | `kind`~, `opens`~, `query_length`~, `rank`~, `search_surface`, `section`~, `source_feed`~ | 0 | payload-01373, payload-02255 |
| `claudeai.directory.unified_search.results` | 2 | `categories_count`~, `connectors_count`~, `errored`~, `in_page_count`~, `more_count`~, `other_count`~, `plugins_count`~, `query_length`~, `search_surface`, `skills_count`~, `yours_count`~, `zero_results`~ | 0 | payload-01374, payload-02253 |
| `claudeai.directory.unified_search.see_all_clicked` | 2 | `query_length`~, `result_count`~, `search_surface`, `section`~ | 0 | payload-01372, payload-02254 |
| `claudeai.domain_capture.admin.claim_clicked` | 1 |  | 0 | payload-02488 |
| `claudeai.domain_capture.admin.claim_initiated` | 1 | `affected_account_count`~, `domain_count`~ | 0 | payload-02487 |
| `claudeai.domain_capture.admin.migration_confirmed` | 1 |  | 0 | payload-02489 |
| `claudeai.dusky_lantern_notice.clicked` | 1 |  | 1 | payload-00670 |
| `claudeai.dusky_lantern_notice.dismissed` | 1 | `source`~ | 1 | payload-00671 |
| `claudeai.dusky_lantern_notice.shown` | 1 |  | 1 | payload-00669 |
| `claudeai.ef_coachmark.tour_step` | 2 | `anchor_id`~, `experience_key`~, `outcome`, `position`~, `step_index`~ | 0 | payload-01294, payload-01295 |
| `claudeai.ef_tile_card.dropped` | 1 | `experience_key`~, `reason`~, `waited_ms`~ | 0 | payload-00834 |
| `claudeai.email_invite.accept_refused` | 3 | `assigns_no_seat`~, `organization_uuid`~, `refusal`~, `surface` | 0 | payload-00245, payload-00838, payload-01184 |
| `claudeai.email_invite.join_page.accept_clicked` | 1 | `assigns_no_seat`~, `landing_deferred`~, `organization_uuid`~, `raven_type`~, `returned_from_sso`~, `role`~, `shared_artifact_kind`~, `was_signed_in`~ | 0 | payload-00839 |
| `claudeai.email_invite.join_page.sign_in_clicked` | 1 | `delivery_method`~, `organization_uuid`~, `raven_type`~ | 0 | payload-00841 |
| `claudeai.email_invite.join_page.viewed` | 1 | `assigns_no_seat`~, `delivery_method`~, `organization_uuid`~, `raven_type`~, `returned_from_sso`~, `role`~, `shared_artifact_kind`~, `signed_in`~, `state`~ | 0 | payload-00840 |
| `claudeai.enterprise.explanation_completed` | 1 | `is_upgrade`~ | 0 | payload-00926 |
| `claudeai.enterprise.flow_started` | 1 | `buying_agent_session`~, `is_upgrade`~, `referral_source`~ | 0 | payload-00927 |
| `claudeai.enterprise.qualification_completed` | 1 | `buying_agent_session`~, `is_upgrade`~, `referral_source`~ | 0 | payload-00930 |
| `claudeai.enterprise.qualification_directed_to_sales` | 1 | `buying_agent_session`~, `is_upgrade`~, `referral_source`~, `selected_options`~ | 0 | payload-00929 |
| `claudeai.enterprise.review_submitted` | 3 | `initial_credits_cents`~, `is_upgrade`~, `payment_method_type`, `per_seat_cap_cents`~, `seat_cap_preset_variant`~, `seats`~, `transition_credit_declined`~, `transition_credit_offered`~ | 0 | payload-00934, payload-00937, payload-00941 |
| `claudeai.enterprise.seats_completed` | 1 | `initial_credits_cents`~, `is_upgrade`~, `per_seat_cap_cents`~, `per_seat_cap_is_preselected`~, `seat_cap_preset_variant`~, `seats`~ | 0 | payload-00942 |
| `claudeai.enterprise.setup_type_completed` | 1 | `is_upgrade`~, `setup_type`~, `upgrade_org_uuid`~ | 0 | payload-00943 |
| `claudeai.enterprise.transition_credit_offer_declined` | 1 |  | 0 | payload-00939 |
| `claudeai.enterprise.transition_credit_offer_restored` | 1 |  | 0 | payload-00940 |
| `claudeai.enterprise.transition_credit_offer_viewed` | 1 |  | 0 | payload-00938 |
| `claudeai.enterprise_owner_setup.completed` | 1 | `flow`~ | 0 | payload-00853 |
| `claudeai.enterprise_owner_setup.dns_sso_option_selected` | 2 | `option` | 0 | payload-00854, payload-00855 |
| `claudeai.enterprise_owner_setup.org_name_failed` | 1 | `failure_reason`~ | 0 | payload-00850 |
| `claudeai.enterprise_owner_setup.org_named` | 1 |  | 0 | payload-00849 |
| `claudeai.enterprise_owner_setup.owner_invite_failed` | 1 | `failure_reason`~ | 0 | payload-00852 |
| `claudeai.enterprise_owner_setup.owner_invite_sent` | 1 |  | 0 | payload-00851 |
| `claudeai.enterprise_owner_setup.step_viewed` | 1 | `step`~ | 0 | payload-00848 |
| `claudeai.enterprise_signup.email_submitted` | 1 | `eligible`~, `reason`~ | 0 | payload-00947 |
| `claudeai.enterprise_signup.link_sent` | 1 |  | 0 | payload-00946 |
| `claudeai.enterprise_signup.page_view` | 1 |  | 0 | payload-00944 |
| `claudeai.enterprise_signup.payment_confirmed` | 3 | `payment_method_type` | 0 | payload-00928, payload-00935, payload-00936 |
| `claudeai.enterprise_signup.pricing_enterprise_cta_click` | 1 | `destination` | 0 | payload-00885 |
| `claudeai.enterprise_signup.qualification_submitted` | 1 | `diverted_to_sales`~ | 0 | payload-00945 |
| `claudeai.enterprise_signup.session_acquired` | 1 | `method` | 0 | payload-02148 |
| `claudeai.epitaxy.continue_on_cloud.blocked_elevated_auth` | 1 | `custom_properties`~, `custom_properties.reason`~, `custom_properties.source`~, `custom_properties.stage`~ | 0 | payload-01646 |
| `claudeai.epitaxy.continue_on_cloud.branch_conflict` | 1 | `custom_properties`~, `custom_properties.conflict_kind`~, `custom_properties.source`~ | 0 | payload-01647 |
| `claudeai.epitaxy.continue_on_cloud.branch_conflict_resolved` | 2 | `custom_properties`~, `custom_properties.resolution`~, `custom_properties.source`~ | 0 | payload-01652, payload-01653 |
| `claudeai.epitaxy.continue_on_cloud.confirmed` | 1 | `custom_properties`~, `custom_properties.had_environment`~, `custom_properties.source`~ | 0 | payload-01651 |
| `claudeai.epitaxy.continue_on_cloud.dismissed_reconnect` | 1 | `custom_properties`~, `custom_properties.presentation`~ | 0 | payload-02607 |
| `claudeai.epitaxy.continue_on_cloud.failed` | 1 | `custom_properties`~, `custom_properties.reason`~, `custom_properties.source`~, `custom_properties.stage`~, `custom_properties.status`~ | 0 | payload-01649 |
| `claudeai.epitaxy.continue_on_cloud.shown` | 2 | `custom_properties`~, `custom_properties.had_environment`~, `custom_properties.presentation`~, `custom_properties.source` | 0 | payload-02037, payload-02605 |
| `claudeai.epitaxy.continue_on_cloud.succeeded` | 1 | `custom_properties`~, `custom_properties.source`~ | 0 | payload-01648 |
| `claudeai.epitaxy.continue_on_cloud.tapped` | 2 | `custom_properties`~, `custom_properties.had_environment`~, `custom_properties.presentation`~, `custom_properties.source` | 0 | payload-02038, payload-02606 |
| `claudeai.epitaxy.sidebar.custom_group_changed` | 1 | `action`~, `deleted_session_count`~, `group_count`~, `is_reassignment`~, `overlay_enabled`~, `session_count_in_group`~, `source`~, `surface`~ | 0 | payload-02743 |
| `claudeai.epitaxy.sidebar.epitaxy_projects_order_changed` | 1 | `method`, `project_count`~ | 0 | payload-02889 |
| `claudeai.epitaxy.sidebar.group_new_session_clicked` | 2 | `archived_only`~, `bucket_kind`~, `group_kind`, `prefill_kind`~, `prefill_rule`~, `session_count`~, `source`~ | 0 | payload-02875, payload-02878 |
| `claudeai.epitaxy.sidebar.project_bulk_action` | 1 | `action`~, `count`~ | 0 | payload-02874 |
| `claudeai.epitaxy.sidebar.project_order_changed` | 2 | `method`~, `project_count`~ | 0 | payload-02876, payload-02877 |
| `claudeai.epitaxy.sidebar.section_changed` | 1 | `section_count`~ | 1 | payload-03205 |
| `claudeai.error_banner.viewed` | 2 | `absence_reason`?~, `banner`~, `chat_backend`?~, `classification`~, `display_kind`, `end_reason`~, `is_external_conversation`~, `is_last_message`?~, `message_uuid`?~, `model_surface`~, `mount_index`~, `retry_offered`?~, `visible_ms`~ | 13 | payload-03026, payload-03028 |
| `claudeai.feature_bad` | 1 | `error_code`~, `feature_name`~ | 1 | payload-03034 |
| `claudeai.feature_ok` | 1 | `feature_name`~ | 1 | payload-03033 |
| `claudeai.find_in_page.closed` | 1 | `had_matches`~, `via`~ | 0 | payload-02911 |
| `claudeai.find_in_page.match_navigated` | 1 |  | 2 | payload-02914 |
| `claudeai.find_in_page.opened` | 1 |  | 0 | payload-02913 |
| `claudeai.find_in_page.searched` | 1 | `match_count`~, `query_length`~ | 1 | payload-02915 |
| `claudeai.find_in_page.stood_down` | 1 | `overlay_kind`~ | 0 | payload-02912 |
| `claudeai.flickering_galaxy.handled` | 1 | `desktop_reason`?~, `on_screen`~, `outcome`~, `tool`~ | 1 | payload-02762 |
| `claudeai.frame_artifact.chat_button_shown` | 1 | `label_variant`~, `not_shown_reason`~, `open_surface`~, `origin_kind`~, `origin_source`~, `placement`~, `shown`~, `step`~ | 0 | payload-02061 |
| `claudeai.frame_artifact.copied` | 1 | `format`~ | 0 | payload-01198 |
| `claudeai.frame_artifact.invitation.action_settled` | 2 | `action`~, `outcome`~ | 0 | payload-01182, payload-01183 |
| `claudeai.frame_artifact.invitation.shown` | 1 | `from_report_link`~, `state`~ | 0 | payload-01181 |
| `claudeai.frame_artifact.open_in_claude` | 4 | `dest_kind`~, `open_surface`~, `origin_source`~, `placement`?~, `seed_delivery`?~, `seed_status`?~, `step`~ | 3 | payload-00483, payload-02062, payload-02248, payload-02972 |
| `claudeai.frame_artifact.tawny_linnet` | 2 | `lasting`~, `outcome`~, `timed_out`?~, `why`~ | 1 | payload-01889, payload-01890 |
| `claudeai.frolicking_brook.accepted` | 1 | `sent`~ | 1 | payload-02054 |
| `claudeai.frolicking_brook.dismissed` | 1 |  | 1 | payload-02055 |
| `claudeai.frolicking_brook.notice_shown` | 1 | `active_value`~, `conversation_uuid`~, `reason`~, `subject_value`~ | 1 | payload-02052 |
| `claudeai.frolicking_brook.shown` | 1 | `auto_mode`~ | 1 | payload-02053 |
| `claudeai.fusion.browse.filter_changed` | 3 | `active_tab`~, `filter_type`, `hidden`?~, `hidden_count`?~, `selected`~ | 1 | payload-01365, payload-01366, payload-01367 |
| `claudeai.fusion.browse.sort_changed` | 1 | `active_tab`~, `sort_by`~ | 0 | payload-01368 |
| `claudeai.fusion.browse_modal.load_failed` | 1 | `active_tab`~, `error_type`~, `load_duration_ms`~, `surface`~ | 0 | payload-01363 |
| `claudeai.fusion.browse_modal.opened` | 1 | `active_tab`~, `surface`~ | 0 | payload-01361 |
| `claudeai.fusion.browse_modal.viewed` | 1 | `active_tab`~, `filter_applied`, `load_duration_ms`~, `load_error`~, `plugins_shown_count`~, `sort_order`~, `surface`~ | 0 | payload-01362 |
| `claudeai.fusion.create_with_claude_applied` | 1 | `client_platform`~, `conversation_uuid`~, `plugin_id`?~, `route`~ | 1 | payload-02550 |
| `claudeai.fusion.create_with_claude_clicked` | 1 | `source`~ | 0 | payload-00684 |
| `claudeai.fusion.customize_applied` | 1 | `client_platform`~, `conversation_uuid`~, `plugin_id`?~, `route`~ | 1 | payload-02550 |
| `claudeai.fusion.customize_clicked` | 1 | `context`~, `is_local`~, `plugin_context`~, `plugin_id`?~, `sub_customization`?~ | 2 | payload-00632 |
| `claudeai.fusion.deep_link.resolved` | 1 | `marketplace_id`?~, `marketplace_name`?~, `plugin_context`~, `resolution`~ | 2 | payload-01364 |
| `claudeai.fusion.default_source.added` | 1 | `entry_point`?~, `marketplace_id`~, `plugin_context`~, `source_type`~ | 1 | payload-00496 |
| `claudeai.fusion.default_source.removed` | 1 | `entry_point`?~, `marketplace_id`~, `plugin_context`~, `source_type`~ | 1 | payload-00496 |
| `claudeai.fusion.deleted` | 1 | `is_local`~, `is_official_plugin`~, `plugin_context`~, `plugin_id_hash`~, `plugin_name`~ | 0 | payload-02696 |
| `claudeai.fusion.detail_viewed` | 1 | `active_tab`~, `is_official_plugin`~, `plugin_id_hash`~, `plugin_name`~, `referrer`~, `surface`~ | 0 | payload-01360 |
| `claudeai.fusion.edited` | 2 | `method`~, `plugin_context`~ | 0 | payload-00361, payload-00362 |
| `claudeai.fusion.github_app_install.clicked` | 1 | `plugin_context`~ | 0 | payload-01645 |
| `claudeai.fusion.github_app_install.shown` | 1 | `plugin_context`~ | 0 | payload-01641 |
| `claudeai.fusion.github_connect.clicked` | 2 | `plugin_context`~ | 0 | payload-00606, payload-01644 |
| `claudeai.fusion.github_connect.shown` | 2 | `plugin_context`~ | 0 | payload-00607, payload-01640 |
| `claudeai.fusion.install_clicked` | 2 | `active_tab`~, `install_scope`~, `is_official_plugin`~, `plugin_id_hash`~, `plugin_name`~, `referrer`~, `surface`~ | 0 | payload-01001, payload-01370 |
| `claudeai.fusion.installed` | 5 | `add_result`?, `chat_backend`?~, `cli_count`~, `install_source`?~, `is_local`~, `is_official_plugin`~, `is_shared`?~, `plugin_context`~, `plugin_id`?~, `plugin_id_hash`~, `plugin_name`~, `scope`?~, `server_plugin_id`?~, `shared_via`?~, `suggestion_surface`?~, `surface`~, `turned_off_reason`?~ | 17 | payload-01677, payload-02693, payload-02695, payload-02700, payload-02704 |
| `claudeai.fusion.pat_clone.failed` | 1 | `error_code`~, `plugin_context`~ | 0 | payload-01643 |
| `claudeai.fusion.pat_clone.succeeded` | 1 | `plugin_context`~ | 0 | payload-01638 |
| `claudeai.fusion.pat_input.shown` | 1 | `error_code`~, `plugin_context`~ | 0 | payload-01642 |
| `claudeai.fusion.plugin_card.save_failed` | 1 | `client_platform`~, `error_code`~, `route`~, `source`~ | 0 | payload-02549 |
| `claudeai.fusion.plugin_card.save_shown` | 1 | `client_platform`~, `flag_opened`~, `route`~, `source`~ | 0 | payload-01452 |
| `claudeai.fusion.plugin_card.share_shown` | 1 | `can_share`~, `client_platform`~, `share_surface`~ | 0 | payload-02251 |
| `claudeai.fusion.source.add_failed` | 1 | `error_code`~, `plugin_context`~ | 0 | payload-01639 |
| `claudeai.fusion.source.added` | 1 | `auto_sync_requested`~, `plugin_context`~, `source_type`~ | 0 | payload-01637 |
| `claudeai.fusion.source.refresh_failed` | 1 | `error_code`~, `plugin_context`~ | 0 | payload-02702 |
| `claudeai.fusion.source.removed` | 1 | `plugin_context`~ | 0 | payload-02703 |
| `claudeai.fusion.suggested_prompt.clicked` | 2 | `caution_band_hidden`~, `dropped`?~, `outcome`?~, `prompt_origin`~, `seed_id`?~, `wait_bucket`?~, `waited`~ | 10 | payload-00498, payload-01627 |
| `claudeai.fusion.suggested_prompt.sent` | 2 | `caution_band_hidden`~, `prompt_origin`~, `seed_id`~ | 3 | payload-00497, payload-01626 |
| `claudeai.fusion.suggested_prompt.shown` | 2 | `plugin_context`~, `plugin_id`?~, `source` | 2 | payload-00499, payload-00500 |
| `claudeai.fusion.toggled` | 2 | `enabled`~, `is_local`~, `is_official_plugin`~, `is_shared`?~, `plugin_context`~, `plugin_id_hash`~, `plugin_name`~, `server_plugin_id`?~, `shared_via`?~, `turned_off_reason`?~, `via` | 3 | payload-02629, payload-02697 |
| `claudeai.fusion.uninstalled` | 2 | `install_source`?, `is_local`~, `is_official_plugin`~, `is_shared`?~, `plugin_context`~, `plugin_id`?~, `plugin_id_hash`~, `plugin_name`~, `server_plugin_id`?~, `shared_via`?~, `surface`~, `turned_off_reason`?~ | 6 | payload-02701, payload-02704 |
| `claudeai.fusion.uploaded` | 2 | `is_local`~, `plugin_context`~ | 0 | payload-01384, payload-02694 |
| `claudeai.gentle_puddle.shown` | 1 | `status`~ | 0 | payload-01932 |
| `claudeai.get_help.clicked` | 2 |  | 0 | payload-02169, payload-02170 |
| `claudeai.github_oauth.callback.fallback_redirect` | 3 | `cause`, `setup_action`~ | 0 | payload-01776, payload-01777, payload-01781 |
| `claudeai.github_oauth.callback.finish_failed` | 2 | `reason`~, `setup_action`~, `status_code`~ | 0 | payload-01779, payload-01780 |
| `claudeai.github_oauth.callback.finish_succeeded` | 1 | `had_return_stash`~, `handoff_id`?~, `has_installation_id`~, `installation_admin`~, `intent`~, `redirect_kind`~, `setup_action`~, `setup_entrypoint`~, `used_selfheal_stash`~ | 1 | payload-01778 |
| `claudeai.github_oauth.callback.github_error` | 1 | `github_error`~, `has_state`~ | 0 | payload-01775 |
| `claudeai.github_oauth.callback.link_report.viewed` | 1 | `complete`~, `linked_count`~, `skipped_count`~ | 0 | payload-01783 |
| `claudeai.github_oauth.callback.recovery_prompt.abandoned` | 1 | `cause`~, `github_error`~ | 0 | payload-01786 |
| `claudeai.github_oauth.callback.recovery_prompt.go_back_clicked` | 1 | `cause`~, `github_error`~ | 0 | payload-01789 |
| `claudeai.github_oauth.callback.recovery_prompt.retry_clicked` | 1 | `cause`~, `github_error`~ | 0 | payload-01788 |
| `claudeai.github_oauth.callback.recovery_prompt.viewed` | 1 | `cause`~, `github_error`~ | 0 | payload-01785 |
| `claudeai.github_oauth.callback.request_sent.viewed` | 1 | `setup_action`~, `setup_entrypoint`~ | 0 | payload-01782 |
| `claudeai.github_oauth.callback.selfheal_prompt.clicked` | 1 |  | 0 | payload-01787 |
| `claudeai.github_oauth.callback.selfheal_prompt.viewed` | 1 | `setup_action`~ | 0 | payload-01784 |
| `claudeai.github_oauth.callback.viewed` | 1 | `github_error`~, `has_code`~, `has_installation_id`~, `has_state`~, `setup_action`~ | 0 | payload-01774 |
| `claudeai.github_oauth.returned` | 1 | `caller`~, `handoff_id`?~ | 1 | payload-02711 |
| `claudeai.github_state.fix_clicked` | 1 |  | 1 | payload-00668 |
| `claudeai.github_state.resolved` | 1 |  | 1 | payload-00666 |
| `claudeai.github_state.shown` | 1 |  | 1 | payload-00667 |
| `claudeai.gleaming_teapot.clicked` | 1 | `days_left`~, `variant`~ | 0 | payload-03171 |
| `claudeai.gleaming_teapot.dismissed` | 1 | `days_left`~, `variant`~ | 0 | payload-03170 |
| `claudeai.gleaming_teapot.shown` | 1 | `days_left`~, `variant`~ | 0 | payload-03159 |
| `claudeai.guest_pass_modal.link_copied` | 1 | `source`~ | 0 | payload-02643 |
| `claudeai.guest_pass_modal.shown` | 1 | `source`~ | 0 | payload-02642 |
| `claudeai.haystack.owner.landing.next.clicked` | 1 |  | 0 | payload-02235 |
| `claudeai.haystack.owner.name.next.clicked` | 1 |  | 0 | payload-02236 |
| `claudeai.haystack.owner.tools.next.clicked` | 1 |  | 0 | payload-02237 |
| `claudeai.haystack.page_viewed` | 1 | `page`~ | 0 | payload-02243 |
| `claudeai.haystack.project.created` | 1 | `connector_count`~ | 0 | payload-02241 |
| `claudeai.haystack.project.creation_error` | 1 |  | 0 | payload-02242 |
| `claudeai.haystack.user.landing.next.clicked` | 1 |  | 0 | payload-02238 |
| `claudeai.haystack.user.request.clicked` | 1 |  | 0 | payload-02239 |
| `claudeai.haystack.user.tool.skip.clicked` | 1 | `tool_id`~ | 0 | payload-02240 |
| `claudeai.hazel_plover.acted` | 1 | `action`, `finding_uuid`~, `session_id`~, `source`?~ | 1 | payload-00630 |
| `claudeai.hazel_plover.dismissed` | 1 | `finding_uuid`~, `surface` | 0 | payload-00623 |
| `claudeai.hazel_plover.shown` | 1 | `finding_uuid`~, `position`~, `surface` | 0 | payload-00622 |
| `claudeai.hazel_plover.tab_changed` | 1 | `new_count`~, `tab`~ | 0 | payload-00624 |
| `claudeai.hipaa.cohort_verdict` | 1 | `decided`~, `desktop_shell`~, `flag_evaluable`~, `flags_for_active_org`~, `flags_fresh`~, `flags_settled`~, `pending_ms`~, `restricted`~ | 0 | payload-03058 |
| `claudeai.humming_quill.resolved` | 1 | `choice`~, `closed_by`~, `wrote_offered_level`~ | 1 | payload-03241 |
| `claudeai.humming_quill.shown` | 1 |  | 1 | payload-03243 |
| `claudeai.in_chat_upsell.connect_gdrive.displayed` | 1 |  | 0 | payload-01283 |
| `claudeai.in_chat_upsell.connect_gdrive.start` | 1 |  | 0 | payload-01284 |
| `claudeai.install_hub.item_clicked` | 2 | `category_id`~, `item_id`~, `presentation`~ | 0 | payload-01995, payload-01997 |
| `claudeai.install_hub.modal_opened` | 1 | `hero_card_id`~, `presentation`~, `ranking_reason`~, `sot_has_chrome`~, `sot_has_claude_code`~, `sot_has_desktop`~, `sot_has_mobile`~, `sot_has_office`~ | 0 | payload-01996 |
| `claudeai.insufficient_seats_modal.shown` | 1 | `can_purchase`~, `mode`~, `seat_tier`~, `seats_needed`~ | 0 | payload-01152 |
| `claudeai.intercom.booted` | 1 | `has_user_hash`~ | 0 | payload-02171 |
| `claudeai.invite_link.add_member_modal.copied` | 1 |  | 0 | payload-00792 |
| `claudeai.invite_link.add_member_modal.expired_seen` | 1 |  | 0 | payload-00785 |
| `claudeai.invite_link.add_member_modal.regenerated` | 1 |  | 0 | payload-00789 |
| `claudeai.invite_link.add_member_modal.shown` | 1 | `state`~ | 0 | payload-00784 |
| `claudeai.invite_link.add_member_modal.toggled` | 1 | `enabled`~, `was_expired`~ | 0 | payload-00791 |
| `claudeai.invite_link.join_page.approved` | 1 | `organization_uuid`~ | 0 | payload-00843 |
| `claudeai.invite_link.join_page.error` | 1 | `error_type`~ | 0 | payload-00845 |
| `claudeai.invite_link.join_page.join_clicked` | 1 |  | 0 | payload-00846 |
| `claudeai.invite_link.join_page.loaded` | 1 |  | 0 | payload-00842 |
| `claudeai.invite_link.join_page.pending` | 1 | `organization_uuid`~ | 0 | payload-00844 |
| `claudeai.invite_link.onboarding.copied` | 1 |  | 0 | payload-00970 |
| `claudeai.invite_link.onboarding.shown` | 1 |  | 0 | payload-00969 |
| `claudeai.invite_link.onboarding_join.completed` | 1 | `organization_uuid`~, `status`~ | 0 | payload-00241 |
| `claudeai.invite_link.onboarding_join.failed` | 1 |  | 0 | payload-00242 |
| `claudeai.invite_link.settings.copied` | 1 |  | 0 | payload-00792 |
| `claudeai.invite_link.settings.expired_seen` | 1 |  | 0 | payload-00790 |
| `claudeai.invite_link.settings.regenerated` | 1 |  | 0 | payload-00789 |
| `claudeai.invite_link.settings.toggled` | 1 | `enabled`~, `was_expired`~ | 0 | payload-00791 |
| `claudeai.invite_team.clicked` | 1 | `source`, `user_type`~ | 0 | payload-02847 |
| `claudeai.invite_team.shown` | 1 | `source`, `user_type`~ | 0 | payload-02848 |
| `claudeai.ip_allowlist.admin.disabled` | 1 | `range_count`~ | 0 | payload-02486 |
| `claudeai.ip_allowlist.admin.enabled` | 1 | `range_count`~ | 0 | payload-02486 |
| `claudeai.ip_allowlist.admin.ranges_updated` | 1 | `added_count`~, `enforcement_enabled`~, `removed_count`~ | 0 | payload-02485 |
| `claudeai.iron_swift.inline_pair_dropped` | 1 | `cause`~, `comparison_uuid`~, `conversation_uuid`~, `pair_complete`~, `pending_frames`~ | 0 | payload-02686 |
| `claudeai.iron_swift.inline_pair_voided` | 1 | `cause`~, `chat_backend`?~, `comparison_uuid`~, `conversation_uuid`~, `shown`~ | 1 | payload-02687 |
| `claudeai.iron_swift.vote_save_bailed` | 1 |  | 1 | payload-02603 |
| `claudeai.iron_swift.vote_submitted` | 1 | `auto_retried`~, `blind`~, `conversation_a`~, `conversation_b`~, `effort_a`~, `effort_b`~, `has_comment`~, `memory_off_a`~, `memory_off_b`~, `model_a`~, `model_b`~, `permission_asymmetry`~, `reasons`~, `shared`~, `thinking_a`~, `thinking_b`~, `time_to_vote_ms`~, `turn_index`~, `winner`~ | 0 | payload-02604 |
| `claudeai.join_your_team_offer.shown` | 1 | `arm`~, `org_count`~, `surface`~ | 0 | payload-00256 |
| `claudeai.jolly_candle.open_chat` | 2 | `host` | 0 | payload-00532, payload-02067 |
| `claudeai.jolly_candle.requested` | 1 |  | 1 | payload-02159 |
| `claudeai.jolly_candle.settled` | 1 | `duration_ms`~, `outcome`~, `size_bucket`?~, `source`?~ | 3 | payload-02160 |
| `claudeai.jolly_candle.unavailable` | 1 | `host`~, `reason`~ | 0 | payload-02161 |
| `claudeai.juniper_tide.clicked` | 1 | `data`~, `data.layout_version`~, `data.options_arm`~, `data.placement`~, `data.surface`~ | 0 | payload-00750 |
| `claudeai.juniper_tide.result` | 1 | `data`~, `data.latency_ms`~, `data.layout_version`~, `data.options_arm`~, `data.placement`~, `data.recovered`~, `data.result`~, `data.surface`~ | 0 | payload-00751 |
| `claudeai.juniper_tide.shown` | 1 | `data`~, `data.arm`~, `data.available`~, `data.billing_path`~, `data.billing_period`~, `data.extra_usage_state`~, `data.hours_until_reset`~, `data.in_experiment`~, `data.layout_version`~, `data.limit_type`, `data.options_arm`~, `data.slot_offered`~, `data.surface`~, `data.tenure_bucket`~, `data.tier`~ | 0 | payload-00752 |
| `claudeai.keelson_garboard.held` | 1 | `email_count`~, `invite_surface`~ | 0 | payload-00787 |
| `claudeai.keyboard_shortcut.pressed` | 1 | `chord`~, `client_platform`~, `command_id`~, `is_mac`~ | 0 | payload-02660 |
| `claudeai.language.auto_switched` | 1 |  | 1 | payload-02896 |
| `claudeai.language.picked` | 1 |  | 1 | payload-02895 |
| `claudeai.learn.academy_opened` | 1 | `academy_id`~, `kind`~, `role_slug`~, `section`~, `slug`~ | 0 | payload-00539 |
| `claudeai.learn.page_viewed` | 1 | `has_for_you`~, `layout`~, `learn_surface`~, `page`~, `role_slug`~ | 0 | payload-00544 |
| `claudeai.learn.prompt_tried` | 1 | `academy_id`~, `destination`~, `role_slug`~, `section`~, `slug`~ | 0 | payload-00540 |
| `claudeai.learn.role_selected` | 1 | `for_you`~, `role_slug`~, `source`~ | 0 | payload-00541 |
| `claudeai.learn.strip_clicked` | 1 | `destination`~, `has_role`~ | 0 | payload-00543 |
| `claudeai.learn.strip_shown` | 1 | `destination`~, `has_role`~ | 0 | payload-00542 |
| `claudeai.library_bundle_editor.draft_discarded` | 1 | `exit`~ | 0 | payload-00674 |
| `claudeai.library_bundle_editor.opened` | 4 | `file_count`~, `source`~, `surface`, `trigger` | 0 | payload-00063, payload-00064, payload-00501, payload-02343 |
| `claudeai.limit_action.add_funds.clicked` | 1 |  | 0 | payload-02965 |
| `claudeai.limit_action.add_funds.shown` | 1 |  | 0 | payload-02964 |
| `claudeai.limit_action.enable_overages.clicked` | 1 | `data`~, `data.user_type`~ | 0 | payload-02958 |
| `claudeai.limit_action.enable_overages.shown` | 1 | `data`~, `data.user_type`~ | 0 | payload-02957 |
| `claudeai.limit_action.increase_spend_limit.clicked` | 1 | `data`~, `data.then_add_funds`~ | 0 | payload-02969 |
| `claudeai.limit_action.increase_spend_limit.shown` | 1 | `data`~, `data.then_add_funds`~ | 0 | payload-02968 |
| `claudeai.limit_action.manage_usage.clicked` | 1 | `data`~, `data.user_type`~ | 0 | payload-02986 |
| `claudeai.limit_action.manage_usage.shown` | 1 | `data`~, `data.user_type`~ | 0 | payload-02985 |
| `claudeai.limit_action.ooc_upgrade_modal.clicked` | 1 |  | 0 | payload-02967 |
| `claudeai.limit_action.ooc_upgrade_modal.shown` | 1 |  | 0 | payload-02966 |
| `claudeai.limit_action.view_usage.clicked` | 1 | `data`~, `data.source`~ | 0 | payload-02959 |
| `claudeai.limit_banner.cta_clicked` | 1 | `data`~, `data.cta`~, `data.cta_variant`~, `data.hours_until_reset`~, `data.surface`~, `data.umber_lark_arm`?~, `data.window_name`~ | 1 | payload-02982 |
| `claudeai.limit_banner.dismissed` | 1 | `data`~, `data.banner_type`~, `data.surface`~, `data.umber_lark_arm`?~, `data.window_name`~ | 1 | payload-02983 |
| `claudeai.limit_banner.shown` | 1 | `data`~, `data.banner_type`~, `data.cta_variant`~, `data.hours_until_reset`~, `data.surface`~, `data.window_name`~ | 0 | payload-02979 |
| `claudeai.limit_wall.shown` | 1 | `data`~, `data.arm`~, `data.hours_until_reset`~, `data.limit_type`~, `data.surface`~, `data.tier`~ | 0 | payload-02981 |
| `claudeai.linden_tern_quay.layout_changed` | 1 | `layout`~ | 0 | payload-00482 |
| `claudeai.login.claude_com_redirect` | 1 | `via`~ | 0 | payload-00889 |
| `claudeai.login.email_submitted` | 1 | `login_intent`~ | 0 | payload-00329 |
| `claudeai.login.mobile_app_download.download_clicked` | 1 | `platform`~ | 0 | payload-00883 |
| `claudeai.login.mobile_app_download.shown` | 1 | `platform`~ | 0 | payload-00887 |
| `claudeai.login.open_email_clicked` | 1 | `provider`~, `screen`~ | 0 | payload-00331 |
| `claudeai.login.page_viewed` | 1 | `referral_campaign`~, `referral_source`~, `selected_plan`~, `variant`~ | 0 | payload-00872 |
| `claudeai.login.popup_google_auth_completed` | 2 | `outcome` | 0 | payload-00869, payload-00870 |
| `claudeai.login.popup_google_auth_handshake_failed` | 1 |  | 0 | payload-00871 |
| `claudeai.login.popup_google_auth_opened` | 1 | `phase` | 0 | payload-00868 |
| `claudeai.login.resend_requested` | 2 |  | 0 | payload-00327, payload-00328 |
| `claudeai.login.sso_domain_clicked` | 1 |  | 0 | payload-00021 |
| `claudeai.luminous_pine.changed` | 1 | `from_value`~, `to_value`~ | 0 | payload-03224 |
| `claudeai.majordomo.conversation_created` | 1 |  | 0 | payload-02379 |
| `claudeai.majordomo.page_viewed` | 1 |  | 0 | payload-02378 |
| `claudeai.majordomo.tool.invoked` | 6 | `change_count`?~, `has_reason`~, `outcome`~, `tool_name`~ | 8 | payload-00577, payload-00578, payload-00579, payload-00580, payload-00581, payload-00582 |
| `claudeai.marble_heron.catchup.reloaded` | 1 | `catchup_surface`~ | 1 | payload-01735 |
| `claudeai.max_effort_warning_band.dismissed` | 2 | `banner_surface`~, `presentation`~, `trigger` | 0 | payload-00764, payload-03161 |
| `claudeai.max_effort_warning_band.shown` | 2 | `banner_surface`~, `presentation`~ | 0 | payload-00763, payload-03160 |
| `claudeai.mcp.auth.abandoned` | 1 | `client_attempt_id`~, `prior_auth_status`~, `reason`~, `seconds_since_init`~, `source`~, `uuid`~ | 0 | payload-02718 |
| `claudeai.mcp.auth.browser_opened` | 1 | `client_attempt_id`~, `outcome`, `product_surface`~, `source`~, `uuid`~ | 0 | payload-02716 |
| `claudeai.mcp.auth.browser_returned` | 1 | `client_attempt_id`~, `product_surface`~, `seconds_since_opened`~, `step`~, `uuid`~ | 0 | payload-02717 |
| `claudeai.mcp.auth.completed` | 4 | `failure_type`~, `prior_auth_status`~, `redacted_url`~, `result`~, `source`~, `uuid`~ | 3 | payload-01634, payload-02720, payload-03274, payload-03275 |
| `claudeai.mcp.auth.init` | 4 | `client_attempt_id`~, `placement`?~, `prior_auth_status`~, `redacted_url`~, `source`~, `uuid`~ | 4 | payload-01635, payload-02719, payload-02721, payload-03276 |
| `claudeai.mcp.bootstrap_stream.completed` | 1 | `auth_auth_required_count`~, `auth_authenticated_count`~, `auth_error_detail`~, `auth_not_required_count`~, `auth_refresh_failed_count`~, `auth_token_invalid_count`~, `connected_count`~, `deleted_servers_pruned_count`~, `deleted_servers_rechecked_count`~, `deleted_servers_relisted_count`~, `disconnected_count`~, `duration_ms`~, `error_retries`~, `outcome`~, `server_count`~, `trigger`~, `ttfb_ms`~ | 0 | payload-02712 |
| `claudeai.mcp.connect_flow.closed` | 1 | `connector_slug`~, `error_kind`~, `last_step_id`~, `outcome`~ | 0 | payload-00917 |
| `claudeai.mcp.connect_flow.opened` | 1 | `connector_slug`~ | 0 | payload-00915 |
| `claudeai.mcp.connect_flow.step_shown` | 1 | `connector_slug`~, `step_id`~ | 0 | payload-00916 |
| `claudeai.mcp.create_server` | 1 | `redacted_url`~, `source`~, `type` | 0 | payload-02791 |
| `claudeai.mcp.delete_server` | 2 | `name`~, `redacted_url`~, `source`~, `type`~, `uuid`~ | 0 | payload-00814, payload-02396 |
| `claudeai.mcp.deleted_servers.rechecked` | 1 |  | 0 | payload-02713 |
| `claudeai.mcp.deleted_servers.relisted` | 1 |  | 0 | payload-02714 |
| `claudeai.mcp.deleted_servers.removed_again` | 1 |  | 0 | payload-02715 |
| `claudeai.mcp.google_sign_in_retry.answered` | 1 | `answer`~ | 1 | payload-02167 |
| `claudeai.mcp.google_sign_in_retry.shown` | 1 |  | 1 | payload-02166 |
| `claudeai.mcp.m365_setup_modal.cancelled` | 1 | `claude_email_type`~, `paid_account_tier`~ | 0 | payload-00718 |
| `claudeai.mcp.m365_setup_modal.continued` | 1 | `claude_email_type`~, `paid_account_tier`~ | 0 | payload-00717 |
| `claudeai.mcp.m365_setup_modal.notify_me_clicked` | 1 | `claude_email_type`~, `paid_account_tier`~ | 0 | payload-00719 |
| `claudeai.mcp.m365_setup_modal.viewed` | 1 | `claude_email_type`~, `paid_account_tier`~ | 0 | payload-00716 |
| `claudeai.mcp.m365_setup_modal.work_account_bypass_clicked` | 1 | `claude_email_type`~, `paid_account_tier`~ | 0 | payload-00720 |
| `claudeai.mcp.post_connect_chip.clicked` | 1 | `arm`~, `chip_id`~, `connector`~, `destination`~, `position`~ | 0 | payload-00079 |
| `claudeai.mcp.post_connect_chip.shown` | 1 | `arm`~, `chip_id`~, `connector`~, `position`~ | 0 | payload-00078 |
| `claudeai.mcp.reauth_prompt.resolved` | 1 |  | 1 | payload-01453 |
| `claudeai.mcp.reauth_prompt.shown` | 1 |  | 1 | payload-01454 |
| `claudeai.mcp.registry.opt_in.allowed` | 1 |  | 0 | payload-01959 |
| `claudeai.mcp.registry.opt_in.denied` | 1 |  | 0 | payload-01960 |
| `claudeai.mcp.registry.opt_in.setting_disabled` | 1 |  | 0 | payload-01031 |
| `claudeai.mcp.registry.opt_in.setting_enabled` | 1 |  | 0 | payload-01030 |
| `claudeai.mcp.registry.opt_in.viewed` | 1 |  | 0 | payload-01958 |
| `claudeai.mcp.registry.searched` | 1 | `connected_count`~, `keyword_count`~, `result_count`~ | 0 | payload-03025 |
| `claudeai.mcp.registry.suggestion.auto_connect_skipped` | 1 | `chin_redesign`?~, `connector_name`~, `connector_uuid`~, `installed_uuid`~, `placement`?~, `reason`~, `session_id`~ | 2 | payload-01814 |
| `claudeai.mcp.registry.suggestion.browse_all_clicked` | 2 | `chin_redesign`?~, `connector_count`~, `connector_uuids`~, `origin`~, `other_connector_count`~, `placement`?~, `session_id`~ | 3 | payload-01808, payload-01811 |
| `claudeai.mcp.registry.suggestion.connect_clicked` | 1 | `chin_redesign`?~, `placement`?~ | 3 | payload-01812 |
| `claudeai.mcp.registry.suggestion.decline_clicked` | 1 | `chin_redesign`?~, `connector_count`~, `connector_names`~, `connector_uuids`~, `had_auth_error`~, `origin`~, `placement`?~, `session_id`~, `via`?~, `was_connected`~ | 2 | payload-01817 |
| `claudeai.mcp.registry.suggestion.enable_clicked` | 1 | `chin_redesign`?~, `connector_name`~, `connector_uuid`~, `had_auth_error`~, `placement`?~, `session_id`~, `was_connected`~ | 2 | payload-01813 |
| `claudeai.mcp.registry.suggestion.use_clicked` | 2 | `chin_redesign`?~, `connector_name`~, `connector_uuid`~, `installed_uuid`~, `origin`~, `placement`?~, `session_id`~ | 3 | payload-01815, payload-01816 |
| `claudeai.mcp.registry.suggestion.viewed` | 1 | `chin_redesign`?~, `connector_count`~, `connector_names`~, `connector_uuids`~, `had_auth_error`~, `origin`~, `placement`?~, `session_id`~, `was_connected`~ | 2 | payload-01809 |
| `claudeai.mcp.tool.toggled` | 2 | `conversation_uuid`~, `redacted_url`~, `setting`~, `source`~, `value`~ | 0 | payload-02655, payload-02796 |
| `claudeai.mcp_app.bridge_event` | 2 | `chat_message_uuid`~, `event_type`~, `log_logger`, `read_me_modules`~, `read_me_platform`~, `sandbox_url`~, `server_uuid`~, `since_mount_ms`~, `tool_name`~, `tool_use_id`~ | 1 | payload-01908, payload-02232 |
| `claudeai.mcp_app.client_not_found` | 1 | `chat_message_uuid`~, `server_uuid`~, `tool_name`~, `tool_use_id`~ | 0 | payload-01904 |
| `claudeai.mcp_app.error` | 1 | `chat_message_uuid`~, `error_code`~, `error_phase`~, `error_type`~, `redacted_url`~, `server_uuid`~, `tool_name`~, `tool_server`~, `tool_use_id`~ | 2 | payload-01905 |
| `claudeai.mcp_app.wrapper_bridge_event` | 1 | `event_type`~, `host_view_session_id`~, `redacted_url`~, `server_name`~, `server_uuid`~ | 0 | payload-00507 |
| `claudeai.mcp_registry_empty` | 1 | `visibility_tags`~ | 0 | payload-02775 |
| `claudeai.melange.external_import_submitted` | 1 | `status`~ | 0 | payload-02729 |
| `claudeai.melange.user_action` | 2 | `action`, `taxonomy_bucket`~ | 0 | payload-02727, payload-02728 |
| `claudeai.member_invite.bulk_submitted` | 1 | `amber_wren_attached`~, `approved_count`~, `pending_count`~, `source`~, `total_count`~ | 0 | payload-00388 |
| `claudeai.member_invite.modal_opened` | 1 |  | 0 | payload-02173 |
| `claudeai.member_invite.settings.toggled` | 1 | `enabled`~ | 0 | payload-02491 |
| `claudeai.member_invite.submitted` | 1 | `amber_wren_attached`~, `source`~, `status`~ | 0 | payload-00387 |
| `claudeai.members.seat_tier_changed` | 3 | `data`~, `data.from_tier`~, `data.source`, `data.to_tier`~ | 0 | payload-02438, payload-02439, payload-02440 |
| `claudeai.memory.account_setting_toggled` | 2 | `enabled`~, `reset_memory`~ | 0 | payload-02778, payload-02779 |
| `claudeai.memory.edit_memory` | 1 | `projectUuid`~ | 0 | payload-02777 |
| `claudeai.memory.edit_modal_opened` | 1 | `projectUuid`~ | 0 | payload-00513 |
| `claudeai.memory.import_modal_opened` | 1 |  | 0 | payload-01010 |
| `claudeai.memory.import_prompt_copied` | 1 |  | 0 | payload-01011 |
| `claudeai.memory.import_resynthesize_completed` | 1 |  | 0 | payload-02782 |
| `claudeai.memory.import_resynthesize_failed` | 1 |  | 0 | payload-02783 |
| `claudeai.memory.import_see_in_action_clicked` | 1 |  | 0 | payload-01013 |
| `claudeai.memory.import_submitted` | 2 | `backend`, `likely_refusal`~, `pasted_char_count`~ | 1 | payload-01012, payload-02781 |
| `claudeai.memory.legacy_memory_downloaded` | 1 |  | 0 | payload-00249 |
| `claudeai.memory.legacy_project_memory_downloaded` | 1 |  | 0 | payload-02333 |
| `claudeai.memory.memory_reset` | 2 |  | 0 | payload-01014, payload-02776 |
| `claudeai.memory.org_setting_toggled` | 1 | `enabled`~ | 0 | payload-01072 |
| `claudeai.mentions.dropdown.opened` | 1 | `time_to_options_ms`~ | 0 | payload-03277 |
| `claudeai.mentions.option.selected` | 1 | `attachment_count`~ | 0 | payload-03278 |
| `claudeai.message.check_for_reply` | 1 | `conversation_uuid`~, `duration_ms`~, `navigator_online`~, `outcome`~, `try_again_offered`~ | 1 | payload-01943 |
| `claudeai.message.completion_failed` | 1 | `assistant_message_uuid`~, `content_blocks_received`~, `conversation_uuid`~, `elapsed_ms`~, `error_classification`~, `error_status_code`~, `error_type`~, `model`~, `transport` | 0 | payload-02654 |
| `claudeai.message.copied` | 1 | `copy_source`~, `renderer`~, `sender`~ | 1 | payload-01936 |
| `claudeai.message.duplicate_key` | 1 | `after_message_start`~, `conversation_uuid`~, `retried_error_type`?~, `verification_retried`?~ | 2 | payload-02648 |
| `claudeai.message.duplicate_key_unverified` | 1 | `conversation_uuid`~, `read_status`~, `reason`~, `retried`~ | 0 | payload-02649 |
| `claudeai.message.edit_started` | 1 | `chat_backend`?, `conversation_uuid`~, `entry_point`~, `message_uuid`~ | 1 | payload-01955 |
| `claudeai.message.edited` | 1 | `chat_backend`?~, `is_identical_content`~, `is_last_human_message`~ | 2 | payload-02118 |
| `claudeai.message.failed_send_uuid_reuse` | 1 | `conversation_uuid`~ | 0 | payload-03030 |
| `claudeai.message.feedback_clicked` | 1 | `chat_backend`?~, `conversation_uuid`~, `input_mode`~, `message_uuid`~, `rating`~, `rating_surface`~, `renderer`~ | 1 | payload-01934 |
| `claudeai.message.first_text` | 1 | `assistant_message_uuid`~, `chat_backend`~, `cli_session_id`?~, `conversation_uuid`~, `first_assistant_message_id`?~, `held_by_host`~, `human_message_uuid`~, `is_incognito`~, `is_new_conversation`~, `is_retry`~, `message_index`~, `model`~, `session_type`?~, `start_to_emit_ms`, `time_in_background_ms`~, `user_message_uuid`?~, `user_wait_before_first_text_ms`?~, `user_waits_before_first_text`?~, `was_queued`~, `was_queued_reason`~ | 6 | payload-02723 |
| `claudeai.message.font_name_reply_shown` | 1 | `message_uuid`~ | 0 | payload-01956 |
| `claudeai.message.opened_stream_lost` | 1 | `conversation_uuid`~, `inline_conversation_create`?~, `persisted`~, `reads`~, `reason`?~, `wait_ms`~ | 2 | payload-02650 |
| `claudeai.message.outside_composer.sent` | 1 | `carrier`~, `conversation_uuid`~, `is_incognito`~, `kind`~ | 0 | payload-02945 |
| `claudeai.message.perceived_ttft` | 1 | `assistant_message_uuid`~, `chat_backend`~, `cli_session_id`?~, `client_ttft_ms`~, `conversation_uuid`~, `document_attachment_count`~, `enabled_web_search`~, `fetch_to_first_byte_ms`~, `first_assistant_message_id`?~, `first_content_ms`~, `first_content_type`~, `first_envelope_fanout_wall_ms`?~, `first_envelope_ms`?~, `first_envelope_received_wall_ms`?~, `first_frame_kind`?~, `first_frame_receipt_via`?~, `first_frame_received_wall_ms`?~, `first_frame_stream_wall_ms`?~, `first_reply_message_created_wall_ms`?~, `first_reply_message_received_wall_ms`?~, `held_by_host`~, `human_message_uuid`~, `image_attachment_count`~, `is_incognito`~, `is_new_conversation`~, `is_retry`~, `is_yukon_gold`~, `message_index`~, `message_length`~, `mm_document_count`?~, `model`~, `network_attempt_count`~, `perceived_ttft_ms`~, `post_fetch_ttft_ms`~, `pre_fetch_time_ms`~, `research_mode`~, `response_open_ms`~, `seconds_since_last_message`?~, `thinking_mode`~, `time_in_background_ms`~, `tool_count`~, `used_inline_conversation_create`~, `user_message_uuid`?~, `was_queued`~, `was_queued_reason`~ | 15 | payload-02724 |
| `claudeai.message.perceived_ttlt` | 1 | `assistant_message_uuid`~, `chat_backend`~, `content_block_count`~, `conversation_uuid`~, `enabled_web_search`~, `held_by_host`~, `human_message_uuid`~, `is_incognito`~, `is_new_conversation`~, `is_retry`~, `message_index`~, `message_length`~, `model`~, `navigated_away`~, `perceived_ttlt_ms`~, `reply_complete_ms`~, `reply_text_chars`~, `research_mode`~, `stop_reason`~, `thinking_mode`~, `time_in_background_ms`~, `tool_count`~, `ttft_ms`~, `visibility_state`~, `waited_for_input`~, `was_queued`~, `was_queued_reason`~ | 0 | payload-02725 |
| `claudeai.message.recovery_completed` | 1 | `attempt_count`~, `conversation_uuid`~, `duration_ms`~, `outcome`~, `probe`~ | 0 | payload-02116 |
| `claudeai.message.recovery_slow_poll_started` | 1 | `attempt_count`~, `conversation_uuid`~, `probe`~ | 0 | payload-02117 |
| `claudeai.message.recovery_started` | 1 | `conversation_uuid`~, `probe`~, `trigger` | 0 | payload-02115 |
| `claudeai.message.selection_copied` | 1 | `copy_source`, `sender` | 1 | payload-01938 |
| `claudeai.message.sent` | 1 | `chat_backend`?~, `conversation_uuid`~, `has_attachments`~, `has_files`~, `has_personalized_style`~, `has_sync_sources`~, `include_profile_preferences`~, `input_mode`~, `is_incognito`~, `is_keep_going`~, `is_negative`~, `is_new_conversation`~, `is_yukon_gold`~, `message_index`~, `message_length`~, `model`~, `multiple_newline_count`~, `screenshot_file_count`~, `seconds_since_last_message`?~, `send_origin`~, `single_newline_count`~, `slash_command`?~, `text_formatting`~ | 4 | payload-02948 |
| `claudeai.message.stopped` | 1 | `assistant_message_uuid`?~, `chat_backend`?~, `completion_request_id`?~, `conversation_uuid`~, `had_visible_content`~, `human_message_uuid`?~, `last_block_kind`~, `ms_since_first_byte`?~, `ms_since_send`?~, `via`~ | 6 | payload-03006 |
| `claudeai.message.streaming_abandoned` | 1 | `abandoned_from`~, `conversation_uuid`~, `is_new_conversation`~, `is_retry`~, `navigated_to`~, `time_before_abandon_ms`~ | 0 | payload-02726 |
| `claudeai.message.user_triggered_retry` | 4 | `banner_classification`~, `is_last_human_message`~, `source`~ | 4 | payload-01402, payload-01403, payload-01935, payload-01957 |
| `claudeai.message.wiggle_container_in_use` | 2 | `auto_open_retry`~, `conversation_uuid`~ | 2 | payload-02651, payload-02652 |
| `claudeai.mini_claude.selection_action` | 2 | `action`, `selection_length`~ | 0 | payload-01930, payload-01931 |
| `claudeai.mini_claude.tooltip_impression` | 1 | `selection_length`~ | 0 | payload-01194 |
| `claudeai.misty_kestrel.diverted_desktop_coder` | 1 | `branch_settled`~, `chat_host`~, `client_platform`~, `experiment_variant`~ | 0 | payload-00182 |
| `claudeai.misty_kestrel.start_failed` | 1 | `branch_settled`~, `chat_host`~, `client_platform`~, `error_name`, `experiment_variant`~, `step`~, `surface` | 0 | payload-00181 |
| `claudeai.model_selector.effort_pick_attempted` | 1 | `effort`~, `in_humming_quill`~, `model`~, `previous_effort`~ | 1 | payload-03242 |
| `claudeai.model_selector.effort_selected` | 1 | `chat_backend`?~, `conversation_uuid`?~, `effort`~, `is_new_conversation`~, `model`~, `model_surface`~, `previous_effort`~ | 1 | payload-02927 |
| `claudeai.model_selector.extra_option_cleared` | 1 | `is_new_conversation`~, `model_id`~ | 1 | payload-02952 |
| `claudeai.model_selector.extra_option_selected` | 1 | `previous_model_id`~ | 1 | payload-02951 |
| `claudeai.model_selector.model_selected` | 2 | `model`~, `model_surface`~, `previous_model`~ | 0 | payload-03237, payload-03238 |
| `claudeai.model_selector.opened` | 2 | `model_surface`~ | 0 | payload-03236, payload-03239 |
| `claudeai.model_selector.upgrade_clicked` | 2 | `model`~, `model_surface`~, `required_plan`~ | 0 | payload-03235, payload-03240 |
| `claudeai.model_usage_banner.dismissed` | 3 | `banner_surface`~, `mode`~, `presentation`~, `trigger` | 0 | payload-00761, payload-02987, payload-02989 |
| `claudeai.model_usage_banner.shown` | 2 | `banner_surface`~, `mode`~, `presentation`~ | 0 | payload-00762, payload-02988 |
| `claudeai.notification.clicked` | 2 | `action`~, `category`~, `location`~, `outcome`~, `target_kind`~, `target_url`~ | 2 | payload-02996, payload-02999 |
| `claudeai.notification.permission.request_started` | 1 | `source`~ | 0 | payload-02993 |
| `claudeai.notification.permission.result` | 1 | `permission`~, `source`~ | 0 | payload-02992 |
| `claudeai.notification.received` | 2 | `category`~, `location`~ | 2 | payload-02994, payload-02997 |
| `claudeai.notification.shown` | 2 | `category`~, `has_actions`~, `location`~, `reason`~, `target_kind`~ | 2 | payload-02995, payload-02998 |
| `claudeai.notification.suppressed` | 2 | `category`~, `has_actions`~, `location`~, `reason`~, `target_kind`~ | 2 | payload-02995, payload-02998 |
| `claudeai.notification_cta.dismissed` | 1 |  | 0 | payload-03166 |
| `claudeai.oak_latch.cap_clicked` | 1 | `action`~, `arm`~, `headroom`~, `request_count`~ | 0 | payload-00106 |
| `claudeai.oak_latch.cap_shown` | 1 | `arm`~, `headroom`~, `request_count`~, `withheld_for`~ | 0 | payload-00105 |
| `claudeai.oak_latch.clicked` | 1 | `arm`~, `request_count`~ | 0 | payload-00103 |
| `claudeai.oak_latch.confirm_closed` | 2 | `arm`~, `outcome`~, `request_count`~ | 0 | payload-00101, payload-00104 |
| `claudeai.oak_latch.confirm_shown` | 1 | `arm`~, `request_count`~ | 0 | payload-00102 |
| `claudeai.oak_latch.dismissed` | 1 | `arm`~, `request_count`~ | 0 | payload-01901 |
| `claudeai.oak_latch.failed` | 1 | `arm`~, `request_count`~ | 0 | payload-00094 |
| `claudeai.oak_latch.offer_accepted` | 1 | `arm` | 0 | payload-00099 |
| `claudeai.oak_latch.offer_declined` | 1 | `arm`, `via`~ | 0 | payload-00100 |
| `claudeai.oak_latch.offer_failed` | 1 | `arm` | 0 | payload-00098 |
| `claudeai.oak_latch.offer_shown` | 1 | `arm`, `request_count`~ | 0 | payload-00093 |
| `claudeai.oak_latch.offer_skipped` | 2 | `arm`, `reason`~ | 0 | payload-00096, payload-00097 |
| `claudeai.oak_latch.shown` | 1 | `arm`~, `request_count`~ | 0 | payload-01900 |
| `claudeai.oak_latch.succeeded` | 1 | `approved_count`~, `arm`~, `request_count`~ | 0 | payload-00095 |
| `claudeai.ochre_wren.download_sign` | 2 | `download_surface`~, `media_type`~, `mode`~, `outcome`~, `size_bytes`~ | 1 | payload-02048, payload-02146 |
| `claudeai.office_addin.fallback_clicked` | 2 | `product`~, `source`~ | 0 | payload-03083, payload-03086 |
| `claudeai.office_addin.install_clicked` | 1 | `product`~, `source`~ | 0 | payload-03084 |
| `claudeai.office_addin_finish_setup_guide.appsource_clicked` | 2 | `arm`~, `host`~, `product`~ | 0 | payload-01624, payload-02142 |
| `claudeai.office_addin_finish_setup_guide.dismissed` | 2 | `arm`~, `host`~, `presentation`, `product`~ | 0 | payload-01625, payload-02230 |
| `claudeai.office_addin_finish_setup_guide.displayed` | 2 | `arm`~, `host`~, `presentation`, `product`~ | 0 | payload-01623, payload-02228 |
| `claudeai.office_addin_finish_setup_guide.steps_opened` | 2 | `arm`~, `host`~, `product`~ | 0 | payload-02229, payload-03085 |
| `claudeai.onboarding.chip_routed` | 1 | `category`~, `chip_id`~, `destination`~, `target`~ | 0 | payload-00202 |
| `claudeai.onboarding.chooser_expansion_agent_clicked` | 1 |  | 0 | payload-00229 |
| `claudeai.onboarding.chooser_expansion_shown` | 1 |  | 0 | payload-00228 |
| `claudeai.onboarding.claude_code_step.install_clicked` | 1 |  | 0 | payload-00200 |
| `claudeai.onboarding.claude_code_step.shown` | 1 |  | 0 | payload-00199 |
| `claudeai.onboarding.claude_code_step.skipped` | 1 |  | 0 | payload-00201 |
| `claudeai.onboarding.desktop_download.shown` | 1 | `platform`~, `referral_campaign`~, `referral_source`~, `variant`~ | 0 | payload-00233 |
| `claudeai.onboarding.desktop_download.skipped` | 1 | `platform`~, `referral_campaign`~, `referral_source`~ | 0 | payload-00234 |
| `claudeai.onboarding.desktop_download.three_column.shown` | 1 | `cc_trial_on_pro`~, `platform`~, `surface`~ | 0 | payload-01207 |
| `claudeai.onboarding.email_invite_accept.completed` | 1 | `organization_uuid`~ | 1 | payload-00243 |
| `claudeai.onboarding.email_invite_accept.failed` | 1 | `organization_uuid`~ | 1 | payload-00244 |
| `claudeai.onboarding.enterprise_2026.chip_clicked` | 1 | `chip_category`~, `chip_id`~, `onboarding_arm`~, `role`~ | 0 | payload-00222 |
| `claudeai.onboarding.enterprise_2026.own_topic_clicked` | 1 | `onboarding_arm`~, `role`~ | 0 | payload-00223 |
| `claudeai.onboarding.enterprise_2026.role_selected` | 1 | `onboarding_arm`~, `role`~ | 0 | payload-00221 |
| `claudeai.onboarding.free_vs_paid.recommended_shown` | 1 | `plan`~ | 0 | payload-02132 |
| `claudeai.onboarding.free_vs_paid.shown` | 1 | `help_me_choose`~, `plan_type_tab`~, `plans_shown`~, `pro_card_label`~, `recommended_plan`~ | 0 | payload-02134 |
| `claudeai.onboarding.gift_redeem.completed` | 1 |  | 0 | payload-00247 |
| `claudeai.onboarding.guest_pass_install.completed` | 1 |  | 0 | payload-00246 |
| `claudeai.onboarding.mobile_app_install.download_clicked` | 1 | `platform`~ | 0 | payload-00231 |
| `claudeai.onboarding.mobile_app_install.shown` | 1 | `platform`~ | 0 | payload-00230 |
| `claudeai.onboarding.mobile_app_install.skipped` | 1 | `platform`~ | 0 | payload-00232 |
| `claudeai.onboarding.name_entry_cowork_session.enrolled` | 1 | `branch`?~, `chat_host`~, `experiment_variant`~, `offer_check`~, `offer_count`?~, `remote_cowork`?~ | 3 | payload-00185 |
| `claudeai.onboarding.name_entry_cowork_session.excluded` | 2 | `chat_host`~, `flags_fresh`~, `hub_chat_gate`~, `hub_delivery`~, `my_access_fresh`~, `offer_check`~, `offer_count`?~, `onboarding_arm`~, `reason`~ | 1 | payload-00183, payload-00184 |
| `claudeai.onboarding.name_entry_cowork_session.start_failed` | 6 | `chat_host`~, `error_name`~, `experiment_variant`~, `first_task_surface`, `flags_fresh`~, `hub_delivery`~, `my_access_fresh`~, `offer_check`~, `offer_count`?~, `onboarding_arm`~ | 8 | payload-00186, payload-00188, payload-00189, payload-00191, payload-00192, payload-00194 |
| `claudeai.onboarding.name_entry_cowork_session.started` | 3 | `chat_host`~, `conversation_uuid`~, `experiment_variant`~, `first_task_surface`, `offer_check`~, `offer_count`?~, `onboarding_arm`~, `session_id`~, `variant_honored`~, `wizard_connected_count`?~, `wizard_preconnected_count`?~ | 8 | payload-00187, payload-00190, payload-00193 |
| `claudeai.onboarding.role_based_install.continue_clicked` | 1 | `surface`~ | 0 | payload-02226 |
| `claudeai.onboarding.role_based_install.instructions_shown` | 1 | `surface`~ | 0 | payload-02225 |
| `claudeai.onboarding.role_onepage.chip_clicked` | 1 | `chip_id`~, `chip_index`~, `mode`, `role`~, `role_label`~ | 0 | payload-00207 |
| `claudeai.onboarding.role_onepage.chips_shown` | 1 | `chip_ids`~, `role`~ | 0 | payload-00203 |
| `claudeai.onboarding.role_onepage.continue_clicked` | 1 | `mode`, `role`~, `role_label`~ | 0 | payload-00209 |
| `claudeai.onboarding.role_onepage.role_changed` | 1 | `mode`, `role`~, `role_label`~ | 0 | payload-00205 |
| `claudeai.onboarding.role_onepage.science_fields_selected` | 1 | `science_fields`~ | 0 | payload-00212 |
| `claudeai.onboarding.role_onepage.science_fields_shown` | 1 |  | 0 | payload-00206 |
| `claudeai.onboarding.role_onepage.shown` | 1 | `mode` | 0 | payload-00204 |
| `claudeai.onboarding.role_onepage.skipped` | 1 | `continue_button_shown`?~, `had_role_selected`~, `mode`, `role`~, `role_label`~ | 1 | payload-00208 |
| `claudeai.onboarding.role_step.shown` | 1 | `onboarding_arm`~, `post_role_arm`~, `prefilled`~, `ui`~ | 0 | payload-00210 |
| `claudeai.onboarding_first_chat.shown` | 1 | `variant`~ | 0 | payload-01430 |
| `claudeai.operon_access_page.viewed` | 1 | `state`~ | 0 | payload-01992 |
| `claudeai.operon_access_request.resolution_toast_shown` | 1 | `resolution`~ | 0 | payload-02917 |
| `claudeai.operon_access_request.submitted` | 1 | `reason`~ | 0 | payload-02916 |
| `claudeai.org_discovery.admin.approval_mode_changed` | 1 | `new_mode`~, `previous_mode`~ | 0 | payload-02490 |
| `claudeai.org_discovery.admin.domain_disabled` | 1 | `domain`~ | 0 | payload-02484 |
| `claudeai.org_discovery.admin.domain_enabled` | 1 | `domain`~ | 0 | payload-02483 |
| `claudeai.org_discovery.admin.verify_domain_required` | 1 | `domain`~ | 0 | payload-02482 |
| `claudeai.org_discovery.banner_shown` | 2 | `organization_uuid`~, `source`~ | 0 | payload-01822, payload-02581 |
| `claudeai.org_discovery.join_approved` | 1 | `organization_uuid`~, `source`~ | 0 | payload-00993 |
| `claudeai.org_discovery.join_failed` | 1 | `organization_uuid`~, `source`~ | 0 | payload-00995 |
| `claudeai.org_discovery.join_pending` | 1 | `organization_uuid`~, `source`~ | 0 | payload-00994 |
| `claudeai.org_discovery.join_requested` | 1 | `org_count`~, `organization_uuid`~, `source`~ | 0 | payload-00992 |
| `claudeai.org_discovery.onboarding_checkbox.disabled` | 1 | `email_domain`~ | 0 | payload-00973 |
| `claudeai.org_discovery.onboarding_checkbox.domain_ineligible` | 1 | `email_domain`~ | 0 | payload-00972 |
| `claudeai.org_discovery.onboarding_checkbox.enabled` | 1 | `email_domain`~ | 0 | payload-00973 |
| `claudeai.org_discovery.onboarding_checkbox.shown` | 1 | `email_domain`~ | 0 | payload-00971 |
| `claudeai.org_discovery.personal_account_selected` | 2 | `has_pending_request`~, `source` | 0 | payload-00257, payload-00258 |
| `claudeai.outlook_connector_mail_banner.cta_clicked` | 1 | `surface`~, `tool`~ | 0 | payload-03141 |
| `claudeai.outlook_connector_mail_banner.dismissed` | 1 | `surface`~, `tool`~ | 0 | payload-03142 |
| `claudeai.outlook_connector_mail_banner.displayed` | 1 | `surface`~, `tool`~ | 0 | payload-03140 |
| `claudeai.overage_bundles.confirmation_dismissed` | 1 | `bundle_id`~, `credits_flow_clarity_arm`~, `via`~ | 0 | payload-00695 |
| `claudeai.overage_bundles.purchase_clicked` | 5 | `amount_source`~, `bundle_id`~, `credits_flow_clarity_arm`~, `currency`~, `entrypoint_source`~, `host`~, `local_credit_minor_units`~, `over_cap`?~, `payment_method_type`~, `price_minor_units`~ | 1 | payload-00696, payload-00697, payload-00698, payload-00699, payload-00700 |
| `claudeai.overage_bundles.purchase_failed` | 5 | `amount_source`~, `bundle_id`~, `credits_flow_clarity_arm`~, `discount_minor_units`~, `error_action`~ | 0 | payload-00686, payload-00687, payload-00688, payload-00689, payload-00690 |
| `claudeai.overage_bundles.purchase_succeeded` | 1 | `amount_source`~, `bundle_id`~, `credits_flow_clarity_arm`~, `discount_minor_units`~, `entrypoint_source`~, `host`~, `payment_method_override`~ | 0 | payload-00691 |
| `claudeai.overage_bundles.selected` | 1 | `bundle_id`~, `credit_minor_units`~, `discount_pct`~, `price_minor_units`~ | 0 | payload-00702 |
| `claudeai.overage_bundles.viewed` | 1 | `auto_reload_variant`~, `bundle_count`~, `cap_remaining_minor_units`~, `credits_flow_clarity_arm`~, `default_bundle_id`~, `entrypoint_source`~, `host`~, `max_discount_pct`~ | 0 | payload-00703 |
| `claudeai.overages.auto_reload_checkout_toggle.dismissed` | 1 | `surface`~ | 0 | payload-00692 |
| `claudeai.overages.auto_reload_checkout_toggle.enable_deferred` | 1 | `reason`~, `surface`~ | 0 | payload-00693 |
| `claudeai.overages.auto_reload_checkout_toggle.toggled` | 1 | `default_on`~, `enabled`~, `surface`~ | 0 | payload-00685 |
| `claudeai.overages.auto_reload_checkout_toggle.viewed` | 1 | `currency`~, `surface`~, `variant`~ | 0 | payload-00704 |
| `claudeai.overages.auto_reload_disabled` | 1 |  | 0 | payload-02640 |
| `claudeai.overages.auto_reload_enabled` | 4 | `surface`~, `via` | 0 | payload-00694, payload-00706, payload-00793, payload-02639 |
| `claudeai.overages.auto_reload_updated` | 1 |  | 0 | payload-02641 |
| `claudeai.overages.disabled` | 2 | `spend_limit_type` | 0 | payload-01835, payload-02352 |
| `claudeai.overages.enabled` | 2 | `is_setup`~, `spend_limit_type` | 0 | payload-02353, payload-03272 |
| `claudeai.overages.monthly_limit_set` | 2 | `is_unlimited`~, `is_zero`~, `source` | 0 | payload-00705, payload-02163 |
| `claudeai.overages.monthly_limit_updated` | 2 | `is_unlimited`~, `is_zero`~, `source` | 0 | payload-00705, payload-02162 |
| `claudeai.overages_or_upgrades_upsell_modal.closed` | 1 | `can_upgrade`~, `credits_explainer_arm`~, `entry_point`~, `entry_source`~, `is_warning`~, `limit_window`~, `overages_enabled`~, `paid_account_tier`~ | 0 | payload-03273 |
| `claudeai.overages_or_upgrades_upsell_modal.overages_clicked` | 1 | `can_upgrade`~, `credits_explainer_arm`~, `entry_source`~, `is_warning`~, `limit_window`~, `overages_enabled`~, `paid_account_tier`~ | 0 | payload-00511 |
| `claudeai.overages_or_upgrades_upsell_modal.upgrade_clicked` | 1 | `can_upgrade`~, `credits_explainer_arm`~, `entry_source`~, `is_warning`~, `limit_window`~, `overages_enabled`~, `paid_account_tier`~, `upgrade_target`~ | 0 | payload-00512 |
| `claudeai.overages_or_upgrades_upsell_modal.viewed` | 1 | `can_upgrade`~, `credits_explainer_arm`~, `entry_point`~, `entry_source`~, `hours_until_reset`~, `is_warning`~, `limit_window`~, `overages_enabled`~, `paid_account_tier`~ | 0 | payload-00510 |
| `claudeai.page.new_chat_input_ready` | 1 | `duration_ms`~, `is_first_load`~ | 1 | payload-03015 |
| `claudeai.page.static_composer_swap` | 1 |  | 1 | payload-03012 |
| `claudeai.perf.composer_typing` | 1 |  | 1 | payload-03010 |
| `claudeai.perf.interaction_histogram` | 1 | `bucket_bounds_ms`~, `build_id`~, `hidden_excluded`~, `key_nav`~, `key_non_nav`~, `key_paste_non_nav`~, `key_send_non_nav`~, `pointer_nav`~, `pointer_non_nav`~, `total_interactions`~ | 0 | payload-03014 |
| `claudeai.perf.interaction_slow` | 1 | `build_id`~, `composer_state`~, `conversation_uuid`~, `duration_ms`~, `focus_at_report`~, `gates`~, `input_delay_ms`~, `interaction_id`~, `interaction_type`~, `is_streaming`~, `is_streaming_source`~, `js_heap_limit_mb`~, `key`~, `key_join_delta_ms`~, `loaf_entry_count`~, `loaf_script_char_pos`~, `loaf_script_duration_ms`~, `loaf_script_forced_layout_ms`~, `loaf_script_function`~, `loaf_script_invoker`~, `loaf_script_invoker_type`~, `loaf_script_source`~, `loaf_total_blocking_ms`~, `loaf_total_forced_layout_ms`~, `message_count`~, `nav_during_interaction`~, `overlay`~, `presentation_delay_ms`~, `processing_ms`~, `raf_interval_max_ms`~, `raf_interval_ms`~, `raf_probe_delay_ms`~, `raf_probe_outcome`~, `sample_rate`~, `send_dispatch`~, `send_index_in_document`~, `send_pre_fetch_ms`~, `tab_age_ms`~, `target`~, `used_js_heap_mb`~, `visibility_at_report`~ | 0 | payload-03013 |
| `claudeai.perf.web_vital` | 1 | `build_version`~, `metric`~, `navigation_type`~, `to_path`?~ | 2 | payload-02645 |
| `claudeai.pewter_finch.admin_toggled` | 1 | `new_state`~ | 0 | payload-01067 |
| `claudeai.pewter_finch.ask_owner_nav_link_shown` | 1 |  | 0 | payload-01501 |
| `claudeai.pewter_finch.ask_owner_page_learn_more_clicked` | 1 |  | 0 | payload-01556 |
| `claudeai.pewter_finch.ask_owner_page_request_button_shown` | 1 |  | 0 | payload-01553 |
| `claudeai.pewter_finch.ask_owner_page_viewed` | 1 |  | 1 | payload-01552 |
| `claudeai.pewter_finch.attribution_toggled` | 1 | `new_state`~ | 0 | payload-01068 |
| `claudeai.pewter_finch.create_content_reset` | 2 | `editor_surface`, `template_kind`~ | 0 | payload-01541, payload-01564 |
| `claudeai.pewter_finch.create_custom_facet_added` | 1 | `answer_type`~, `category_count`~, `custom_facet_count`~, `editor_surface`~, `has_description`~, `has_meanings`~ | 0 | payload-01539 |
| `claudeai.pewter_finch.create_custom_facet_details_opened` | 1 | `answer_type`~, `dialog_mode`~, `editor_surface`~ | 0 | payload-01538 |
| `claudeai.pewter_finch.create_custom_facet_dialog_opened` | 1 | `dialog_mode`~, `editor_surface`~ | 0 | payload-01536 |
| `claudeai.pewter_finch.create_custom_facet_edited` | 1 | `answer_type`~, `category_count`~, `custom_facet_count`~, `editor_surface`~, `has_description`~, `has_meanings`~ | 0 | payload-01539 |
| `claudeai.pewter_finch.create_custom_facet_removed` | 1 | `custom_facet_count`~, `editor_surface`~ | 0 | payload-01537 |
| `claudeai.pewter_finch.create_custom_facets_shown` | 1 | `editor_surface`~ | 0 | payload-01535 |
| `claudeai.pewter_finch.create_step_shown` | 1 | `create_step`~, `step_entry`~ | 0 | payload-01545 |
| `claudeai.pewter_finch.create_template_picked` | 2 | `editor_surface`, `is_content_edited`~, `loupe_preset_id`?~, `template_kind`?~, `template_uuid`?~ | 1 | payload-01540, payload-01562 |
| `claudeai.pewter_finch.report_drilldown` | 1 |  | 2 | payload-00466 |
| `claudeai.pewter_finch.report_drilldown_closed` | 1 |  | 2 | payload-00467 |
| `claudeai.pewter_finch.report_edit_template_clicked` | 1 | `report_uuid`~, `template_uuid`~ | 0 | payload-01531 |
| `claudeai.pewter_finch.report_event_rejected` | 1 | `field`?~, `reason`~ | 2 | payload-00468 |
| `claudeai.pewter_finch.report_feedback_submitted` | 1 | `organization_uuid`?~, `previous_spend_rating`~, `previous_value_rating`~, `report_uuid`~, `spend_rating`~, `value_rating`~ | 1 | payload-00583 |
| `claudeai.pewter_finch.report_interaction` | 2 | `counter`, `failed`~, `organization_uuid`?~, `props`~, `report_uuid`~, `view_surface`~, `viewer_kind`?~ | 3 | payload-00465, payload-00470 |
| `claudeai.pewter_finch.report_part_viewed` | 2 | `counter`~, `failed`~, `organization_uuid`?~, `part`~, `part_kind`, `props`~, `report_uuid`~, `view_surface`~, `viewer_kind`?~ | 2 | payload-00464, payload-00471 |
| `claudeai.pewter_finch.report_viewed` | 2 | `foreign_script_hosts`~, `hash_listed`~, `last_body_tag`~, `organization_uuid`?~, `report_uuid`~, `script_count`~, `script_kept`~, `view_surface`~ | 2 | payload-00462, payload-00463 |
| `claudeai.pewter_finch.requested` | 1 | `custom_facet_category_count`?~, `custom_facet_count`?~, `custom_facet_scale_count`?~, `custom_facet_yes_no_count`?~, `is_content_edited`?~, `loupe_preset_id`~, `products`~, `question_count`?~, `report_uuid`~, `template_kind`?~, `template_uuid`?~ | 2 | payload-01546 |
| `claudeai.pewter_finch.scope_create_group_line_clicked` | 1 |  | 0 | payload-01534 |
| `claudeai.pewter_finch.scope_create_group_line_shown` | 1 |  | 0 | payload-01532 |
| `claudeai.pewter_finch.scope_create_group_row_clicked` | 1 |  | 0 | payload-01533 |
| `claudeai.pewter_finch.spend_limits_cta_clicked` | 1 | `report_uuid`~, `view_surface`~ | 1 | payload-01528 |
| `claudeai.pewter_finch.spend_limits_dialog_closed` | 1 | `create_group_shown`~, `entry`~, `failed_step`?~, `group_limit_mode`~, `outcome`~, `raised_count`~, `report_uuid`~, `view_surface`~ | 1 | payload-01530 |
| `claudeai.pewter_finch.spend_limits_dialog_opened` | 1 | `any_above_ladder`~, `attributed`~, `can_create_group`~, `entry`~, `groups_count`~, `people_count`~, `people_with_suggestion_count`~, `report_uuid`~, `view_surface`~ | 0 | payload-01529 |
| `claudeai.pewter_finch.spend_limits_shown` | 1 | `report_uuid`~, `view_surface`~ | 1 | payload-01527 |
| `claudeai.pewter_finch.template_deleted` | 1 | `template_uuid`~ | 0 | payload-01547 |
| `claudeai.pewter_finch.template_duplicate_clicked` | 1 | `template_uuid`~ | 0 | payload-01549 |
| `claudeai.pewter_finch.template_editor_shown` | 1 | `editor_mode`~, `template_uuid`~ | 0 | payload-01558 |
| `claudeai.pewter_finch.template_save_as_opened` | 2 | `editor_surface`, `is_content_edited`~ | 0 | payload-01544, payload-01561 |
| `claudeai.pewter_finch.template_save_refused` | 2 | `refusal_kind`~ | 2 | payload-01543, payload-01560 |
| `claudeai.pewter_finch.template_saved` | 2 | `custom_facet_count`~, `loupe_preset_id`~, `question_count`~, `template_uuid`~ | 2 | payload-01542, payload-01559 |
| `claudeai.pewter_finch.template_use_in_report_clicked` | 1 | `template_uuid`~ | 0 | payload-01563 |
| `claudeai.pewter_finch.templates_tab_shown` | 1 | `tab_state`~, `template_count`~ | 0 | payload-01548 |
| `claudeai.pewter_finch.turn_on_nav_link_shown` | 1 |  | 0 | payload-01500 |
| `claudeai.pewter_finch.turn_on_page_cta_clicked` | 1 |  | 1 | payload-01555 |
| `claudeai.pewter_finch.turn_on_page_learn_more_clicked` | 1 |  | 0 | payload-01556 |
| `claudeai.pewter_finch.turn_on_page_templates_link_clicked` | 1 | `template_count`~ | 0 | payload-01557 |
| `claudeai.pewter_finch.turn_on_page_templates_link_shown` | 1 | `template_count`~ | 0 | payload-01554 |
| `claudeai.pewter_finch.turn_on_page_viewed` | 1 |  | 1 | payload-01552 |
| `claudeai.pewter_finch.turn_on_request_badge_shown` | 1 |  | 0 | payload-00060 |
| `claudeai.pewter_finch.turn_on_request_row_denied` | 1 |  | 0 | payload-02368 |
| `claudeai.pewter_finch.turn_on_request_row_deny_clicked` | 1 |  | 0 | payload-02365 |
| `claudeai.pewter_finch.turn_on_request_row_review_clicked` | 1 |  | 0 | payload-02364 |
| `claudeai.pewter_finch.turn_on_request_row_shown` | 1 |  | 0 | payload-02359 |
| `claudeai.pewter_finch.turned_on_toast_cta_clicked` | 1 |  | 0 | payload-01065 |
| `claudeai.pewter_finch.turned_on_toast_shown` | 1 |  | 0 | payload-01066 |
| `claudeai.plugin.suggestion.dismissed` | 1 | `plugin_id`?~, `trigger`~ | 2 | payload-01174 |
| `claudeai.plugin.suggestion.install_clicked` | 1 | `plugin_id`?~, `trigger`~ | 2 | payload-01173 |
| `claudeai.plugin.suggestion.install_failed` | 2 | `is_official_plugin`~, `plugin_name`~, `plugin_name_hash`~ | 4 | payload-01678, payload-02558 |
| `claudeai.plugin.suggestion.search_completed` | 1 | `corpus`?, `result_count`~, `search_backend`~, `session_id`~, `suggestion_surface`~, `top_capability_type`~, `trigger`~, `user_message_uuid`~ | 1 | payload-01674 |
| `claudeai.plugin.suggestion.skill_try_clicked` | 1 | `plugin_id`?~, `skill_name`~ | 2 | payload-01169 |
| `claudeai.plugin.suggestion.viewed` | 1 | `plugin_count`~, `plugin_id`?~, `trigger`~ | 2 | payload-01170 |
| `claudeai.plugin_setup.card_clicked` | 1 |  | 1 | payload-01483 |
| `claudeai.plugin_setup.card_dismissed` | 1 |  | 1 | payload-01484 |
| `claudeai.plugin_setup.card_shown` | 1 | `has_connect`~, `installed_by`~ | 1 | payload-01479 |
| `claudeai.plugin_setup.connect` | 1 | `outcome`~ | 1 | payload-01476 |
| `claudeai.plugin_setup.connect_confirm` | 2 | `accepted`~ | 2 | payload-01477, payload-01478 |
| `claudeai.plugin_setup.task_staged` | 2 | `via` | 2 | payload-01481, payload-01482 |
| `claudeai.plugin_setup.task_started` | 1 | `via`~ | 1 | payload-01480 |
| `claudeai.plugins.connector_setup_connect_clicked` | 1 | `connector_kind`~ | 1 | payload-02273 |
| `claudeai.plugins.connector_setup_dismissed` | 1 | `remaining_connector_count`~, `via`~ | 1 | payload-02274 |
| `claudeai.plugins.connector_setup_reminder_shown` | 1 | `surface`~ | 1 | payload-02122 |
| `claudeai.plugins.connector_setup_shown` | 1 | `actionable_connector_count`~, `ask_admin_connector_count`~, `first_party_connector_count`~, `missing_connector_count`~, `trigger`~ | 1 | payload-02272 |
| `claudeai.plugins.enable_consent.cancelled` | 1 | `method`~, `ms_since_shown`?~, `subject`~ | 1 | payload-02677 |
| `claudeai.plugins.enable_consent.continued` | 1 | `ms_since_shown`~, `subject`~ | 0 | payload-02676 |
| `claudeai.plugins.enable_consent.not_turned_on` | 2 | `reason`~, `subject`~ | 0 | payload-02551, payload-02698 |
| `claudeai.plugins.enable_consent.shown` | 2 | `notice`~, `subject`~ | 0 | payload-02552, payload-02699 |
| `claudeai.plugins.personal_marketplace_auto_sync_toggled` | 3 | `enabled`~, `marketplace_id`~, `origin` | 0 | payload-01000, payload-01369, payload-01636 |
| `claudeai.plugins.plugin.sndp_submitted` | 1 | `plugin_id`~ | 1 | payload-00892 |
| `claudeai.plugins.plugin.trnst_shared` | 1 | `plugin_id`~, `share_count`?~, `share_target`~ | 1 | payload-00115 |
| `claudeai.plugins.plugin.upload_validation_failed` | 2 | `error_count`~, `upload_type`~ | 0 | payload-00061, payload-01161 |
| `claudeai.plugins.sovr_decided` | 1 | `action`~, `kind`~, `outcome`~, `surface`~ | 0 | payload-00811 |
| `claudeai.plugins.sovr_files_viewed` | 1 | `admin_page`, `kind`~ | 0 | payload-02502 |
| `claudeai.plugins.trnst_ntc_clicked` | 1 |  | 1 | payload-00905 |
| `claudeai.plugins.trnst_ntc_dismissed` | 1 |  | 1 | payload-00907 |
| `claudeai.plugins.trnst_ntc_primary_clicked` | 1 |  | 1 | payload-00904 |
| `claudeai.plugins.trnst_ntc_primary_result` | 1 | `result`~ | 1 | payload-02638 |
| `claudeai.plugins.trnst_ntc_shown` | 1 | `arrived_on`~, `repeat`~ | 1 | payload-00908 |
| `claudeai.plugins.trnst_ntc_turned_off` | 1 |  | 1 | payload-00906 |
| `claudeai.plus_menu.opened` | 1 |  | 0 | payload-03223 |
| `claudeai.plus_menu.screenshot_clicked` | 1 |  | 0 | payload-01153 |
| `claudeai.pricing.approve_outcome` | 1 | `approve_type`~, `ms_since_view`~, `outcome`~, `press_seq`~, `rejection_reason`~ | 1 | payload-02296 |
| `claudeai.pricing.billing_address_escalated` | 1 | `ms_since_view`~ | 2 | payload-02293 |
| `claudeai.pricing.billing_address_held` | 1 | `ms_since_view`~ | 2 | payload-02292 |
| `claudeai.pricing.card_form_wallets` | 1 | `ms_since_view`~ | 2 | payload-02287 |
| `claudeai.pricing.checkout_form_ready` | 2 | `consent_mode`~, `display_amount_minor`~, `display_currency`~, `ms_since_view`~, `saved_address_primed`~ | 2 | payload-02283, payload-02300 |
| `claudeai.pricing.checkout_payment_option` | 1 | `ms_since_view`~ | 2 | payload-02288 |
| `claudeai.pricing.checkout_plan_changed` | 1 | `ms_since_view`~ | 2 | payload-02301 |
| `claudeai.pricing.checkout_step_lifecycle` | 1 | `approve_settled`~, `challenge_shown`~, `charged`~, `close_reason`~, `idv_status`~, `is_idv_replay`~, `is_phone_replay`~, `ms_in_step`~, `ms_since_view`~, `phase`~, `press_seq`~, `should_poll`~, `step`~ | 1 | payload-02299 |
| `claudeai.pricing.checkout_timing` | 3 | `approve_ms`, `billing_interval`~, `challenge_ms`, `charged`~, `confirm_ms`, `finalize_ms`, `intent_ms`, `is_idv_replay`~, `outcome_kind`~, `plan_type`~ | 5 | payload-02298, payload-02302, payload-02307 |
| `claudeai.pricing.currency_selected` | 1 | `from_currency`~, `to_currency`~ | 1 | payload-02294 |
| `claudeai.pricing.express_checkout_cancelled` | 1 | `ms_since_view`~ | 1 | payload-02290 |
| `claudeai.pricing.express_checkout_confirm_started` | 1 | `ms_since_view`~ | 2 | payload-02289 |
| `claudeai.pricing.express_checkout_ready` | 1 | `ms_since_view`~ | 2 | payload-02286 |
| `claudeai.pricing.express_checkout_refused` | 1 | `ms_since_view`~ | 2 | payload-02291 |
| `claudeai.pricing.extra_usage_banner.clicked` | 1 | `paid_account_tier`~ | 0 | payload-02596 |
| `claudeai.pricing.extra_usage_banner.viewed` | 1 | `paid_account_tier`~ | 0 | payload-02595 |
| `claudeai.pricing.gift_code_check_timed_out` | 1 | `elapsed_ms`~, `surface`~ | 0 | payload-02562 |
| `claudeai.pricing.gift_code_late_verdict_ignored` | 1 | `elapsed_ms`~, `gift_state`~, `surface`~ | 0 | payload-02563 |
| `claudeai.pricing.gift_code_redirected` | 1 | `after_release`~, `elapsed_ms`~, `gift_state`~, `surface`~ | 0 | payload-02564 |
| `claudeai.pricing.max_plan_toggled` | 1 | `new_plan_type`~ | 0 | payload-02560 |
| `claudeai.pricing.mobile_subscription_notice.credits_clicked` | 1 | `billing_type`~ | 0 | payload-02589 |
| `claudeai.pricing.mobile_subscription_notice.deeplink_clicked` | 1 | `billing_type`~ | 0 | payload-02588 |
| `claudeai.pricing.mobile_subscription_notice.qr_shown` | 1 | `billing_type`~ | 0 | payload-02587 |
| `claudeai.pricing.mobile_subscription_notice.viewed` | 1 | `billing_type`~, `paid_account_tier`~ | 0 | payload-02586 |
| `claudeai.pricing.payment_failed` | 34 | `action`, `billing_interval`?~, `browser_check_hint`~, `decline_code`?~, `error_code`~, `error_message`~, `error_type`~, `expected_entity`~, `failure_stage`~, `in_place_upgrade`~, `ms_since_view`?~, `plan_type`?~, `product`~, `recovered_to_pending`~, `resent`~, `response_entity`~, `team_promo_offer_code`~ | 20 | payload-00918, payload-00919, payload-00920, payload-00931, payload-00932, payload-00933, payload-00955, payload-00958, payload-00959, payload-00960, payload-00961, payload-00962, payload-00963, payload-00964, payload-00965, payload-00966, payload-00967, payload-01155, payload-01156, payload-02297, payload-02304, payload-02308, payload-02309, payload-02310, payload-02311, payload-02312, payload-02313, payload-02314, payload-02315, payload-02568, payload-02569, payload-02571, payload-02573, payload-02574 |
| `claudeai.pricing.payment_form_submitted` | 7 | `action`, `billing_interval`?~, `has_promo`~, `has_tax_id`~, `max_plan_type`?~, `ms_since_view`~, `plan_type`~, `product`~, `promo_code`~, `signup_source`~, `team_promo_offer_code`~, `timing_instrumented`?~ | 13 | payload-02295, payload-02305, payload-02565, payload-02566, payload-02567, payload-02570, payload-02572 |
| `claudeai.pricing.payment_method_selected` | 1 | `payment_method_type`~ | 1 | payload-02284 |
| `claudeai.pricing.payment_modal.viewed` | 3 | `billing_interval`~, `max_plan_type`~, `uses_saved_payment_method`~ | 3 | payload-02282, payload-02575, payload-02592 |
| `claudeai.pricing.plan_tab_selected` | 1 | `new_plan_tab`~ | 0 | payload-02599 |
| `claudeai.pricing.plan_toggled` | 3 | `new_interval`~ | 0 | payload-00948, payload-02128, payload-02593 |
| `claudeai.pricing.promo_applied` | 2 | `billing_interval`~, `discount_percent`~, `duration`~, `promo_code`~ | 0 | payload-02590, payload-02591 |
| `claudeai.pricing.team_card_period_toggled` | 1 | `new_interval`~ | 0 | payload-02130 |
| `claudeai.pricing.transition_credit_banner.viewed` | 1 |  | 0 | payload-02129 |
| `claudeai.pricing.wallet_availability` | 1 |  | 2 | payload-02285 |
| `claudeai.projects.activity.shared_conversation.opened` | 1 | `snapshot_uuid`~ | 0 | payload-01128 |
| `claudeai.projects.chat_starter.clicked` | 1 | `chat_starter_id`~, `project_subtype`~, `project_type`~ | 0 | payload-01126 |
| `claudeai.projects.conversation_moved` | 1 | `conversation_uuid`~, `project_uuid`~, `source` | 0 | payload-02890 |
| `claudeai.projects.delete_confirmed` | 1 | `from_local_project`?~, `migration_status`?~ | 2 | payload-02773 |
| `claudeai.projects.list_view.switched` | 1 | `is_archived`~, `new_category`~, `old_category`~ | 0 | payload-00325 |
| `claudeai.projects.open_in_cowork.clicked` | 1 | `project_uuid`~ | 0 | payload-01127 |
| `claudeai.projects.project.shared` | 1 | `project_uuid`~, `share_count`?~, `share_target`~ | 1 | payload-01293 |
| `claudeai.projects.project.viewed` | 1 | `project_uuid`~ | 0 | payload-01150 |
| `claudeai.projects.project_starter.clicked` | 1 | `path`~, `project_subtype`~, `project_type`~ | 0 | payload-02179 |
| `claudeai.projects.sort.switched` | 1 | `new_sort`~, `old_sort`~ | 0 | payload-00326 |
| `claudeai.projects.starred` | 4 | `project_uuid`~, `source`~ | 0 | payload-01134, payload-01137, payload-02681, payload-02830 |
| `claudeai.projects.unstarred` | 5 | `project_uuid`~, `source`~ | 0 | payload-00324, payload-01134, payload-01137, payload-02681, payload-02830 |
| `claudeai.quiet_wren.row_shown` | 1 |  | 0 | payload-00059 |
| `claudeai.quiet_wren.session_started` | 2 | `navigated`~, `onboarding_variant`~, `org_switched`~, `role_known`~, `session_id`?~, `variant_honored`~ | 2 | payload-00057, payload-00058 |
| `claudeai.quiet_wren.start_failed` | 1 | `error_name`~, `onboarding_variant`~ | 0 | payload-00056 |
| `claudeai.radiant_pine.link_added` | 1 |  | 1 | payload-00605 |
| `claudeai.rate_limit.probe_fired` | 1 | `representative_claim`~, `superseded`~, `within_limit`~ | 0 | payload-02661 |
| `claudeai.read_aloud.completed` | 3 | `conversation_uuid`~, `duration_ms`~, `location`~, `outcome`~, `start_trigger`~, `surface`~ | 3 | payload-01397, payload-02157, payload-02318 |
| `claudeai.read_aloud.playback_toggled` | 3 | `action`~, `conversation_uuid`~, `location`~, `surface`~, `trigger`~ | 0 | payload-01395, payload-02158, payload-02319 |
| `claudeai.read_aloud.started` | 3 | `conversation_uuid`~, `location`~, `start_trigger`~, `surface`~, `text_char_count`~, `voice_id`~ | 0 | payload-01396, payload-02156, payload-02317 |
| `claudeai.recents.grouping_toggled` | 2 | `from`~, `to`~ | 0 | payload-02857, payload-02861 |
| `claudeai.recents.type_filter_toggled` | 1 | `from`~, `to`~ | 0 | payload-02858 |
| `claudeai.recommend_claude_apps.cta_clicked` | 2 | `app_id`~, `cta_type`~, `has_custom_description`~, `host_surface`?~, `platform`~ | 2 | payload-02045, payload-02047 |
| `claudeai.recommend_claude_apps.viewed` | 1 | `app_count`~, `app_ids`~, `custom_description_count`~, `host_surface`?~ | 1 | payload-02044 |
| `claudeai.research.suggestion.dismissed` | 1 |  | 0 | payload-00055 |
| `claudeai.research.suggestion.start_clicked` | 1 | `is_retry`~ | 0 | payload-00054 |
| `claudeai.research.suggestion.viewed` | 1 |  | 0 | payload-00053 |
| `claudeai.research_invitation.funnel_step` | 1 | `action`~, `invitation_surface`~, `study_id`~ | 0 | payload-02231 |
| `claudeai.resubscribe.notice_button_clicked` | 2 | `variant` | 0 | payload-01168, payload-02479 |
| `claudeai.review_comment.batch_sent` | 3 | `comment_count`~ | 3 | payload-01413, payload-02800, payload-02950 |
| `claudeai.review_comment.created` | 3 | `comment_id`~ | 6 | payload-00642, payload-00646, payload-02801 |
| `claudeai.review_comment.edited` | 4 | `comment_id`~ | 8 | payload-00644, payload-00645, payload-02801, payload-02802 |
| `claudeai.review_comment.removed` | 3 | `comment_id`~ | 6 | payload-00643, payload-02803, payload-03180 |
| `claudeai.review_comment.sent` | 4 | `comment_id`~, `send_mode`~, `thread_length`~ | 8 | payload-01412, payload-02798, payload-02799, payload-02949 |
| `claudeai.safety.block_scanner.cta_clicked` | 1 | `entry_surface` | 0 | payload-03082 |
| `claudeai.safety.block_scanner.cta_shown` | 2 | `entry_surface` | 0 | payload-03079, payload-03177 |
| `claudeai.safety.block_scanner.modal_action` | 2 | `action`~, `entry_surface`?~, `remediated_surfaces`~ | 2 | payload-02620, payload-02622 |
| `claudeai.safety.block_scanner.remediate_clicked` | 1 | `culprit_surface`~, `editor`~, `entry_surface`?~ | 1 | payload-02621 |
| `claudeai.safety.block_scanner.remediation_editor_closed` | 2 | `culprit_surface`~, `entry_surface`?~, `outcome`~ | 2 | payload-02623, payload-02624 |
| `claudeai.safety.block_scanner.scan_completed` | 1 | `attribution`~, `degraded_count`~, `duration_ms`~, `entry_surface`?~, `outcome`~ | 1 | payload-03077 |
| `claudeai.safety.block_scanner.scan_started` | 1 | `entry_surface`?~ | 1 | payload-03075 |
| `claudeai.safety.block_scanner.scan_unavailable` | 2 | `entry_surface`?~, `reason`~ | 2 | payload-03074, payload-03076 |
| `claudeai.safety.csae_banner.link_clicked` | 1 | `variant`~ | 1 | payload-01920 |
| `claudeai.safety.cta_retry.sent` | 1 | `conversation_uuid`~, `model`~, `text_changed`~ | 0 | payload-01435 |
| `claudeai.safety.election_banner.link_clicked` | 1 |  | 1 | payload-01921 |
| `claudeai.safety.model_fallback_banner.explanation_link_clicked` | 1 | `conversation_uuid`~, `entry_surface`, `fallback_model`~, `href`~, `original_model`~ | 0 | payload-03081 |
| `claudeai.safety.model_fallback_banner.rendered` | 1 | `conversation_uuid`~, `entry_surface`, `fallback_model`~, `original_model`~ | 0 | payload-03078 |
| `claudeai.safety.self_harm_banner.browse_clicked` | 1 | `helpline_name`~ | 1 | payload-01924 |
| `claudeai.safety.self_harm_banner.call_clicked` | 1 | `helpline_name`~ | 1 | payload-01923 |
| `claudeai.safety.self_harm_banner.chat_clicked` | 1 | `helpline_name`~ | 1 | payload-01922 |
| `claudeai.safety.self_harm_banner.dropdown_opened` | 1 |  | 1 | payload-01925 |
| `claudeai.safety.self_harm_banner.resources_clicked` | 1 |  | 1 | payload-01926 |
| `claudeai.santolina.clicked` | 1 | `organization_uuid`~, `parent_organization_uuid`~ | 0 | payload-02492 |
| `claudeai.seat_allocation.dialog_opened` | 1 | `is_enterprise`~, `is_self_serve_enterprise`~, `seat_journey_id`~ | 0 | payload-01881 |
| `claudeai.seat_allocation.purchase_failed` | 1 | `allocations`~, `is_enterprise`~, `is_self_serve_enterprise`~, `seat_journey_id`~ | 1 | payload-01882 |
| `claudeai.seat_allocation.purchase_succeeded` | 1 | `allocations`~, `is_enterprise`~, `is_self_serve_enterprise`~, `seat_journey_id`~, `three_ds`~ | 0 | payload-01883 |
| `claudeai.seat_allocation.try_again_clicked` | 1 | `is_enterprise`~, `is_self_serve_enterprise`~, `seat_journey_id`~ | 0 | payload-01884 |
| `claudeai.seat_cap_banner.clicked` | 1 | `action`~, `is_at_cap`~ | 0 | payload-02468 |
| `claudeai.seat_cap_banner.dismissed` | 1 | `is_at_cap`~ | 0 | payload-02469 |
| `claudeai.seat_cap_banner.request_opened` | 1 | `source`~ | 0 | payload-00726 |
| `claudeai.seat_cap_banner.request_sent` | 1 | `current_limit`~, `requested_total`~, `source`~ | 0 | payload-00725 |
| `claudeai.seat_cap_banner.shown` | 1 | `can_upgrade_plan`~, `is_at_cap`~, `seat_request_enabled`~, `upgrade_cta_shown`~ | 0 | payload-02467 |
| `claudeai.serene_lighthouse.card_clicked` | 2 | `conversation_uuid`~, `kind`~, `origin`~, `tool_use_id`~, `via`~ | 0 | payload-00355, payload-01944 |
| `claudeai.serene_lighthouse.card_viewed` | 1 | `conversation_uuid`~, `is_live`~, `kind`~, `origin`~, `tool_use_id`~ | 0 | payload-00379 |
| `claudeai.serene_lighthouse.chrome_toggled` | 2 | `conversation_uuid`~, `full`~, `kind`~, `surface`?~ | 1 | payload-00069, payload-00073 |
| `claudeai.serene_lighthouse.editor_result` | 1 | `conversation_uuid`~, `is_live`~, `op`~, `outcome`~, `pane`~, `server`~, `tool_use_id`~ | 0 | payload-01945 |
| `claudeai.serene_lighthouse.load_result` | 2 | `conversation_uuid`~, `first_probe`~, `kind`~, `seconds_since_import`?~, `status`~, `surface`?~, `visible_ms`~ | 2 | payload-00067, payload-00071 |
| `claudeai.serene_lighthouse.opened` | 2 | `auto_opened`?~, `conversation_uuid`~, `kind`~, `origin`~, `reexpanded`?~, `surface`?~ | 5 | payload-00066, payload-00070 |
| `claudeai.serene_lighthouse.popped_out` | 2 | `conversation_uuid`~, `kind`~, `pane_status`~, `surface`?~, `via`~ | 1 | payload-00068, payload-00072 |
| `claudeai.session.error_occurred` | 1 | `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `session_id`~, `session_type`~, `surface`, `user_message_uuid`~ | 1 | payload-01690 |
| `claudeai.session.message_outcome` | 1 | `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `had_first_response`~, `is_product_failure`~, `model`~, `outcome`~, `seconds_to_outcome`~, `session_id`~, `session_type`~, `surface`~, `user_message_uuid`~ | 1 | payload-01686 |
| `claudeai.session.response_delayed` | 1 | `connection_state`~, `delay_type`~, `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `has_last_error`~, `seconds_since_last_activity`~, `seconds_since_user_message`~, `session_id`~, `session_type`~, `surface`~, `user_message_uuid`~ | 1 | payload-01685 |
| `claudeai.session.response_received` | 1 | `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `is_final`~, `seconds_since_user_message`~, `session_id`~, `session_type`~, `surface`~, `user_message_uuid`~ | 1 | payload-01684 |
| `claudeai.session.tracking_ended` | 1 | `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `end_reason`~, `had_first_response`~, `seconds_since_user_message`~, `session_id`~, `session_type`~, `surface`~, `user_message_uuid`~ | 1 | payload-01687 |
| `claudeai.session.user_message_sent` | 1 | `desktop_app_version`?~, `desktop_cpu_model`?~, `desktop_os_version`?~, `desktop_total_memory`?~, `session_id`~, `session_type`~, `surface`~, `user_message_uuid`~ | 1 | payload-01683 |
| `claudeai.session_row.archive_finished` | 1 | `action`~, `origin`~, `row_kind`, `server_worded_error`~, `succeeded`~ | 0 | payload-02684 |
| `claudeai.session_row.rename_finished` | 1 |  | 1 | payload-03206 |
| `claudeai.settings.capabilities.opened` | 1 | `source` | 0 | payload-03167 |
| `claudeai.settings.chat_font.active` | 1 | `font`~ | 0 | payload-02907 |
| `claudeai.settings.closed` | 1 | `distinct_section_count`~, `first_section`~, `focused`~, `in_settings_modal`~, `last_section`~, `open_duration_ms`~, `section_view_count`~, `visit_id`~ | 0 | payload-00819 |
| `claudeai.settings.deep_link_full_page_load` | 1 | `action`~, `other_build`~ | 0 | payload-02710 |
| `claudeai.settings.export_audit_logs.submitted` | 1 | `audit_logs_period`~ | 0 | payload-02370 |
| `claudeai.settings.export_data.submitted` | 1 | `conversations_period`~, `include_file_content`~, `own_data_only`~ | 0 | payload-02371 |
| `claudeai.settings.platform_api_key_card.clicked` | 1 | `in_settings_modal`~ | 0 | payload-01118 |
| `claudeai.settings.platform_api_key_card.shown` | 1 | `in_settings_modal`~ | 0 | payload-01117 |
| `claudeai.settings.platform_link.clicked` | 1 | `in_settings_modal`~ | 0 | payload-02807 |
| `claudeai.settings.platform_link.shown` | 1 | `in_settings_modal`~ | 0 | payload-02806 |
| `claudeai.settings.preview_feature.toggled` | 2 | `account_uuid`~, `action`~, `feature_id`~ | 0 | payload-01028, payload-02836 |
| `claudeai.settings.section_viewed` | 1 | `focused`~, `in_settings_modal`~, `ms_since_settings_open`~, `previous_section`~, `section`~, `view_index`~, `visit_id`~ | 0 | payload-00818 |
| `claudeai.setup_cowork.role_picker.dismissed` | 1 | `session_id`~ | 0 | payload-03189 |
| `claudeai.setup_cowork.role_picker.shown` | 1 | `session_id`~ | 0 | payload-01962 |
| `claudeai.setup_cowork.role_selected` | 4 | `persist_attempted`~, `role_label`~, `session_id`~, `source`, `work_function`~ | 0 | payload-03122, payload-03186, payload-03187, payload-03188 |
| `claudeai.setup_cowork.step_reached` | 5 | `session_id`~, `step` | 0 | payload-01171, payload-01172, payload-01810, payload-01961, payload-03121 |
| `claudeai.shiny_mitten.admin_add_credits_clicked` | 1 | `data`~, `data.surface`~ | 0 | payload-02356 |
| `claudeai.shiny_mitten.admin_dismissed` | 1 | `data`~, `data.count`~, `data.surface`~ | 0 | payload-02355 |
| `claudeai.shiny_mitten.admin_shown` | 1 | `data`~, `data.surface`~ | 0 | payload-02354 |
| `claudeai.shiny_mitten.clicked` | 1 | `data`~, `data.surface`~ | 0 | payload-02955 |
| `claudeai.shiny_mitten.shown` | 1 | `data`~, `data.surface`~ | 0 | payload-02956 |
| `claudeai.sidebar.container_toggled` | 1 | `action`~, `child_count`~, `container_kind`~, `gate_on`~, `surface`~ | 0 | payload-02887 |
| `claudeai.sidebar.multi_select.action_run` | 1 | `action`~ | 1 | payload-03098 |
| `claudeai.sidebar.multi_select.selected` | 1 | `via`~ | 1 | payload-03097 |
| `claudeai.sidebar.multi_select.tip_triggered` | 1 | `action`~ | 1 | payload-03096 |
| `claudeai.sidebar.pin_census` | 1 | `group_by`~, `kind`, `pinned_section_collapsed`~, `status_filter`~ | 1 | payload-02851 |
| `claudeai.sidebar.pin_changed` | 1 |  | 1 | payload-02971 |
| `claudeai.sidebar.state_set` | 2 | `is_expanded`~, `source`~ | 0 | payload-02838, payload-02839 |
| `claudeai.sidebar.view_all_clicked` | 1 |  | 1 | payload-03207 |
| `claudeai.site_test.evidence_opened` | 2 | `run_id`~, `view` | 0 | payload-02220, payload-02221 |
| `claudeai.site_test.run_started` | 1 | `run_id`~, `selection`~, `target_id`~, `trigger` | 0 | payload-02215 |
| `claudeai.site_test.site_created` | 1 | `target_id`~ | 0 | payload-02214 |
| `claudeai.site_test.spec_saved` | 3 | `change`, `target_id`~ | 0 | payload-02217, payload-02218, payload-02219 |
| `claudeai.site_test.verification_checked` | 1 | `outcome`~, `target_id`~ | 0 | payload-02216 |
| `claudeai.skill.suggestion.add_clicked` | 1 | `backing_plugin_id`?~, `skill_id`?~, `skill_name_hash`~, `source`~, `trigger`~ | 2 | payload-02559 |
| `claudeai.skill.suggestion.dismissed` | 1 | `source`~, `trigger`~ | 1 | payload-02556 |
| `claudeai.skill.suggestion.expanded` | 1 | `skill_count`~, `source`~ | 1 | payload-02554 |
| `claudeai.skill.suggestion.try_clicked` | 1 | `skill_name`~, `skill_name_hash`~, `source`~ | 1 | payload-02557 |
| `claudeai.skill.suggestion.view_all_clicked` | 1 | `skill_count`~, `source`~ | 1 | payload-02555 |
| `claudeai.skill.suggestion.viewed` | 1 | `skill_count`~, `source`~, `trigger`~ | 1 | payload-02553 |
| `claudeai.skills.add_skill.modal.opened` | 1 | `plugin_context`~, `source`~ | 0 | payload-00804 |
| `claudeai.skills.add_skill.quick_create.clicked` | 1 | `plugin_context`~ | 0 | payload-00805 |
| `claudeai.skills.add_skill.upload.clicked` | 1 | `plugin_context`~ | 0 | payload-00806 |
| `claudeai.skills.add_skill.with_claude.clicked` | 1 | `plugin_context`~ | 0 | payload-02630 |
| `claudeai.skills.empty_state.exposure` | 1 | `arm`~, `empty_state_surface`~ | 0 | payload-00800 |
| `claudeai.skills.empty_state.learn_more_clicked` | 1 | `destination`, `empty_state_surface`~, `placement`~ | 1 | payload-00803 |
| `claudeai.skills.empty_state.video_opened` | 1 | `empty_state_surface`~ | 1 | payload-00801 |
| `claudeai.skills.empty_state.video_played` | 1 | `empty_state_surface`~, `placement`~ | 1 | payload-00802 |
| `claudeai.skills.file_save_skill.clicked` | 1 | `session_id`~, `skill_name_hash`~, `source`~ | 0 | payload-00599 |
| `claudeai.skills.preview_modal.opened` | 1 | `creator_type`~, `scope`~, `skill_id`~ | 0 | payload-01965 |
| `claudeai.skills.skill.deleted` | 1 | `creator_type`~, `is_shared`~, `is_wrapped`~, `scope`~, `skill_id`~ | 1 | payload-02068 |
| `claudeai.skills.skill.downloaded` | 2 | `creator_type`~, `is_wrapped`~, `scope`~, `skill_id`~ | 0 | payload-00505, payload-01966 |
| `claudeai.skills.skill.edit_with_claude_clicked` | 1 | `creator_type`~, `scope`~, `skill_id`~ | 0 | payload-02631 |
| `claudeai.skills.skill.inline_edit.opened` | 2 | `creator_type`~, `plugin_context`~, `scope`~, `skill_id`~, `source`~, `trigger` | 0 | payload-00502, payload-01003 |
| `claudeai.skills.skill.inline_edit.succeeded` | 2 | `creator_type`~, `scope`~, `skill_id`~, `source`~, `storage`~ | 0 | payload-01968, payload-01969 |
| `claudeai.skills.skill.quick_create.succeeded` | 1 | `creator_type`~, `scope`~, `skill_id`~, `source`~, `storage`~ | 0 | payload-01968 |
| `claudeai.skills.skill.renamed` | 2 | `is_wrapped`~, `new_skill_id`~, `source`~, `source_creator_type`~, `source_scope`~, `source_skill_id`~ | 0 | payload-01970, payload-02628 |
| `claudeai.skills.skill.replace_started` | 1 | `creator_type`~, `scope`~, `skill_id`~ | 0 | payload-01967 |
| `claudeai.skills.skill.save_failed` | 1 | `error_code`?~, `error_kind`?~, `mode`~, `reason`~, `skill_id`?~, `source`~, `write_kind`~ | 4 | payload-01971 |
| `claudeai.skills.skill.shared` | 1 | `creator_type`~, `scope`~, `share_count`?~, `share_target`~, `skill_id`~, `skill_name_hash`~ | 1 | payload-01607 |
| `claudeai.skills.skill.sndp_submitted` | 1 | `skill_id`~, `source_skill_id`~, `wrapped_on_submit`~ | 1 | payload-00891 |
| `claudeai.skills.skill.toggled` | 1 | `creator_type`~, `is_shared`~, `new_state`~, `scope`~, `shared_via`~, `skill_id`~, `skill_name_hash`~, `surface`~, `turned_off_reason`?~ | 1 | payload-02249 |
| `claudeai.skills.skill.try_in_chat_clicked` | 1 | `caution_band_hidden`~, `dropped`?~, `outcome`?~, `seed_id`?~ | 6 | payload-00813 |
| `claudeai.skills.skill.try_in_chat_sent` | 1 | `caution_band_hidden`~, `seed_id`~ | 1 | payload-00812 |
| `claudeai.skills.skill.try_in_chat_shown` | 1 | `creator_type`~, `scope`~, `skill_id`~, `source` | 0 | payload-02637 |
| `claudeai.skills.skill.upload.succeeded` | 1 | `creator_type`~, `is_replace`~, `scope`~, `skill_id`~, `upload_method`~ | 0 | payload-01281 |
| `claudeai.skills.skill_creator_enable_prompt.dismissed` | 1 | `source`~ | 0 | payload-02627 |
| `claudeai.skills.skill_creator_enable_prompt.enabled` | 1 | `source`~ | 0 | payload-02626 |
| `claudeai.skills.skill_creator_enable_prompt.shown` | 1 | `source`~ | 0 | payload-02625 |
| `claudeai.skills.upload_failed` | 1 | `error_code`~, `scope`~, `upload_method`~ | 0 | payload-01282 |
| `claudeai.slash_command.not_offered` | 1 | `held`~, `slash_command`~ | 0 | payload-02954 |
| `claudeai.slash_command_menu.auto_resolved` | 1 | `item_label`~, `item_type`~ | 0 | payload-03039 |
| `claudeai.slash_command_menu.item_selected` | 2 | `item_label`~, `item_type`~ | 0 | payload-00795, payload-03040 |
| `claudeai.slash_command_menu.opened` | 2 |  | 0 | payload-00794, payload-03038 |
| `claudeai.slate_heron.attached` | 1 | `project_uuid`~ | 0 | payload-00783 |
| `claudeai.snuggly_balloon.opened` | 1 | `card_room`?~, `placement`~, `via`~ | 3 | payload-00681 |
| `claudeai.snuggly_balloon.tab_used` | 1 | `section_id`~ | 0 | payload-00682 |
| `claudeai.snuggly_balloon.tool_used` | 1 | `action`~, `tool_id`~, `via`?~ | 1 | payload-00679 |
| `claudeai.snuggly_balloon.window_action` | 1 | `action`~, `section_id`?~, `tool_id`?~, `via`?~ | 3 | payload-00680 |
| `claudeai.spend_limit_increase_modal.closed` | 1 |  | 0 | payload-02974 |
| `claudeai.spend_limit_increase_modal.remove_limit_clicked` | 1 |  | 0 | payload-01680 |
| `claudeai.spend_limit_increase_modal.save_clicked` | 1 | `new_limit_minor`~ | 0 | payload-01679 |
| `claudeai.spend_limit_increase_modal.viewed` | 1 |  | 0 | payload-02973 |
| `claudeai.splendid_teapot.continued` | 1 | `report_uuid`~, `show_id`~ | 0 | payload-01524 |
| `claudeai.splendid_teapot.left` | 1 | `control`~, `report_uuid`~, `show_id`~ | 0 | payload-01525 |
| `claudeai.splendid_teapot.shown` | 1 | `report_uuid`~, `show_id`~ | 0 | payload-01523 |
| `claudeai.splendid_teapot.started` | 1 | `report_uuid`~ | 0 | payload-01526 |
| `claudeai.storage.error` | 1 | `error_name`~, `key`~, `operation`, `source`~ | 0 | payload-02832 |
| `claudeai.subscription.cancel_entry.clicked` | 1 | `refund_eligible`~, `refund_flow_variant`~ | 0 | payload-01885 |
| `claudeai.subscription.cancel_modal.app_card_clicked` | 1 | `app`~, `variant`~ | 0 | payload-01841 |
| `claudeai.subscription.cancel_modal.completed_with_reason` | 1 | `has_feedback`~, `reason`~, `variant`~ | 0 | payload-01856 |
| `claudeai.subscription.cancel_modal.downgrade_clicked` | 2 | `max_plan_type`?~, `offer_variant`~, `target_plan`~, `variant`~ | 1 | payload-01840, payload-01860 |
| `claudeai.subscription.cancel_modal.link_arm_action.clicked` | 1 | `action`~, `refund_flow_variant`~ | 0 | payload-01850 |
| `claudeai.subscription.cancel_modal.pause_instead_clicked` | 1 | `variant`~ | 0 | payload-01859 |
| `claudeai.subscription.cancel_modal.reason_selected` | 1 | `reason`~, `variant`~ | 0 | payload-01857 |
| `claudeai.subscription.cancel_modal.shown` | 1 | `apps_not_tried`~, `apps_used`~, `variant`~ | 0 | payload-01853 |
| `claudeai.subscription.cancel_modal.skipped_via_escape_hatch` | 1 | `variant`~ | 0 | payload-01855 |
| `claudeai.subscription.cancel_modal.survey_step.shown` | 1 | `step_type`~, `variant`~ | 0 | payload-01852 |
| `claudeai.subscription.cancel_modal.survey_step_abandoned` | 1 | `reason`~, `variant`~ | 0 | payload-01858 |
| `claudeai.subscription.cancel_modal.usage_stats.segment` | 1 | `cleared_bars`~, `high_usage_min_cleared`~, `max_cards`~, `rules_applied`~, `segment`~, `thresholds`~ | 0 | payload-01851 |
| `claudeai.subscription.cancel_modal.usage_stats.shown` | 1 | `api_value_gate_passed`~, `segment`~, `stat_keys`~ | 0 | payload-01842 |
| `claudeai.subscription.pause_modal.blocked_cancel_scheduled` | 1 |  | 0 | payload-01848 |
| `claudeai.subscription.pause_modal.confirm_clicked` | 1 |  | 0 | payload-01847 |
| `claudeai.subscription.pause_modal.failed` | 2 |  | 0 | payload-01845, payload-01846 |
| `claudeai.subscription.pause_modal.maybe_later_clicked` | 1 |  | 0 | payload-01849 |
| `claudeai.subscription.pause_modal.shown` | 1 |  | 0 | payload-01843 |
| `claudeai.subscription.pause_modal.succeeded` | 1 |  | 0 | payload-01844 |
| `claudeai.subscription.resume_modal.confirm_clicked` | 1 | `source`~ | 0 | payload-00119 |
| `claudeai.subscription.resume_modal.failed` | 1 | `error_code`?~, `source`~, `status_code`?~ | 2 | payload-00117 |
| `claudeai.subscription.resume_modal.shown` | 1 | `source`~ | 0 | payload-00118 |
| `claudeai.subscription.resume_modal.succeeded` | 1 | `source`~ | 0 | payload-00116 |
| `claudeai.subscription.unpause_modal.confirm_clicked` | 1 | `phase`~ | 0 | payload-00493 |
| `claudeai.subscription.unpause_modal.failed` | 2 | `phase`~ | 0 | payload-00491, payload-00492 |
| `claudeai.subscription.unpause_modal.shown` | 1 | `phase`~ | 0 | payload-00490 |
| `claudeai.subscription.unpause_modal.succeeded` | 1 | `phase`~ | 0 | payload-00491 |
| `claudeai.sync_source.created` | 2 | `sync_source_type`~, `sync_surface`, `trigger`~ | 0 | payload-00143, payload-02797 |
| `claudeai.tawny_pipit.dialog_action` | 1 | `action`~, `arm`~, `interval`?~ | 1 | payload-01633 |
| `claudeai.tawny_pipit.dialog_shown` | 1 | `arm`~ | 0 | payload-01632 |
| `claudeai.tawny_pipit.offer_eligible` | 1 | `arm`~, `client_platform`~, `ui_locale`~ | 0 | payload-01631 |
| `claudeai.team_promo.eligibility_viewed` | 1 | `offer_code`~, `reason`~, `status`~ | 0 | payload-00988 |
| `claudeai.team_promo.ending_banner.clicked` | 1 | `days_until`~ | 0 | payload-03169 |
| `claudeai.team_promo.ending_banner.dismissed` | 1 | `can_manage_billing`~, `days_until`~ | 0 | payload-03168 |
| `claudeai.team_promo.ending_banner.shown` | 1 | `can_manage_billing`~, `days_until`~ | 0 | payload-03162 |
| `claudeai.team_promo.link_sent` | 1 | `offer_code`~ | 0 | payload-00990 |
| `claudeai.team_promo.start_page_view` | 1 | `offer_code`~ | 0 | payload-00989 |
| `claudeai.team_share_upsell_nudge.clicked` | 1 | `surface`~, `trigger` | 0 | payload-00027 |
| `claudeai.team_share_upsell_nudge.dismissed` | 1 | `surface`~ | 0 | payload-00029 |
| `claudeai.team_share_upsell_nudge.option_selected` | 1 | `option`~, `surface`~ | 0 | payload-00028 |
| `claudeai.team_share_upsell_nudge.shown` | 1 | `surface`~ | 0 | payload-00026 |
| `claudeai.team_signup.checkout_submitted` | 1 | `interval`~, `prem_seats`~, `std_seats`~ | 0 | payload-02306 |
| `claudeai.team_signup.email_submitted` | 1 | `eligible`~, `reason`~ | 0 | payload-00985 |
| `claudeai.team_signup.flow_started` | 1 | `buying_agent_session`~, `is_upgrade`~, `referral_source`~ | 0 | payload-00981 |
| `claudeai.team_signup.invites_submitted` | 3 | `invite_count`~, `premium_invite_count`~, `skipped`~, `standard_invite_count`~ | 0 | payload-00974, payload-00975, payload-00976 |
| `claudeai.team_signup.link_sent` | 1 |  | 0 | payload-00984 |
| `claudeai.team_signup.page_view` | 1 |  | 0 | payload-00983 |
| `claudeai.team_signup.payment_confirmed` | 1 |  | 0 | payload-00982 |
| `claudeai.team_signup.pricing_team_cta_click` | 1 | `destination` | 0 | payload-00884 |
| `claudeai.team_signup.session_acquired` | 1 | `method` | 0 | payload-02147 |
| `claudeai.team_trial.cta_clicked` | 2 | `billing_interval`~, `billing_interval_picked`~, `pill_variant`, `surface`~ | 0 | payload-01406, payload-02131 |
| `claudeai.teams.b2b_onboarding_role_page.viewed` | 1 | `source` | 0 | payload-00856 |
| `claudeai.teams.b2b_onboarding_role_selected` | 1 | `role`~, `selected_other`~, `source` | 0 | payload-00857 |
| `claudeai.teams.existing_subscription_warning_modal.viewed` | 2 | `existing_plan`~ | 0 | payload-00968, payload-00987 |
| `claudeai.teams.in_place_upgrade_choice.changed` | 1 | `surface`, `upgrade_type`~ | 0 | payload-00980 |
| `claudeai.teams.in_place_upgrade_pending.cancelled` | 1 | `surface`~ | 0 | payload-00957 |
| `claudeai.teams.in_place_upgrade_pending.continue_clicked` | 1 | `surface`~ | 0 | payload-00950 |
| `claudeai.teams.in_place_upgrade_pending.continue_failed` | 4 | `error_code`~, `surface`~ | 0 | payload-00951, payload-00952, payload-00953, payload-00954 |
| `claudeai.teams.in_place_upgrade_pending.other_card_clicked` | 1 | `surface`~ | 0 | payload-00956 |
| `claudeai.teams.in_place_upgrade_pending.viewed` | 1 | `surface`~ | 0 | payload-00949 |
| `claudeai.teams.name_entered` | 2 |  | 0 | payload-00979, payload-00986 |
| `claudeai.teams.procurement_packet.link_clicked` | 1 | `document`~ | 0 | payload-00977 |
| `claudeai.teams.procurement_packet.opened` | 1 |  | 0 | payload-00978 |
| `claudeai.television.notification_modal.viewed` | 1 |  | 0 | payload-00250 |
| `claudeai.television.remote_idle_notification` | 1 | `outcome`~ | 1 | payload-00145 |
| `claudeai.television.session.created` | 1 | `session_id`~, `source`~ | 0 | payload-02675 |
| `claudeai.television.sessions_watch.demand_restored` | 1 | `platform`~, `suppressed_duration_ms`~, `trigger`~, `watch_tags`~ | 0 | payload-02926 |
| `claudeai.television.sessions_watch.demand_suppressed` | 1 | `platform`~, `watch_tags`~ | 0 | payload-02925 |
| `claudeai.television.sessions_watch.fatal` | 1 | `detail`~, `http_status`~, `watch_tags`~ | 0 | payload-02673 |
| `claudeai.television.sessions_watch.keepalive_tolerance_withdrawn` | 1 | `granted_keepalive_seconds`~, `watch_tags`~ | 0 | payload-02671 |
| `claudeai.television.sessions_watch.refused` | 1 | `http_status`~, `source`~, `watch_tags`~ | 0 | payload-02672 |
| `claudeai.television.sessions_watch.refused_recovered` | 1 | `refused_duration_ms`~, `watch_tags`~ | 0 | payload-02670 |
| `claudeai.television.sessions_watch.retry_loop` | 1 | `detail`~, `http_status`~, `watch_tags`~ | 0 | payload-02674 |
| `claudeai.thinking_cell.clicked` | 4 | `is_opening`~, `is_streaming`~, `renderer`, `renderer_surface`~, `thinking_block_count`~, `trigger` | 0 | payload-01401, payload-01950, payload-01951, payload-01952 |
| `claudeai.tidy_sunrise.data_export_finished` | 1 | `duration_ms`~, `error_toast_shown`~, `export_surface`~, `outcome`~, `skipped_count`?~, `slow_fallback_shown`~, `target_kind`~ | 2 | payload-01279 |
| `claudeai.tidy_sunrise.data_export_started` | 1 | `export_surface`~, `target_kind`~ | 0 | payload-01277 |
| `claudeai.tidy_sunrise.export_fallback_shown` | 1 | `export_surface`~, `outcome`~, `target_kind`~ | 0 | payload-01280 |
| `claudeai.tidy_sunrise.export_show_folder_clicked` | 1 | `export_surface`~, `reason`~ | 0 | payload-01276 |
| `claudeai.tidy_sunrise.export_slow_fallback_shown` | 1 | `export_surface`~, `target_kind`~ | 0 | payload-01278 |
| `claudeai.tidy_sunrise.home_card_cta_clicked` | 1 | `cta`~ | 0 | payload-00766 |
| `claudeai.tidy_sunrise.home_card_open_code_finished` | 1 | `outcome`~ | 0 | payload-00767 |
| `claudeai.tidy_sunrise.home_card_shown` | 1 |  | 0 | payload-00765 |
| `claudeai.tidy_sunrise.move_project_clicked` | 1 | `reasons`~, `space_id`~ | 0 | payload-01139 |
| `claudeai.tidy_tulip.toggled` | 1 | `enabled`~, `project_uuid`~ | 0 | payload-02332 |
| `claudeai.tidy_tulip.viewed` | 1 | `enabled`~, `project_uuid`~, `switch_visible`~ | 0 | payload-02334 |
| `claudeai.umber_lark.dialog_action` | 1 | `action`~, `interval`?~, `price_status`~, `showing`~ | 1 | payload-01630 |
| `claudeai.umber_lark.dialog_shown` | 1 | `showing`~ | 0 | payload-01629 |
| `claudeai.umber_lark.notice_shown` | 1 | `arm`~, `day0_offer_seen`~, `hours_until_reset`~, `window_name`~ | 0 | payload-02984 |
| `claudeai.unassigned_seat_wall.shown` | 1 | `data`~, `data.cta_variant`~, `data.request_state`~, `data.source`~ | 0 | payload-02970 |
| `claudeai.unhandled_error_code` | 1 | `conversation_uuid`~, `error_code`~, `error_type`~, `project_uuid`~ | 0 | payload-02646 |
| `claudeai.upgrade.duplicate_purchase_notice_shown` | 1 | `plan`~ | 0 | payload-02582 |
| `claudeai.upgrade.enterprise_contact_sales.click` | 1 |  | 0 | payload-02135 |
| `claudeai.upgrade.plans_page_viewed` | 1 | `initial_plan_tab`~, `org_type`~, `presentation`~ | 1 | payload-02597 |
| `claudeai.upgrade.pro_max_step_routed` | 1 | `arm`~, `presentation`~ | 1 | payload-02594 |
| `claudeai.upgrade.returner_state_shown` | 1 | `arm`~ | 0 | payload-02598 |
| `claudeai.upgrade_pill_header.clicked` | 1 | `client_platform`~, `pill_variant`, `surface`~ | 0 | payload-01407 |
| `claudeai.upgrade_pill_header.dismissed` | 1 | `client_platform`~, `dismiss_count`~, `reappeared`~, `surface`~ | 0 | payload-01405 |
| `claudeai.upgrade_pill_header.shown` | 1 | `client_platform`~, `dismiss_count`~, `reappeared`~, `surface`~ | 0 | payload-01404 |
| `claudeai.upgrade_prompt.dismissed` | 1 | `conversation_uuid`~, `feature`~, `tool_use_id`~ | 0 | payload-03155 |
| `claudeai.upgrade_prompt.upgrade_clicked` | 1 | `conversation_uuid`~, `feature`~, `tool_use_id`~ | 0 | payload-03154 |
| `claudeai.upgrade_prompt.viewed` | 1 | `conversation_uuid`~, `feature`~, `tool_use_id`~ | 0 | payload-03156 |
| `claudeai.usage_recommendation.action_clicked` | 1 | `data`~, `data.action_kind`~, `data.tip_id`~, `data.tip_pct`?~ | 1 | payload-03164 |
| `claudeai.usage_recommendation.dismissed` | 1 | `data`~, `data.tip_id`~ | 0 | payload-03172 |
| `claudeai.usage_recommendation.dont_show` | 1 | `data`~, `data.tip_id`~ | 0 | payload-03165 |
| `claudeai.usage_recommendation.shown` | 1 | `data`~, `data.action_kind`~, `data.tip_id`~, `data.tip_pct`?~ | 1 | payload-03163 |
| `claudeai.user_menu.item_clicked` | 5 | `item`, `surface`~ | 0 | payload-02168, payload-02172, payload-02174, payload-02175, payload-02176 |
| `claudeai.valiant_balloon.drafted` | 1 | `schedule_applied`~, `surface`~ | 0 | payload-00132 |
| `claudeai.velvety_wave.deep_link_opened` | 1 |  | 1 | payload-01837 |
| `claudeai.web.sidebar.design_entry_clicked` | 1 | `frame_mode`~, `open_behavior`~ | 0 | payload-02853 |
| `claudeai.web.sidebar.design_entry_shown` | 1 | `frame_mode`~, `open_behavior`~, `tabs`~ | 0 | payload-02855 |
| `claudeai.web_search.suggestion.dismissed` | 1 |  | 0 | payload-02109 |
| `claudeai.web_search.suggestion.turn_on_clicked` | 1 | `is_retry`~ | 0 | payload-02107 |
| `claudeai.web_search.suggestion.turn_on_failed` | 1 | `reason`~ | 0 | payload-02108 |
| `claudeai.web_search.suggestion.viewed` | 1 |  | 0 | payload-02106 |
| `claudeai.widget.clicked` | 1 | `action`~, `conversation_uuid`~, `is_incognito`~, `widget_type`~ | 1 | payload-03047 |
| `claudeai.widget.element_shown` | 1 | `conversation_uuid`~, `element`~, `is_incognito`~, `widget_type`~ | 0 | payload-03049 |
| `claudeai.widget.image_error` | 1 | `image_host`~, `image_surface`~, `widget_type`~ | 0 | payload-03050 |
| `claudeai.widget.render` | 2 | `render_status`~, `widget_type`~ | 1 | payload-00039, payload-03048 |
| `claudeai.widget.shown` | 1 | `conversation_uuid`~, `is_incognito`~, `widget_type`~ | 0 | payload-03046 |
| `claudeai.wiggly_forest_banner.clicked` | 1 | `kind`~ | 0 | payload-01613 |
| `claudeai.wiggly_forest_banner.dismissed` | 1 | `kind`~ | 0 | payload-01614 |
| `claudeai.wiggly_forest_banner.shown` | 1 | `kind`~ | 0 | payload-01612 |
| `claudeai.wiggly_forest_notice.shown` | 1 | `kind`~ | 0 | payload-02369 |
| `claudeai.wild_planet.shown` | 1 | `data`~, `data.kind`~, `data.plan`~ | 1 | payload-03001 |
| `claudeai.wild_snowflake.copy_deleted_move` | 1 | `result`~ | 0 | payload-01998 |
| `claudeai.wild_snowflake.create_project_clicked` | 1 | `fail_reason`~, `space_id`~ | 0 | payload-01146 |
| `claudeai.wild_snowflake.learn_more_opened` | 1 | `space_id`~, `stage`~, `state`~ | 0 | payload-01145 |
| `claudeai.wild_snowflake.links_run` | 1 | `already_synced`~, `connector`~, `drive_links`~, `left_reason_folder`~, `left_reason_limit`~, `left_reason_refused`~, `left_text`~, `links_total`~, `other_links`~, `outcome`~, `run`~, `synced`~ | 0 | payload-00142 |
| `claudeai.wild_snowflake.move_clicked` | 1 | `source`~, `space_id`~, `stage`~, `state`~ | 0 | payload-01143 |
| `claudeai.wild_snowflake.move_outcome` | 1 | `copy_started`~, `duration_ms`~, `outcome`~, `project_uuid`?~, `queued`~, `reason`?~, `space_id`~, `stage`~, `wave`?~ | 3 | payload-01144 |
| `claudeai.wild_snowflake.moved_project_gone` | 2 | `surface` | 0 | payload-01140, payload-02244 |
| `claudeai.wild_snowflake.open_project_clicked` | 3 | `surface`~ | 0 | payload-01141, payload-01149, payload-02747 |
| `claudeai.wild_snowflake.refusal_shown` | 1 | `open_project_offered`~, `reason`~, `surface`~ | 0 | payload-02748 |
| `claudeai.wild_snowflake.reminder_shown` | 1 | `fail_reason`?~, `folders_over`?~, `hub_active`~, `move_offered`~, `space_id`~, `stage`~, `state`~, `surface` | 2 | payload-01142 |
| `claudeai.wild_snowflake.remote_sessions_pass` | 1 | `active_share`~, `already_applied`~, `applied`~, `ended_on_failures`~, `failed`~, `first_report`~, `gone`~, `gone_on_write`~, `invalid_id`~, `left_for_later`~, `no_access`~, `other_target`~, `sessions`~, `settled`~, `stopped`~, `target_since`~, `target_unavailable`~ | 0 | payload-00144 |
| `claudeai.wild_snowflake.show_folders_clicked` | 1 | `folders_over`~, `space_id`~ | 0 | payload-01147 |
| `claudeai.wild_snowflake.update_clicked` | 1 | `fail_reason`~, `space_id`~, `update_ready`~ | 0 | payload-01148 |
| `claudeai.workflow_size_warning_band.dismissed` | 1 | `banner_surface`, `presentation`~ | 1 | payload-02011 |
| `claudeai.workflow_size_warning_band.shown` | 1 | `banner_surface`, `presentation`~ | 1 | payload-02010 |
| `claudeai.workflow_size_warning_band.stopped` | 1 | `banner_surface`, `presentation`~ | 1 | payload-02012 |
| `claudeai.yukon_gold.enabled` | 1 |  | 0 | payload-03099 |
| `claudeai.yukon_gold.session_created` | 4 | `files_selected`~, `folders_selected`~, `has_project`~, `memory_mode`~, `permission_mode`~, `permission_mode_source`~, `projects_attached`~, `routing_reason`~, `session_id`~, `session_type`~, `source`~, `space_id`~ | 0 | payload-00255, payload-01681, payload-02749, payload-03132 |
| `code.share.copy_link.clicked` | 1 | `session_id`~, `share_id`~ | 0 | payload-00711 |
| `code.share.login_redirect` | 1 | `share_id`~ | 0 | payload-00888 |
| `code.share.modal.share_button.clicked` | 1 | `session_id`~ | 0 | payload-00707 |
| `code.share.modal.support_revoke_button.clicked` | 1 | `session_id`~, `share_id`~ | 0 | payload-00710 |
| `code.share.modal.unshare_button.clicked` | 1 | `session_id`~, `share_id`~ | 0 | payload-00709 |
| `code.share.open_link.clicked` | 1 | `session_id`~, `share_id`~ | 0 | payload-00712 |
| `code.share.page.viewed` | 1 | `session_id`~, `share_id`~ | 0 | payload-02155 |
| `code.share.secrets_detected` | 1 | `secret_count`~, `secret_types`~, `session_id`~ | 0 | payload-00708 |
| `console.ip_allowlist.admin.disabled` | 1 | `range_count`~ | 0 | payload-02486 |
| `console.ip_allowlist.admin.enabled` | 1 | `range_count`~ | 0 | payload-02486 |
| `console.ip_allowlist.admin.ranges_updated` | 1 | `added_count`~, `enforcement_enabled`~, `removed_count`~ | 0 | payload-02485 |
| `cowork.auto_mode.always_allow_overridden` | 1 | `request_id`~, `session_id`~, `source`, `tool_name`~ | 0 | payload-02760 |
| `cowork.file.gdrive_export.failed` | 2 | `error_code`~, `file_extension`~, `transport`, `via_file_uuid`~ | 1 | payload-01213, payload-01214 |
| `cowork.file.gdrive_export.success` | 1 |  | 1 | payload-01212 |
| `cowork.file.open_action` | 3 | `action`~, `caller`~, `chat_backend`?, `file_extension`~, `from_scratchpad`~, `is_remote`~, `location`~, `outcome`~, `primary_available`~, `primary_source`~, `session_id`~, `space_id`~ | 1 | payload-01211, payload-01217, payload-01220 |
| `cowork.file.share_file` | 2 | `artifact_kind`, `caller`~, `file_extension`~, `session_id`~, `space_id`~ | 0 | payload-01218, payload-01219 |
| `cowork.file_explorer.entry_clicked` | 1 | `session_id`~, `surface` | 0 | payload-00409 |
| `cowork.file_explorer.file_previewed` | 1 | `session_id`~ | 0 | payload-00396 |
| `cowork.file_explorer.opened` | 1 | `folder_count`~, `session_id`~ | 0 | payload-00395 |
| `cowork.first_conversation.started` | 2 |  | 0 | payload-02750, payload-03133 |
| `cowork.global_instruction.dismissed` | 1 |  | 0 | payload-01621 |
| `cowork.global_instruction.import` | 1 | `content_length`~, `outcome`~ | 0 | payload-01622 |
| `cowork.global_instruction.loaded` | 1 | `content_length`~, `has_existing_content`~, `source`~ | 0 | payload-01617 |
| `cowork.global_instruction.opened` | 1 |  | 0 | payload-01620 |
| `cowork.global_instruction.save_failed` | 1 |  | 0 | payload-01619 |
| `cowork.global_instruction.saved` | 1 | `content_length`~ | 0 | payload-01618 |
| `cowork.launch_code_session` | 1 | `had_suggested_cwd`~, `launched_session_id`~, `source`~, `source_session_id`~, `target`~, `used_branch`~, `used_worktree`~ | 0 | payload-00774 |
| `cowork.mcp.tools.called.tmp` | 1 | `server_uuid`~, `tool_name`~ | 0 | payload-02761 |
| `cowork.memory_editor.dismissed` | 1 | `session_id`~ | 0 | payload-00401 |
| `cowork.memory_editor.loaded` | 2 | `content_length`~, `has_existing_content`~, `session_id`~ | 0 | payload-00397, payload-00398 |
| `cowork.memory_editor.opened` | 1 | `session_id`~ | 0 | payload-00402 |
| `cowork.memory_editor.save_failed` | 1 | `session_id`~ | 0 | payload-00400 |
| `cowork.memory_editor.saved` | 1 | `content_length`~, `session_id`~ | 0 | payload-00399 |
| `cowork_browser.closed` | 1 | `is_hub_chat`~, `session_id`~, `session_type`~, `source`~ | 0 | payload-03071 |
| `cowork_browser.opened` | 3 | `is_hub_chat`~, `session_id`~, `session_type`~, `source`~ | 1 | payload-00443, payload-00449, payload-03071 |
| `crochet.install.challenge.started` | 1 | `challenge_id`~, `challenge_type`~ | 0 | payload-01977 |
| `crochet.install.try_usecase.clicked` | 1 | `use_case_title`~ | 0 | payload-01976 |
| `crochet.landing.install_extension.clicked` | 1 | `has_max_subscription`~, `has_raven`~, `is_logged_in`~ | 0 | payload-01975 |
| `desktop_dxt_installed` | 2 | `app_version`~, `event_source`~, `extension_author`~, `extension_id`~, `extension_name`~, `extension_version`~, `total_extensions_installed`~ | 0 | payload-00128, payload-01751 |
| `extended_onboarding.completed` | 1 | `onboarding_arm`~, `role`~ | 0 | payload-00224 |
| `extended_onboarding.connector.completed` | 2 | `connector_name`~, `mode`~, `step`~ | 0 | payload-00160, payload-00167 |
| `extended_onboarding.connector.skipped` | 2 | `connector_name`~, `mode`~, `step`~ | 0 | payload-00162, payload-00170 |
| `extended_onboarding.connector.started` | 2 | `connector_name`~, `mode`~, `step`~ | 0 | payload-00161, payload-00168 |
| `extended_onboarding.connector_connect.browse_all_clicked` | 1 | `mode`~ | 0 | payload-00165 |
| `extended_onboarding.connector_connect.browse_closed` | 1 | `connected_here_count`~, `installed_here_count`~, `mode`~ | 0 | payload-00169 |
| `extended_onboarding.connector_connect.completed` | 2 | `attempted`~, `connected_before_count`~, `connected_here_count`~, `connector_names_connected`~, `directory_connected_count`~, `mode`~, `nudged`~, `outcome`~, `rows_connected_count`~, `skipped_count`~, `source_status`~ | 0 | payload-00166, payload-00171 |
| `extended_onboarding.connector_connect.shown` | 1 | `governed`~, `mode`~, `needs_flow_count`~, `rows_count`~, `source`~ | 0 | payload-00164 |
| `extended_onboarding.connector_connect.skip_confirm` | 1 | `action`~, `mode`~ | 0 | payload-00172 |
| `extended_onboarding.connector_connect.why_expanded` | 1 | `mode`~ | 0 | payload-00173 |
| `extended_onboarding.example_prompts.chip_clicked` | 1 | `category_id`~, `prompt_id`~ | 0 | payload-00218 |
| `extended_onboarding.example_prompts.own_topic_clicked` | 1 |  | 0 | payload-00219 |
| `extended_onboarding.hear_about.skipped` | 1 |  | 0 | payload-00163 |
| `extended_onboarding.started` | 1 | `onboarding_arm`~ | 0 | payload-00220 |
| `extended_onboarding.topics.completed` | 1 | `topics_selected`~ | 0 | payload-00215 |
| `extended_onboarding.work_function.completed` | 1 | `work_function`~ | 0 | payload-00214 |
| `extra_usage_refund.confirm_clicked` | 1 |  | 0 | payload-01831 |
| `extra_usage_refund.execute_result` | 2 | `failed_grant_count`~, `ineligible_reason`~, `refunded_grant_count`~, `status`~ | 0 | payload-01829, payload-01830 |
| `extra_usage_refund.modal_shown` | 1 |  | 0 | payload-01824 |
| `extra_usage_refund.preview_result` | 1 | `eligible`~, `ineligible_reason`~ | 0 | payload-01826 |
| `file_upload_too_large` | 1 | `large_files`~ | 0 | payload-03003 |
| `grove_policy_submitted` | 2 | `dismissable`~, `location`, `state`~ | 0 | payload-00216, payload-00817 |
| `grove_policy_toggled` | 2 | `location`, `state`~ | 0 | payload-00217, payload-00816 |
| `grove_policy_viewed` | 1 | `dismissable`~, `location` | 0 | payload-00815 |
| `image_search.domain_clicked` | 1 | `conversation_uuid`~ | 0 | payload-00041 |
| `image_search.image_clicked` | 1 | `conversation_uuid`~ | 0 | payload-00040 |
| `image_search.malformed_images` | 1 | `conversation_uuid`~, `malformed_count`~, `valid_count`~ | 0 | payload-01949 |
| `image_search.shown` | 1 |  | 0 | call-00031 |
| `kyc.idv_complete.page_viewed` | 1 | `inquiry_id`~, `reference_id`~, `status`~ | 0 | payload-00847 |
| `kyc.modal_shown` | 1 | `from_notification_kind`~, `has_session_url`~, `initial_status`~, `inquiry_id`~ | 0 | payload-00545 |
| `kyc.session_refresh_requested` | 2 | `inquiry_id`~, `status`~, `url_changed`~ | 0 | payload-00557, payload-00559 |
| `kyc.verification_completed` | 3 |  | 3 | payload-00547, payload-00550, payload-00555 |
| `kyc.verification_failed` | 5 | `status`~ | 0 | payload-00546, payload-00548, payload-00553, payload-00554, payload-00558 |
| `kyc.verification_retried` | 1 | `inquiry_id`~, `inquiry_id_changed`~ | 0 | payload-00552 |
| `kyc.verification_retry_attempted` | 1 | `prior_inquiry_id`~ | 0 | payload-00549 |
| `kyc.verification_retry_declined` | 1 | `retry_exhausted`~, `status`~ | 0 | payload-00551 |
| `kyc.verification_started` | 1 | `inquiry_id`~, `url_age_ms`~, `url_source`~ | 0 | payload-00556 |
| `landing.hero.claude_design_video.viewed` | 1 |  | 0 | call-00763 |
| `landing.hero.kt3_video.viewed` | 1 |  | 0 | call-00764 |
| `landing.section.features.viewed` | 1 |  | 0 | call-00762 |
| `landing.section.pricing.viewed` | 1 |  | 0 | call-00766 |
| `login.account.created` | 1 | `authMethod`~, `flow`~, `oauth_client_slug`~, `signup_origin`~, `surface`~ | 0 | payload-01261 |
| `login.apple.error` | 2 | `error`~ | 0 | payload-00837, payload-01254 |
| `login.apple.finished` | 1 |  | 0 | payload-01257 |
| `login.apple.started` | 1 |  | 0 | payload-00836 |
| `login.apple.verification_error` | 2 | `error`~ | 0 | payload-01256, payload-01258 |
| `login.apple.verifying` | 1 |  | 0 | payload-01259 |
| `login.email.code_verification_error` | 2 | `error`~, `error_type`~ | 0 | payload-01242, payload-01267 |
| `login.email.error` | 1 | `error_code`~, `error_type`~ | 0 | payload-00330 |
| `login.email.finished` | 2 |  | 0 | payload-01240, payload-01264 |
| `login.email.magic_link_send_error` | 1 | `error`~, `error_type`~ | 0 | payload-01237 |
| `login.email.magic_link_sent` | 1 |  | 0 | payload-01236 |
| `login.email.magic_link_success` | 2 |  | 0 | payload-01241, payload-01263 |
| `login.email.magic_link_verification_error` | 2 | `error`~ | 0 | payload-01243, payload-01266 |
| `login.email.sending_magic_link` | 1 |  | 0 | payload-01238 |
| `login.email.sso_initiated` | 6 |  | 0 | payload-01235, payload-01239, payload-01246, payload-01250, payload-01255, payload-01260 |
| `login.email.verifying_code` | 1 |  | 0 | payload-01244 |
| `login.email.verifying_magic_link` | 1 |  | 0 | payload-01245 |
| `login.google.error` | 2 | `error`~ | 0 | payload-00015, payload-00016 |
| `login.google.finished` | 3 | `flow_type`? | 1 | payload-01247, payload-01251, payload-01262 |
| `login.google.one_tap_dropped` | 1 | `reason`~ | 0 | payload-00018 |
| `login.google.started` | 2 | `flow_type`~ | 0 | payload-00017, payload-00019 |
| `login.google.verification_error` | 3 | `error`~ | 0 | payload-01248, payload-01252, payload-01265 |
| `login.google.verifying` | 2 |  | 0 | payload-01249, payload-01253 |
| `max_subscription.downgraded_to_max` | 1 | `max_plan_type`~, `target_plan_type`~ | 0 | payload-02578 |
| `max_subscription.downgraded_to_pro` | 1 | `max_plan_type`~, `target_plan_type`~ | 0 | payload-02580 |
| `max_subscription.extension_coupon_redeemed` | 1 | `max_plan_type`~ | 0 | payload-02577 |
| `mcp.prompts.listed` | 1 | `prompt_count_on_server`~ | 0 | payload-02823 |
| `mcp.prompts.used` | 1 | `argument_count`~, `assistant_messages`~, `image_messages`~, `text_messages`~, `user_messages`~ | 0 | payload-02790 |
| `mcp.resources.listed` | 1 | `resource_count_on_server`~ | 0 | payload-02822 |
| `mcp.resources.read` | 2 | `mime_type`~, `type` | 0 | payload-02788, payload-02789 |
| `mcp.sampling.requested` | 1 | `max_tokens`~, `message_count`~ | 0 | payload-02685 |
| `mcp.servers.connected` | 2 | `result` | 0 | payload-02842, payload-02843 |
| `mcp.servers.listed` | 1 | `server_count`~ | 0 | payload-02841 |
| `mcp.tools.called` | 3 | `argument_count`~, `result` | 0 | payload-01946, payload-02656, payload-02657 |
| `mcp.tools.listed` | 1 | `tool_count_on_server`~ | 0 | payload-02821 |
| `mcp.websocket.authfailure` | 1 | `server_uuid`~ | 0 | payload-02819 |
| `mcp.websocket.transport.connection.failed` | 1 | `server_uuid`~, `used_authentication`~ | 0 | payload-02820 |
| `mcp_app.height_first_updated` | 1 | `chat_message_uuid`~, `has_tool_result`~, `height`~, `redacted_url`~, `server_name`~, `server_uuid`~, `time_to_height_ms`~, `tool_name`~, `tool_use_id`~ | 0 | payload-01906 |
| `mcp_app.initialized` | 1 | `chat_message_uuid`~, `host_path`, `time_to_initialized_ms`~, `was_reinitialized`~ | 1 | payload-01907 |
| `mcp_app.interaction` | 1 | `chat_message_uuid`~, `kind`~, `server_name`~ | 1 | payload-01909 |
| `mcp_app.prefill_consent` | 2 | `action`~, `redacted_url`~, `server_name`~, `server_uuid`~, `surface` | 1 | payload-00014, payload-01910 |
| `mcp_app.settings_toggled` | 1 | `enabled`~, `redacted_url`~, `server_name`~, `server_uuid`~ | 0 | payload-01029 |
| `oauth.authorize.approved` | 1 | `client_id`~, `client_name`~ | 1 | payload-01597 |
| `oauth.authorize.bounced_to_login` | 1 | `client_id`~, `reason`, `return_to`~ | 0 | payload-02745 |
| `oauth.authorize.denied` | 1 | `client_id`~, `client_name`~ | 1 | payload-01598 |
| `oauth.authorize.failure` | 1 | `client_id`~, `client_name`~, `error_code`~, `error_type`~, `status`~ | 1 | payload-01197 |
| `oauth.authorize.glowing_coral` | 2 | `challenge_asked`~, `client_id`~, `post_ms`~, `stage`, `wait_until_ms`~, `waited_ms`~ | 4 | payload-01594, payload-01595 |
| `oauth.authorize.org_access_denied_viewed` | 1 | `client_id`~, `flow_id`~, `product_surface`~ | 0 | payload-01590 |
| `oauth.authorize.org_selected` | 1 | `is_switch`~ | 1 | payload-01599 |
| `oauth.authorize.page_viewed` | 1 |  | 2 | payload-01592 |
| `oauth.authorize.silent_answered` | 2 | `cause`~, `client_id`~, `error`~ | 0 | payload-01593, payload-02744 |
| `oauth.authorize.success` | 1 | `client_id`~, `client_name`~ | 1 | payload-01196 |
| `oauth.authorize.switch_account_clicked` | 1 | `source` | 1 | payload-01591 |
| `oauth.authorize.switch_org_clicked` | 1 | `had_org_pin`~, `source`~ | 1 | payload-01596 |
| `oauth.authorize.window_too_small_shown` | 1 |  | 2 | payload-01589 |
| `onboarding.age_verification.complete` | 5 | `flow`~ | 0 | payload-00022, payload-00025, payload-00509, payload-01754, payload-01756 |
| `onboarding.age_verification.start` | 5 | `flow`~ | 0 | payload-00023, payload-00024, payload-00508, payload-01753, payload-01755 |
| `onboarding.invite_accept_page.invite_accept.submitted` | 1 |  | 0 | call-02428 |
| `onboarding.invite_accept_page.invite_accept_by_token.submitted` | 1 |  | 0 | call-02429 |
| `onboarding.invite_accept_page.invite_reject.submitted` | 1 |  | 0 | call-02430 |
| `onboarding.invite_accept_page.loaded` | 1 | `assigns_no_seat`~, `landing_deferred`~, `organization_uuid`~, `shared_artifact_kind`~ | 0 | payload-01185 |
| `onboarding.phone_verification.error_sending_code` | 1 | `error_code`~, `flow`~, `surface`, `version` | 0 | payload-02103 |
| `onboarding.phone_verification.verified_code` | 1 | `flow`~, `surface`, `version` | 0 | payload-02105 |
| `onboarding.started` | 1 | `referral_campaign`~, `referral_source`~ | 0 | payload-00248 |
| `payment_state_slow_poll` | 1 | `invoice_created_ts`~, `product_capability`~, `rate_limit_tier`~, `subscription_kind`~ | 0 | payload-01463 |
| `payment_state_timed_out` | 1 | `invoice_created_ts`~, `product_capability`~, `rate_limit_tier`~, `subscription_kind`~ | 0 | payload-01464 |
| `pro_subscription.downgraded_to_monthly` | 1 | `target_plan_type` | 0 | payload-02579 |
| `pro_subscription.upgraded_to_annual` | 1 |  | 0 | payload-02561 |
| `pro_subscription.upgraded_to_max` | 1 | `max_plan_type`~ | 0 | payload-02576 |
| `self_serve_refund.choice_selected` | 1 | `choice`~ | 0 | payload-01833 |
| `self_serve_refund.confirm_clicked` | 1 |  | 0 | payload-01832 |
| `self_serve_refund.execute_result` | 2 | `ineligible_reason`~, `status`~ | 0 | payload-01827, payload-01828 |
| `self_serve_refund.modal_shown` | 1 |  | 0 | payload-01823 |
| `self_serve_refund.preview_result` | 1 | `eligible`~, `ineligible_reason`~ | 0 | payload-01825 |
| `sheets.oauth_error.upgrade_clicked` | 1 |  | 0 | payload-01601 |
| `sheets.oauth_error.viewed` | 1 |  | 0 | payload-01600 |
| `sse_interrupted` | 1 | `content_blocks_received`~, `conversation_uuid`~, `elapsed_ms`~, `model`~, `transport` | 0 | payload-02653 |
| `television.acorn_drey_admin_login_list_saved` | 4 | `admin_page`~, `list`, `login_count`~ | 0 | payload-00714, payload-00715, payload-01233, payload-01234 |
| `television.acorn_drey_admin_repo_budget_change` | 1 | `admin_page`~, `has_budget`~ | 0 | payload-01769 |
| `television.acorn_drey_admin_repo_greeting_change` | 1 | `admin_page`~, `has_greeting`~ | 0 | payload-01770 |
| `television.acorn_drey_admin_repo_mode_change` | 1 | `admin_page`~, `new_mode`~ | 0 | payload-01771 |
| `television.acorn_drey_admin_repo_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01772 |
| `television.acorn_drey_admin_save_error` | 2 | `admin_page`~, `error_reason`~ | 0 | payload-01768, payload-01773 |
| `television.acorn_drey_admin_scope_change` | 3 | `admin_page`~, `new_scope`~ | 0 | payload-00713, payload-01231, payload-01232 |
| `television.acorn_drey_admin_viewed` | 1 | `admin_page`~ | 0 | payload-01767 |
| `television.claude_code_angelica_admin_toggle` | 2 | `new_state`~, `source`~ | 0 | payload-02212, payload-02213 |
| `television.claude_code_channels_admin_toggle` | 1 | `new_state`~ | 0 | payload-01085 |
| `television.claude_code_desktop_admin_toggle` | 1 | `new_state`~ | 0 | payload-01090 |
| `television.claude_code_desktop_bypass_permissions_admin_toggle` | 1 | `new_state`~ | 0 | payload-01095 |
| `television.claude_code_penguin_mode_admin_toggle` | 1 | `new_state`~ | 0 | payload-01092 |
| `television.claude_code_quick_web_setup_admin_toggle` | 1 | `new_state`~ | 0 | payload-01096 |
| `television.claude_code_remote_control_admin_toggle` | 1 | `new_state`~ | 0 | payload-01093 |
| `television.claude_code_remote_control_default_admin_toggle` | 1 | `new_state`~ | 0 | payload-01084 |
| `television.claude_code_routines_admin_toggle` | 1 | `new_state`~ | 0 | payload-01071 |
| `television.claude_code_self_hosted_runners_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-02372 |
| `television.claude_code_team_memory_mode_admin_change` | 1 | `new_state`~ | 0 | payload-01089 |
| `television.claude_code_trusted_devices_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01069 |
| `television.claude_code_web_admin_toggle` | 1 | `new_state`~ | 0 | payload-01091 |
| `television.claude_code_workflows_admin_toggle` | 1 | `new_state`~ | 0 | payload-01094 |
| `television.cobalt_plinth_admin_toggle` | 2 | `admin_page`~, `new_state`~ | 0 | payload-01073, payload-01074 |
| `television.cobalt_plinth_external_sharing_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01076 |
| `television.cobalt_plinth_org_sharing_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01077 |
| `television.cobalt_plinth_presence_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01078 |
| `television.cobalt_plinth_thistle_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-01075 |
| `television.cobalt_plinth_type_admin_toggle` | 1 | `admin_page`~, `feature`~, `new_state`~ | 0 | payload-01079 |
| `television.conductor_admin_toggle` | 1 | `new_state`~ | 0 | payload-02481 |
| `ts.banner.shown` | 1 | `account_uuid`~, `conversation_uuid`~, `flag_type`~, `ipCountry`~, `organization_uuid`~ | 0 | payload-01428 |
| `voice_session_cancelled` | 1 | `conversation_uuid`~ | 1 | payload-02092 |
| `voice_session_ended` | 2 | `conversation_uuid`~ | 2 | payload-02090, payload-02709 |
| `voice_session_error` | 1 | `conversation_uuid`~ | 1 | payload-02708 |
| `voice_session_started` | 1 | `conversation_uuid`~ | 1 | payload-02706 |
| `voice_turn_completed` | 2 | `conversation_uuid`~ | 2 | payload-02091, payload-02707 |
| `wiggle.file.add_to_project` | 1 |  | 1 | payload-01417 |
| `wiggle.file.copied_as_image` | 1 |  | 1 | payload-01416 |
| `wiggle.file.copy_to_clipboard` | 1 |  | 2 | payload-01415 |
| `wiggle.file.created` | 2 | `chat_message_uuid`~, `delivery_kind`~, `delivery_surface`~ | 2 | payload-01432, payload-01433 |
| `wiggle.file.download_as_pdf` | 1 |  | 1 | payload-01418 |
| `wiggle.file.download_failed` | 4 | `content_length_bucket`~, `elapsed_bucket`~, `online`~, `phase`~, `reason`~, `route`~, `source`~, `status`~, `ttfb_bucket`~, `visibility`~ | 0 | payload-02659, payload-03066, payload-03068, payload-03069 |
| `wiggle.file.download_started` | 2 | `content_length_bucket`~, `http_status`~, `route`~, `sized_by`~, `total_bucket`~, `ttfb_bucket`~, `via`~ | 0 | payload-02658, payload-03067 |
| `wiggle.file.downloaded` | 4 | `download_mechanism`~ | 4 | payload-00013, payload-00991, payload-03065, payload-03179 |
| `wiggle.file.downloaded_all` | 1 | `conversation_uuid`~, `file_count`~, `is_snapshot`~, `snapshot_uuid`~, `source`~ | 0 | payload-03070 |
| `wiggle.file.gdrive_export.attempted` | 1 |  | 1 | payload-00263 |
| `wiggle.file.gdrive_export.failed` | 1 | `error_code`~, `error_message`~, `error_type`~ | 1 | payload-00265 |
| `wiggle.file.gdrive_export.success` | 1 |  | 1 | payload-00264 |
| `wiggle.file.publish_artifact` | 1 | `artifact_kind`~, `publish_route`~ | 1 | payload-01419 |
| `wiggle.file.share_artifact` | 1 | `artifact_kind`~, `publish_route`~ | 1 | payload-01419 |
| `wiggle.gdrive.connection.initiated` | 1 | `caller_identifier`~, `error_type`~, `organization_id`~ | 0 | payload-00261 |
| `wiggle.gdrive.connection.modal_shown` | 1 | `caller_identifier`~, `error_type`~, `organization_id`~ | 0 | payload-00260 |
| `wiggle.gdrive.connection.success` | 1 | `caller_identifier`~, `error_type`~, `organization_id`~ | 0 | payload-00259 |
