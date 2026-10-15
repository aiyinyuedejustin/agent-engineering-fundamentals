# analytics_payload 完整有界字典

[返回索引](README.md)

位置数是语法计数。字段并集不是必填 schema；`?` 表示至少一处条件加入，`~` 表示至少一处可能 undefined。所有值仍可能被未知 spread 或后置清理改变。这里的记录数包含已提取字段的条件 spread 与未解析形式；直接字面量对象展开会被内联，不计入此列。它不是未知字段集合数。源码位置与每处类型详见 index.json 的 sites/field_forms/shapes 分片。

| 名称 | 位置数 | 字段并集 | 已记录 spread 数 | 位置编号 |
|---|---:|---|---:|---|
| `account_migration.domain_capture_banner_shown` | 1 |  | 0 | payload-00317 |
| `account_migration.nudge_shown` | 2 | `surface` | 0 | payload-00315, payload-00316 |
| `account_migration.option_selected` | 1 | `entry_point`~, `option`~, `surface`~ | 0 | payload-00314 |
| `account_migration.submitted` | 2 | `action`, `entry_point`~, `surface`~ | 0 | payload-00312, payload-00313 |
| `activity_panel.feedback` | 1 | `conversation_uuid`~, `session_id`~, `todo_status`~, `type` | 0 | payload-00636 |
| `activity_panel.resource_closed` | 10 | `conversation_uuid`~, `file_category`~, `file_extension`~, `resource_type`, `server_name`~, `session_id`~, `skill_name`~, `trigger` | 0 | payload-00413, payload-00415, payload-00417, payload-00419, payload-00421, payload-00423, payload-00425, payload-00427, payload-00430, payload-00432 |
| `activity_panel.resource_opened` | 12 | `conversation_uuid`~, `file_category`~, `file_extension`~, `resource_type`, `section`~, `server_name`~, `session_id`~, `skill_name`~, `trigger`~ | 0 | payload-00411, payload-00414, payload-00416, payload-00418, payload-00420, payload-00422, payload-00424, payload-00426, payload-00428, payload-00429, payload-00431, payload-00433 |
| `activity_panel.resources_appeared` | 1 | `conversation_uuid`~, `resource_count`~, `session_id`~, `total_resources`~ | 0 | payload-00410 |
| `activity_panel.todos_appeared` | 1 | `conversation_uuid`~, `session_id`~, `todo_count`~ | 0 | payload-00412 |
| `activity_panel.toggle_closed` | 3 | `conversation_uuid`~, `session_id`~, `source`~ | 0 | payload-00406, payload-00407, payload-02732 |
| `activity_panel.toggle_opened` | 3 | `conversation_uuid`~, `session_id`~, `source`~ | 0 | payload-00406, payload-00408, payload-02732 |
| `appeals.restricted.appeal_submitted` | 1 | `ban_category`~, `org_scoped`~ | 0 | payload-00867 |
| `appeals.restricted.export_clicked` | 1 | `export_policy`~ | 0 | payload-00861 |
| `appeals.restricted.export_failed` | 1 | `export_policy`~ | 0 | payload-00859 |
| `appeals.restricted.export_submitted` | 1 | `export_policy`~ | 0 | payload-00860 |
| `appeals.restricted.page_viewed` | 2 | `ban_category`~, `banned_org_count`~, `hide_steps_card`~, `state`~ | 0 | payload-00858, payload-00866 |
| `appeals.restricted.review_cta_clicked` | 2 | `org_scoped`~ | 0 | payload-00863, payload-00865 |
| `appeals.restricted.yoti_clicked` | 2 | `org_scoped`~ | 0 | payload-00862, payload-00864 |
| `apps.activation_credit_claim_failed` | 2 | `limit_window`~, `reason` | 0 | payload-01287, payload-01289 |
| `apps.activation_credit_claimed` | 1 | `limit_window`~ | 0 | payload-01288 |
| `apps.activation_credit_offer_dismissed` | 1 | `limit_window`~ | 0 | payload-01286 |
| `apps.activation_credit_offer_shown` | 1 | `initial_step`~, `limit_window`~, `trigger`~ | 0 | payload-01285 |
| `apps.activation_credit_upgrade_clicked` | 1 | `limit_window`~ | 0 | payload-01290 |
| `apps.credit_promo_claim_failed` | 3 | `page`~, `placement`~, `reason` | 0 | payload-01165, payload-02348, payload-02350 |
| `apps.credit_promo_claimed` | 2 | `overages_enabled`~, `page`~, `placement`~ | 0 | payload-01164, payload-02349 |
| `apps.credit_promo_offer_dismissed` | 2 | `method`, `placement` | 0 | payload-03245, payload-03246 |
| `apps.credit_promo_offer_shown` | 2 | `page`~, `placement` | 0 | payload-02351, payload-03244 |
| `apps.credits_required_wall_shown` | 1 | `route`~, `target_model_id`~ | 0 | payload-03234 |
| `apps.download_button_clicked` | 11 | `platform`~, `referral_campaign`~, `referral_source`~, `source`~, `userPlatform`~ | 0 | payload-00235, payload-00239, payload-00886, payload-01027, payload-01115, payload-01166, payload-01993, payload-01994, payload-02046, payload-02123, payload-03054 |
| `apps.message_limit_modal_dismissed` | 1 | `stop_state`?~, `variant` | 1 | payload-02978 |
| `apps.message_limit_modal_shown` | 1 | `arm`?~, `pro_offer`?~, `stop_state`?~, `variant` | 3 | payload-02977 |
| `apps.message_limit_modal_upgrade_clicked` | 2 | `arm`~, `interval`?~, `stop_state`?~, `target`~, `variant` | 3 | payload-01209, payload-02976 |
| `apps.message_limit_tile_clicked` | 1 | `tile`~ | 0 | payload-02975 |
| `apps.project_limit_modal_dismissed` | 1 | `variant` | 0 | payload-01457 |
| `apps.project_limit_modal_shown` | 1 |  | 0 | payload-03009 |
| `apps.project_limit_modal_upgrade_clicked` | 1 | `variant` | 0 | payload-01456 |
| `apps.project_limit_tile_clicked` | 1 | `tile`~ | 0 | payload-01455 |
| `artifact.claude_access_prompt.resolved` | 1 | `context_type`~, `outcome`~ | 0 | payload-02050 |
| `artifact.claude_access_prompt.shown` | 1 | `context_type`~ | 0 | payload-02051 |
| `artifact.connectors.withheld` | 1 | `reason`~ | 0 | payload-02049 |
| `artifact.public.copy` | 1 | `artifact_id`~ | 0 | payload-01228 |
| `artifact.public.share` | 1 | `artifact_id`~ | 0 | payload-01226 |
| `artifact.public.support_link` | 1 | `artifact_id`~ | 0 | payload-01229 |
| `artifact.public.view` | 1 | `artifact_id`~, `show_code_view`~, `show_copy_button`~, `show_support_link`~ | 0 | payload-01227 |
| `artifact.publish.modal.publish_button_clicked` | 1 | `artifact_language`~, `artifact_type`~, `message_uuid`~ | 0 | payload-00278 |
| `artifact.publish_button_clicked` | 1 | `artifact_language`~, `artifact_type`~, `message_uuid`~ | 0 | payload-01798 |
| `artifact.repl.permission_denied` | 1 | `method`~, `sandbox_surface` | 0 | payload-02902 |
| `artifact.share.modal.share_button_clicked` | 1 | `artifact_language`~, `artifact_type`~, `message_uuid`~ | 0 | payload-01805 |
| `artifact.share_button_clicked` | 1 | `artifact_language`~, `artifact_type`~, `message_uuid`~ | 0 | payload-01797 |
| `artifact.studio.create_button_clicked` | 6 | `action`, `from`?~, `opens`?, `source`, `template`~, `via` | 6 | payload-00474, payload-00475, payload-00476, payload-00477, payload-00478, payload-01757 |
| `artifact.studio.create_mode_selected` | 1 | `create_mode`~ | 0 | payload-01429 |
| `artifactinlinefeedback.selection.clicked` | 2 | `source` | 0 | payload-01291, payload-01292 |
| `billing.checkout_session_incomplete_fallback` | 1 | `plan`~ | 0 | payload-02585 |
| `billing.checkout_session_promo_fallback` | 1 | `plan`~, `reason`~ | 0 | payload-02583 |
| `billing.payment_method_precollect.added` | 1 | `set_default`~, `started_from`~ | 0 | payload-01878 |
| `billing.payment_method_precollect.failed` | 1 | `reason`, `started_from`~ | 0 | payload-01877 |
| `billing.payment_method_precollect.started` | 1 | `started_from`~ | 0 | payload-01876 |
| `billing.payment_method_precollect.viewed` | 1 |  | 0 | payload-01880 |
| `billing.payment_verification.failed` | 2 | `reason`~, `started_from`~ | 0 | payload-01873, payload-01874 |
| `billing.payment_verification.started` | 1 | `started_from`~ | 0 | payload-01875 |
| `billing.payment_verification.verified` | 1 | `outcome`~, `started_from`~ | 0 | payload-01872 |
| `billing.payment_verification.viewed` | 1 |  | 0 | payload-01879 |
| `cc_celebration.back_to_claude_clicked` | 1 | `source`~ | 0 | payload-02262 |
| `cc_celebration.cta_clicked` | 1 | `cta_url`~, `section`~ | 0 | payload-02268 |
| `cc_celebration.dismissed` | 1 |  | 0 | payload-02267 |
| `cc_celebration.game_engagement_summary` | 1 | `duration_seconds`~, `modifications_applied`~, `total_jumps`~, `total_key_presses`~, `total_moves`~, `unique_actions_used`~ | 0 | payload-02265 |
| `cc_celebration.game_modification_applied` | 1 | `modification`~ | 0 | payload-02263 |
| `cc_celebration.game_section_viewed` | 1 |  | 0 | payload-02264 |
| `cc_celebration.install_command_copied` | 1 |  | 0 | payload-02261 |
| `cc_celebration.resource_link_clicked` | 1 | `resource_type`~ | 0 | payload-02260 |
| `cc_celebration.scroll_down_clicked` | 1 |  | 0 | payload-02257 |
| `cc_celebration.section_viewed` | 1 | `section`~ | 0 | payload-02256 |
| `cc_celebration.shown` | 1 |  | 0 | payload-02266 |
| `cc_celebration.social_proof_card_clicked` | 1 | `card_category`~, `card_headline`~, `card_url`~ | 0 | payload-02259 |
| `cc_celebration.ticket_clicked` | 1 |  | 0 | payload-02258 |
| `chat.conversation.first_conversation_created` | 2 | `surface` | 0 | payload-00213, payload-02833 |
| `chat.conversation.token_limit_exceeded` | 1 | `conversation_uuid`~, `project_uuid`~ | 0 | payload-02647 |
| `chat.conversations.invalidate` | 5 | `action` | 0 | payload-02678, payload-02688, payload-02689, payload-02690, payload-02692 |
| `chat.share.access_page.retry_clicked` | 1 | `state` | 0 | payload-01192 |
| `chat.share.access_page.viewed` | 1 | `previous_state`~, `signed_in`~, `state`~ | 0 | payload-01193 |
| `chat.share.button.clicked` | 1 | `conversation_uuid`~ | 0 | payload-01423 |
| `chat.share.copy_link.clicked` | 2 | `conversation_uuid`~, `snapshot_uuid`~ | 0 | payload-00810, payload-01451 |
| `chat.share.modal.opened` | 1 | `cheeky_cosmos_offered`~, `conversation_uuid`~, `dialog`~, `is_public`~, `is_shared`~, `plan`~, `visibility`~ | 0 | payload-01420 |
| `chat.share.modal.share_button.clicked` | 2 | `conversation_uuid`~ | 0 | payload-00808, payload-01436 |
| `chat.share.modal.unshare_button.clicked` | 2 | `conversation_uuid`~, `snapshot_uuid`~ | 0 | payload-00807, payload-01447 |
| `chat.share.open_link.clicked` | 1 | `conversation_uuid`~, `snapshot_uuid`~ | 0 | payload-00809 |
| `chat_project_create` | 1 | `project_type`~, `project_uuid`~, `source`~ | 0 | payload-02792 |
| `chorus.bright_charm.attach_outcome` | 1 | `outcome`~, `project_uuid`~, `reason`?~, `source`~ | 1 | payload-01486 |
| `chorus.bright_charm.folder_edit_outcome` | 1 | `action`~, `entry`?~, `outcome`~, `project_uuid`~, `reason`?~, `skipped`?~, `unsent`?~ | 4 | payload-01275 |
| `chorus.bright_charm.folder_not_staged` | 1 | `os`~, `project_uuid`~, `reason`~ | 0 | payload-01135 |
| `chorus.bright_charm.folder_relink_prompt` | 1 | `os`~, `outcome`~, `project_uuid`~ | 0 | payload-01136 |
| `chorus.conversation_created` | 2 | `cgw_pick`?~, `conversation_uuid`~, `has_project`~, `launch_source`?, `slash_command`?~, `source`~ | 4 | payload-00566, payload-02817 |
| `chorus.cowork_upsell.add_folder_blocked` | 1 | `source`~ | 0 | payload-01485 |
| `chorus.cowork_upsell.send_blocked` | 1 | `source`~, `upsell_variant`~ | 0 | payload-02816 |
| `chorus.cowork_upsell_modal.dismissed` | 1 | `variant`~ | 0 | payload-03037 |
| `chorus.cowork_upsell_modal.displayed` | 1 | `variant`~ | 0 | payload-03035 |
| `chorus.cowork_upsell_modal.upgrade_clicked` | 1 | `variant`~ | 0 | payload-03036 |
| `chorus.ideas.suggestion_clicked` | 1 | `idea_id`~, `idea_surface`~, `ideas_variant`~, `list_variant`, `position`~ | 0 | payload-02899 |
| `chorus.ideas.suggestions_shown` | 1 | `idea_id`~, `ideas_variant`~, `list_variant`, `position`~ | 0 | payload-02898 |
| `chorus.nux.surface_select_coachmark.dismissed` | 1 |  | 0 | payload-03042 |
| `chorus.nux.surface_select_coachmark.displayed` | 1 |  | 0 | payload-03041 |
| `chorus.project_create.files_outcome` | 1 | `added_count`~, `failed_count`~, `file_count`~, `outcome`~, `project_uuid`~, `source`~ | 0 | payload-03222 |
| `chorus.snug_coral.accepted` | 2 | `action`~, `artifact_type`~, `intent`~, `position`~, `query_length`~, `source`~, `via`~ | 0 | payload-00663, payload-00664 |
| `chorus.snug_coral.shown` | 1 | `artifact_count`~, `completion_count`~, `connector_count`~, `query_length`~, `row_count`~, `topic_count`~, `trigger`~ | 0 | payload-00662 |
| `chorus.surface_select.changed` | 1 | `control_variant`~, `from_surface`~, `to_surface`~ | 0 | payload-03043 |
| `chorus.surface_select.cowork_upsell_clicked` | 1 | `upsell_variant`~ | 0 | payload-03045 |
| `chorus.surface_select.cowork_upsell_displayed` | 1 | `upsell_variant`~ | 0 | payload-03044 |
| `claude.cowork.doc_editor.feedback_submitted` | 1 | `doc_id`~, `file_id`, `file_uuid`~, `previous_rating`~, `rating`~, `subarea`~ | 1 | payload-01409 |
| `claude.cowork.feedback_opened` | 2 | `session_id`~, `source`~, `survey_appearance_id`~, `survey_response`~ | 0 | payload-00676, payload-00759 |
| `claude.cowork.feedback_redirected` | 2 | `destination`, `product_area`, `report_type`, `source`~ | 0 | payload-00677, payload-00760 |
| `claude.cowork.feedback_submitted` | 2 | `cli_session_id`~, `feedback_id`~, `included_transcript`~, `inference_log_ids`~, `is_cowork_remote_mode`~, `model`~, `report_type`, `session_id`~, `source`~, `switch_to_local_reason`~ | 1 | payload-00675, payload-00758 |
| `claude.cowork.feedback_survey.appeared` | 1 | `appearance_id`~, `claude_code_session_id`~, `effort_level`~, `is_remote`~, `last_assistant_message_id`~, `model`~, `presentation`~, `session_id`~, `survey_surface`~, `survey_type`~ | 1 | payload-00444 |
| `claude.cowork.feedback_survey.humble_spring_answered` | 1 | `answer`~, `appearance_id`~, `session_id`~, `survey_surface`~ | 0 | payload-00447 |
| `claude.cowork.feedback_survey.humble_spring_shown` | 1 | `appearance_id`~, `session_id`~, `survey_surface`~ | 0 | payload-00446 |
| `claude.cowork.feedback_survey.responded` | 1 | `appearance_id`~, `claude_code_session_id`~, `effort_level`~, `is_remote`~, `last_assistant_message_id`~, `model`~, `presentation`~, `response`~, `session_id`~, `survey_surface`~, `survey_type`~ | 1 | payload-00445 |
| `claude.cowork.live_artifact.chat_session_started` | 1 | `artifact_id`~ | 0 | payload-00912 |
| `claude.cowork.live_artifact.deleted` | 1 | `artifact_id`~ | 0 | payload-02772 |
| `claude.cowork.live_artifact.detail_page_viewed` | 1 | `artifact_id`~, `drawer_restored`~, `opener`?~ | 1 | payload-00913 |
| `claude.cowork.live_artifact.imported` | 1 | `artifact_id`~, `had_mcp_tools`~ | 0 | payload-02042 |
| `claude.cowork.live_artifact.list_page_viewed` | 1 |  | 0 | payload-02041 |
| `claude.cowork.live_artifact.popout_closed` | 1 | `artifact_id`~, `duration_ms`~ | 0 | payload-02150 |
| `claude.cowork.live_artifact.popout_opened` | 1 | `artifact_id`~, `entry_point`~ | 0 | payload-02149 |
| `claude.cowork.live_artifact.printed_to_pdf` | 1 | `artifact_id`~ | 0 | payload-00910 |
| `claude.cowork.live_artifact.republish_modal_viewed` | 1 | `artifact_id`~, `legacy_share`~, `prior_republish`~ | 0 | payload-00460 |
| `claude.cowork.live_artifact.republish_pin_swapped` | 1 | `artifact_id`~ | 0 | payload-00442 |
| `claude.cowork.live_artifact.republish_session_started` | 1 | `artifact_id`~ | 0 | payload-00461 |
| `claude.cowork.live_artifact.restored` | 1 | `artifact_id`~ | 0 | payload-00911 |
| `claude.cowork.live_artifact.starred` | 2 | `artifact_id`~, `source`~, `starred`~ | 0 | payload-02683, payload-02871 |
| `claude.cowork.live_artifact.starter_chip_clicked` | 1 | `chip_id`~ | 0 | payload-02043 |
| `claude.cowork.mini_compose.closed` | 3 | `had_draft`~, `slot`~ | 0 | payload-01022, payload-01023, payload-01024 |
| `claude.cowork.mini_compose.intercept_declined` | 1 | `artifact_surface`~, `reason`~ | 0 | payload-02234 |
| `claude.cowork.mini_compose.minimized` | 2 | `slot`~ | 0 | payload-01021, payload-02844 |
| `claude.cowork.mini_compose.opened` | 1 | `artifact_surface`~, `slot`~, `source`~ | 0 | payload-01025 |
| `claude.cowork.mini_compose.prompt_submitted` | 1 | `artifact_surface`~, `auto_initiated`~, `slot`~, `source`~ | 0 | payload-01026 |
| `claude.cowork.rippling_charm_notice.added` | 1 | `host_surface`~, `stop_flag`~ | 0 | payload-01707 |
| `claude.cowork.task.stop_button` | 12 | `duration_ms`~, `error_name`~, `is_local`~, `is_primary_composer`~, `ok`~, `reason`~, `session_id`~, `stage`, `stop_surface`~, `trigger` | 4 | payload-01699, payload-01701, payload-01702, payload-01713, payload-01731, payload-01733, payload-02953, payload-03226, payload-03227, payload-03228, payload-03229, payload-03230 |
| `claude.cowork.valiant_eclipse_notice.added` | 1 | `fallback_model`~, `host_surface`~, `original_model`~, `trigger`~ | 0 | payload-02069 |
| `claude.cowork.web_fetch_approval.approved` | 2 | `scope`~, `standing_grant_withheld`~ | 0 | payload-01474, payload-01475 |
| `claude.cowork.web_fetch_approval.dismissed` | 1 |  | 0 | payload-01473 |
| `claude.cowork.web_fetch_approval.viewed` | 1 | `host_grant_available`~, `host_grant_withheld_reason`?~ | 1 | payload-01472 |
| `claude.cowork.writing_draft.feedback_submitted` | 1 | `feedback_type`~, `is_revision`?~, `reasons`~ | 1 | payload-00914 |
| `claude_code_install_page.advanced_setup_clicked` | 1 |  | 0 | payload-01979 |
| `claude_code_install_page.command_copied` | 1 | `command`~ | 0 | payload-01978 |
| `claude_code_install_page.done_clicked` | 1 |  | 0 | payload-01981 |
| `claude_code_install_page.troubleshooting_clicked` | 1 |  | 0 | payload-01980 |
| `claude_code_onboard_landing.auth_resolved` | 1 | `auth_state`~, `short_code`~ | 0 | payload-01986 |
| `claude_code_onboard_landing.copy_guide_clicked` | 1 |  | 0 | payload-01988 |
| `claude_code_onboard_landing.copy_step_clicked` | 2 | `step`~ | 0 | payload-01989, payload-01991 |
| `claude_code_onboard_landing.guide_content_copied` | 1 |  | 0 | payload-01982 |
| `claude_code_onboard_landing.guide_downloaded` | 1 |  | 0 | payload-01983 |
| `claude_code_onboard_landing.guide_expand_toggled` | 2 | `expanded`~, `source` | 0 | payload-01984, payload-01990 |
| `claude_code_onboard_landing.guide_view_changed` | 1 | `view`~ | 0 | payload-01985 |
| `claude_code_onboard_landing.setup_step_changed` | 1 | `from_step`~, `to_step`~, `trigger`~ | 0 | payload-01987 |
| `claude_code_upgrade_page.upgrade_clicked` | 1 |  | 0 | payload-01603 |
| `claude_code_upgrade_page.viewed` | 1 |  | 0 | payload-01602 |
| `claude_code_web.disabled.cli_command_copied` | 1 |  | 0 | payload-01337 |
| `claude_code_web.disabled.viewed` | 1 |  | 0 | payload-01336 |
| `claude_code_web.family_app.cli_command.copied` | 1 |  | 0 | payload-01339 |
| `claude_code_web.family_app.cta.clicked` | 2 | `data`~, `data.source` | 0 | payload-01342, payload-01345 |
| `claude_code_web.family_app.upgrade.clicked` | 6 | `data`~, `data.action`, `data.source` | 0 | payload-01340, payload-01341, payload-01343, payload-01344, payload-01346, payload-01347 |
| `claude_code_web.family_app.viewed` | 1 | `data`~, `data.user_type`~ | 0 | payload-01338 |
| `claudeai.access_block_notice.action_clicked` | 1 | `action_kind`~ | 0 | payload-03191 |
| `claudeai.access_block_notice.shown` | 1 | `action_kind`~, `reason`~ | 0 | payload-03190 |
| `claudeai.account_settings.cowork_trusted_devices_toggle` | 1 | `new_state`~ | 0 | payload-01106 |
| `claudeai.admin.agent_proxy.connector_gallery_opened` | 1 | `arm`~, `scope_kind`~ | 0 | payload-02329 |
| `claudeai.admin.agent_proxy.credential_modal_opened` | 1 | `arm`~, `credential_type`~, `entry`~, `preset_id`~ | 0 | payload-01736 |
| `claudeai.admin.agent_proxy.credential_result` | 1 | `auth_kind`~, `error_reason`~, `ms_since_open`~, `outcome`~, `submit_id`~ | 1 | payload-01738 |
| `claudeai.admin.agent_proxy.credential_submit` | 1 | `auth_kind`~, `submit_id`~ | 1 | payload-01737 |
| `claudeai.admin.agent_proxy.oauth_completed` | 2 | `credential_id`~, `profile_id`~ | 0 | payload-01747, payload-01748 |
| `claudeai.admin.agent_proxy.oauth_confirm_cancelled` | 1 | `profile_id`~ | 0 | payload-01744 |
| `claudeai.admin.agent_proxy.oauth_error` | 5 | `error_code`~, `profile_id`~ | 0 | payload-01741, payload-01745, payload-01746, payload-01749, payload-01750 |
| `claudeai.admin.agent_proxy.oauth_popup_blocked` | 2 | `profile_id`~ | 0 | payload-01740, payload-01743 |
| `claudeai.admin.agent_proxy.oauth_started` | 2 | `profile_id`~ | 0 | payload-01739, payload-01742 |
| `claudeai.admin.kindling_launch.planned` | 1 | `announce_will_follow`~, `channel_reset_agent_ids`~, `channel_reset_count`~, `install_enabled_before`~, `install_will_flip`~, `off_channel_agent_ids`~, `off_channel_count`~, `simplified_admin`~, `workspace_agent_ids`~, `workspace_count`~ | 1 | payload-00660 |
| `claudeai.admin.kindling_launch.step_completed` | 1 | `done_count`~, `ok`~, `step`~, `target_count`~, `wrote_any`~ | 1 | payload-00661 |
| `claudeai.admin.kindling_settings.access_mode_changed` | 1 | `from`~, `to`~ | 0 | payload-02327 |
| `claudeai.admin.kindling_settings.amber_ledger_changed` | 1 | `enabled`~ | 0 | payload-02381 |
| `claudeai.admin.kindling_settings.guest_policy_changed` | 1 | `from`~, `is_org_default`~, `source`~, `tag_surface`~, `to`~ | 0 | payload-02328 |
| `claudeai.admin.kindling_settings.oncall_member_repo_admin_changed` | 1 | `enabled`~ | 0 | payload-02390 |
| `claudeai.admin.kindling_setup.dismissed` | 2 | `flow`, `last_step`~, `wizard_surface`~ | 0 | payload-02324, payload-02388 |
| `claudeai.admin.kindling_setup.error` | 4 | `flow`, `kind`, `step`~, `tool`~, `wizard_surface`~ | 0 | payload-02384, payload-02385, payload-02386, payload-02389 |
| `claudeai.admin.kindling_setup.launched` | 2 | `flow`, `notify_members`~, `notify_supported`~, `pairing_scope`~, `wizard_surface`~ | 0 | payload-02326, payload-02387 |
| `claudeai.admin.kindling_setup.opened` | 2 | `flow`, `resumed`~, `wizard_surface`~ | 0 | payload-02322, payload-02382 |
| `claudeai.admin.kindling_setup.pair_confirm` | 1 | `outcome`~, `wizard_surface`~ | 0 | payload-02321 |
| `claudeai.admin.kindling_setup.saved_for_later` | 1 | `wizard_surface`~ | 0 | payload-02325 |
| `claudeai.admin.kindling_setup.step_viewed` | 2 | `flow`, `step`~, `wizard_surface`~ | 0 | payload-02323, payload-02383 |
| `claudeai.admin.kindling_usage.channel_cap_saved` | 1 | `cap_minor`~, `is_kill_switch`~, `mode`~, `previous_mode`~, `tag_surface`~ | 0 | payload-02523 |
| `claudeai.admin.kindling_usage.channels_at_limit_banner_viewed` | 1 | `count`~, `is_lower_bound`~, `tag_surface`~ | 0 | payload-02524 |
| `claudeai.admin.kindling_usage.cistern_expand_requested` | 1 | `premium_seats`~, `source`, `used_percent`~ | 0 | payload-02380 |
| `claudeai.admin.kindling_usage.default_channel_cap_saved` | 1 | `is_unlimited`~, `new_cap_minor`~, `previous_cap_minor`~, `tag_surface`~ | 0 | payload-02526 |
| `claudeai.admin.kindling_usage.org_limit_saved` | 1 | `is_kill_switch`~, `is_unlimited`~, `new_limit_minor`~, `previous_limit_minor`~, `source`~, `tag_surface`~ | 0 | payload-02320 |
| `claudeai.admin.kindling_usage.paused_state_viewed` | 1 | `is_kill_switch`~, `tag_surface`~ | 0 | payload-02525 |
| `claudeai.admin.tag_channel_patterns.added` | 2 | `pattern_count`~, `source`~, `workspaces`~ | 0 | payload-00375, payload-02330 |
| `claudeai.admin.tag_channel_patterns.removed` | 2 | `pattern_count`~, `source`~, `workspaces`~ | 0 | payload-00376, payload-02331 |
| `claudeai.admin.tag_credential_notice.action` | 2 | `action`~ | 3 | payload-02362, payload-02366 |
| `claudeai.admin.tag_credential_notice.shown` | 1 | `has_connector`?~, `repository_count`?~ | 2 | payload-02358 |
| `claudeai.admin.tag_oncall_deeplink.landed` | 1 | `admitted`~, `outcome`~ | 0 | payload-02391 |
| `claudeai.admin.tag_oncall_setup.channel_join` | 1 | `already_in`?, `channels_requested`~, `entry_source`~, `failed_other`?, `failed_unjoinable`?, `failed_wrong_pick`?, `flow`, `joined`?, `profile_id`~, `run_id`~, `transport_error`~, `trigger`~, `variant`~ | 1 | payload-00371 |
| `claudeai.admin.tag_oncall_setup.channels_selected` | 1 | `autojoin_on`~, `channels_picked`~, `entry_source`~, `flow`, `has_prefix`~, `mode`~, `newly_created`~, `pattern_count`~, `profile_id`~, `run_id`~, `would_join_count`~ | 0 | payload-00372 |
| `claudeai.admin.tag_oncall_setup.deployed` | 2 | `bind_failed`~, `channels_bound`~, `entry_source`~, `flow`, `has_prefix`~, `join_failed`~, `join_requested`~, `join_succeeded`~, `mode`~, `profile_id`~, `run_id`~, `unbind_failed`~, `unbound`~ | 0 | payload-00377, payload-00378 |
| `claudeai.admin.tag_oncall_setup.error` | 1 | `entry_source`~, `flow`, `kind`~, `step`~, `variant`~, `wizard_surface` | 0 | payload-00370 |
| `claudeai.admin.tag_oncall_setup.opened` | 1 | `entry_source`~, `flow`, `profile_id`~, `resumed`~, `run_id`~, `variant`~, `wizard_surface` | 0 | payload-00373 |
| `claudeai.admin.tag_oncall_setup.step_completed` | 1 | `detail`~, `entry_source`~, `flow`, `notify_members`~, `notify_supported`~, `outcome`~, `profile_id`~, `run_id`~, `scm_provider`~, `step`~, `variant`~ | 0 | payload-00369 |
| `claudeai.admin.tag_oncall_setup.step_viewed` | 1 | `entry_source`~, `flow`, `run_id`~, `step`~, `variant`~, `wizard_surface` | 0 | payload-00374 |
| `claudeai.admin_activation.fund_unlock.exited` | 1 | `step`~ | 0 | payload-01113 |
| `claudeai.admin_activation.fund_unlock.feature_enabled` | 2 | `feature` | 0 | payload-01111, payload-01112 |
| `claudeai.admin_activation.fund_unlock.funded` | 1 | `amount_cents`~ | 0 | payload-01109 |
| `claudeai.admin_activation.fund_unlock.payment_failed` | 2 |  | 0 | payload-01108, payload-01110 |
| `claudeai.admin_activation.fund_unlock.skipped` | 1 |  | 0 | payload-01114 |
| `claudeai.admin_activation.fund_unlock.step_viewed` | 1 | `step`~ | 0 | payload-01107 |
| `claudeai.admin_connectors.apm_bulk_action_completed` | 2 | `action`~, `applied`~, `failed`~, `not_attempted`~, `selected`~ | 0 | payload-02397, payload-02398 |
| `claudeai.admin_connectors.apm_connector_viewed` | 1 | `arrived_by`~, `connector_kind`~, `server_uuid`~ | 0 | payload-02413 |
| `claudeai.admin_connectors.details_opened` | 1 | `connector_kind`~, `server_uuid`~, `source`~ | 0 | payload-02399 |
| `claudeai.admin_connectors.list_viewed` | 1 | `layout`~ | 0 | payload-02400 |
| `claudeai.admin_connectors.plugin_enabled` | 2 | `action`, `cli_count`~, `is_official_plugin`~, `plugin_id_hash`~, `plugin_name`, `preference`~ | 0 | payload-00829, payload-00830 |
| `claudeai.admin_connectors.tool_policy_changed` | 4 | `is_wildcard`~, `new_value`~, `previous_value`~, `server_uuid`~ | 0 | payload-00562, payload-00563, payload-00564, payload-02804 |
| `claudeai.admin_connectors.tool_policy_save_failed` | 2 | `reenable_required`~, `server_uuid`~ | 0 | payload-00560, payload-02805 |
| `claudeai.admin_connectors.tool_policy_section_viewed` | 1 | `server_uuid`~, `tool_count`~ | 0 | payload-00561 |
| `claudeai.admin_extensions.allowlist_extension_added` | 1 | `extension_id`~ | 0 | payload-01015 |
| `claudeai.admin_extensions.allowlist_extension_removed` | 1 | `extension_id`~ | 0 | payload-01016 |
| `claudeai.admin_extensions.blocklist_added` | 1 | `extension_id`~ | 0 | payload-02546 |
| `claudeai.admin_extensions.blocklist_removed` | 1 | `extension_id`~ | 0 | payload-02547 |
| `claudeai.admin_extensions.extension_deleted` | 1 | `extension_id`~ | 0 | payload-02545 |
| `claudeai.admin_extensions.uploaded` | 2 | `extension_id`~, `is_new_version`~ | 0 | payload-02543, payload-02548 |
| `claudeai.admin_extensions.version_deleted` | 1 | `extension_id`~, `extension_version`~ | 0 | payload-02544 |
| `claudeai.admin_invite.failed` | 1 | `after_stay_open`~, `reason`~ | 0 | payload-00788 |
| `claudeai.admin_invite.submitted` | 1 | `after_stay_open`~, `amber_wren_attached`~, `count`~, `role`~, `seat_tier`~, `slate_heron_attached`~, `source`?~, `used_csv`~ | 1 | payload-00786 |
| `claudeai.admin_plugins.apm_policy_viewed` | 1 | `can_edit`~ | 0 | payload-02516 |
| `claudeai.admin_plugins.apm_related_link_clicked` | 2 | `target`~ | 0 | payload-02512, payload-02513 |
| `claudeai.admin_plugins.apm_roles_link_clicked` | 1 | `capability`~ | 0 | payload-02514 |
| `claudeai.admin_plugins.connector_setup_dismissed` | 1 | `admin_page`?~, `marketplace_id`~, `remaining_connector_count`~, `trigger`~ | 1 | payload-02427 |
| `claudeai.admin_plugins.connector_setup_enabled` | 1 | `admin_page`?~, `connector_kind`~, `marketplace_id`~, `trigger`~ | 1 | payload-02426 |
| `claudeai.admin_plugins.connector_setup_shown` | 1 | `admin_page`?~, `marketplace_id`~, `missing_connector_count`~, `trigger`~ | 1 | payload-02425 |
| `claudeai.admin_plugins.file_browser_tab_selected` | 1 | `plugin_id`~, `tab`~, `tenancy`~ | 0 | payload-02345 |
| `claudeai.admin_plugins.marketplace_auto_sync_toggled` | 1 | `enabled`~, `marketplace_id`~ | 0 | payload-02423 |
| `claudeai.admin_plugins.marketplace_created` | 6 | `auto_sync_enabled`~, `default_plugin_installation_preference`~, `entry_point`?~, `is_default`~, `marketplace_id`~, `source_type`~ | 2 | payload-00062, payload-00368, payload-00494, payload-01208, payload-02428, payload-02429 |
| `claudeai.admin_plugins.marketplace_default_pref_changed` | 1 | `is_default`~, `marketplace_id`~, `new_preference`~, `previous_preference`~ | 0 | payload-02432 |
| `claudeai.admin_plugins.marketplace_default_pref_confirm_cancelled` | 1 | `is_default`~, `marketplace_id`~, `new_preference`~ | 0 | payload-02434 |
| `claudeai.admin_plugins.marketplace_default_pref_confirm_shown` | 1 | `is_default`~, `marketplace_id`~, `new_preference`~ | 0 | payload-02435 |
| `claudeai.admin_plugins.marketplace_default_pref_confirmed` | 1 | `is_default`~, `marketplace_id`~, `new_preference`~ | 0 | payload-02433 |
| `claudeai.admin_plugins.marketplace_deleted` | 2 | `is_default`?~, `marketplace_id`~, `source_type`~ | 1 | payload-00495, payload-02420 |
| `claudeai.admin_plugins.marketplace_page_viewed` | 1 | `kind`~, `marketplace_id`~ | 0 | payload-02436 |
| `claudeai.admin_plugins.marketplace_sync_completed` | 1 | `is_default`~, `marketplace_id`~, `sync_status`~ | 0 | payload-02424 |
| `claudeai.admin_plugins.marketplace_synced` | 1 | `entry_point`~, `marketplace_id`~ | 0 | payload-02421 |
| `claudeai.admin_plugins.marketplace_validated` | 1 | `marketplace_id`~, `plugin_error_count`~, `plugins_with_warnings_count`~, `valid`~ | 0 | payload-02422 |
| `claudeai.admin_plugins.marketplace_webhook_cleared` | 1 | `marketplace_id`~ | 0 | payload-02419 |
| `claudeai.admin_plugins.marketplace_webhook_provisioned` | 1 | `is_rotation`~, `marketplace_id`~, `provisioning_mode`~, `webhook_auth`~ | 0 | payload-02644 |
| `claudeai.admin_plugins.marketplaces_page_viewed` | 1 | `marketplace_count`~, `viewer`~ | 0 | payload-02437 |
| `claudeai.admin_plugins.plugin_authored` | 2 | `entry_point`?~, `file_count`~, `flavor`, `marketplace_id`~, `plugin_id`~, `tenancy`~ | 1 | payload-00065, payload-02431 |
| `claudeai.admin_plugins.plugin_deleted` | 3 | `admin_page`~, `item_owner`~, `plugin_id`~ | 0 | payload-02347, payload-02494, payload-02500 |
| `claudeai.admin_plugins.plugin_files_viewed` | 1 | `plugin_id`~ | 0 | payload-02495 |
| `claudeai.admin_plugins.plugin_group_preference_changed` | 2 | `admin_page`~, `group_uuid`~, `marketplace_id`~, `new_preference`~, `plugin_id`~, `previous_preference`~ | 0 | payload-02493, payload-02504 |
| `claudeai.admin_plugins.plugin_preference_changed` | 3 | `admin_page`~, `marketplace_id`~, `new_preference`~, `plugin_id`~, `previous_preference`~ | 0 | payload-02346, payload-02501, payload-02503 |
| `claudeai.admin_plugins.plugin_uploaded` | 1 | `marketplace_id`~ | 0 | payload-02430 |
| `claudeai.admin_plugins.plugin_version_save_failed` | 1 | `conflict`~, `marketplace_id`~, `plugin_id`~, `tenancy`~ | 1 | payload-00359 |
| `claudeai.admin_plugins.plugin_version_saved` | 1 | `delta_size`~, `marketplace_id`~, `plugin_id`~, `saved_version`~, `tenancy`~ | 0 | payload-00358 |
| `claudeai.admin_plugins.version_compared` | 1 | `admin_page`, `compared_version`~, `current_version`~, `plugin_id`~ | 0 | payload-02508 |
| `claudeai.admin_plugins.version_head_change_failed` | 1 | `error_kind`~, `refusal`~ | 1 | payload-00357 |
| `claudeai.admin_plugins.version_head_changed` | 1 |  | 1 | payload-00356 |
| `claudeai.admin_plugins.version_history_opened` | 1 | `plugin_id`~, `tenancy`~ | 0 | payload-02342 |
| `claudeai.admin_plugins.version_viewed` | 2 | `entry`, `plugin_id`~, `tenancy`~, `viewed_version`~ | 0 | payload-00503, payload-02344 |
| `claudeai.admin_request.admin_dismissed` | 4 | `data`~, `data.action`, `data.count`~, `data.request_type`~, `data.requester_seat_tier`~, `data.source`~ | 0 | payload-02367, payload-02395, payload-02459, payload-02460 |
| `claudeai.admin_request.agent_credential.admin_approved` | 1 |  | 1 | payload-02452 |
| `claudeai.admin_request.agent_credential.admin_dismissed` | 1 |  | 1 | payload-02450 |
| `claudeai.admin_request.agent_credential.connect_clicked` | 1 |  | 1 | payload-02451 |
| `claudeai.admin_request.enable_connector.approved` | 2 | `action`, `failed_count`~, `mcp_server_uuid`~, `request_count`~, `skipped_count`~ | 0 | payload-02392, payload-02393 |
| `claudeai.admin_request.enable_connector.dismissed` | 2 | `blocked`~, `mcp_server_uuid`~, `request_count`~, `source`~ | 0 | payload-01676, payload-02394 |
| `claudeai.admin_request.enable_connector.modal_opened` | 1 | `connector_count`~, `source`~ | 0 | payload-02456 |
| `claudeai.admin_request.enable_connector.see_what_it_does_clicked` | 5 | `entry`, `mcp_server_uuid`~, `source` | 0 | payload-02361, payload-02401, payload-02403, payload-02454, payload-02466 |
| `claudeai.admin_request.join_org.approved` | 2 | `action`, `request_count`~, `request_type`~, `request_types`~, `source`~, `sources`~ | 0 | payload-01605, payload-01606 |
| `claudeai.admin_request.join_org.auto_approve_nudge_accepted` | 1 |  | 0 | payload-02453 |
| `claudeai.admin_request.join_org.auto_approve_nudge_dismissed` | 1 |  | 0 | payload-02465 |
| `claudeai.admin_request.join_org.auto_approve_nudge_shown` | 1 |  | 0 | payload-02455 |
| `claudeai.admin_request.join_org.shown` | 1 | `data`~, `data.request_count`~, `data.source`, `data.user_type` | 0 | payload-02457 |
| `claudeai.admin_request.limit_increase.admin_upgrade_clicked` | 3 | `data`~, `data.action`, `data.source` | 0 | payload-02462, payload-02463, payload-02464 |
| `claudeai.admin_request.limit_increase.member_request_clicked` | 2 | `data`~, `data.scope`~, `data.source`~ | 0 | payload-01587, payload-02961 |
| `claudeai.admin_request.limit_increase.shown` | 3 | `data`~, `data.request_count`~, `data.source`~, `data.user_type` | 0 | payload-01586, payload-02457, payload-02960 |
| `claudeai.admin_request.seat_upgrade.admin_upgrade_clicked` | 3 | `data`~, `data.action`, `data.can_upgrade_without_purchase`~, `data.request_count`~, `data.requester_seat_tier`~, `data.seats_to_purchase`~, `data.selected_tier`~, `data.source`, `data.unassigned_request_count`~, `data.upgrade_count`~ | 0 | payload-02449, payload-02458, payload-02461 |
| `claudeai.admin_request.seat_upgrade.admin_upgrade_completed` | 1 | `data`~, `data.selected_tier`~, `data.source`, `data.total_attempted`~, `data.upgraded_count`~, `data.upgraded_from_unassigned_count`~ | 0 | payload-02448 |
| `claudeai.admin_request.seat_upgrade.member_request_clicked` | 1 | `data`~, `data.seat_tier`~, `data.source`~ | 0 | payload-02962 |
| `claudeai.admin_request.seat_upgrade.purchase_modal_shown` | 1 | `data`~, `data.seats_to_purchase`~, `data.selected_tier`~, `data.source`, `data.upgrade_count`~ | 0 | payload-02447 |
| `claudeai.admin_request.seat_upgrade.shown` | 3 | `data`~, `data.request_count`~, `data.seat_tier`~, `data.source`, `data.user_type` | 0 | payload-01588, payload-02457, payload-02963 |
| `claudeai.admin_settings.analytics_claude_academy.academy_link_clicked` | 1 | `link`~ | 0 | payload-01507 |
| `claudeai.admin_settings.cc_bounty.card_viewed` | 1 | `settings_surface`~ | 0 | payload-01060 |
| `claudeai.admin_settings.cc_bounty.modal_opened` | 2 | `settings_surface`~, `source` | 0 | payload-01061, payload-01062 |
| `claudeai.admin_settings.cc_bounty.nudge_sent` | 2 | `path`, `queued`~ | 0 | payload-01058, payload-01059 |
| `claudeai.admin_settings.claude_science_resources.link_clicked` | 1 | `target`~ | 0 | payload-00665 |
| `claudeai.admin_settings.coral_lantern.confirmed` | 1 |  | 1 | payload-02529 |
| `claudeai.admin_settings.coral_lantern.dismissed` | 1 |  | 1 | payload-02528 |
| `claudeai.admin_settings.coral_lantern.opened` | 1 |  | 1 | payload-02527 |
| `claudeai.admin_settings.cowork_deploy_modal.link_clicked` | 1 | `target`~ | 0 | payload-02415 |
| `claudeai.admin_settings.cowork_deploy_modal.shown` | 1 |  | 0 | payload-02414 |
| `claudeai.admin_settings.cowork_deploy_section.link_clicked` | 1 | `target`~ | 0 | payload-02416 |
| `claudeai.admin_settings.cowork_remote_control_toggle` | 1 | `new_state`~ | 0 | payload-01070 |
| `claudeai.admin_settings.ent_upgrade_preview.clicked` | 1 | `upsell_surface`~ | 0 | payload-01176 |
| `claudeai.admin_settings.ent_upgrade_preview.shown` | 2 | `upsell_surface`~ | 0 | payload-01177, payload-01178 |
| `claudeai.admin_settings.models.changes_discarded` | 1 |  | 1 | payload-02477 |
| `claudeai.admin_settings.models.left_unsaved` | 1 | `page_hidden`~, `save_in_flight`~ | 1 | payload-02478 |
| `claudeai.admin_settings.models.model_updates_launch_toggled` | 1 | `model_id`~, `opted_out` | 0 | payload-02472 |
| `claudeai.admin_settings.models.model_updates_opt_in_clicked` | 1 |  | 0 | payload-02471 |
| `claudeai.admin_settings.models.org_access_changed` | 1 | `blocked_by_roles`~, `blocking_role_count`~, `enabled`~, `model_id`~ | 0 | payload-02474 |
| `claudeai.admin_settings.models.role_access_changed` | 1 | `blocked_by_roles`~, `from_disable_link`~, `granted_role_count`~, `model_id`~ | 0 | payload-02475 |
| `claudeai.admin_settings.models.save_attempted` | 1 | `default_model_changed`~, `org_access_dirty`~, `org_mode_changed`~, `org_models_turned_off`~, `org_models_turned_on`~, `org_row_sent`~, `outcome`~, `role_changed_models`~, `role_rows_failed`~, `role_rows_sent`~, `stopped_before_writes`~, `succeeded`~ | 0 | payload-02476 |
| `claudeai.admin_settings.models.save_blocked_by_roles` | 1 | `blocking_role_count`~, `model_id`~ | 0 | payload-02473 |
| `claudeai.admin_settings.mossy_mochi.changed` | 1 | `enabled`~, `enabled_1`~, `enabled_2`~, `enabled_3`~, `enabled_4`~, `setting`~ | 0 | payload-02375 |
| `claudeai.admin_settings.notifications.action_taken` | 1 | `action`~, `notification_created_at`?~, `notification_first_seen_at`?~, `notification_id`~, `notification_type`~ | 2 | payload-01202 |
| `claudeai.admin_settings.notifications.learn_more_clicked` | 2 | `notification_created_at`?~, `notification_first_seen_at`?~, `notification_id`~, `notification_type` | 2 | payload-00833, payload-01203 |
| `claudeai.admin_settings.notifications.panel_viewed` | 1 | `badge_count`~, `default_tab`~, `requests_count`~, `unviewed_updates_count`~, `updates_count`~ | 0 | payload-02480 |
| `claudeai.admin_settings.role_save.advisory_timeout` | 3 | `check`, `group_size`~, `reason`~, `removed_group_count`~ | 0 | payload-02520, payload-02521, payload-02522 |
| `claudeai.admin_settings.search.no_results` | 2 | `query_length`~, `surface` | 0 | payload-02535, payload-02538 |
| `claudeai.admin_settings.search.opened` | 2 | `surface` | 0 | payload-02537, payload-02540 |
| `claudeai.admin_settings.search.result_selected` | 2 | `anchor`~, `kind`~, `position`~, `query_length`~, `result_count`~, `route`~, `surface` | 0 | payload-02536, payload-02539 |
| `claudeai.admin_setup_checklist.callout.dismissed` | 2 | `callout_id`~, `org_size_bucket`~, `resumed`~, `shown`~, `step_id`~, `via`~ | 1 | payload-00777, payload-00778 |
| `claudeai.admin_setup_checklist.callout.learn_more_clicked` | 2 |  | 2 | payload-00780, payload-00782 |
| `claudeai.admin_setup_checklist.callout.shown` | 2 |  | 2 | payload-00779, payload-00781 |
| `claudeai.admin_setup_checklist.closed` | 1 | `done`~, `org_size_bucket`~, `placement`~, `source`~, `total`~ | 0 | payload-00346 |
| `claudeai.admin_setup_checklist.completed_all` | 1 | `observed`~, `org_size_bucket`~, `total`~ | 0 | payload-00341 |
| `claudeai.admin_setup_checklist.delegate.cancelled` | 2 | `org_size_bucket`~, `source`~, `step_id`~, `via`~ | 0 | payload-00337, payload-00339 |
| `claudeai.admin_setup_checklist.delegate.failed` | 1 | `org_size_bucket`~, `reason`~, `source`~, `step_id`~, `target`~ | 0 | payload-00336 |
| `claudeai.admin_setup_checklist.delegate.opened` | 1 | `org_size_bucket`~, `source`, `step_id`~ | 0 | payload-00349 |
| `claudeai.admin_setup_checklist.delegate.removed` | 1 | `org_size_bucket`~, `step_id`~ | 0 | payload-00350 |
| `claudeai.admin_setup_checklist.delegate.seat_check_unavailable` | 1 | `org_size_bucket`~, `source`~, `step_id`~ | 0 | payload-00338 |
| `claudeai.admin_setup_checklist.delegate.sent` | 1 | `org_size_bucket`~, `source`~, `step_id`~, `target`~ | 0 | payload-00335 |
| `claudeai.admin_setup_checklist.filter.changed` | 1 | `filter`~, `org_size_bucket`~ | 0 | payload-00333 |
| `claudeai.admin_setup_checklist.hidden` | 1 | `done`~, `org_size_bucket`~, `total`~ | 0 | payload-00343 |
| `claudeai.admin_setup_checklist.inline.shown` | 1 | `done`~, `org_size_bucket`~, `total`~ | 0 | payload-00347 |
| `claudeai.admin_setup_checklist.opened` | 1 | `done`~, `org_size_bucket`~, `placement`~, `source`~, `total`~ | 0 | payload-00346 |
| `claudeai.admin_setup_checklist.pill.shown` | 1 | `done`~, `org_size_bucket`~, `total`~ | 0 | payload-00348 |
| `claudeai.admin_setup_checklist.step.completed` | 1 | `completion`~, `observed`~, `org_size_bucket`~, `step_id`~ | 0 | payload-00340 |
| `claudeai.admin_setup_checklist.step.lets_go` | 1 | `completion`~, `org_size_bucket`~, `step_id`~ | 0 | payload-00332 |
| `claudeai.admin_setup_checklist.step.skipped` | 1 | `org_size_bucket`~, `step_id`~ | 0 | payload-00345 |
| `claudeai.admin_setup_checklist.step.unskipped` | 1 | `org_size_bucket`~, `step_id`~ | 0 | payload-00344 |
| `claudeai.admin_setup_checklist.tour.ended` | 1 | `org_size_bucket`~, `shown`~, `step_id`~, `stop`~, `stop_index`~, `stops`~, `via`~ | 0 | payload-00776 |
| `claudeai.admin_setup_checklist.tour.started` | 1 | `org_size_bucket`~, `step_id`~, `stops`~ | 0 | payload-00334 |
| `claudeai.admin_setup_checklist.tour.stop_skipped` | 1 | `org_size_bucket`~, `step_id`~, `stop`~, `stop_index`~, `stops`~ | 0 | payload-00775 |
| `claudeai.admin_setup_checklist.unhidden` | 1 | `done`~, `org_size_bucket`~, `total`~ | 0 | payload-00342 |
| `claudeai.admin_setup_wizard.completed` | 1 |  | 0 | payload-00569 |
| `claudeai.admin_setup_wizard.step_back` | 1 | `step`~ | 0 | payload-00568 |
| `claudeai.admin_setup_wizard.step_continued` | 1 | `step`~ | 0 | payload-00568 |
| `claudeai.admin_setup_wizard.step_skipped` | 1 | `step`~ | 0 | payload-00568 |
| `claudeai.admin_setup_wizard.step_viewed` | 1 | `step`~ | 0 | payload-00567 |
| `claudeai.admin_skills.cscp_created` | 1 |  | 0 | payload-02498 |
| `claudeai.admin_skills.cscp_deleted` | 1 |  | 0 | payload-02499 |
| `claudeai.admin_skills.cscp_tested` | 1 | `kind`~ | 0 | payload-02496 |
| `claudeai.admin_skills.cscp_toggled` | 1 | `new_state`~ | 0 | payload-02497 |
| `claudeai.admin_skills.oinv_access_opened` | 1 | `admin_page`~, `entry`~, `kind`~, `scope`~ | 0 | payload-02505 |
| `claudeai.admin_skills.oinv_filtered` | 1 | `audience`~, `filter`~, `kind`~, `order`~, `page`~, `scope`~ | 0 | payload-02511 |
| `claudeai.admin_skills.oinv_item_tab` | 1 | `tab`~ | 0 | payload-02507 |
| `claudeai.admin_skills.oinv_opened` | 1 | `kind`~, `page`~, `scope`~ | 0 | payload-02509 |
| `claudeai.admin_skills.oinv_scan_findings` | 1 | `verdict`~ | 0 | payload-02506 |
| `claudeai.admin_skills.oinv_viewed` | 1 | `page`~ | 0 | payload-02510 |
| `claudeai.admin_skills.sharing_toggled` | 4 | `new_state`~, `publish_policy`~, `sharing_type` | 0 | payload-02515, payload-02517, payload-02518, payload-02519 |
| `claudeai.admin_skills.sndp_queue_viewed` | 1 | `page`~, `pending_count`~ | 0 | payload-02404 |
| `claudeai.admin_skills.sndp_review.approve_opened` | 1 | `proposed_install_preference`~ | 1 | payload-02408 |
| `claudeai.admin_skills.sndp_review.approved` | 1 | `audience_offered`~, `destination_kind`~, `group_count`~, `install_preference`~, `proposed_install_preference`~, `publish_state`~ | 1 | payload-02405 |
| `claudeai.admin_skills.sndp_review.denied` | 1 |  | 1 | payload-02412 |
| `claudeai.admin_skills.sndp_review.deny_opened` | 1 |  | 1 | payload-02407 |
| `claudeai.admin_skills.sndp_review.duplicate_compared` | 1 | `match_kind`~, `reason`~ | 1 | payload-02410 |
| `claudeai.admin_skills.sndp_review.duplicate_opened` | 1 | `match_kind`~, `position`~, `reason`~ | 1 | payload-02409 |
| `claudeai.admin_skills.sndp_review.files_viewed` | 1 | `entry`~ | 1 | payload-02402 |
| `claudeai.admin_skills.sndp_review.opened` | 1 | `duplicate_hints`~, `scan`~, `status`~, `submission_id`~ | 1 | payload-02406 |
| `claudeai.admin_skills.sndp_review.refused` | 1 | `error_kind`~, `refusal`~, `verb`~ | 1 | payload-02411 |
| `claudeai.admin_spend_limit_banner.clicked` | 1 | `variant`~ | 0 | payload-00381 |
| `claudeai.admin_spend_limit_banner.dismissed` | 1 | `variant`~ | 0 | payload-00382 |
| `claudeai.admin_spend_limit_banner.shown` | 1 | `variant`~ | 0 | payload-00380 |
| `claudeai.admin_usage_billabong.limit_saved` | 1 | `accepted`~, `scope`~ | 1 | payload-02446 |
| `claudeai.admin_usage_billabong.suggestion_used` | 1 | `scope`~ | 1 | payload-02445 |
| `claudeai.admin_usage_keystone.abandoned` | 1 | `confirm_cancelled`~, `had_blocking_preview`~, `last_would_block_bucket`~, `previews_rendered`~, `scope_type`~ | 0 | payload-02444 |
| `claudeai.admin_usage_keystone.confirm` | 1 | `blocked_share_bucket`~, `result`~, `scope_type`~, `would_block_bucket`~ | 0 | payload-02442 |
| `claudeai.admin_usage_keystone.saved` | 1 | `cap_minor_at_first_blocking_preview`~, `confirm`~, `currency`~, `current_cap_minor`~, `decision_changed`~, `direction`~, `first_edited_cap_minor`~, `previews_rendered`~, `save_label`~, `saved_cap_minor`~, `scope_type`~, `would_block_bucket_at_saved`~ | 0 | payload-02443 |
| `claudeai.admin_usage_keystone.shown` | 1 | `blocked_share_bucket`~, `direction`~, `preview_state`~, `scope_type`~, `top_active_bucket`~, `trigger`~, `would_block_bucket`~ | 0 | payload-02441 |
| `claudeai.ai_fluency.report.failed` | 1 | `elapsed_ms`~, `is_parse_error`~, `phase`~ | 0 | payload-02127 |
| `claudeai.ai_fluency.report.generated` | 1 | `cc_count`~, `chat_count`~, `cowork_count`~, `features_on_cc`~, `features_on_chat`~, `features_on_cowork`~, `parse_ms`~, `prefetch_ms`~, `stream_ms`~, `total_ms`~ | 0 | payload-02126 |
| `claudeai.amber_lynx_glade.fired` | 1 | `data`~, `data.channels`~ | 0 | payload-03000 |
| `claudeai.amber_quill.people.removed` | 1 | `arm`~ | 0 | payload-01298 |
| `claudeai.amber_quill.people.row_shown` | 1 | `arm`~, `mode`~ | 0 | payload-01296 |
| `claudeai.amber_quill.people.sent` | 1 | `admin_request_count`~, `arm`~, `from_suggested_count`~, `invite_count`~, `member_count`~ | 0 | payload-01297 |
| `claudeai.amber_quill.share.opened` | 1 | `artifact_uuid_hash`~, `source`~ | 0 | payload-00565 |
| `claudeai.amber_reed.menu_shown` | 1 |  | 0 | payload-03196 |
| `claudeai.amber_reed.offer_capped` | 2 | `arm`~ | 0 | payload-03195, payload-03198 |
| `claudeai.amber_reed.offer_dismissed` | 1 | `arm`~, `engaged`~, `reason` | 0 | payload-03197 |
| `claudeai.amber_wren.attached` | 1 | `conversation_uuid`~ | 0 | payload-01604 |
| `claudeai.analytics.chat.card_interacted` | 1 | `action`~, `card_kind`~ | 0 | payload-00390 |
| `claudeai.analytics.chat.card_rendered` | 1 | `card_kind`~, `is_collapsed`~, `is_empty`~, `is_envelope_rendering`~, `is_error`~, `is_truncated`~, `row_count`~ | 0 | payload-00391 |
| `claudeai.analytics.chat.conversation_started` | 2 | `is_envelope_rendering`~, `is_landing`~ | 0 | payload-01506, payload-01570 |
| `claudeai.analytics.chat.template_chip_clicked` | 2 | `action`, `category`~, `is_envelope_rendering`~, `pill_id`~ | 0 | payload-01505, payload-01569 |
| `claudeai.analytics.dashboard.export_clicked` | 5 | `chat_app`~, `dashboard_surface`~, `export_type`, `period`~, `table`~ | 0 | payload-01498, payload-01520, payload-01521, payload-01565, payload-01567 |
| `claudeai.analytics.dashboard.export_downloaded` | 4 | `dashboard_surface`~, `export_type`, `period`~, `table`~ | 0 | payload-01499, payload-01522, payload-01566, payload-01568 |
| `claudeai.analytics.dashboard.see_all_opened` | 1 | `dashboard_surface`~, `table`~ | 0 | payload-01504 |
| `claudeai.analytics.dashboard.spend_card_viewed` | 1 | `basis`~, `card`, `dashboard_surface`~, `period`~ | 0 | payload-01573 |
| `claudeai.analytics.dashboard.time_range_changed` | 3 | `dashboard_surface`~, `preset`~, `time_range_days`~ | 0 | payload-01497, payload-01503, payload-01615 |
| `claudeai.app_install_banner.clicked` | 1 | `experiment_arm`?~, `platform`~, `variant`~ | 1 | payload-02910 |
| `claudeai.app_install_banner.dismissed` | 1 | `experiment_arm`?~, `platform`~, `variant`~ | 1 | payload-02909 |
| `claudeai.app_install_banner.displayed` | 1 | `experiment_arm`?~, `platform`~, `variant`~ | 1 | payload-02908 |
| `claudeai.artifact.client_rebuilt_over_record` | 1 | `artifact_type`~, `chat_host`~, `is_latest_version`~, `message_uuid`~, `reason`~, `record_percent_of_shown_length`~ | 0 | payload-01794 |
| `claudeai.artifact.comment.sent_to_claude` | 4 | `destination`~, `summon_source`~ | 0 | payload-00531, payload-02063, payload-02065, payload-02066 |
| `claudeai.artifact.comment.summon_handoff_settled` | 2 | `destination`~, `outcome`~, `reason`?~, `rescue_outcome`~, `rescue_step`~, `self_filter_class`~, `session_kind`?~, `told`~, `turn`?~ | 3 | payload-00538, payload-02064 |
| `claudeai.artifact.comment.summon_turn_ended` | 1 | `end`~, `surface`~ | 0 | payload-01200 |
| `claudeai.artifact.comment.summon_waiting_opened` | 1 | `reveal`~, `surface`~, `via`~ | 0 | payload-01201 |
| `claudeai.artifact.comment.summon_waiting_shown` | 1 | `surface`~ | 0 | payload-01199 |
| `claudeai.artifact.copied` | 2 | `artifact_type`~, `char_count`~, `format`, `has_citations`~, `message_uuid`~ | 0 | payload-01800, payload-01801 |
| `claudeai.artifact.copied_as_image` | 1 | `artifact_type`~, `message_uuid`~ | 0 | payload-01802 |
| `claudeai.artifact.downloaded` | 2 | `artifact_type`~, `format`, `has_citations`~, `message_uuid`~ | 0 | payload-01803, payload-01804 |
| `claudeai.artifact.dwell` | 1 | `artifact_type`~, `capped`~, `dwell_ms`~, `message_uuid`~ | 0 | payload-01796 |
| `claudeai.artifact.export_feedback.sent` | 1 | `artifact_uuid_hash`~, `conversation_uuid`~, `format`~, `message_uuid`~, `rating`~, `reason_key`~ | 0 | payload-00530 |
| `claudeai.artifact.images_placed` | 1 | `message_uuid`~ | 1 | payload-01431 |
| `claudeai.artifacts.execution.error` | 1 | `artifact_version_uuid`~, `error_type`~, `source`~ | 0 | payload-01799 |
| `claudeai.artifacts.plan_banner.clicked` | 1 | `from`?~ | 1 | payload-00480 |
| `claudeai.artifacts.plan_banner.dismissed` | 1 | `from`?~ | 1 | payload-00481 |
| `claudeai.artifacts.plan_banner.shown` | 1 | `from`?~ | 1 | payload-00479 |
| `claudeai.billing.annual_switch_offer.cta_clicked` | 1 | `arm`~ | 0 | payload-01465 |
| `claudeai.billing.annual_switch_offer.dismissed` | 1 | `arm`~ | 0 | payload-01466 |
| `claudeai.billing.annual_switch_offer.eligible` | 1 | `arm`~, `ms_since_mount`~ | 0 | payload-01458 |
| `claudeai.billing.annual_switch_offer.unresolved_at_dismiss` | 1 | `ms_since_mount`~ | 0 | payload-01459 |
| `claudeai.billing.csfc_payment_tip.opened` | 1 |  | 0 | payload-01158 |
| `claudeai.billing.invoices.pdf_opened` | 1 | `invoice_status`~ | 0 | payload-01834 |
| `claudeai.billing.overdue_invoice.add_card_opened` | 1 |  | 0 | payload-01870 |
| `claudeai.billing.overdue_invoice.details_opened` | 2 | `from` | 0 | payload-01869, payload-01887 |
| `claudeai.billing.overdue_invoice.hosted_page_opened` | 2 | `from`~ | 0 | payload-01861, payload-01871 |
| `claudeai.billing.overdue_invoice.pay_opened` | 1 | `billing_reason`~, `entry_point`~, `plan`~, `subscription_status`~ | 0 | payload-01886 |
| `claudeai.billing.overdue_invoice.pay_result` | 1 | `outcome`~, `replay`?~ | 2 | payload-01862 |
| `claudeai.billing.overdue_invoice.pay_submitted` | 1 | `card`~, `make_default`~, `replay`?~ | 1 | payload-01863 |
| `claudeai.billing.overdue_invoice.three_ds_result` | 4 | `kind`, `outcome`~ | 0 | payload-01864, payload-01865, payload-01866, payload-01867 |
| `claudeai.billing.overdue_invoice.view_invoice_clicked` | 1 |  | 0 | payload-01868 |
| `claudeai.billing.payment_methods.add_opened` | 2 |  | 0 | payload-00824, payload-01381 |
| `claudeai.billing.payment_methods.add_succeeded` | 2 | `set_as_default`~, `via_redirect`~ | 0 | payload-00825, payload-01821 |
| `claudeai.billing.payment_methods.removed` | 2 | `outcome`~ | 0 | payload-00822, payload-00823 |
| `claudeai.billing.payment_methods.set_default` | 2 | `outcome`, `source`~ | 0 | payload-00820, payload-00821 |
| `claudeai.billing.post_checkout_landing.eligible` | 1 | `arm`~, `ms_since_mount`~, `product`~, `tier_change`~ | 0 | payload-01460 |
| `claudeai.billing.post_checkout_landing.notice_cta_clicked` | 1 | `arm`, `product`~, `tier_change`~ | 0 | payload-01818 |
| `claudeai.billing.post_checkout_landing.notice_dismissed` | 1 | `arm`, `product`~, `tier_change`~ | 0 | payload-01819 |
| `claudeai.billing.post_checkout_landing.notice_shown` | 1 | `arm`, `product`~, `renewal_shown`~, `tier_change`~ | 0 | payload-01820 |
| `claudeai.billing.post_checkout_landing.unresolved_at_dismiss` | 1 | `ms_since_mount`~, `product`~, `reason`~ | 0 | payload-01461 |
| `claudeai.billing.transition_credit_turned_off` | 1 | `outcome`~ | 0 | payload-01838 |
| `claudeai.billing.transition_credit_turned_on` | 1 | `outcome`~ | 0 | payload-01839 |
| `claudeai.brass_falcon.coachmark_dismissed` | 1 |  | 1 | payload-01903 |
| `claudeai.brass_falcon.coachmark_shown` | 1 |  | 1 | payload-01902 |
| `claudeai.brass_falcon.edit_opened` | 1 | `content_length`~, `ephemeral`~, `load_ms`~ | 1 | payload-00030 |
| `claudeai.brass_falcon.edited` | 1 | `change_count`~, `content_length`~, `ephemeral`~ | 1 | payload-00037 |
| `claudeai.brass_falcon.format_applied` | 1 | `action`~, `source`~ | 1 | payload-00038 |
| `claudeai.brass_falcon.load_failed` | 1 | `error_kind`~, `mode` | 1 | payload-00031 |
| `claudeai.brass_falcon.merge_failed` | 3 | `content_length`~, `ephemeral`~, `error_kind`~ | 3 | payload-00033, payload-00034, payload-00035 |
| `claudeai.brass_falcon.save_failed` | 1 | `content_length`~, `ephemeral`~, `error_kind`~, `trigger`~ | 1 | payload-00036 |
| `claudeai.bright_fountain.clicked` | 1 | `arm` | 0 | payload-01190 |
| `claudeai.bright_fountain.create_failed` | 1 | `arm`~, `status_code`~ | 0 | payload-01179 |
| `claudeai.bright_fountain.created` | 1 | `arm`~, `fork_conversation_uuid`~, `in_project`~, `message_count`~, `notified_sharer`~ | 0 | payload-01180 |
| `claudeai.bright_fountain.exposed` | 1 | `arm`~ | 0 | payload-01191 |
| `claudeai.bright_fountain.first_message_sent` | 1 | `arm`, `fork_conversation_uuid`~ | 0 | payload-01673 |
| `claudeai.bright_fountain.submitted` | 1 | `arm`, `has_attachments`~ | 0 | payload-00107 |
| `claudeai.buy_credits_modal.switch_models` | 1 | `target_model`~ | 0 | payload-00701 |
| `claudeai.buying_agent.checkout_cta_clicked` | 3 | `billing_interval`~, `destination`, `is_upgrade`~, `plan`~, `premium_seats`~, `seats`~, `session_id`~ | 1 | payload-01032, payload-01037, payload-01038 |
| `claudeai.buying_agent.conversation_started` | 2 | `entry`, `entry_path`~, `is_embedded`~, `session_id`~ | 2 | payload-01034, payload-01035 |
| `claudeai.buying_agent.logged_out_login_clicked` | 1 |  | 1 | payload-01044 |
| `claudeai.buying_agent.logged_out_viewed` | 1 |  | 1 | payload-01043 |
| `claudeai.buying_agent.outcome_shown` | 3 | `followup`~, `outcome`, `reason`~, `session_id`~ | 2 | payload-01033, payload-01036, payload-01040 |
| `claudeai.buying_agent.widget_answered` | 3 | `question_count`~, `seats`~, `session_id`~, `source`~, `team`~, `tool`~ | 0 | payload-01039, payload-01041, payload-01042 |
| `claudeai.buzzing_reef.auto_reload` | 1 | `build_id`~, `other_build`~, `outcome`~, `reason`~ | 0 | payload-01053 |
| `claudeai.buzzing_reef.card_seen` | 1 | `ms_since_open`~, `position`~, `section`~ | 0 | payload-01048 |
| `claudeai.buzzing_reef.cards_done_clicked` | 1 |  | 0 | payload-01055 |
| `claudeai.buzzing_reef.help_closed` | 1 |  | 0 | payload-01057 |
| `claudeai.buzzing_reef.help_opened` | 1 | `after_failed_connect`~ | 0 | payload-01056 |
| `claudeai.buzzing_reef.load_failed` | 1 | `after_auto_reload`~, `build_id`~, `delivery`~, `other_build`~ | 0 | payload-01050 |
| `claudeai.buzzing_reef.nav_row_shown` | 1 | `location`~ | 0 | payload-02864 |
| `claudeai.buzzing_reef.no_slack_asks_dismissed` | 1 | `already_resolved_count`~, `failed_count`~, `request_count`~, `result`~ | 0 | payload-02357 |
| `claudeai.buzzing_reef.no_slack_asks_row_action` | 1 | `action`~, `requester_count`~ | 0 | payload-02363 |
| `claudeai.buzzing_reef.no_slack_asks_row_shown` | 1 | `requester_count`~ | 0 | payload-02360 |
| `claudeai.buzzing_reef.rail_action` | 1 |  | 1 | payload-01045 |
| `claudeai.buzzing_reef.rail_viewed` | 1 | `channels_count`~, `details_withheld`~, `org_wide`~, `rules_count`~, `runbooks_count`?~, `skills_count`~, `tools_count`~, `viewer_can_manage`~, `workspaces_count`~ | 1 | payload-01054 |
| `claudeai.buzzing_reef.setup_left` | 1 | `channels_seen`~, `chat_open`~, `max_scroll_pct`~, `seconds_on_page`~ | 1 | payload-01049 |
| `claudeai.buzzing_reef.setup_progress_viewed` | 1 | `complete`~, `done`~, `steps_done`~, `total`~ | 0 | payload-01051 |
| `claudeai.buzzing_reef.setup_step_reached` | 1 | `complete`~, `done`~, `step`~, `total`~ | 0 | payload-01052 |
| `claudeai.buzzing_reef.viewed` | 2 | `delivery`~, `entry_block`?~, `has_bundle`~, `state`~ | 3 | payload-01046, payload-01047 |
| `claudeai.c3.waiting_notification` | 1 |  | 1 | payload-00140 |
| `claudeai.c4excel_chat_banner_upsell.cta_clicked` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03088 |
| `claudeai.c4excel_chat_banner_upsell.dismissed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03089 |
| `claudeai.c4excel_chat_banner_upsell.displayed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03087 |
| `claudeai.c4ppt_chat_banner_upsell.cta_clicked` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03091 |
| `claudeai.c4ppt_chat_banner_upsell.dismissed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03092 |
| `claudeai.c4ppt_chat_banner_upsell.displayed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03090 |
| `claudeai.c4word_chat_banner_upsell.cta_clicked` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03094 |
| `claudeai.c4word_chat_banner_upsell.dismissed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03095 |
| `claudeai.c4word_chat_banner_upsell.displayed` | 1 | `presentation`~, `surface`~, `trigger_type`~ | 0 | payload-03093 |
| `claudeai.cai_ancient_oasis.clicked` | 1 | `carried`~ | 0 | payload-00277 |
| `claudeai.cai_ancient_oasis.seen` | 1 | `reveal`~ | 0 | payload-00275 |
| `claudeai.cai_ancient_oasis.shown` | 1 |  | 0 | payload-00276 |
| `claudeai.cai_effervescent_fern.refresh` | 1 | `conversation_uuid`~, `outcome`~, `probe_ms`~, `reason`~, `trigger`~ | 0 | payload-00633 |
| `claudeai.cai_effervescent_fern.send_hold` | 1 | `conversation_uuid`~, `held_ms`~, `release`~ | 0 | payload-00634 |
| `claudeai.cai_effervescent_fern.send_settle` | 1 | `conversation_uuid`~, `outcome`~, `waited_ms`~ | 0 | payload-00635 |
| `claudeai.cai_fizzy_bonbon.connect_clicked` | 2 | `app`~, `connect_all_count`?~, `connector_kind`~ | 1 | payload-01205, payload-01206 |
| `claudeai.cai_fizzy_bonbon.shown` | 1 | `actionable_connector_count`~, `ask_admin_connector_count`~, `listed_connector_count`~, `missing_connector_count`~ | 0 | payload-01204 |
| `claudeai.cai_flickering_frost.shown` | 1 | `kind`~, `placement`~ | 0 | payload-00909 |
| `claudeai.cai_giggly_snowglobe.exported` | 1 | `file_count`~ | 0 | payload-01009 |
| `claudeai.cai_groovy_gizmo.clicked` | 1 |  | 1 | payload-00364 |
| `claudeai.cai_groovy_gizmo.dismissed` | 1 |  | 1 | payload-00365 |
| `claudeai.cai_groovy_gizmo.filter_applied` | 3 | `source` | 0 | payload-02531, payload-02532, payload-02533 |
| `claudeai.cai_groovy_gizmo.raise_opened` | 1 | `source` | 0 | payload-02530 |
| `claudeai.cai_groovy_gizmo.shown` | 1 |  | 1 | payload-00363 |
| `claudeai.cai_iridescent_cupcake.settled` | 1 | `data`~, `data.outcome`~ | 0 | payload-01163 |
| `claudeai.cai_iridescent_cupcake.shown` | 1 |  | 0 | payload-01162 |
| `claudeai.cai_luminous_kite.settled` | 1 | `data`~, `data.not_listed`~, `data.outcome`~ | 0 | payload-00922 |
| `claudeai.cai_luminous_kite.started` | 1 |  | 0 | payload-00921 |
| `claudeai.cai_melodic_pizza.clicked` | 2 | `action`, `file_extension`~, `menu_surface`~ | 0 | payload-00134, payload-00273 |
| `claudeai.cai_melodic_pizza.resolved` | 1 | `menu_surface`~, `outcome`~ | 0 | payload-00274 |
| `claudeai.cai_polished_river.clicked` | 5 | `action`~, `connector`~, `from` | 5 | payload-00046, payload-00048, payload-00050, payload-00051, payload-00052 |
| `claudeai.cai_polished_river.menu_opened` | 1 | `from`~ | 1 | payload-00044 |
| `claudeai.cai_polished_river.released` | 1 | `basis`~, `hold_ms`~, `reason`~, `released_to`~ | 1 | payload-00042 |
| `claudeai.cai_polished_river.resolved` | 1 | `connector`~, `outcome`~ | 1 | payload-00049 |
| `claudeai.cai_polished_river.resumed` | 1 | `connector`~, `outcome`~ | 1 | payload-00043 |
| `claudeai.cai_polished_river.shown` | 1 | `basis`~, `hold_ms`~, `providers`~ | 1 | payload-00047 |
| `claudeai.cai_polished_river.tip_shown` | 1 |  | 1 | payload-00045 |
| `claudeai.cai_precious_crystal.clicked` | 1 | `connect_surface`~, `source`~ | 0 | payload-00262 |
| `claudeai.cai_precious_crystal.connect_clicked` | 1 | `action`, `source`~ | 0 | payload-01947 |
| `claudeai.cai_precious_crystal.connect_resolved` | 1 | `outcome`~, `source`~ | 0 | payload-01948 |
| `claudeai.cai_shimmying_mochi.accepted` | 1 |  | 1 | payload-00611 |
| `claudeai.cai_shimmying_mochi.dismissed` | 1 |  | 1 | payload-00613 |
| `claudeai.cai_shimmying_mochi.ignored` | 1 |  | 1 | payload-00615 |
| `claudeai.cai_shimmying_mochi.matched` | 1 | `composer_mode`~, `match_kind`~, `match_tier`~, `redacted_url`~, `remedy`~, `uuid`~ | 0 | payload-03153 |
| `claudeai.cai_shimmying_mochi.resolved` | 1 | `outcome`~, `remedy` | 1 | payload-00617 |
| `claudeai.cai_shimmying_mochi.shown` | 1 |  | 1 | payload-00609 |
| `claudeai.cai_silly_tide.tile_viewed` | 1 |  | 0 | payload-01574 |
| `claudeai.cai_wild_dawn.accepted` | 1 | `action`~ | 1 | payload-00610 |
| `claudeai.cai_wild_dawn.dismissed` | 1 |  | 1 | payload-00612 |
| `claudeai.cai_wild_dawn.ignored` | 1 |  | 1 | payload-00614 |
| `claudeai.cai_wild_dawn.matched` | 1 |  | 1 | payload-00618 |
| `claudeai.cai_wild_dawn.resolved` | 1 | `outcome`~ | 1 | payload-00616 |
| `claudeai.cai_wild_dawn.shown` | 1 |  | 1 | payload-00608 |
| `claudeai.card_list.cta_clicked` | 1 | `action_type`~, `analytics_id`~, `button_index`~, `platform`~, `tool_name`~ | 0 | payload-02124 |
| `claudeai.card_list.viewed` | 1 | `analytics_ids`~, `card_count`~, `display_type`~, `tool_name`~ | 0 | payload-02125 |
| `claudeai.cedar_chute.channel_selected` | 1 |  | 0 | payload-03281 |
| `claudeai.cedar_chute.draft_edited` | 1 |  | 0 | payload-00658 |
| `claudeai.cedar_chute.menu_shown` | 1 | `row_count`~ | 0 | payload-03279 |
| `claudeai.cedar_chute.offer_accepted` | 1 |  | 0 | payload-00656 |
| `claudeai.cedar_chute.offer_dismissed` | 1 |  | 0 | payload-00659 |
| `claudeai.cedar_chute.offer_shown` | 1 |  | 0 | payload-00655 |
| `claudeai.cedar_chute.post_delivered` | 1 | `connector_changed`?~, `indeterminate`?~ | 2 | payload-00657 |
| `claudeai.cedar_chute.post_failed` | 1 | `connector_changed`?~, `indeterminate`?~ | 2 | payload-00657 |
| `claudeai.cedar_chute.search_unreadable` | 1 | `reason`~ | 0 | payload-03280 |
| `claudeai.cedar_ember.clicked` | 1 | `data`~ | 0 | payload-01913 |
| `claudeai.cedar_ember.confirmed` | 1 | `data`~, `data.percent_used_max`~ | 1 | payload-01914 |
| `claudeai.cedar_ember.result` | 1 | `data`~, `data.at_limit`~, `data.cleared`~, `data.early_use`~, `data.entry`?~, `data.gives_back`~, `data.grant_id`~, `data.is_retry`~, `data.latency_ms`~, `data.limit_type`~, `data.link_limit_type`?~, `data.percent_used_max`~, `data.reason`~, `data.recovered`~, `data.reset_landed`~, `data.resets_left`~, `data.result`~, `data.source`~, `data.ui_version`?~ | 1 | payload-01911 |
| `claudeai.cedar_ember.shown` | 1 | `data`~, `data.at_limit`~, `data.billing_path`~, `data.billing_period`~, `data.credits_band`~, `data.early_use`~, `data.extra_usage_state`~, `data.gives_back`~, `data.grant_id`~, `data.grants`~, `data.hours_until_reset`~, `data.layout_version`~, `data.limit_type`~, `data.limit_types`~, `data.notify_card`?~, `data.offered`~, `data.resets_left`~, `data.source`, `data.surface`~, `data.tenure_bucket`~, `data.tier`~, `data.ui_version`?~ | 1 | payload-01912 |
| `claudeai.cedar_ember.wall_link_clicked` | 1 | `data`~, `data.credits_band`~, `data.extra_usage_state`~, `data.gives_back`~, `data.grant_id`~, `data.grants`~, `data.hours_until_reset`~, `data.layout_version`~, `data.limit_type`~, `data.limit_types`~, `data.notify_card`~, `data.resets_left`~, `data.source`, `data.surface`~, `data.tenure_bucket`~, `data.tier`~, `data.ui_version`~ | 0 | payload-01915 |
| `claudeai.cedar_wren.dismissed` | 2 | `reason` | 2 | payload-01019, payload-01020 |
| `claudeai.cedar_wren.opened` | 1 | `conversation_uuid`~, `created`~, `with_page`~ | 1 | payload-01018 |
| `claudeai.cedar_wren.shown` | 1 |  | 1 | payload-01017 |
| `claudeai.certification.billing_owed_group_shown` | 1 | `billing_owed_row_count`~ | 0 | payload-01125 |
| `claudeai.certification.page_load_no_identifier` | 1 |  | 1 | payload-01124 |
| `claudeai.cerulean_ibex_meadow.cta_clicked` | 2 | `data`~, `data.arm`~, `data.cta`~, `data.surface`~ | 0 | payload-01916, payload-01917 |
| `claudeai.cerulean_ibex_meadow.cta_result` | 1 | `data`~, `data.ok`~, `data.surface`~ | 0 | payload-02991 |
| `claudeai.cerulean_ibex_meadow.shown` | 1 | `data`~, `data.arm`~, `data.days_since_first_paid`~, `data.eligible`~, `data.limit_type`~, `data.surface`~, `data.tier`~ | 0 | payload-02990 |
| `claudeai.chat.body_not_painted` | 2 | `chat_host`~, `data_hub_ready`~, `desktop_app`~, `hidden_at_open`~, `hidden_since_open`~, `host`~, `ms_since_open`~, `ms_since_visible`~ | 2 | payload-01387, payload-01393 |
| `claudeai.chat.body_unhidden_by_backstop` | 1 | `desktop_app`~, `drawer_maximized`~, `drawer_open`~, `host`~, `narrow_overlay`~, `peeking`~, `visibility_state`~ | 0 | payload-01391 |
| `claudeai.chat.capability_tip.clicked` | 1 |  | 2 | payload-00351 |
| `claudeai.chat.capability_tip.dismissed` | 1 |  | 1 | payload-00353 |
| `claudeai.chat.capability_tip.shown` | 1 | `cta_shown`~ | 1 | payload-00352 |
| `claudeai.chat.draft.attachments_stitched` | 1 | `missing_count`~, `stitched_count`~ | 0 | payload-02787 |
| `claudeai.chat.draft.restored` | 1 | `attachment_count`~, `attachment_placeholder_count`~, `draft_matches_mirror_draft`~, `file_count`~, `is_plain_single_paragraph`~, `queue_depth`~, `text_bytes_bucket`~, `text_starts_with_slash`~ | 0 | payload-02786 |
| `claudeai.chat.draft.write_failed` | 1 | `error_name`~ | 0 | payload-02785 |
| `claudeai.chat.empty_pane_unmaximized` | 1 |  | 1 | payload-01389 |
| `claudeai.chat.file_upload.added` | 1 |  | 1 | payload-02784 |
| `claudeai.chat.file_upload.rejected` | 1 | `accepts_any_file_type`?~, `cap_bytes`?~, `chat_kind`?~, `file_count`~, `file_extensions`?~, `new_session_cap_bytes`?~, `reason`~ | 5 | payload-03002 |
| `claudeai.chat.fortnight.file_card_taken` | 1 | `action`~, `card_age_bucket`~, `card_row_source`~, `conversation_uuid`~, `version_gt_1`~ | 0 | payload-01221 |
| `claudeai.chat.fortnight.new_chat_after_viewing_other` | 1 | `minutes_since_view_bucket`?~, `new_conversation_uuid`~, `previous_chat_age_bucket`~, `previous_conversation_uuid`?~, `within_5min`~ | 2 | payload-01225 |
| `claudeai.chat.fortnight.paste_matched_prior_output` | 1 | `conversation_uuid`~, `paste_size_bucket`~, `score_bucket`~, `source`~, `source_chat_age_bucket`~ | 0 | payload-01222 |
| `claudeai.chat.fortnight.repeat_upload` | 1 | `composer`~, `conversation_uuid`?~, `days_since_first_bucket`?~, `repeat`~, `via`~ | 2 | payload-01224 |
| `claudeai.chat.fortnight.turn_ended` | 1 | `conversation_age_bucket`~, `conversation_uuid`~, `ends_in_question`~, `has_focus`~, `message_uuid`~, `turn_index`~, `visibility_state`~ | 0 | payload-01223 |
| `claudeai.chat.growth_line_sa.clicked` | 2 | `method`~, `time_to_click_ms`~ | 2 | payload-00602, payload-00603 |
| `claudeai.chat.growth_line_sa.dismissed` | 1 |  | 1 | payload-00604 |
| `claudeai.chat.growth_line_sa.qualified` | 1 | `conversation_uuid`~, `message_uuid`~, `neighbour_surfaces_changed`~ | 0 | payload-01210 |
| `claudeai.chat.growth_line_sa.shown` | 1 |  | 1 | payload-00601 |
| `claudeai.chat.growth_prompts.eligible` | 1 | `conversation_uuid`~, `first_prompt`~, `message_uuid`~, `prompts`~ | 0 | payload-03144 |
| `claudeai.chat.message_queue.auto_sent` | 2 | `queue_wait_ms`~ | 2 | payload-02930, payload-02944 |
| `claudeai.chat.message_queue.cancelled` | 1 | `queue_depth`~ | 0 | payload-02934 |
| `claudeai.chat.message_queue.capped` | 2 |  | 0 | payload-02928, payload-02932 |
| `claudeai.chat.message_queue.discarded` | 1 | `queue_depth`~ | 0 | payload-02937 |
| `claudeai.chat.message_queue.folder_wait_timed_out` | 1 | `queue_depth`~ | 0 | payload-02940 |
| `claudeai.chat.message_queue.queued` | 3 |  | 3 | payload-02929, payload-02931, payload-02933 |
| `claudeai.chat.message_queue.requeued` | 1 | `reason`~ | 0 | payload-02943 |
| `claudeai.chat.message_queue.returned_to_editor` | 6 | `queue_depth`~, `reason`~ | 0 | payload-02935, payload-02936, payload-02938, payload-02939, payload-02941, payload-02942 |
| `claudeai.chat.next_step_row.clicked` | 1 | `method`~, `position`~, `time_to_click_ms`~ | 1 | payload-02601 |
| `claudeai.chat.next_step_row.dismissed` | 1 |  | 1 | payload-02602 |
| `claudeai.chat.next_step_row.shown` | 1 |  | 1 | payload-02600 |
| `claudeai.chat.paper_finch.clicked` | 1 | `claude_doc`~, `conversation_uuid`~, `message_uuid`~, `route`~ | 0 | payload-01940 |
| `claudeai.chat.paper_finch.shown` | 1 | `claude_doc`~, `conversation_uuid`~, `message_uuid`~, `route`~ | 0 | payload-01939 |
| `claudeai.chat.popout.closed` | 1 | `duration_ms`~, `reason`~ | 0 | payload-02154 |
| `claudeai.chat.popout.opened` | 1 | `entry_point`~ | 0 | payload-02153 |
| `claudeai.chat.sync_message_loss` | 5 | `conversation_uuid`~, `current_last_uuid`~, `current_path_count`~, `new_last_uuid`~, `new_path_count`~, `new_tree_count`~, `prev_tree_count`~, `reason`, `source`?~, `sync_action`~, `tree_lost_count` | 3 | payload-01434, payload-03021, payload-03022, payload-03023, payload-03024 |
| `claudeai.chat.tool_approval.decided` | 1 | `decision`~, `render_to_decision_ms`?~ | 3 | payload-00282 |
| `claudeai.chat.tool_approval.notify_prompt_clicked` | 1 |  | 2 | payload-00284 |
| `claudeai.chat.tool_approval.notify_prompt_shown` | 1 |  | 2 | payload-00283 |
| `claudeai.chat.tool_approval.removed` | 1 | `cause`~, `render_to_remove_ms`~ | 1 | payload-00280 |
| `claudeai.chat.tool_approval.rendered` | 1 |  | 1 | payload-00281 |
| `claudeai.chats_page.row_opened` | 1 |  | 1 | payload-01899 |
| `claudeai.cheeky_cosmos.mode_changed` | 1 | `conversation_uuid`~, `mode`~ | 0 | payload-01421 |
| `claudeai.cic_sidepanel.context_sent` | 1 | `backend`, `conversation_uuid`~, `first_in_panel`~, `tab_line`~, `tab_line_cut`~ | 0 | payload-00727 |
| `claudeai.cic_sidepanel.input_ready` | 1 | `ant_build`~ | 1 | payload-02758 |
| `claudeai.cic_sidepanel.mode_decided` | 1 | `ant_build`~, `ms_since_load`~, `tab_known`~ | 1 | payload-02757 |
| `claudeai.cic_sidepanel.site_card_decided` | 1 | `backend`~, `conversation_uuid`?~, `decision`~, `standing_grant_allowed`~, `tool_name`~, `wait_ms`?~ | 2 | payload-00755 |
| `claudeai.cic_sidepanel.static_composer` | 1 | `box_shown`~, `composer`~, `composer_usable_ms`~, `extension_version`~, `hidden_at_load`~, `panel_document`~, `panel_load_id`~, `second_boot`~ | 4 | payload-01616 |
| `claudeai.cic_sidepanel.thimble.cleared` | 1 | `cause`~, `found`~ | 0 | payload-00753 |
| `claudeai.cic_sidepanel.thimble.copy_failed` | 1 | `reason`~ | 0 | payload-00754 |
| `claudeai.cic_sidepanel.tool_call_end` | 1 | `backend`~, `bridge_request_id`?~, `card_wait_ms`?~, `conversation_uuid`?~, `duration_ms`~, `outcome`~, `permission_mode`~, `reason`?~, `server_consented`?~, `tool_name`~ | 5 | payload-00756 |
| `claudeai.claude_code_dashboard.coding_boost_view_changed` | 1 | `view`~ | 0 | payload-01510 |
| `claudeai.claude_code_dashboard.exported` | 1 |  | 0 | payload-01513 |
| `claudeai.claude_code_dashboard.github_app_link_clicked` | 1 |  | 0 | payload-01512 |
| `claudeai.claude_code_dashboard.leaderboard_view_changed` | 1 | `view`~ | 0 | payload-01511 |
| `claudeai.claude_code_dashboard.page_viewed` | 1 |  | 0 | payload-01508 |
| `claudeai.claude_code_dashboard.time_range_changed` | 2 | `end_date`~, `start_date`~, `time_period`~ | 0 | payload-01509, payload-01519 |
| `claudeai.claude_code_dashboard_legacy.exported` | 1 |  | 0 | payload-01518 |
| `claudeai.claude_code_dashboard_legacy.month_changed` | 1 | `month`~, `year`~ | 0 | payload-01515 |
| `claudeai.claude_code_dashboard_legacy.page_viewed` | 1 |  | 0 | payload-01514 |
| `claudeai.claude_code_dashboard_legacy.table_page_changed` | 1 | `page`~ | 0 | payload-01516 |
| `claudeai.claude_code_dashboard_legacy.table_searched` | 1 | `search_query_length`~ | 0 | payload-01517 |
| `claudeai.claude_code_install_nudge.dismissed` | 1 |  | 1 | payload-03103 |
| `claudeai.claude_code_install_nudge.displayed` | 1 |  | 1 | payload-03100 |
| `claudeai.claude_code_install_nudge.install_clicked` | 1 | `surface`~ | 2 | payload-03101 |
| `claudeai.claude_code_install_nudge.install_menu_opened` | 1 |  | 1 | payload-03102 |
| `claudeai.claude_science_chat_banner_upsell.cta_clicked` | 1 | `cta`~ | 1 | payload-02270 |
| `claudeai.claude_science_chat_banner_upsell.dismissed` | 1 | `cta`~ | 1 | payload-02271 |
| `claudeai.claude_science_chat_banner_upsell.displayed` | 1 | `cta`~ | 1 | payload-02269 |
| `claudeai.coach.card.load_failed` | 1 | `failure_kind`~ | 1 | payload-00626 |
| `claudeai.coach.card.loaded` | 1 | `after_failure`~ | 1 | payload-00625 |
| `claudeai.coach.conversation_start.timed` | 1 | `ended_ms`~, `ending`~, `first_text_received_ms`~, `opener`~, `org_snapshot_sent`~, `request_sent_ms`~, `session_created_ms`~, `session_id`~, `src`~ | 0 | payload-00627 |
| `claudeai.coach.conversation_started` | 2 | `entry`, `hook_type`~, `report_uuid`?~, `session_id`~, `show_id`?~, `src`~ | 1 | payload-00628, payload-00629 |
| `claudeai.coach.recommendation_acted` | 1 | `action`~, `hook_type`~, `session_id`~ | 1 | payload-00620 |
| `claudeai.coach.recommendation_shown` | 1 | `already_done`~, `control_drawn`~, `hook_type`~, `session_id`~ | 1 | payload-00619 |
| `claudeai.coach.reply.ended_without_text` | 1 | `ending`~, `session_id`~, `stopped`~ | 0 | payload-00631 |
| `claudeai.cobalt_latch.setup_banner_shown` | 1 |  | 0 | payload-03031 |
| `claudeai.cobalt_plinth.popout_closed` | 1 | `duration_ms`~ | 0 | payload-02152 |
| `claudeai.cobalt_plinth.popout_opened` | 1 | `entry_point`~ | 0 | payload-02151 |
| `claudeai.code.acorn_drey.connect_github_clicked` | 1 |  | 0 | payload-01766 |
| `claudeai.code.acorn_drey.contributions_viewed` | 1 | `github_connected`~, `has_rows`~, `pr_count`~ | 0 | payload-01759 |
| `claudeai.code.acorn_drey.customize_change` | 1 | `setting`~, `value`~ | 0 | payload-01765 |
| `claudeai.code.acorn_drey.instructions_saved` | 1 | `length`~ | 0 | payload-01764 |
| `claudeai.code.acorn_drey.mode_change` | 1 | `mode`~ | 0 | payload-01763 |
| `claudeai.code.acorn_drey.toggle` | 1 | `setting`, `value`~ | 0 | payload-01760 |
| `claudeai.code.acorn_drey.toggle_error` | 1 | `attempted_value`~, `error_code`~, `setting`~ | 0 | payload-01762 |
| `claudeai.code.acorn_drey.viewed` | 1 |  | 0 | payload-01761 |
| `claudeai.code.ccr_teleport_band.blocked` | 2 | `custom_properties`~, `custom_properties.branch_source`~, `custom_properties.creative`~, `custom_properties.owner_is_self`~, `custom_properties.reason`~, `custom_properties.uncommitted_files`~, `custom_properties.unpushed_commits`~ | 0 | payload-02013, payload-02014 |
| `claudeai.code.ccr_teleport_band.connect_clicked` | 1 | `custom_properties`~, `custom_properties.creative`~ | 0 | payload-02017 |
| `claudeai.code.ccr_teleport_band.connect_exposed` | 1 | `custom_properties`~, `custom_properties.copy_ready`~, `custom_properties.variant`~ | 0 | payload-02024 |
| `claudeai.code.ccr_teleport_band.dismissed` | 1 | `custom_properties`~, `custom_properties.creative`~, `custom_properties.stage`~ | 0 | payload-02019 |
| `claudeai.code.ccr_teleport_band.fix_repo_access_clicked` | 1 | `custom_properties`~, `custom_properties.creative`~ | 0 | payload-02016 |
| `claudeai.code.ccr_teleport_band.ineligible` | 1 | `custom_properties`~, `custom_properties.reason`~ | 0 | payload-02021 |
| `claudeai.code.ccr_teleport_band.install_return_continued` | 1 | `custom_properties`~, `custom_properties.creative`~ | 0 | payload-02018 |
| `claudeai.code.ccr_teleport_band.reveal_deferred` | 1 | `custom_properties`~, `custom_properties.creative`~ | 0 | payload-02025 |
| `claudeai.code.ccr_teleport_band.shown` | 2 | `custom_properties`~, `custom_properties.creative`~, `custom_properties.stage` | 0 | payload-02022, payload-02023 |
| `claudeai.code.ccr_teleport_band.switched` | 1 | `custom_properties`~, `custom_properties.branch_source`~, `custom_properties.created_environment`~, `custom_properties.creative`~, `custom_properties.uncommitted_files`~, `custom_properties.unpushed_commits`~ | 0 | payload-02015 |
| `claudeai.code.ccr_teleport_band.switched_back` | 1 | `custom_properties`~, `custom_properties.ms_since_switch`~ | 0 | payload-02020 |
| `claudeai.code.connect_github_link.opened` | 1 | `has_org`~, `link`~ | 0 | payload-02923 |
| `claudeai.code.default_env.created` | 1 | `environment_id`~ | 0 | payload-02026 |
| `claudeai.code.default_env.failed` | 1 |  | 0 | payload-02027 |
| `claudeai.code.default_env.offered` | 1 |  | 0 | payload-02028 |
| `claudeai.code.default_env.selected` | 1 |  | 0 | payload-02029 |
| `claudeai.code.env_picker.opened` | 1 | `eligible_for_onramp`~ | 0 | payload-00149 |
| `claudeai.code.environment.archive_error` | 1 | `environment_id`~ | 1 | payload-00526 |
| `claudeai.code.environment.archived` | 1 | `environment_id`~ | 0 | payload-00525 |
| `claudeai.code.environment.created` | 4 | `config_type`~, `environment_id`~ | 0 | payload-01087, payload-01302, payload-02030, payload-02177 |
| `claudeai.code.environment.creation_error` | 4 | `config_type`~ | 4 | payload-01088, payload-01303, payload-02031, payload-02178 |
| `claudeai.code.environment.token_generated` | 1 | `environment_id`~ | 0 | payload-01080 |
| `claudeai.code.environment.token_generation_error` | 1 | `error_message`~ | 0 | payload-01081 |
| `claudeai.code.environment.token_revoke_error` | 1 | `error_message`~ | 0 | payload-01083 |
| `claudeai.code.environment.token_revoked` | 1 | `environment_id`~ | 0 | payload-01082 |
| `claudeai.code.environment.update_error` | 2 | `environment_id`~ | 2 | payload-00524, payload-00528 |
| `claudeai.code.environment.updated` | 2 | `environment_id`~ | 0 | payload-00523, payload-00527 |
| `claudeai.code.environment_modal.viewed` | 5 | `config_type`~, `environment_id`~, `modal_type`, `step`~ | 0 | payload-00522, payload-00529, payload-01086, payload-01097, payload-01301 |
| `claudeai.code.fotw_band.claim_failed` | 2 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~, `custom_properties.reason`~ | 0 | payload-02001, payload-02002 |
| `claudeai.code.fotw_band.claim_succeeded` | 1 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~ | 0 | payload-02000 |
| `claudeai.code.fotw_band.dismissed` | 4 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~, `custom_properties.variant` | 0 | payload-02006, payload-02007, payload-02008, payload-02009 |
| `claudeai.code.fotw_band.fulfilled` | 1 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~ | 0 | payload-02003 |
| `claudeai.code.fotw_band.shown` | 1 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~, `custom_properties.variant`~ | 0 | payload-02004 |
| `claudeai.code.fotw_band.try_clicked` | 1 | `custom_properties`~, `custom_properties.campaign`~, `custom_properties.feature`~, `custom_properties.outcome`~, `custom_properties.prefilled`~, `custom_properties.variant`~ | 0 | payload-02005 |
| `claudeai.code.ghe_connect_handoff_dialog.confirmed` | 2 | `action`, `can_switch`~, `handoff_id`?~, `target`~ | 2 | payload-00650, payload-00651 |
| `claudeai.code.ghe_connect_handoff_dialog.dismissed` | 1 | `can_switch`~, `handoff_id`?~, `target`~ | 1 | payload-00649 |
| `claudeai.code.ghe_connect_handoff_dialog.shown` | 1 | `can_switch`~, `handoff_id`?~, `target`~ | 1 | payload-00648 |
| `claudeai.code.github_app.install_button.clicked` | 4 | `ghe_config_id`~, `source`~ | 0 | payload-00155, payload-01581, payload-01582, payload-01650 |
| `claudeai.code.github_app.repo_dropdown.opened` | 1 | `repos_count`~ | 0 | payload-01579 |
| `claudeai.code.github_connect.clicked` | 8 | `action`, `source`~ | 0 | payload-00156, payload-00157, payload-00354, payload-00389, payload-00537, payload-01385, payload-01650, payload-01752 |
| `claudeai.code.github_connect_tooltip.cta_clicked` | 1 | `step`~ | 1 | payload-00152 |
| `claudeai.code.github_connect_tooltip.dismissed` | 1 | `step`~ | 1 | payload-00151 |
| `claudeai.code.github_connect_tooltip.settings_clicked` | 1 | `step`~ | 1 | payload-00153 |
| `claudeai.code.github_connect_tooltip.shown` | 1 | `step`~ | 1 | payload-00150 |
| `claudeai.code.github_handoff.landed` | 2 | `handoff_id`?~, `outcome`~, `target`~ | 2 | payload-00647, payload-02831 |
| `claudeai.code.github_handoff.opened` | 1 | `caller`~, `handoff_id`~, `popup_blocked`~, `surface`~, `target`~ | 0 | payload-02722 |
| `claudeai.code.github_handoff_banner.confirmed` | 1 | `action`, `target`~ | 1 | payload-00076 |
| `claudeai.code.github_handoff_banner.dismissed` | 1 | `target`~ | 1 | payload-00077 |
| `claudeai.code.github_handoff_banner.shown` | 1 | `handoff_id`?~, `target`~ | 1 | payload-00075 |
| `claudeai.code.github_help_link.clicked` | 1 | `source`~ | 0 | payload-00148 |
| `claudeai.code.github_relink_dialog.confirmed` | 1 | `dispatched`~, `intent`~ | 1 | payload-00654 |
| `claudeai.code.github_relink_dialog.dismissed` | 1 | `after_confirm`~, `intent`~ | 1 | payload-00653 |
| `claudeai.code.github_relink_dialog.shown` | 1 | `entrypoint`~, `handoff_id`?~, `intent`~ | 1 | payload-00652 |
| `claudeai.code.github_sso_banner.clicked` | 1 | `org_count`~ | 0 | payload-01583 |
| `claudeai.code.github_sso_banner.shown` | 2 | `org_count`~ | 0 | payload-01578, payload-01580 |
| `claudeai.code.github_sso_reconnect` | 1 | `action`~, `source`~ | 1 | payload-00835 |
| `claudeai.code.keep_awake_band.battery_off_clicked` | 1 | `custom_properties`~ | 0 | payload-02611 |
| `claudeai.code.keep_awake_band.dismissed` | 1 | `custom_properties`~ | 0 | payload-02613 |
| `claudeai.code.keep_awake_band.message_sent` | 1 | `custom_properties`~ | 0 | payload-02610 |
| `claudeai.code.keep_awake_band.shown` | 1 | `custom_properties`~ | 0 | payload-02609 |
| `claudeai.code.keep_awake_band.turn_off_clicked` | 1 | `custom_properties`~ | 0 | payload-02612 |
| `claudeai.code.lantern_ember.dismissed` | 1 | `custom_properties`~, `custom_properties.phase`~ | 0 | payload-01585 |
| `claudeai.code.lantern_ember.shown` | 1 | `custom_properties`~, `custom_properties.phase`~ | 0 | payload-01584 |
| `claudeai.code.local_pr.detected_for_branch` | 1 | `session_id`~, `via`~ | 0 | payload-02731 |
| `claudeai.code.message.submitted` | 2 | `image_count`~, `is_local`~, `message_length`~, `session_id`~ | 0 | payload-01688, payload-01728 |
| `claudeai.code.no_seat_access_page.viewed` | 1 |  | 0 | payload-01335 |
| `claudeai.code.onboarding.env_setup.completed` | 4 | `auth_path`, `environment_name`~, `option`~ | 0 | payload-01306, payload-01308, payload-01326, payload-01333 |
| `claudeai.code.onboarding.env_setup.error` | 3 | `auth_path`, `error_message`~, `option`~ | 0 | payload-01307, payload-01327, payload-01334 |
| `claudeai.code.onboarding.env_setup.option_selected` | 1 | `environment_name`~, `option`~ | 0 | payload-01305 |
| `claudeai.code.onboarding.env_setup.viewed` | 1 |  | 0 | payload-01304 |
| `claudeai.code.onboarding.github_app.already_installed` | 1 |  | 0 | payload-01313 |
| `claudeai.code.onboarding.github_app.completed` | 1 | `source` | 0 | payload-01310 |
| `claudeai.code.onboarding.github_app.install_button.clicked` | 1 |  | 0 | payload-01314 |
| `claudeai.code.onboarding.github_app.installation.completed` | 1 | `installation_id`~ | 0 | payload-01309 |
| `claudeai.code.onboarding.github_app.returned_without_install` | 1 |  | 0 | payload-01311 |
| `claudeai.code.onboarding.github_app.skipped` | 1 |  | 0 | payload-01315 |
| `claudeai.code.onboarding.github_app.viewed` | 1 |  | 0 | payload-01312 |
| `claudeai.code.onboarding.github_auth.alt_auth.viewed` | 2 |  | 0 | payload-01325, payload-01330 |
| `claudeai.code.onboarding.github_auth.connect_clicked` | 2 | `method` | 0 | payload-01317, payload-01331 |
| `claudeai.code.onboarding.github_auth.get_token_clicked` | 1 |  | 0 | payload-01332 |
| `claudeai.code.onboarding.github_auth.oauth_clicked` | 1 |  | 0 | payload-01323 |
| `claudeai.code.onboarding.github_auth.skipped` | 1 |  | 0 | payload-01324 |
| `claudeai.code.onboarding.github_auth.terminal_step.connected_while_viewing` | 1 | `auth_source`~, `connected_on_first_poll`~, `connection_shape`~, `elapsed_ms`~, `error_count`~, `poll_count`~ | 0 | payload-01321 |
| `claudeai.code.onboarding.github_auth.terminal_step.polling_ended` | 1 | `elapsed_ms`~, `error_count`~, `poll_count`~, `reason`~ | 0 | payload-01320 |
| `claudeai.code.onboarding.github_auth.terminal_step.viewed` | 1 |  | 0 | payload-01322 |
| `claudeai.code.onboarding.github_auth.token_import_failed` | 1 | `reason`~, `status_code`?~ | 1 | payload-01329 |
| `claudeai.code.onboarding.github_auth.token_imported` | 1 |  | 0 | payload-01328 |
| `claudeai.code.onboarding.github_auth.viewed` | 1 | `source` | 0 | payload-01316 |
| `claudeai.code.onboarding.skip_to_code.env_created` | 1 |  | 0 | payload-01319 |
| `claudeai.code.onboarding.skip_to_code.fallback` | 1 | `reason`~ | 0 | payload-01318 |
| `claudeai.code.preset.override_chord` | 1 | `field`~ | 0 | payload-02033 |
| `claudeai.code.preset.override_reset` | 1 |  | 0 | payload-02036 |
| `claudeai.code.preset.override_saved` | 2 | `when` | 0 | payload-02032, payload-02035 |
| `claudeai.code.preset.started_with_overrides` | 1 | `count`~, `fields`~ | 0 | payload-02034 |
| `claudeai.code.render_loop_detected` | 1 | `metadata`~, `metadata.component`~, `metadata.render_count`~, `metadata.time_window_ms`~, `metadata.url`~, `renderer_surface`?~ | 2 | payload-00251 |
| `claudeai.code.repo_picker.closed` | 2 | `dead_end`~, `free_input`~, `open_ms`~, `outcome`~, `repos_count`~, `source`~, `trigger`?~ | 1 | payload-00159, payload-01577 |
| `claudeai.code.repo_picker.refresh_clicked` | 1 | `fetch_in_flight`~, `last_load_failed`~, `list_age_bucket`~, `picker`~, `source` | 0 | payload-00154 |
| `claudeai.code.repo_picker.shown` | 2 | `dead_end`~, `free_input`~, `repos_count`?~, `source`~, `trigger`~ | 1 | payload-00158, payload-01576 |
| `claudeai.code.routine.created` | 1 | `has_api_trigger`~, `has_github_trigger`~, `schedule_kind`~, `source`~, `surface`, `unified_scheduled_tasks`~ | 0 | payload-00536 |
| `claudeai.code.routine.not_found.create_clicked` | 1 | `missing_routine_kind`~ | 0 | payload-01383 |
| `claudeai.code.routine.not_found.viewed` | 1 | `create_offered`~, `missing_routine_kind`~, `state`~ | 0 | payload-01382 |
| `claudeai.code.session.first_text` | 1 | `cli_session_id`?~, `drawn_by`~, `first_assistant_message_id`?~, `first_request_id`?~, `first_text_assistant_message_id`?~, `first_text_form`?~, `first_text_receipt_ms`?~, `first_text_wait_end`~, `is_new_session`~, `mid_turn`~, `model`?~, `navigated_away`~, `open_local_session_count`?~, `publish_hold_ms`?~, `requests_before_first_text`?~, `send_to_arm_ms`?~, `session_id`?~, `session_type`?~, `start_to_emit_ms`~, `tab_age_ms`~, `time_in_background_ms`~, `ttfvt_first_text_paint_ms`?~, `ttfvt_first_text_paint_unheld_ms`?~, `user_message_uuid`?~, `user_wait_before_first_text_ms`~, `user_waits_before_first_text`~, `working_indicator_paint_ms`?~ | 18 | payload-03011 |
| `claudeai.code.session.init_breakdown` | 1 | `bind_corrected`?~, `create_kind`?~, `is_new_session`~, `session_id`~, `session_mode`~, `session_type`~, `ttft_ms`~ | 6 | payload-03017 |
| `claudeai.code.session.stopped` | 2 | `is_local`~, `session_id`~ | 0 | payload-01700, payload-01732 |
| `claudeai.code.session.ttft` | 1 | `bind_corrected`?~, `cic_surface`~, `cli_session_id`?~, `client_send_epoch_ms`~, `completed_after_remount`~, `create_kind`?~, `create_request_ms`?~, `dispatch_first`?~, `fetch_to_first_byte_ms`?~, `first_assistant_message_id`?~, `first_content_type`?~, `first_frame_kind`?~, `first_paint_kind`?~, `first_paint_wait_end`~, `first_request_id`?~, `is_new_session`~, `mid_turn`?~, `navigated_away`~, `open_local_session_count`?~, `pre_fetch_ms`?~, `reply_arm`?, `requesting_to_first_byte_ms`?~, `response_open_ms`?~, `send_to_arm_ms`?~, `session_id`~, `session_type`?~, `start_source`?~, `tab_age_ms`~, `time_in_background_ms`~, `time_to_request_ms`?~, `ttft_first_frame_ms`?~, `ttft_first_paint_ms`?~, `ttft_ms`~, `user_message_uuid`?~ | 24 | payload-03016 |
| `claudeai.code.sessions.heartbeat_check_batch` | 1 | `sent`~, `trigger`~ | 1 | payload-02756 |
| `claudeai.code.sidebar.session_opened` | 1 | `group_by`~, `is_nested`~, `is_pinned`~, `is_running`~, `is_unread`~, `section`~, `session_type`~, `sidebar`, `sidebar_state`~, `via`~ | 0 | payload-02870 |
| `claudeai.code.simulator.fold` | 1 | `direction`~, `outcome`?, `ready_ms`?~ | 1 | payload-00672 |
| `claudeai.code.simulator.stream_stall` | 1 | `device_platform`~, `outcome`~, `reopened`~ | 1 | payload-00673 |
| `claudeai.code.sleep_band.continue_clicked` | 1 | `custom_properties`~ | 0 | payload-02616 |
| `claudeai.code.sleep_band.continue_in_cloud_clicked` | 1 | `custom_properties`~, `custom_properties.had_environment`~ | 1 | payload-02619 |
| `claudeai.code.sleep_band.dismissed` | 1 | `custom_properties`~ | 0 | payload-02617 |
| `claudeai.code.sleep_band.keep_awake_clicked` | 1 | `custom_properties`~ | 0 | payload-02618 |
| `claudeai.code.sleep_band.message_sent` | 1 | `custom_properties`~, `custom_properties.from_continue`~ | 1 | payload-02615 |
| `claudeai.code.stale_compact_band.compact_clicked` | 1 | `custom_properties`~ | 0 | payload-02040 |
| `claudeai.code.stale_compact_band.shown` | 1 | `custom_properties`~ | 0 | payload-02039 |
| `claudeai.code.teleport_to_cloud.cancelled` | 2 | `custom_properties`~, `custom_properties.phase`~, `custom_properties.source`~ | 2 | payload-01655, payload-01662 |
| `claudeai.code.teleport_to_cloud.cleanup_asked` | 2 | `custom_properties`~, `custom_properties.ask`~, `custom_properties.source`~ | 2 | payload-01659, payload-01665 |
| `claudeai.code.teleport_to_cloud.completed` | 3 | `custom_properties`~, `custom_properties.already_uploaded`?~, `custom_properties.attempt`~, `custom_properties.branch_source`?~, `custom_properties.destination`?~, `custom_properties.dirty_tree_recovery`?~, `custom_properties.duration_ms`~, `custom_properties.include_untracked`?~, `custom_properties.left_behind`?~, `custom_properties.skip_push`?~, `custom_properties.snapshot_commit`?~, `custom_properties.source`~, `custom_properties.tracked_changes`?~, `custom_properties.unpushed_commits`?~, `custom_properties.untracked_included`?~, `custom_properties.unverified`~ | 11 | payload-00138, payload-01657, payload-01670 |
| `claudeai.code.teleport_to_cloud.failed` | 7 | `custom_properties`~, `custom_properties.attempt`~, `custom_properties.detail`?~, `custom_properties.duration_ms`~, `custom_properties.phase`?~, `custom_properties.reason`~, `custom_properties.recovery_available`?~, `custom_properties.skip_push`?~, `custom_properties.source`~ | 16 | payload-01656, payload-01664, payload-01666, payload-01667, payload-01668, payload-01669, payload-01671 |
| `claudeai.code.teleport_to_cloud.plan_read` | 1 | `custom_properties`~ | 2 | payload-01660 |
| `claudeai.code.teleport_to_cloud.readiness_checked` | 1 | `custom_properties`~, `custom_properties.at`~, `custom_properties.dirty`?~, `custom_properties.skip_push`?~, `custom_properties.source`~, `custom_properties.verdict`~ | 3 | payload-01663 |
| `claudeai.code.teleport_to_cloud.resumed` | 2 | `custom_properties`~, `custom_properties.source`~, `custom_properties.trigger`~ | 1 | payload-01658, payload-01672 |
| `claudeai.code.teleport_to_cloud.settled` | 3 | `custom_properties`~, `custom_properties.group`~, `custom_properties.pin`~, `custom_properties.source`~ | 0 | payload-00137, payload-01654, payload-01661 |
| `claudeai.code.tool_approval.skipped_already_acknowledged` | 1 | `session_id`~, `tool_type`~ | 0 | payload-02252 |
| `claudeai.code.transcript_width.changed` | 2 | `prop`, `width`~ | 0 | payload-00131, payload-02141 |
| `claudeai.code_block.copied` | 1 |  | 1 | payload-01937 |
| `claudeai.code_cowork_discovery.cta_clicked` | 2 | `data`~, `data.copy`~, `data.cta`~, `data.feature`~, `data.surface`, `data.variant`~ | 0 | payload-01973, payload-02825 |
| `claudeai.code_cowork_discovery.shown` | 2 | `data`~, `data.copy`~, `data.cta`~, `data.feature`~, `data.surface`, `data.variant`~ | 0 | payload-01972, payload-02824 |
| `claudeai.code_cowork_discovery.upgrade_clicked` | 2 | `data`~, `data.copy`~, `data.cta`~, `data.feature`~, `data.surface`, `data.variant`~ | 0 | payload-01974, payload-02826 |
| `claudeai.code_security.disabled` | 1 | `settings_surface` | 0 | payload-02374 |
| `claudeai.code_security.enabled` | 1 | `from_setup_dialog`~, `settings_surface` | 0 | payload-02373 |
| `claudeai.code_security.finding.detail_opened` | 1 | `scan_project_id`~, `severity`~, `status`~ | 0 | payload-00595 |
| `claudeai.code_security.finding.triaged` | 1 | `action`~, `reason`~, `scan_project_id`~, `severity`~ | 0 | payload-00594 |
| `claudeai.code_security.findings.exported` | 1 | `filter_severities`~, `filter_statuses`~, `finding_count`~, `format`~, `scan_id`~, `scan_project_id`~, `scope`~, `surface`~ | 0 | payload-00593 |
| `claudeai.code_security.hedge.edited` | 1 | `action`~, `count`~, `surface`~, `target`~ | 0 | payload-00585 |
| `claudeai.code_security.hedge.section_expanded` | 1 | `surface`~ | 0 | payload-00589 |
| `claudeai.code_security.new_project.auto_opened` | 1 |  | 0 | payload-00596 |
| `claudeai.code_security.project.archive_undone` | 1 | `scan_project_id`~ | 0 | payload-00584 |
| `claudeai.code_security.scan.pause_notice_shown` | 1 | `billing_reason`~, `entry_surface`, `resume_offered`~, `scan_id`~, `scan_project_id`~ | 0 | payload-00598 |
| `claudeai.code_security.scan.resume_requested` | 1 | `billing_reason`~, `entry_surface`, `error_code`~, `outcome`~, `scan_id`~, `scan_project_id`~ | 0 | payload-00597 |
| `claudeai.code_security.schedule.deleted` | 1 | `scan_project_id`~ | 0 | payload-00587 |
| `claudeai.code_security.schedule.saved` | 1 | `scan_project_id`~ | 0 | payload-00586 |
| `claudeai.code_security.spend_limit.saved` | 1 | `currency`~, `limit_minor`~, `source`~ | 0 | payload-02376 |
| `claudeai.code_security.suspended_support.clicked` | 1 | `settings_surface`~ | 0 | payload-00366 |
| `claudeai.code_security.weekly_scans.disabled` | 1 | `default_enabled`~ | 0 | payload-00592 |
| `claudeai.code_security.weekly_scans.enabled` | 1 | `default_enabled`~ | 0 | payload-00592 |
| `claudeai.code_security.weekly_scans.submitted` | 1 | `default_enabled`~, `enabled`~, `outcome`~, `project_is_new`~, `scan_project_id`~ | 0 | payload-00591 |
| `claudeai.command_palette.item_selected` | 1 | `command_id`~, `command_type`~ | 1 | payload-00518 |
| `claudeai.command_palette.opened` | 6 | `entrypoint`~, `first_open`~, `jump_offered`?~, `lists_load`?~, `open_duration_ms`?~, `open_source`?~, `open_trigger`?~, `retrigger`~, `row_type`~, `was_hidden`?~ | 5 | payload-00515, payload-00516, payload-00517, payload-00519, payload-00520, payload-00521 |
| `claudeai.command_palette.session_ended` | 1 | `carried`?~, `clicked_position`~, `clicked_rank`~, `entrypoint`~, `executed_mode`~, `filter_used`?~, `has_highlight`~, `idle_time_ms`~, `is_code_route`~, `no_results`~, `outcome`~, `result_source`~, `search_id`~, `search_version_str`~, `shown_positions`~, `shown_server_ranks`~, `total_time_ms`~ | 2 | payload-00514 |
| `claudeai.compass.approval_modal.confirmed` | 1 | `always_allow_connector_count`~, `always_allow_enabled`~, `always_allow_shown`~, `selected_tool_count`~ | 0 | payload-01792 |
| `claudeai.compass.approval_modal.skipped` | 1 | `via`~ | 0 | payload-01793 |
| `claudeai.compass.approval_modal.viewed` | 1 |  | 0 | payload-01791 |
| `claudeai.compass.panel_dwell` | 1 | `capped`~, `conversation_uuid`~, `dwell_ms`~, `observed_running`~, `result_poll_interval_ms`~, `result_since_open_ms`~, `task_id`~ | 0 | payload-02541 |
| `claudeai.compass.panel_opened` | 1 | `conversation_uuid`?~, `task_id`~ | 1 | payload-00678 |
| `claudeai.compass.sources_viewed` | 1 | `task_id`~ | 0 | payload-02542 |
| `claudeai.completion_endpoint.override_changed` | 1 | `source`, `value`~ | 0 | payload-00683 |
| `claudeai.composer_format_shortcut.pressed` | 1 | `client_platform`~, `is_mac`~ | 1 | payload-02840 |
| `claudeai.composer_upsell.cta_clicked` | 1 | `banner_id`~, `platform`~ | 0 | payload-03149 |
| `claudeai.composer_upsell.displayed` | 1 | `banner_id`~, `platform`~ | 0 | payload-03152 |
| `claudeai.composer_upsell.ms_link_observed` | 1 | `has_ms_connector`~, `link_class`~, `link_shape`~, `platform`~, `would_match`~ | 0 | payload-03151 |
| `claudeai.composer_upsell.trigger_matched` | 1 | `banner_id`~, `detail`~ | 0 | payload-03150 |
| `claudeai.config.reporting_endpoint_fallback` | 1 | `host`~ | 0 | payload-02903 |
| `claudeai.connect_github.connect_clicked` | 1 | `placement`~ | 0 | payload-00089 |
| `claudeai.connect_github.disconnect_cancelled` | 1 |  | 0 | payload-00091 |
| `claudeai.connect_github.disconnect_clicked` | 1 | `three_card_panel`~ | 0 | payload-00092 |
| `claudeai.connect_github.disconnect_confirmed` | 1 |  | 0 | payload-00090 |
| `claudeai.connect_github.report_issue_clicked` | 1 | `account_state`~, `app_state`~, `client`~, `repo_check_state`~, `report_code`~ | 0 | payload-00081 |
| `claudeai.connect_github.viewed` | 1 | `account_state`~, `connected`~, `connected_known`~, `entrypoint`~, `has_check_repo`~, `has_org_param`~, `is_desktop_handoff`~, `source`~, `three_card_panel`~ | 0 | payload-00088 |
| `claudeai.connector_request.button_impression` | 1 | `button_state`~, `mcp_server_uuid`~, `source`~ | 0 | payload-01007 |
| `claudeai.connector_request.failed` | 1 | `mcp_server_uuid`~, `reason`~, `source`?~, `status_code`?~ | 2 | payload-01005 |
| `claudeai.connector_request.resolution_toast_shown` | 1 | `mcp_server_uuid`~, `resolution`~ | 0 | payload-01004 |
| `claudeai.connector_request.submitted` | 1 | `mcp_server_uuid`~, `source`?~ | 1 | payload-01006 |
| `claudeai.connectors.github_app_installations.fix_clicked` | 1 | `account_type`~, `row_state`~ | 0 | payload-00082 |
| `claudeai.connectors.github_app_installations.fix_completed` | 1 | `outcome`~, `reason`?~, `row_state`~ | 1 | payload-00083 |
| `claudeai.connectors.github_app_installations.install_clicked` | 1 | `reason`?~, `source`~ | 1 | payload-00086 |
| `claudeai.connectors.github_app_installations.resume_clicked` | 1 | `account_type`~, `source` | 0 | payload-00087 |
| `claudeai.connectors.github_app_installations.retry_clicked` | 1 | `state`~ | 0 | payload-00085 |
| `claudeai.connectors.github_app_installations.rows_expanded` | 1 | `hidden_count`~, `row_count`~ | 0 | payload-00080 |
| `claudeai.connectors.github_app_installations.viewed` | 1 | `confirmed_count`?~, `has_suspended`?~, `hidden_linked_count`?~, `installation_count`?~, `not_found_count`?~, `not_ready_count`?~, `row_count`?~, `selected_count`?~, `state`~, `unlinked_count`?~, `visible_count`?~ | 1 | payload-00084 |
| `claudeai.conversation.citation_clicked` | 1 | `citationSourceTool`~, `messageUuid`~, `webDomainName`~ | 1 | payload-01230 |
| `claudeai.conversation.feedback.sent` | 1 | `artifacts_enabled`~, `chat_backend`?~, `conversationHasArtifacts`~, `conversation_uuid`~, `input_mode`~, `message_uuid`~, `type`~ | 1 | payload-02691 |
| `claudeai.conversation.marked_read` | 1 | `conversation_uuid`~, `source`~ | 0 | payload-02733 |
| `claudeai.conversation.marked_unread` | 1 | `conversation_uuid`~, `source`~ | 0 | payload-02733 |
| `claudeai.conversation.recent.opened` | 3 | `conversation_uuid`~, `index`~, `sidebar`, `sidebar_state`~ | 0 | payload-01129, payload-01130, payload-02869 |
| `claudeai.conversation.setting.toggled` | 3 | `conversation_uuid`~, `setting`~, `source`~, `value`~ | 0 | payload-02793, payload-02794, payload-02795 |
| `claudeai.conversation.starred` | 4 | `conversation_uuid`~, `source`~ | 0 | payload-00108, payload-01425, payload-02679, payload-02735 |
| `claudeai.conversation.unstarred` | 5 | `conversation_uuid`~, `source`~ | 0 | payload-00108, payload-00392, payload-01425, payload-02679, payload-02735 |
| `claudeai.conversation_search.account_setting_toggled` | 1 | `enabled`~ | 0 | payload-02780 |
| `claudeai.conversation_search.session_ended` | 1 | `clicked_position`~, `clicked_rank`~, `entry_point`~, `executed_mode`~, `idle_time_ms`~, `outcome`~, `search_id`~, `search_version_str`~, `shown_positions`~, `shown_server_ranks`~, `total_time_ms`~ | 0 | payload-01758 |
| `claudeai.conversation_tree.navigated` | 1 | `direction`~, `is_last_human_message`~ | 0 | payload-02119 |
| `claudeai.copper_heron.banner_dismissed` | 1 |  | 0 | payload-03136 |
| `claudeai.copper_heron.banner_displayed` | 1 |  | 0 | payload-03135 |
| `claudeai.copper_heron.clicked` | 1 | `context`~, `entry_point`~, `purpose`~, `session_id`?~ | 1 | payload-03126 |
| `claudeai.copper_heron.coachmark_dismissed` | 1 |  | 0 | payload-02901 |
| `claudeai.copper_heron.coachmark_displayed` | 1 |  | 0 | payload-02900 |
| `claudeai.copper_heron.delivered` | 4 | `context`~, `image_count`~, `leg`~, `purpose`, `session_id`~, `user_retries`~ | 0 | payload-01299, payload-02947, payload-03129, payload-03131 |
| `claudeai.copper_heron.delivery_failed` | 7 | `context`~, `kept`~, `reason`~, `refusal_code`?~, `session_id`?~, `user_retries`~ | 5 | payload-00146, payload-01300, payload-03124, payload-03125, payload-03128, payload-03130, payload-03134 |
| `claudeai.copper_heron.staged` | 1 | `context`~, `duration_ms`~, `session_id`?~, `transcript_chunks`~ | 1 | payload-00147 |
| `claudeai.copper_heron.staged_discarded` | 1 | `context`~, `reviewed`~, `session_id`?~ | 1 | payload-01175 |
| `claudeai.copper_heron.viewed` | 3 | `context`~, `entry_point`~ | 0 | payload-01154, payload-03127, payload-03225 |
| `claudeai.copper_signpost.continue_to_sync_clicked` | 1 | `location`~ | 0 | payload-00487 |
| `claudeai.copper_signpost.dismissed` | 1 | `location`~ | 0 | payload-00488 |
| `claudeai.copper_signpost.evaluated` | 1 | `has_claude_code_access`~, `is_editing_existing`~, `location`~, `signpost_version`, `snoozed`~ | 0 | payload-00489 |
| `claudeai.copper_signpost.shown` | 1 | `location`~ | 0 | payload-00485 |
| `claudeai.copper_signpost.try_claude_code_clicked` | 1 | `location`~ | 0 | payload-00486 |
| `claudeai.copper_wren.survey_feedback_submitted` | 1 | `learning`~, `previous_learning`~, `survey_uuid`~ | 0 | payload-01575 |
| `claudeai.cowork.active_doc_bar.title_clicked` | 1 | `is_remote`~, `session_id`~ | 0 | payload-00434 |
| `claudeai.cowork.active_doc_bar.viewed` | 1 | `is_remote`~, `session_id`~ | 0 | payload-00435 |
| `claudeai.cowork.auq_pending_empty_block` | 1 | `backend`~, `card_rendered`~, `has_buffered_input`~, `request_input_usable`~, `session_id`~, `tool_use_id`~ | 0 | payload-01954 |
| `claudeai.cowork.auq_pending_empty_block_resolved` | 1 | `backend`~, `duration_ms`~, `resolution`~, `session_id`~, `tool_use_id`~ | 0 | payload-01953 |
| `claudeai.cowork.branch_clicked` | 1 | `session_id`~ | 0 | payload-01933 |
| `claudeai.cowork.cli_connector.unmatched_default.set` | 1 | `audience`~, `choice`~, `cli`~, `is_official_plugin`~, `org_cap`~, `plugin_id`?~, `plugin_id_hash`~, `plugin_name`~ | 1 | payload-01159 |
| `claudeai.cowork.cli_connector.unmatched_default.viewed` | 1 | `audience`~, `cli`~, `is_official_plugin`~, `op_count`~, `org_cap`~, `plugin_id`?~, `plugin_id_hash`~, `plugin_name`~ | 1 | payload-01160 |
| `claudeai.cowork.cloud_task_notification` | 1 | `hold_ms`~, `outcome`~, `prev_status`~, `raw_status`~, `session_id`~, `trigger`~ | 0 | payload-00141 |
| `claudeai.cowork.composer_load_timeout` | 1 | `disabled_ms`~, `message_count`~, `session_id`~, `session_kind`~, `timed_out`~ | 0 | payload-00453 |
| `claudeai.cowork.composer_submit_blocked` | 1 | `attempts`~, `session_id`~, `wedged`~, `window_ms`~ | 0 | payload-00452 |
| `claudeai.cowork.doc_draft.stream_ended` | 1 | `chars_streamed`~, `duration_ms`~, `is_remote`~, `outcome`~, `session_id`~, `tool_use_id`~ | 0 | payload-00473 |
| `claudeai.cowork.doc_draft.stream_started` | 1 | `is_remote`~, `session_id`~, `tool_use_id`~ | 0 | payload-00472 |
| `claudeai.cowork.doc_name.fallback_rendered` | 1 | `doc_id`~, `source`~ | 0 | payload-03073 |
| `claudeai.cowork.document.arrived` | 1 | `auto_opened`~, `file_extension`~, `file_id`~, `held_by`~, `is_remote`~, `origin`~, `session_id`~, `source_extension`~ | 0 | payload-00394 |
| `claudeai.cowork.document.export_outcome` | 2 | `attempts`~, `baseline_ext`~, `caller`~, `deliver`~, `duration_ms`~, `engine`, `error_code`~, `error_detail`~, `file_extension`~, `file_id`~, `format`~, `is_remote`~, `ok`~, `session_id`~, `wake_waited_ms`~, `was_asleep`~ | 0 | payload-01215, payload-01216 |
| `claudeai.cowork.document_funnel.click_funneled` | 1 | `failure_reason`~, `file_extension`~, `is_remote`~, `outcome`~, `session_id`~ | 0 | payload-01408 |
| `claudeai.cowork.document_funnel.exposed` | 1 | `gate_enabled`~, `is_remote`~, `session_id`~ | 0 | payload-03072 |
| `claudeai.cowork.effort_switched` | 2 | `new_effort`~, `previous_effort`~, `session_id`~, `session_type`~ | 0 | payload-01697, payload-01730 |
| `claudeai.cowork.error_try_again_clicked` | 2 | `had_prefill_text`~, `retried_failed_send`~, `session_id`~ | 0 | payload-00454, payload-00455 |
| `claudeai.cowork.file_detail.load_outcome` | 1 | `agent_route_type`~, `blocked_reason`~, `by_delivery_only_reason`~, `chat_turn_streaming`~, `display_file_type`~, `duration_ms`~, `entry_point`~, `failure_reason`~, `file_extension`~, `file_format`~, `folder`~, `held_for_turn`?~, `http_status`~, `intent_reads_started_focus`~, `intent_reads_started_hover`~, `intent_reads_started_press`~, `intent_reads_unclaimed`~, `intent_reads_unclaimed_card`~, `intent_reads_unclaimed_pill`~, `intent_reads_unclaimed_scratchpad`~, `intent_reads_unclaimed_sidebar_card`~, `ipc_error_code`~, `is_output_path`~, `is_pane_open`~, `is_remote`~, `is_snapshot`~, `is_task_run`?~, `load_via`~, `online`~, `online_wait_ms`~, `path_reported_gone`~, `pinned_by_chat_host`~, `pressed`~, `read_joined`~, `read_reason`~, `read_started_by`~, `reread_past_cache`?~, `response_opened`~, `restored`~, `selection_age_ms`~, `selection_has_file_uuid`~, `served_folder_relation`?~, `session_id`~, `success`~, `superseded`~, `too_large`?~ | 5 | payload-01414 |
| `claudeai.cowork.file_preview.rendered` | 1 | `blob_ready_ms`~, `content_bytes`~, `decline_reason`~, `duration_ms`~, `failure_reason`~, `is_remote`~, `is_vm_path`~, `media_loaded_ms`~, `native_preview_enabled`~, `render_path`~, `success`~, `via_fallback`~ | 1 | payload-01410 |
| `claudeai.cowork.folder_picker.browse_clicked` | 2 | `placement` | 0 | payload-02815, payload-03257 |
| `claudeai.cowork.folder_picker.browse_result` | 3 | `chosen`~, `placement` | 0 | payload-02814, payload-03252, payload-03254 |
| `claudeai.cowork.folder_picker.create_project_clicked` | 1 | `query_length`?~, `source`?, `typed_create_enabled`~ | 1 | payload-03260 |
| `claudeai.cowork.folder_picker.default_toggled` | 1 | `selected`?~, `set`~, `target_kind`~ | 2 | payload-03255 |
| `claudeai.cowork.folder_picker.enter_took_match` | 1 | `create_row_shown`~, `row_kind`~, `typed_create_enabled`~ | 0 | payload-03262 |
| `claudeai.cowork.folder_picker.no_match_typed` | 1 |  | 0 | payload-03264 |
| `claudeai.cowork.folder_picker.opened` | 1 | `create_offered`~, `default_set`~, `more_count`~, `pinned_count`~, `project_locked`~, `recent_count`~, `typed_create_enabled`~ | 0 | payload-03265 |
| `claudeai.cowork.folder_picker.opened_typed_create_off` | 1 |  | 0 | payload-03266 |
| `claudeai.cowork.folder_picker.opened_typed_create_on` | 1 |  | 0 | payload-03266 |
| `claudeai.cowork.folder_picker.selected` | 7 | `already_selected`~, `gems_definitively_unavailable`~, `index`~, `is_project`~, `kind`~, `placement`, `project_kind`~, `routing_reason`~ | 0 | payload-02811, payload-02812, payload-02813, payload-03253, payload-03258, payload-03259, payload-03267 |
| `claudeai.cowork.folder_picker.star_untrusted` | 1 | `target_kind`~ | 1 | payload-03256 |
| `claudeai.cowork.folder_picker.typed_create_clicked` | 1 |  | 0 | payload-03261 |
| `claudeai.cowork.folder_picker.typed_create_shown` | 1 |  | 0 | payload-03263 |
| `claudeai.cowork.inline_review.decision` | 1 | `decision`~, `session_id`~, `source`~ | 0 | payload-01157 |
| `claudeai.cowork.leading_slash_text.let_through` | 1 |  | 0 | payload-02946 |
| `claudeai.cowork.mcp_status_anomaly` | 1 | `session_id`~ | 1 | payload-01693 |
| `claudeai.cowork.message_edited` | 1 | `session_id`~ | 0 | payload-00458 |
| `claudeai.cowork.migrated_sessions_listed` | 2 | `count`~, `surface`~ | 0 | payload-02774, payload-02888 |
| `claudeai.cowork.model_not_found.retry_clicked` | 1 | `fallback_model`~, `original_model`~ | 0 | payload-01398 |
| `claudeai.cowork.model_switched` | 2 | `new_model`~, `previous_model`~, `session_id`~, `session_type`~ | 0 | payload-01696, payload-01729 |
| `claudeai.cowork.model_version_floor_applied` | 2 | `entry`, `requested_model`~, `session_id`~, `session_type`, `start_kind`~, `substituted_model`~ | 0 | payload-00451, payload-03123 |
| `claudeai.cowork.overage.switch_clicked` | 1 | `fallback_model`~, `original_model`~ | 0 | payload-01399 |
| `claudeai.cowork.pending_permissions_rehydrated` | 1 | `session_id`~, `trigger`~ | 1 | payload-01682 |
| `claudeai.cowork.plugin_connector.linked` | 1 | `connector_connected`~, `connector_directory_uuid`?~, `connector_uuid`~, `is_official_plugin`~, `marketplace_name`~, `match`, `plugin_id`?~, `plugin_id_hash`~, `plugin_name`~, `plugin_server_name`?~, `plugin_source`~, `server_plugin_id`?~ | 3 | payload-02922 |
| `claudeai.cowork.plugin_local_mcp_count` | 1 | `connected`~, `session_id`~ | 0 | payload-01692 |
| `claudeai.cowork.porter_handoff.clicked` | 1 |  | 0 | payload-00268 |
| `claudeai.cowork.porter_handoff.install_clicked` | 2 | `source`, `step`~ | 0 | payload-00271, payload-00272 |
| `claudeai.cowork.porter_handoff.outcome` | 1 |  | 1 | payload-00266 |
| `claudeai.cowork.porter_handoff.shown` | 1 |  | 0 | payload-00270 |
| `claudeai.cowork.porter_handoff.step` | 2 | `handler`?~, `previous_step`~, `step`~ | 1 | payload-00267, payload-00269 |
| `claudeai.cowork.post_upgrade_brief.carousel_shown` | 1 | `arm`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00728 |
| `claudeai.cowork.post_upgrade_brief.connect_gate_blocked` | 1 | `arm`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00737 |
| `claudeai.cowork.post_upgrade_brief.connector_clicked` | 2 | `arm`~, `connector`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00732, payload-00738 |
| `claudeai.cowork.post_upgrade_brief.connector_connected` | 2 | `arm`~, `connector`~, `entry`~, `product_screens`~, `upgrade_kind`~, `via`~ | 0 | payload-00731, payload-00733 |
| `claudeai.cowork.post_upgrade_brief.create_failed` | 5 | `arm`~, `entry`~, `error_code`, `http_status`, `product_screens`~, `reason`, `upgrade_kind`~ | 2 | payload-00740, payload-00741, payload-00744, payload-00745, payload-00746 |
| `claudeai.cowork.post_upgrade_brief.dismissed` | 1 | `arm`~, `entry`~, `product_screens`~, `step`~, `total_steps`~, `upgrade_kind`~ | 0 | payload-00734 |
| `claudeai.cowork.post_upgrade_brief.oauth_resumed` | 1 | `arm`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00730 |
| `claudeai.cowork.post_upgrade_brief.product_command_copied` | 1 | `arm`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00736 |
| `claudeai.cowork.post_upgrade_brief.product_tile_clicked` | 1 | `arm`~, `card`~, `destination`~, `entry`~, `exits_flow`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00735 |
| `claudeai.cowork.post_upgrade_brief.setup_confirmed` | 4 | `arm`~, `destination`~, `entry`~, `product_screens`~, `upgrade_kind`~ | 0 | payload-00739, payload-00742, payload-00743, payload-00747 |
| `claudeai.cowork.post_upgrade_brief.skipped_predicted_refusal` | 1 | `hw`~, `org_requires`~, `routes_to_cloud`~, `source`, `tdv1_key`~, `upgrade_kind`~, `would_bind`~ | 0 | payload-01888 |
| `claudeai.cowork.post_upgrade_brief.step_viewed` | 1 | `arm`~, `card`~, `entry`~, `product_screens`~, `step`~, `total_steps`~, `upgrade_kind`~ | 0 | payload-00729 |
| `claudeai.cowork.preferred_browser.set` | 1 | `client_surface`~, `is_desktop`~, `prefers_chrome`~, `source`~, `value`~ | 0 | payload-02746 |
| `claudeai.cowork.project_warning.cancelled` | 1 | `method`~, `project_uuid`~, `variant`~, `will_use_tools`~ | 0 | payload-03233 |
| `claudeai.cowork.project_warning.confirmed` | 1 | `project_uuid`~, `variant`~, `will_use_tools`~ | 0 | payload-03232 |
| `claudeai.cowork.project_warning.shown` | 1 | `project_uuid`~, `variant`~, `will_use_tools`~ | 0 | payload-03231 |
| `claudeai.cowork.refusal_fallback.continue_clicked` | 1 | `fallback_model`~, `original_model`~, `session_id`~ | 0 | payload-03193 |
| `claudeai.cowork.refusal_fallback.edit_retry_clicked` | 2 | `fallback_model`~, `original_model`~, `session_id`~, `source` | 0 | payload-00438, payload-03194 |
| `claudeai.cowork.refusal_fallback.edit_saved` | 1 | `original_model`~, `session_id`~, `source`~, `text_changed`~ | 0 | payload-00459 |
| `claudeai.cowork.refusal_fallback.start_new_session_clicked` | 1 | `session_id`~ | 0 | payload-03192 |
| `claudeai.cowork.refusal_fallback_band.viewed` | 1 | `fallback_model`~, `original_model`~, `session_id`~ | 0 | payload-00436 |
| `claudeai.cowork.refusal_fallback_band.why_expanded` | 1 | `fallback_model`~, `original_model`~, `session_id`~ | 0 | payload-00437 |
| `claudeai.cowork.remote.api_error` | 4 | `backend`, `error_name`?~, `operation`~, `recovered`~, `session_id`~, `status`~ | 2 | payload-01712, payload-02666, payload-02668, payload-02669 |
| `claudeai.cowork.remote.bound_ledger_late_settle` | 1 | `backend`, `session_id`~ | 0 | payload-01724 |
| `claudeai.cowork.remote.bound_ledger_release` | 2 | `backend`, `session_id`~, `timer` | 0 | payload-01722, payload-01723 |
| `claudeai.cowork.remote.cic_tool_call_refused` | 1 | `extension_version`~, `reason`~, `session_id_digest`?~, `tool_name`~ | 1 | payload-00757 |
| `claudeai.cowork.remote.conversation_workspace_opened` | 3 | `action`~, `backend`, `has_conversation`~, `session_id_digest`?~, `source`~ | 1 | payload-00252, payload-01719, payload-01720 |
| `claudeai.cowork.remote.epitaxy_control_ws_fallback` | 5 | `backend`, `session_id`~, `status`?~, `subtype`~, `trigger`?~ | 3 | payload-00796, payload-00797, payload-00798, payload-00799, payload-02664 |
| `claudeai.cowork.remote.gap_fill_recovered` | 1 | `backend`, `covered`~, `gap_from`~, `gap_to`~, `read`~, `session_id`~, `tail_events`~, `was_retry`~ | 0 | payload-01727 |
| `claudeai.cowork.remote.inaccessible_session` | 1 | `action`~, `backend`, `session_id`~, `source`~, `status`~ | 0 | payload-01718 |
| `claudeai.cowork.remote.mcp_tool_call_end` | 1 | `client_name`, `client_timeout_ms`, `client_version`~, `dropped_blocks`, `mcp_server_slug`, `received_blocks`, `received_chars`, `request_id_route`, `session_id_digest`?~, `tool_use_id`~, `toolbox_request_id`, `wait_ms` | 2 | payload-01628 |
| `claudeai.cowork.remote.message_send_outcome` | 3 | `backend`, `cic_page_created_session`~, `cic_surface`~, `client_surface`~, `duplicate`~, `error_class`~, `has_cic_tab_reminder`~, `has_sequence_num`~, `latency_ms`~, `outcome`, `session_id`~, `session_type`, `status`~, `user_message_uuid`~ | 0 | payload-01708, payload-01709, payload-01710 |
| `claudeai.cowork.remote.registry_unavailable` | 1 | `backend`, `desktop_version`?~, `unavailable_reason`~ | 1 | payload-02662 |
| `claudeai.cowork.remote.session_create_outcome` | 2 | `backend`, `bind_skip_reason`?, `bound`~, `error_name`~, `latency_ms`~, `model_policy_fallback`?~, `origin_artifact_recorded`?~, `outcome`, `session_id_digest`?~ | 11 | payload-03114, payload-03117 |
| `claudeai.cowork.remote.sign_outcome` | 1 | `backend`, `session_id`~ | 1 | payload-02663 |
| `claudeai.cowork.remote.signer_fallthrough` | 1 | `backend`, `branch`~, `session_id`~ | 0 | payload-02667 |
| `claudeai.cowork.remote.stream_effect_recycle` | 1 | `backend`, `ctx_changed`~, `did_remount`~, `gb_gate_now`~, `gb_gate_was`~, `is_account_pending_now`~, `is_account_pending_was`~, `is_gb_pending_now`~, `is_gb_pending_was`~, `is_writable_latched_now`~, `is_writable_now`~, `is_writable_was`~, `org_available_now`~, `org_available_was`~, `project_mode_now`~, `project_mode_was`~, `session_id`~, `session_id_changed`~ | 0 | payload-01725 |
| `claudeai.cowork.remote.stream_stuck_loop` | 1 | `backend`, `fire_count`~, `last_signal`~, `session_id`~, `span_ms`~ | 0 | payload-01726 |
| `claudeai.cowork.remote.tool_list_state` | 2 | `acked_server_count`?~, `backend`, `bridge_server_acked`?~, `phase`, `push_retries`?~, `session_id_digest`?~ | 5 | payload-01721, payload-03115 |
| `claudeai.cowork.remote.transcript_load` | 1 | `eager_pages_config`~, `events`~, `fetch_ms`~, `has_older`~, `mode`, `pages`, `session_id`~ | 0 | payload-01689 |
| `claudeai.cowork.remote.untrusted_device_403` | 1 | `backend`, `browser_key_present`?~, `cowork_gate_active`~, `diagnostics_deferred`?~, `emitter`~, `events_signed`?~, `events_total`?~, `header_attached`?~, `header_maker_present`?~, `header_send_disabled_gate`~, `hw_attestation`~, `hw_unavailable_reason`?~, `kid_class`?~, `ledger_hit`?~, `ledger_size`~, `operation`~, `per_message_attestation_gate`~, `probable_cause`~, `reason`~, `registry_handle_present`~, `registry_ipc_available`~, `route_class`~, `self_attestation_gate`~, `self_filter`~, `session_id`?~, `signer_present`?~, `sub_reason`?~ | 7 | payload-02665 |
| `claudeai.cowork.remote.worker_dead_turn_fail` | 4 | `backend`, `session_id`~, `source`, `verdict`, `was_streaming`~ | 0 | payload-01714, payload-01715, payload-01716, payload-01717 |
| `claudeai.cowork.remote_backend.changed` | 1 | `from`~, `source`~, `to`~ | 0 | payload-02751 |
| `claudeai.cowork.resume_warm.composer_focus` | 1 | `focus_trigger`~, `pointer_type`?~, `since_mount_ms`~ | 1 | payload-02058 |
| `claudeai.cowork.resume_warm.keepalive_end` | 1 | `end_reason`~, `in_turn_ping_count`~, `mount_duration_ms`~, `periodic_gate_on`~, `post_submit_failed_ping_count`~, `post_submit_ping_count`~, `submitted`~, `total_failed_ping_count`~, `total_ping_count`~ | 0 | payload-02060 |
| `claudeai.cowork.resume_warm.outcome` | 2 | `head_start_ms`~, `outcome`~, `surface`~, `visible_at_submit`~ | 2 | payload-02056, payload-02059 |
| `claudeai.cowork.resume_warm.pointer_would_ping` | 1 | `activity_event`~, `pointer_gate_on`~ | 0 | payload-02057 |
| `claudeai.cowork.rewind_clicked` | 2 | `had_prefill_text`~, `is_latest_target`~, `is_remote`~, `local_refusal`?~, `outcome`~, `reject_reason`?~, `session_id`~ | 2 | payload-00456, payload-00457 |
| `claudeai.cowork.scheduled_task.approval_backend_choice` | 1 | `chosen_backend`~, `default_backend`~, `reroute_reason`~ | 0 | payload-01471 |
| `claudeai.cowork.scheduled_task.approval_bind_declined` | 1 | `after_line`~, `reason`~ | 0 | payload-01470 |
| `claudeai.cowork.scheduled_task.create_clicked` | 1 | `entry_point`~, `method`~ | 0 | payload-03220 |
| `claudeai.cowork.scheduled_task.create_refused` | 1 | `entry_point`~, `reason`~, `sessionType` | 0 | payload-01348 |
| `claudeai.cowork.scheduled_task.created` | 3 | `device_bind_outcome`?~, `device_bind_unsigned_reason`?~, `entry_point`~, `has_folders`~, `project_uuid`~, `sessionType`~, `space_id`~, `unified_scheduled_tasks`~ | 2 | payload-01351, payload-01963, payload-01964 |
| `claudeai.cowork.scheduled_task.deleted` | 3 | `space_id`~, `task_kind`~ | 0 | payload-02096, payload-02102, payload-02867 |
| `claudeai.cowork.scheduled_task.detail_page_viewed` | 1 | `space_id`~, `task_kind`~ | 0 | payload-02093 |
| `claudeai.cowork.scheduled_task.disabled` | 2 | `space_id`~, `task_kind`~ | 0 | payload-02095, payload-02765 |
| `claudeai.cowork.scheduled_task.duplicated` | 1 | `deduplicated`~, `had_warnings`~ | 0 | payload-02771 |
| `claudeai.cowork.scheduled_task.enabled` | 3 | `space_id`~, `task_kind`~ | 0 | payload-02094, payload-02763, payload-02770 |
| `claudeai.cowork.scheduled_task.grant_save_outcome` | 1 | `announced`~, `client_surface`~, `code`?~, `outcome`~, `step_up`~ | 1 | payload-01711 |
| `claudeai.cowork.scheduled_task.list_page_viewed` | 1 |  | 0 | payload-02101 |
| `claudeai.cowork.scheduled_task.migrated_to_remote` | 1 | `deduplicated`~, `earlier_version`~, `had_warnings`~ | 0 | payload-02768 |
| `claudeai.cowork.scheduled_task.migration_reverted` | 1 | `dropped_cloud_copy_lingering`~, `lane`~, `prompt_copy_back_failed`~ | 0 | payload-02769 |
| `claudeai.cowork.scheduled_task.run` | 1 | `sessionType`~, `space_id`~, `task_kind`~ | 0 | payload-02767 |
| `claudeai.cowork.scheduled_task.run_output_opened` | 2 | `entry_point`, `sessionType`~, `task_kind`~ | 0 | payload-02097, payload-03214 |
| `claudeai.cowork.scheduled_task.run_refused` | 1 | `model`~, `reason`, `trigger`~ | 0 | payload-02766 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.dismissed` | 1 | `arm`~ | 0 | payload-02882 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.ghost_clicked` | 1 | `arm`~, `mode`~ | 0 | payload-02880 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.ghost_shown` | 1 | `arm`~, `mode`~ | 0 | payload-02879 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.row_retired` | 3 | `arm`~, `mode`~, `trigger`~ | 0 | payload-02881, payload-02883, payload-02886 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.setup_completed` | 1 | `arm`~ | 0 | payload-02884 |
| `claudeai.cowork.scheduled_task.sidebar_discovery.task_created` | 1 | `arm`~ | 0 | payload-02885 |
| `claudeai.cowork.scheduled_task.starter_template_clicked` | 1 | `position`~, `source`~, `template_id`~ | 0 | payload-02100 |
| `claudeai.cowork.scheduled_task.starter_templates_shown` | 1 | `source`~, `template_ids`~ | 0 | payload-02099 |
| `claudeai.cowork.scheduled_task.updated` | 3 | `device_bind_outcome`?, `space_id`~ | 1 | payload-01349, payload-01350, payload-02098 |
| `claudeai.cowork.session.folder_added` | 2 | `folders_after`~, `folders_before`~, `message_count`~, `session_type`~, `source`~, `timing` | 0 | payload-03018, payload-03020 |
| `claudeai.cowork.session.folder_rejected` | 1 | `folders_rejected`~, `folders_requested`~, `legacy_root`~, `reason`~, `session_type`~, `source`~ | 0 | payload-03019 |
| `claudeai.cowork.session.marked_read` | 5 | `session_id`~, `source`~ | 0 | payload-01427, payload-02734, payload-02741, payload-02764, payload-02865 |
| `claudeai.cowork.session.marked_unread` | 5 | `session_id`~, `source`~ | 0 | payload-01427, payload-02734, payload-02741, payload-02764, payload-02865 |
| `claudeai.cowork.session.opened` | 4 | `has_pending_permissions`~, `is_running`~, `is_unread`~, `session_id`~, `sidebar`, `sidebar_state`~, `source`~ | 0 | payload-01131, payload-01132, payload-02818, payload-02872 |
| `claudeai.cowork.session.starred` | 6 | `has_space`~, `session_id`~, `source`~, `starred`~ | 0 | payload-00109, payload-00254, payload-00393, payload-01426, payload-02680, payload-02740 |
| `claudeai.cowork.session_browser_context` | 1 | `builtin_browser_on`~, `chrome_connector_on`~, `chrome_extension_installed`~, `client_surface`~, `is_chat`~, `is_desktop`~, `is_remote`~, `preferred_browser`~, `prefers_chrome`~, `session_id`~, `session_type`~ | 0 | payload-03120 |
| `claudeai.cowork.session_chrome_extension_connection` | 1 | `chrome_extension_connected`~, `is_remote`~, `known_after_ms`~, `session_id`~, `session_type`~ | 0 | payload-03119 |
| `claudeai.cowork.skill.invoked` | 1 | `session_id`~, `skill_name`~, `skill_name_hash`~ | 1 | payload-01694 |
| `claudeai.cowork.skill_create_nudge.clicked` | 2 | `conversation_uuid`~, `session_id`~, `surface` | 0 | payload-00125, payload-00404 |
| `claudeai.cowork.skill_create_nudge.dismissed` | 2 | `conversation_uuid`~, `session_id`~, `surface` | 0 | payload-00126, payload-00405 |
| `claudeai.cowork.skill_create_nudge.viewed` | 2 | `conversation_uuid`~, `session_id`~, `surface` | 0 | payload-00124, payload-00403 |
| `claudeai.cowork.skill_proposal.adopted` | 1 | `created_missing_target`?~, `library`~, `proposal_kind`~, `save_surface`~ | 2 | payload-02136 |
| `claudeai.cowork.skill_proposal.dismissed` | 1 | `proposal_kind`~ | 1 | payload-02112 |
| `claudeai.cowork.skill_proposal.save_blocked` | 1 | `blocked_rule`~, `proposal_kind`~ | 1 | payload-02110 |
| `claudeai.cowork.skill_proposal.undismissed` | 1 | `proposal_kind`~ | 1 | payload-02113 |
| `claudeai.cowork.skill_save_card.approved` | 1 | `is_update`~ | 0 | payload-01469 |
| `claudeai.cowork.skill_save_card.dismissed` | 1 | `is_update`~ | 0 | payload-01468 |
| `claudeai.cowork.skill_save_card.viewed` | 1 | `is_update`~ | 0 | payload-01467 |
| `claudeai.cowork.slash_command.invoked` | 1 | `command_name`~, `command_name_hash`~, `is_official_plugin`~, `is_plugin`~, `marketplace_name`~, `plugin_id_hash`~, `plugin_name`~, `plugin_name_hash`~, `plugin_source`~, `session_id`~ | 0 | payload-03064 |
| `claudeai.cowork.sleepy_popcorn` | 1 | `new_model`~, `outcome`~, `previous_model`~, `session_id`~, `session_type`~ | 0 | payload-00448 |
| `claudeai.cowork.space.created` | 3 | `creation_method`, `folder_count`~, `has_instructions`~, `is_remote`~, `project_count`~, `space_id`~ | 0 | payload-00320, payload-00321, payload-00506 |
| `claudeai.cowork.space.deleted` | 3 | `space_id`~, `was_viewing`~ | 0 | payload-00323, payload-01999, payload-02829 |
| `claudeai.cowork.space.file_viewer_opened` | 1 | `is_session_scoped`~, `source`~, `space_id`~ | 0 | payload-01268 |
| `claudeai.cowork.space.folder_added` | 1 | `space_id`~, `surface` | 0 | payload-01270 |
| `claudeai.cowork.space.folder_removed` | 1 | `space_id`~, `surface` | 0 | payload-01271 |
| `claudeai.cowork.space.instructions_updated` | 1 | `char_count`~, `has_instructions`~, `space_id`~, `surface` | 0 | payload-01269 |
| `claudeai.cowork.space.onboarding.path_selected` | 1 | `path`~ | 0 | payload-00319 |
| `claudeai.cowork.space.onboarding.viewed` | 1 |  | 0 | payload-00318 |
| `claudeai.cowork.space.project_removed` | 1 | `space_id`~, `surface` | 0 | payload-01272 |
| `claudeai.cowork.space.renamed` | 2 | `description_changed`~, `name_changed`~, `space_id`~ | 0 | payload-02827, payload-02873 |
| `claudeai.cowork.space.scheduled_task_linked` | 1 | `space_id`~ | 0 | payload-01273 |
| `claudeai.cowork.space.scheduled_task_unlinked` | 1 | `space_id`~ | 0 | payload-01274 |
| `claudeai.cowork.space.session_moved` | 8 | `had_prior_space`~, `session_id`~, `session_type`~, `source`, `space_id`~ | 0 | payload-00831, payload-00832, payload-02736, payload-02737, payload-02738, payload-02891, payload-02892, payload-02893 |
| `claudeai.cowork.space.session_removed` | 2 | `session_id`~, `session_type`, `space_id`~ | 0 | payload-02739, payload-02742 |
| `claudeai.cowork.space.starred` | 5 | `source`~, `space_id`~, `starred`~ | 0 | payload-00110, payload-00322, payload-01138, payload-02682, payload-02828 |
| `claudeai.cowork.space.viewed` | 1 | `folder_count`~, `has_instructions`~, `project_count`~, `session_count`~, `space_id`~ | 0 | payload-01133 |
| `claudeai.cowork.subagent.invoked` | 1 | `session_id`~, `subagent_name`~, `subagent_name_hash`~ | 1 | payload-01695 |
| `claudeai.cowork.thinking_detected` | 1 | `session_id`~ | 0 | payload-01691 |
| `claudeai.cowork.thinking_switched` | 1 | `new_thinking`~, `previous_thinking`~, `session_id`~, `session_type`~ | 0 | payload-01698 |
| `claudeai.cowork.unsupervised_mode.defaulted` | 1 | `mode`, `source`~ | 0 | payload-03251 |
| `claudeai.cowork.unsupervised_mode.disabled` | 1 | `previous_mode`~, `variant`~ | 0 | payload-03250 |
| `claudeai.cowork.unsupervised_mode.enabled` | 2 | `chrome_skip_all`~, `mode`~, `variant`~ | 0 | payload-03248, payload-03249 |
| `claudeai.cowork.unsupervised_mode.warning_modal.cancelled` | 1 |  | 0 | payload-01610 |
| `claudeai.cowork.unsupervised_mode.warning_modal.chrome_toggled` | 1 | `enabled`~ | 0 | payload-01609 |
| `claudeai.cowork.unsupervised_mode.warning_modal.confirmed` | 1 | `chrome_section_shown`~, `chrome_skip_all`~ | 0 | payload-01611 |
| `claudeai.cowork.unsupervised_mode.warning_modal.shown` | 1 |  | 0 | payload-01608 |
| `claudeai.cowork.warm_claim_result` | 2 | `bind_readiness`~, `discard_reason`~, `had_slot`~, `session_id_digest`?~, `sign_retry_elapsed_ms`~, `sign_retry_index`~, `sign_retry_schedule`~, `wait_timed_out`~ | 5 | payload-03116, payload-03118 |
| `claudeai.cowork.warm_start.outcome` | 4 | `head_start_ms`~, `held_for_ms`~, `mcp_put_ms`~, `mcp_put_skipped`?~, `origin_artifact_recorded`?~, `outcome`~, `primer_arm`~, `reconciled`~, `sdk_mcp_wait_ms`~, `sdk_mcp_wait_result`~, `session_id_digest`?~, `site`, `unused_discards`~ | 7 | payload-03110, payload-03111, payload-03112, payload-03113 |
| `claudeai.cowork.workflow.stop_clicked` | 2 | `is_local`~, `session_id`~ | 0 | payload-01703, payload-01734 |
| `claudeai.cowork.workflow_approval.approved` | 1 | `is_managed`~, `session_id`~, `tool_use_id`~, `via_keyboard`~ | 0 | payload-02247 |
| `claudeai.cowork.workflow_approval.dismissed` | 1 | `is_managed`~, `session_id`~, `tool_use_id`~, `via_keyboard`~ | 0 | payload-02247 |
| `claudeai.cowork.workflow_approval.viewed` | 1 | `is_managed`~, `phase_count`~, `session_id`~, `tool_use_id`~ | 0 | payload-02246 |
| `claudeai.cowork_agent_notice.action_clicked` | 1 | `action`~, `notice_surface`~ | 0 | payload-01102 |
| `claudeai.cowork_agent_notice.action_finished` | 3 | `action`, `during_export`~, `exported_count`~, `failed_count`~, `folder_offered`~, `notice_surface`~, `reason`~, `scheduled_tasks`~, `skipped_count`~, `status`~, `uploaded_count`~ | 0 | payload-01103, payload-01104, payload-01105 |
| `claudeai.cowork_agent_notice.actions_shown` | 1 | `export_shown`~, `folder_shown`~, `move_shown`~, `notice_surface`~, `open_shown`~ | 0 | payload-01099 |
| `claudeai.cowork_agent_notice.dismissed` | 1 | `notice_surface`~ | 0 | payload-01101 |
| `claudeai.cowork_agent_notice.preview_failed` | 1 | `failure`~, `notice_surface`~ | 0 | payload-01100 |
| `claudeai.cowork_agent_notice.shown` | 1 | `notice_surface`~ | 0 | payload-01098 |
| `claudeai.cowork_docs.conflict_recovered` | 1 | `is_remote`~, `session_id`~ | 1 | payload-01706 |
| `claudeai.cowork_docs.tool_error` | 1 | `is_remote`~, `session_id`~ | 1 | payload-01704 |
| `claudeai.cowork_docs.write_call` | 1 | `is_remote`~, `session_id`~ | 1 | payload-01705 |
| `claudeai.cowork_grace_banner.dismissed` | 1 |  | 0 | payload-03173 |
| `claudeai.cowork_grace_banner.shown` | 1 |  | 0 | payload-03174 |
| `claudeai.cowork_grace_banner.upgrade_clicked` | 1 |  | 0 | payload-03175 |
| `claudeai.cowork_guest_pass_upsell_banner.cta_clicked` | 1 |  | 0 | payload-03105 |
| `claudeai.cowork_guest_pass_upsell_banner.dismissed` | 1 |  | 0 | payload-03106 |
| `claudeai.cowork_guest_pass_upsell_banner.displayed` | 1 |  | 0 | payload-03104 |
| `claudeai.cowork_loading_tip.connector_check` | 1 | `outcome`~, `took_s`~ | 0 | payload-00127 |
| `claudeai.cowork_loading_tip.cta_clicked` | 1 | `cta_autosend`~, `cta_target`~ | 1 | payload-00122 |
| `claudeai.cowork_loading_tip.dismissed` | 1 |  | 1 | payload-00123 |
| `claudeai.cowork_loading_tip.displayed` | 1 |  | 1 | payload-00120 |
| `claudeai.cowork_loading_tip.qualified_impression` | 1 |  | 1 | payload-00121 |
| `claudeai.cowork_unbound_folders_banner.restart_clicked` | 1 |  | 0 | payload-00441 |
| `claudeai.cowork_unbound_folders_banner.update_cta_clicked` | 1 |  | 0 | payload-00440 |
| `claudeai.cowork_unbound_folders_banner.update_nudge_displayed` | 1 |  | 0 | payload-00439 |
| `claudeai.cowork_upload_coachmark.cta_clicked` | 1 | `platform`~ | 0 | payload-03057 |
| `claudeai.cowork_upload_coachmark.dismissed` | 1 |  | 0 | payload-03056 |
| `claudeai.cowork_upload_coachmark.displayed` | 1 |  | 0 | payload-03055 |
| `claudeai.cowork_writing_style_upsell_banner.cta_clicked` | 1 |  | 0 | payload-03138 |
| `claudeai.cowork_writing_style_upsell_banner.dismissed` | 1 |  | 0 | payload-03139 |
| `claudeai.cowork_writing_style_upsell_banner.displayed` | 1 |  | 0 | payload-03137 |
| `claudeai.credits_required.member_request_sent` | 1 | `target_model_id`~ | 0 | payload-00285 |
| `claudeai.csv2.end.named` | 1 | `after_own_prompt`~, `at_tail`~, `empty`~, `id_age`~, `id_version`~, `names_audience`~, `row`~, `send_failed`~, `sender`~, `server_echoed`~, `since_turn_end`~, `stop`~, `stop_pressed`~, `streaming`~, `user_stopped`~, `view`~, `voice`~ | 0 | payload-01386 |
| `claudeai.csv2.option.selected` | 1 | `audience`~, `conversation_uuid`~, `was_shared`~ | 0 | payload-01437 |
| `claudeai.csv2.people.refused` | 1 | `conversation_uuid`~, `n_recipients`~, `reason`~ | 0 | payload-01439 |
| `claudeai.csv2.people.removed` | 1 | `conversation_uuid`~, `grant_kind`~, `was_invited`~ | 0 | payload-01448 |
| `claudeai.csv2.people.submitted` | 1 | `conversation_uuid`~, `n_accounts`~, `n_emails`~, `n_groups`~, `was_shared`~ | 0 | payload-01438 |
| `claudeai.csv2.request.approved` | 1 | `conversation_uuid`~, `is_external`~ | 0 | payload-01449 |
| `claudeai.csv2.request.clicked` | 1 |  | 0 | payload-01186 |
| `claudeai.csv2.request.denied` | 1 | `conversation_uuid`~, `is_external`~ | 0 | payload-01450 |
| `claudeai.csv2.request.link_opened` | 1 | `conversation_uuid`~ | 0 | payload-01424 |
| `claudeai.csv2.request.refused` | 2 | `reason`~ | 0 | payload-01188, payload-01189 |
| `claudeai.csv2.request.sent` | 1 | `result`~ | 0 | payload-01187 |
| `claudeai.csv2.settings.opened` | 1 | `conversation_uuid`~, `was_shared`~ | 0 | payload-01440 |
| `claudeai.csv2.step.cancelled` | 3 | `conversation_uuid`~ | 0 | payload-01442, payload-01443, payload-01445 |
| `claudeai.csv2.step.confirmed` | 1 | `conversation_uuid`~ | 0 | payload-01446 |
| `claudeai.csv2.step.viewed` | 2 | `conversation_uuid`~ | 0 | payload-01441, payload-01444 |
| `claudeai.csv2.update.clicked` | 2 | `conversation_uuid`~, `source` | 0 | payload-01400, payload-01422 |
| `claudeai.csv_invite.file_rejected` | 1 | `file_extension`~, `file_size_bytes`~, `mime_type`~, `reason`~, `source`~ | 0 | payload-00533 |
| `claudeai.csv_invite.file_uploaded` | 1 | `capped`~, `capped_count`~, `detected_delimiter`~, `detected_encoding`~, `email_column_source`~, `email_count`~, `error_name`?~, `fallback_reason`?~, `file_extension`~, `file_size_bytes`~, `has_role_column`~, `has_seat_tier_column`~, `parser_fallback`~, `parser_variant`~, `skipped_count`~, `source`~, `suspected_non_utf8`~, `zero_result_reason`~ | 3 | payload-00535 |
| `claudeai.csv_invite.parse_failed` | 1 | `error_name`~, `file_size_bytes`~, `parser_variant`~, `source`~, `stage`~ | 0 | payload-00534 |
| `claudeai.customize.add_failed` | 1 | `add_result`?~, `add_surface`~, `error_kind`?~ | 5 | payload-02341 |
| `claudeai.customize.add_succeeded` | 1 | `add_result`?~, `add_surface`~, `error_kind`?~ | 5 | payload-02341 |
| `claudeai.customize.broken_connectors_banner.action` | 1 | `action`~, `count`~, `flag`~ | 0 | payload-00638 |
| `claudeai.customize.broken_connectors_banner.shown` | 1 | `count`~, `flag`~ | 0 | payload-00637 |
| `claudeai.customize.broken_connectors_card.action` | 2 | `action`~, `cls`~, `count`~, `flag`~ | 0 | payload-00640, payload-00641 |
| `claudeai.customize.broken_connectors_card.shown` | 1 | `count`~, `flag`~, `sign_in_count`~ | 0 | payload-00639 |
| `claudeai.customize.connector_link_missed` | 1 | `link_kind`~ | 0 | payload-02338 |
| `claudeai.customize.detail_tab_changed` | 1 | `from`~, `section`~, `to`~ | 1 | payload-00576 |
| `claudeai.customize.detail_viewed` | 1 | `from_block_key`~, `from_block_kind`~, `from_block_position`~, `from_rank`~, `section`~, `tab`~, `via`~ | 1 | payload-00575 |
| `claudeai.customize.discover.opened` | 1 | `destination`~, `has_marketplace_filter`~, `has_query`~, `section`~, `source`~ | 0 | payload-03032 |
| `claudeai.customize.discover_home.add_clicked` | 1 |  | 2 | payload-00572 |
| `claudeai.customize.discover_home.block_viewed` | 1 | `item_count`~, `section`~ | 1 | payload-00570 |
| `claudeai.customize.discover_home.item_clicked` | 1 | `section`~ | 2 | payload-00571 |
| `claudeai.customize.discover_home.see_all_clicked` | 1 | `section`~ | 1 | payload-00573 |
| `claudeai.customize.discover_home.viewed` | 1 | `block_count`~, `block_keys`~, `promo_count`~, `section`~ | 0 | payload-00574 |
| `claudeai.customize.discover_search.results` | 1 | `addable_count`~, `load_error`~, `load_ms`~, `own_count`~, `query_length`~, `section`~ | 0 | payload-02121 |
| `claudeai.customize.link_forwarded` | 1 | `section`~ | 0 | payload-01002 |
| `claudeai.customize.list_filter_changed` | 1 |  | 1 | payload-02339 |
| `claudeai.customize.list_sort_changed` | 1 |  | 1 | payload-02340 |
| `claudeai.customize.opened` | 1 | `entry`~, `presentation`~, `section`~, `tab`~ | 0 | payload-02336 |
| `claudeai.customize.section_changed` | 1 | `from`~, `to`~ | 0 | payload-02335 |
| `claudeai.customize.sndp_live_link_clicked` | 1 | `item_id`~, `live_item_id`~, `section`~ | 0 | payload-00897 |
| `claudeai.customize.sndp_offered` | 1 | `as_library_manager`~, `item_id`~, `policy`~, `section`~, `share_surface`~ | 0 | payload-00896 |
| `claudeai.customize.sndp_opened` | 1 | `as_library_manager`~, `entry`~, `is_resubmission`~, `item_id`~, `policy`~, `section`~ | 0 | payload-00890 |
| `claudeai.customize.sndp_status_viewed` | 1 | `item_id`~, `section`~, `state`~, `submission_id`~ | 0 | payload-00895 |
| `claudeai.customize.sndp_submit_failed` | 1 | `as_library_manager`~, `error_kind`~, `is_resubmission`~, `item_id`~, `policy`~, `refusal`~, `section`~ | 0 | payload-00893 |
| `claudeai.customize.sndp_withdrawn` | 1 | `held`~, `item_id`~, `section`~, `submission_id`~ | 0 | payload-00894 |
| `claudeai.customize.tab_changed` | 1 | `from`~, `section`~, `to`~ | 0 | payload-02337 |
| `claudeai.customize.updh_add_clicked` | 1 |  | 1 | payload-00998 |
| `claudeai.customize.updh_item_dismissed` | 1 |  | 1 | payload-02634 |
| `claudeai.customize.updh_item_shown` | 1 |  | 1 | payload-02632 |
| `claudeai.customize.updh_item_view_clicked` | 1 |  | 1 | payload-02633 |
| `claudeai.customize.updh_proceed_clicked` | 1 | `renamed`~ | 1 | payload-00999 |
| `claudeai.customize.updh_shown` | 1 |  | 1 | payload-00996 |
| `claudeai.customize.updh_view_clicked` | 1 |  | 1 | payload-00997 |
| `claudeai.design.org_sharing_admin_toggle` | 1 | `admin_page`~, `new_state`~ | 0 | payload-03063 |
| `claudeai.desktop.api_signin.abandoned` | 1 |  | 0 | payload-00876 |
| `claudeai.desktop.api_signin.completed` | 1 |  | 0 | payload-00875 |
| `claudeai.desktop.api_signin.fork_opened` | 1 | `config_source`~, `destination`~, `provider`~ | 0 | payload-00882 |
| `claudeai.desktop.api_signin.oauth_result` | 1 | `error_kind`~, `ok`~ | 0 | payload-00874 |
| `claudeai.desktop.api_signin.started` | 1 | `config_source`~, `has_existing_credential`~ | 0 | payload-00873 |
| `claudeai.desktop.auto_archive_inactive_changed` | 1 | `days`~ | 0 | payload-01123 |
| `claudeai.desktop.code.landing.git_became_available` | 1 | `platform`~, `previous_reason`~ | 0 | payload-01790 |
| `claudeai.desktop.code.scheduled_task.created` | 1 | `entry_point`~, `sessionType`, `unified_scheduled_tasks`~ | 0 | payload-01352 |
| `claudeai.desktop.code.scheduled_task.deleted` | 3 |  | 0 | payload-01896, payload-01897, payload-02866 |
| `claudeai.desktop.code.scheduled_task.disabled` | 2 |  | 0 | payload-01895, payload-01898 |
| `claudeai.desktop.code.scheduled_task.enabled` | 2 |  | 0 | payload-01895, payload-01898 |
| `claudeai.desktop.code.scheduled_task.run` | 1 |  | 0 | payload-01894 |
| `claudeai.desktop.code.worktree_toggled` | 1 | `enabled`~, `source`~ | 0 | payload-01356 |
| `claudeai.desktop.cowork.reinstall_cancelled` | 1 |  | 0 | payload-02165 |
| `claudeai.desktop.cowork.reinstall_initiated` | 1 |  | 0 | payload-02164 |
| `claudeai.desktop.dock_bounce_toggled` | 1 | `prop` | 0 | payload-02139 |
| `claudeai.desktop.first_login.completed` | 1 |  | 0 | payload-02904 |
| `claudeai.desktop.gilded_compass_end_user_nudge.clicked` | 1 | `nudge_reason`~, `target_mode`~, `variant`~ | 0 | payload-01354 |
| `claudeai.desktop.gilded_compass_end_user_nudge.dismissed` | 1 | `nudge_reason`~, `variant`~ | 0 | payload-01355 |
| `claudeai.desktop.gilded_compass_end_user_nudge.shown` | 1 | `nudge_reason`~, `variant`~ | 0 | payload-01353 |
| `claudeai.desktop.keep_awake_toggled` | 1 | `enabled`~ | 0 | payload-01008 |
| `claudeai.desktop.notification_level_changed` | 1 | `level`~, `notification_type`~ | 0 | payload-01122 |
| `claudeai.desktop.notification_sound_changed` | 1 | `prop` | 0 | payload-02138 |
| `claudeai.desktop.open_with.opened` | 1 | `destination`~, `extensions`~, `file_count`~, `file_group`~, `folder_count`~ | 0 | payload-02905 |
| `claudeai.desktop.open_with.viewer_shown` | 1 | `extension`~, `file_count`~, `file_group`~, `outcome`~ | 0 | payload-02233 |
| `claudeai.desktop.output_style_default_changed` | 1 | `to_default`~ | 0 | payload-01119 |
| `claudeai.desktop.provider_signin.claudeai_exit` | 1 | `step`~ | 0 | payload-00881 |
| `claudeai.desktop.provider_signin.result` | 2 | `ok`~, `provider`~ | 0 | payload-00878, payload-00880 |
| `claudeai.desktop.provider_signin.started` | 2 | `auth_kind`~, `config_source`~, `provider`~ | 0 | payload-00877, payload-00879 |
| `claudeai.desktop.remote_control_default_toggled` | 1 | `prop` | 0 | payload-02140 |
| `claudeai.desktop.sidebar.create_menu_opened` | 1 | `item_id`~, `sidebar_state`~ | 0 | payload-03219 |
| `claudeai.desktop.sidebar.design_entry_clicked` | 1 | `frame_mode`~, `open_behavior`~ | 0 | payload-02852 |
| `claudeai.desktop.sidebar.design_entry_shown` | 1 | `frame_mode`~, `open_behavior`~, `tabs`~ | 0 | payload-02854 |
| `claudeai.desktop.sidebar.dispatch_row_clicked` | 1 | `sidebar_state`~ | 0 | payload-03215 |
| `claudeai.desktop.sidebar.edit_changed` | 1 | `action`~ | 0 | payload-03218 |
| `claudeai.desktop.sidebar.edit_opened` | 1 |  | 0 | payload-03217 |
| `claudeai.desktop.sidebar.family_toggled` | 1 |  | 1 | payload-03208 |
| `claudeai.desktop.sidebar.group_toggled` | 1 | `action`~, `column_kind`~, `group_by`~, `group_kind`~, `session_count`~ | 0 | payload-03204 |
| `claudeai.desktop.sidebar.mode_pill_selected` | 3 | `compact`~, `from_mode`~, `sidebar_state`~, `to_mode`~, `via`~ | 4 | payload-02849, payload-02850, payload-03212 |
| `claudeai.desktop.sidebar.more_flyout_opened` | 1 | `edit_in_place_offered`~, `sidebar_state`~ | 0 | payload-03216 |
