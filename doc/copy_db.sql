-- ┌────────┬───────────────────────────────────────────────┬───────┬─────────┐
-- │ Schema │                     Name                      │ Type  │  Owner  │
-- ├────────┼───────────────────────────────────────────────┼───────┼─────────┤
-- │ public │ [ ] account_emailaddress                      │ table │ linuxos │
-- │ public │ [ ] account_emailconfirmation                 │ table │ linuxos │
-- │ public │ [ ] accounts_remembertoken                    │ table │ linuxos │
-- │ public │ [ ] accounts_userrating                       │ table │ linuxos │
-- │ public │ [ ] article_article                           │ table │ linuxos │
-- │ public │ [ ] article_category                          │ table │ linuxos │
-- │ public │ [ ] attachment_attachment                     │ table │ linuxos │
-- │ public │ [ ] attachment_attachmentimage                │ table │ linuxos │
-- │ public │ [ ] attachment_temporaryattachment            │ table │ linuxos │
-- │ public │ [ ] attachment_uploadsession                  │ table │ linuxos │
-- │ public │ [ ] auth_group                                │ table │ linuxos │
-- │ public │ [ ] auth_group_permissions                    │ table │ linuxos │
-- │ public │ [ ] auth_permission                           │ table │ linuxos │
-- │ public │ [ ] auth_user                                 │ table │ linuxos │
-- │ public │ [ ] auth_user_groups                          │ table │ linuxos │
-- │ public │ [ ] auth_user_user_permissions                │ table │ linuxos │
-- │ public │ [ ] blog_blog                                 │ table │ linuxos │
-- │ public │ [ ] blog_post                                 │ table │ linuxos │
-- │ public │ [ ] django_admin_log                          │ table │ linuxos │
-- │ public │ [ ] django_comment_flags                      │ table │ linuxos │
-- │ public │ [ ] django_comments                           │ table │ linuxos │
-- │ public │ [ ] django_content_type                       │ table │ linuxos │
-- │ public │ [ ] django_migrations                         │ table │ linuxos │
-- │ public │ [ ] django_session                            │ table │ linuxos │
-- │ public │ [ ] django_site                               │ table │ linuxos │
-- │ public │ [ ] forum_section                             │ table │ linuxos │
-- │ public │ [ ] forum_topic                               │ table │ linuxos │
-- │ public │ [ ] hitcount_hitcount                         │ table │ linuxos │
-- │ public │ [ ] news_news                                 │ table │ linuxos │
-- │ public │ [ ] notifications_event                       │ table │ linuxos │
-- │ public │ [ ] notifications_inbox                       │ table │ linuxos │
-- │ public │ [ ] polls_choice                              │ table │ linuxos │
-- │ public │ [ ] polls_poll                                │ table │ linuxos │
-- │ public │ [ ] polls_recordip                            │ table │ linuxos │
-- │ public │ [ ] polls_recorduser                          │ table │ linuxos │
-- │ public │ [ ] reversion_revision                        │ table │ linuxos │
-- │ public │ [ ] reversion_version                         │ table │ linuxos │
-- │ public │ [ ] threaded_comments_rootheader              │ table │ linuxos │
-- │ public │ [ ] threaded_comments_userdiscussionattribute │ table │ linuxos │
-- │ public │ [ ] wiki_page                                 │ table │ linuxos │
-- └────────┴───────────────────────────────────────────────┴───────┴─────────┘

DELETE FROM auth_permission;
DELETE FROM django_content_type;
INSERT INTO django_content_type (id, app_label, model)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, app_label, model FROM django_content_type')
		AS t1(id integer, app_label text, model text);
