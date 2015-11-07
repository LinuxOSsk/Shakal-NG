-- ┌────────┬───────────────────────────────────────────────┬───────┬─────────┐
-- │ Schema │                     Name                      │ Type  │  Owner  │
-- ├────────┼───────────────────────────────────────────────┼───────┼─────────┤
-- │ public │ [x] account_emailaddress                      │ table │ linuxos │
-- │ public │ [x] account_emailconfirmation                 │ table │ linuxos │
-- │ public │ [x] accounts_remembertoken                    │ table │ linuxos │
-- │ public │ [*] accounts_userrating                       │ table │ linuxos │
-- │ public │ [ ] article_article                           │ table │ linuxos │
-- │ public │ [ ] article_category                          │ table │ linuxos │
-- │ public │ [ ] attachment_attachment                     │ table │ linuxos │
-- │ public │ [ ] attachment_attachmentimage                │ table │ linuxos │
-- │ public │ [ ] attachment_temporaryattachment            │ table │ linuxos │
-- │ public │ [ ] attachment_uploadsession                  │ table │ linuxos │
-- │ public │ [*] auth_group                                │ table │ linuxos │
-- │ public │ [*] auth_group_permissions                    │ table │ linuxos │
-- │ public │ [*] auth_permission                           │ table │ linuxos │
-- │ public │ [*] auth_user                                 │ table │ linuxos │
-- │ public │ [*] auth_user_groups                          │ table │ linuxos │
-- │ public │ [*] auth_user_user_permissions                │ table │ linuxos │
-- │ public │ [ ] blog_blog                                 │ table │ linuxos │
-- │ public │ [ ] blog_post                                 │ table │ linuxos │
-- │ public │ [*] django_admin_log                          │ table │ linuxos │
-- │ public │ [ ] django_comment_flags                      │ table │ linuxos │
-- │ public │ [ ] django_comments                           │ table │ linuxos │
-- │ public │ [*] django_content_type                       │ table │ linuxos │
-- │ public │ [x] django_migrations                         │ table │ linuxos │
-- │ public │ [x] django_session                            │ table │ linuxos │
-- │ public │ [*] django_site                               │ table │ linuxos │
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


CREATE EXTENSION dblink;


DELETE FROM auth_permission;
DELETE FROM django_content_type;
DELETE FROM django_site;


-- auth

INSERT INTO django_content_type (id, app_label, model)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, app_label, model FROM django_content_type')
		AS t1(id integer, app_label character varying(100), model character varying(100));

INSERT INTO auth_group(id, name)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, name FROM auth_group')
		AS t1(id integer, name character varying(80));

INSERT INTO auth_permission(id, name, content_type_id, codename)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, name, content_type_id, codename FROM auth_permission')
		AS t1(id integer, name character varying(255), content_type_id integer, codename character varying(100));

INSERT INTO auth_group_permissions(id, group_id, permission_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, group_id, permission_id FROM auth_group_permissions')
		AS t1(id integer, group_id integer, permission_id integer);

INSERT INTO auth_user(id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, jabber, url, signature, display_mail, distribution, original_info, filtered_info, year)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, jabber, url, signature, display_mail, distribution, original_info, filtered_info, year FROM auth_user')
		AS t1(id integer, password character varying(128), last_login timestamp with time zone, is_superuser boolean, username character varying(30), first_name character varying(30), last_name character varying(30), email character varying(254), is_staff boolean, is_active boolean, date_joined timestamp with time zone, jabber character varying(127), url character varying(255), signature character varying(255), display_mail boolean, distribution character varying(50), original_info text, filtered_info text, year smallint);

INSERT INTO auth_user_groups(id, user_id, group_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, user_id, group_id FROM auth_user_groups')
		AS t1(id integer, user_id integer, group_id integer);

INSERT INTO auth_user_user_permissions(id, user_id, permission_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, user_id, permission_id FROM auth_user_user_permissions')
		AS t1(id integer, user_id integer, permission_id integer);


-- django

INSERT INTO django_admin_log(id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id FROM django_admin_log')
		AS t1(id integer, action_time timestamp with time zone, object_id text, object_repr character varying(200), action_flag smallint, change_message text, content_type_id integer, user_id integer);

INSERT INTO django_site(id, domain, name)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, domain, name FROM django_site')
		AS t1(id integer, domain character varying(100), name character varying(50));


-- accounts

INSERT INTO accounts_userrating(id, comments, articles, helped, news, wiki, rating, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, comments, articles, helped, news, wiki, rating, user_id FROM accounts_userrating')
		AS t1(id integer, comments integer, articles integer, helped integer, news integer, wiki integer, rating integer, user_id integer);
