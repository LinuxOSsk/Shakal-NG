-- ┌────────┬───────────────────────────────────────────────┬───────┬─────────┐
-- │ Schema │                     Name                      │ Type  │  Owner  │
-- ├────────┼───────────────────────────────────────────────┼───────┼─────────┤
-- │ public │ [*] account_emailaddress                      │ table │ linuxos │
-- │ public │ [x] account_emailconfirmation                 │ table │ linuxos │
-- │ public │ [x] accounts_remembertoken                    │ table │ linuxos │
-- │ public │ [*] accounts_userrating                       │ table │ linuxos │
-- │ public │ [*] article_article                           │ table │ linuxos │
-- │ public │ [*] article_category                          │ table │ linuxos │
-- │ public │ [*] attachment_attachment                     │ table │ linuxos │
-- │ public │ [x] attachment_attachmentimage                │ table │ linuxos │
-- │ public │ [*] attachment_uploadsession                  │ table │ linuxos │
-- │ public │ [*] auth_group                                │ table │ linuxos │
-- │ public │ [*] auth_group_permissions                    │ table │ linuxos │
-- │ public │ [*] auth_permission                           │ table │ linuxos │
-- │ public │ [*] auth_user                                 │ table │ linuxos │
-- │ public │ [*] auth_user_groups                          │ table │ linuxos │
-- │ public │ [*] auth_user_user_permissions                │ table │ linuxos │
-- │ public │ [*] blog_blog                                 │ table │ linuxos │
-- │ public │ [*] blog_post                                 │ table │ linuxos │
-- │ public │ [*] comments_commentflag                      │ table │ linuxos │
-- │ public │ [*] comments_comment                          │ table │ linuxos │
-- │ public │ [*] comments_rootheader                       │ table │ linuxos │
-- │ public │ [*] comments_userdiscussionattribute          │ table │ linuxos │
-- │ public │ [*] django_admin_log                          │ table │ linuxos │
-- │ public │ [*] django_content_type                       │ table │ linuxos │
-- │ public │ [x] django_migrations                         │ table │ linuxos │
-- │ public │ [x] django_session                            │ table │ linuxos │
-- │ public │ [*] django_site                               │ table │ linuxos │
-- │ public │ [*] forum_section                             │ table │ linuxos │
-- │ public │ [*] forum_topic                               │ table │ linuxos │
-- │ public │ [*] hitcount_hitcount                         │ table │ linuxos │
-- │ public │ [*] news_news                                 │ table │ linuxos │
-- │ public │ [*] notifications_event                       │ table │ linuxos │
-- │ public │ [*] notifications_inbox                       │ table │ linuxos │
-- │ public │ [*] polls_choice                              │ table │ linuxos │
-- │ public │ [*] polls_poll                                │ table │ linuxos │
-- │ public │ [*] polls_recordip                            │ table │ linuxos │
-- │ public │ [*] polls_recorduser                          │ table │ linuxos │
-- │ public │ [*] reversion_revision                        │ table │ linuxos │
-- │ public │ [*] reversion_version                         │ table │ linuxos │
-- │ public │ [*] wiki_page                                 │ table │ linuxos │
-- └────────┴───────────────────────────────────────────────┴───────┴─────────┘


CREATE EXTENSION dblink;


DELETE FROM auth_permission;
DELETE FROM django_content_type;
DELETE FROM django_site;


INSERT INTO django_content_type (id, app_label, model)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, app_label, model FROM django_content_type')
		AS t1(id integer, app_label character varying(100), model character varying(100));

UPDATE django_content_type SET app_label = 'comments' WHERE app_label = 'threaded_comments';

-- auth

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

INSERT INTO auth_user(id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, jabber, url, signature, display_mail, distribution, original_info, filtered_info, year, settings)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, jabber, url, signature, display_mail, distribution, original_info, filtered_info, year, '''' FROM auth_user')
		AS t1(id integer, password character varying(128), last_login timestamp with time zone, is_superuser boolean, username character varying(30), first_name character varying(30), last_name character varying(30), email character varying(254), is_staff boolean, is_active boolean, date_joined timestamp with time zone, jabber character varying(127), url character varying(255), signature character varying(255), display_mail boolean, distribution character varying(50), original_info text, filtered_info text, year smallint, settings text);

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


-- account

INSERT INTO account_emailaddress(email, verified, "primary", user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT email, true, true, MAX(id) FROM auth_user WHERE is_active = true AND email LIKE ''%@%'' GROUP BY email')
		AS t1(email character varying(254), verified boolean, "primary" boolean, user_id integer);

INSERT INTO account_emailaddress(email, verified, "primary", user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT email, false, true, MAX(id) FROM auth_user WHERE is_active = false AND email LIKE ''%@%'' GROUP BY email')
		AS t1(email character varying(254), verified boolean, "primary" boolean, user_id integer);


-- accounts

INSERT INTO accounts_userrating(id, comments, articles, helped, news, wiki, rating, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, comments, articles, helped, news, wiki, rating, user_id FROM accounts_userrating')
		AS t1(id integer, comments integer, articles integer, helped integer, news integer, wiki integer, rating integer, user_id integer);


-- attachments

INSERT INTO attachment_attachment(id, attachment, created, size, object_id, content_type_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, attachment, created, size, object_id, content_type_id FROM attachment_attachment')
		AS t1(id integer, attachment character varying(100), created timestamp with time zone, size integer, object_id integer, content_type_id integer);

INSERT INTO attachment_uploadsession(id, created, uuid)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, created, uuid FROM attachment_uploadsession')
		AS t1(id integer, created timestamp with time zone, uuid character varying(32));

-- article

INSERT INTO article_category(id, name, slug, description)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, name, slug, description FROM article_category')
		AS t1(id integer, name character varying(255), slug character varying(50), description text);

INSERT INTO article_article(id, title, slug, perex, annotation, content, authors_name, pub_time, created, updated, published, top, image, author_id, category_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, slug, perex, annotation, content, authors_name, pub_time, pub_time, updated, published, top, image, author_id, category_id FROM article_article')
		AS t1(id integer, title character varying(255), slug character varying(50), perex text, annotation text, content text, authors_name character varying(255), pub_time timestamp with time zone, created timestamp with time zone, updated timestamp with time zone, published boolean, top boolean, image character varying(100), author_id integer, category_id integer);


-- blog

INSERT INTO blog_blog(id, title, slug, original_description, filtered_description, original_sidebar, filtered_sidebar, created, updated, author_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, slug, original_description, filtered_description, original_sidebar, filtered_sidebar, created, updated, author_id FROM blog_blog')
		AS t1(id integer, title character varying(100), slug character varying(50), original_description text, filtered_description text, original_sidebar text, filtered_sidebar text, created timestamp with time zone, updated timestamp with time zone, author_id integer);

INSERT INTO blog_post(id, title, slug, original_perex, filtered_perex, original_content, filtered_content, pub_time, created, updated, linux, blog_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, slug, original_perex, filtered_perex, original_content, filtered_content, pub_time, created, updated, linux, blog_id FROM blog_post')
		AS t1(id integer, title character varying(100), slug character varying(50), original_perex text, filtered_perex text, original_content text, filtered_content text, pub_time timestamp with time zone, created timestamp with time zone, updated timestamp with time zone, linux boolean, blog_id integer);


-- threaded_comments

INSERT INTO comments_comment(id, object_id, subject, user_name, original_comment, filtered_comment, created, ip_address, is_public, is_removed, is_locked, updated, lft, rght, tree_id, level, content_type_id, parent_id, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, object_id, subject, user_name, original_comment, filtered_comment, submit_date, ip_address, is_public, is_removed, is_locked, updated, lft, rght, tree_id, level, content_type_id, parent_id, user_id FROM django_comments')
		AS t1(id integer, object_id text, subject character varying(100), user_name character varying(50), original_comment text, filtered_comment text, created timestamp with time zone, ip_address inet, is_public boolean, is_removed boolean, is_locked boolean, updated timestamp with time zone, lft integer, rght integer, tree_id integer, level integer, content_type_id integer, parent_id integer, user_id integer);

INSERT INTO comments_commentflag(id, flag, flag_date, comment_id, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, flag, flag_date, comment_id, user_id FROM django_comment_flags')
		AS t1(id integer, flag character varying(30), flag_date timestamp with time zone, comment_id integer, user_id integer);

ALTER TABLE comments_rootheader ALTER COLUMN last_comment DROP NOT NULL;
INSERT INTO comments_rootheader(id, pub_date, last_comment, comment_count, is_locked, object_id, content_type_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, pub_date, last_comment, comment_count, is_locked, object_id, content_type_id FROM threaded_comments_rootheader')
		AS t1(id integer, pub_date timestamp with time zone, last_comment timestamp with time zone, comment_count integer, is_locked boolean, object_id integer, content_type_id integer);
UPDATE comments_rootheader SET last_comment = (SELECT MAX(created) FROM comments_comment WHERE cast(comments_comment.object_id as integer) = comments_rootheader.object_id AND comments_comment.content_type_id = comments_rootheader.content_type_id) WHERE last_comment IS NULL;
UPDATE comments_rootheader SET last_comment = NOW() WHERE last_comment IS NULL;
ALTER TABLE comments_rootheader ALTER COLUMN last_comment SET NOT NULL;

INSERT INTO comments_userdiscussionattribute(id, time, watch, discussion_id, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, time, watch, discussion_id, user_id FROM threaded_comments_userdiscussionattribute')
		AS t1(id integer, time timestamp with time zone, watch boolean, discussion_id integer, user_id integer);


-- forum

INSERT INTO forum_section(id, name, slug, description)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, name, slug, description FROM forum_section')
		AS t1(id integer, name character varying(255), slug character varying(50), description text);

INSERT INTO forum_topic(id, title, original_text, filtered_text, created, updated, authors_name, is_removed, is_resolved, author_id, section_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, original_text, filtered_text, created, updated, authors_name, is_removed, is_resolved, author_id, section_id FROM forum_topic')
		AS t1(id integer, title character varying(100), original_text text, filtered_text text, created timestamp with time zone, updated timestamp with time zone, authors_name character varying(50), is_removed boolean, is_resolved boolean, author_id integer, section_id integer);


-- hitcount

INSERT INTO hitcount_hitcount(id, hits, object_id, content_type_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, hits, object_id, content_type_id FROM hitcount_hitcount')
		AS t1(id integer, hits integer, object_id integer, content_type_id integer);


-- news

INSERT INTO news_news(id, title, slug, original_short_text, filtered_short_text, original_long_text, filtered_long_text, created, updated, authors_name, approved, author_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, slug, original_short_text, filtered_short_text, original_long_text, filtered_long_text, created, updated, authors_name, approved, author_id FROM news_news')
		AS t1(id integer, title character varying(255), slug character varying(50), original_short_text text, filtered_short_text text, original_long_text text, filtered_long_text text, created timestamp with time zone, updated timestamp with time zone, authors_name character varying(255), approved boolean, author_id integer);


-- notifications

INSERT INTO notifications_event(id, object_id, time, action, level, message, author_id, content_type_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, object_id, time, action, level, message, author_id, content_type_id FROM notifications_event')
		AS t1(id integer, object_id integer, time timestamp with time zone, action character varying(1), level integer, message text, author_id integer, content_type_id integer);

INSERT INTO notifications_inbox(id, readed, event_id, recipient_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, readed, event_id, recipient_id FROM notifications_inbox')
		AS t1(id integer, readed boolean, event_id integer, recipient_id integer);


-- polls

INSERT INTO polls_poll(id, question, slug, object_id, active_from, created, updated, checkbox, approved, answer_count, content_type_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, question, slug, object_id, active_from, CASE WHEN active_from IS NULL THEN NOW() ELSE active_from END created, CASE WHEN active_from IS NULL THEN NOW() ELSE active_from END created, checkbox, approved, choice_count, content_type_id FROM polls_poll')
		AS t1(id integer, question text, slug character varying(50), object_id integer, active_from timestamp with time zone, created timestamp with time zone, updated timestamp with time zone, checkbox boolean, approved boolean, answer_count integer, content_type_id integer);

INSERT INTO polls_choice(id, choice, votes, poll_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, choice, votes, poll_id FROM polls_choice')
		AS t1(id integer, choice character varying(255), votes integer, poll_id integer);

INSERT INTO polls_recordip(id, ip, date, poll_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, ip, date, poll_id FROM polls_recordip')
		AS t1(id integer, ip inet, date timestamp with time zone, poll_id integer);

INSERT INTO polls_recorduser(id, date, poll_id, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, date, poll_id, user_id FROM polls_recorduser')
		AS t1(id integer, date timestamp with time zone, poll_id integer, user_id integer);


-- reversion

INSERT INTO reversion_revision(id, manager_slug, date_created, comment, user_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, manager_slug, date_created, comment, user_id FROM reversion_revision')
		AS t1(id integer, manager_slug character varying(191), date_created timestamp with time zone, comment text, user_id integer);

INSERT INTO reversion_version(id, object_id, object_id_int, format, serialized_data, object_repr, content_type_id, revision_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, object_id, object_id_int, format, serialized_data, object_repr, content_type_id, revision_id FROM reversion_version')
		AS t1(id integer, object_id text, object_id_int integer, format character varying(255), serialized_data text, object_repr text, content_type_id integer, revision_id integer);


-- wiki_page

INSERT INTO wiki_page(id, title, created, updated, slug, original_text, filtered_text, page_type, lft, rght, tree_id, level, last_author_id, parent_id)
	SELECT * FROM
		dblink('dbname=linuxos', 'SELECT id, title, created, updated, slug, original_text, filtered_text, page_type, lft, rght, tree_id, level, last_author_id, parent_id FROM wiki_page')
		AS t1(id integer, title character varying(255), created timestamp with time zone, updated timestamp with time zone, slug character varying(50), original_text text, filtered_text text, page_type character varying(1), lft integer, rght integer, tree_id integer, level integer, last_author_id integer, parent_id integer);


BEGIN;
SELECT setval(pg_get_serial_sequence('"django_admin_log"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "django_admin_log";
SELECT setval(pg_get_serial_sequence('"auth_permission"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_permission";
SELECT setval(pg_get_serial_sequence('"auth_group_permissions"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_group_permissions";
SELECT setval(pg_get_serial_sequence('"auth_group"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_group";
SELECT setval(pg_get_serial_sequence('"django_content_type"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "django_content_type";
SELECT setval(pg_get_serial_sequence('"django_site"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "django_site";
SELECT setval(pg_get_serial_sequence('"account_emailaddress"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "account_emailaddress";
SELECT setval(pg_get_serial_sequence('"account_emailconfirmation"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "account_emailconfirmation";
SELECT setval(pg_get_serial_sequence('"reversion_revision"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "reversion_revision";
SELECT setval(pg_get_serial_sequence('"reversion_version"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "reversion_version";
SELECT setval(pg_get_serial_sequence('"auth_user_groups"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user_groups";
SELECT setval(pg_get_serial_sequence('"auth_user_user_permissions"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user_user_permissions";
SELECT setval(pg_get_serial_sequence('"auth_user"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "auth_user";
SELECT setval(pg_get_serial_sequence('"accounts_userrating"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "accounts_userrating";
SELECT setval(pg_get_serial_sequence('"article_category"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "article_category";
SELECT setval(pg_get_serial_sequence('"article_article"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "article_article";
SELECT setval(pg_get_serial_sequence('"attachment_attachment"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "attachment_attachment";
SELECT setval(pg_get_serial_sequence('"attachment_uploadsession"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "attachment_uploadsession";
SELECT setval(pg_get_serial_sequence('"blog_blog"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "blog_blog";
SELECT setval(pg_get_serial_sequence('"blog_post"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "blog_post";
SELECT setval(pg_get_serial_sequence('"forum_section"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "forum_section";
SELECT setval(pg_get_serial_sequence('"forum_topic"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "forum_topic";
SELECT setval(pg_get_serial_sequence('"hitcount_hitcount"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "hitcount_hitcount";
SELECT setval(pg_get_serial_sequence('"news_news"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "news_news";
SELECT setval(pg_get_serial_sequence('"notifications_event"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_event";
SELECT setval(pg_get_serial_sequence('"notifications_inbox"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_inbox";
SELECT setval(pg_get_serial_sequence('"polls_poll"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "polls_poll";
SELECT setval(pg_get_serial_sequence('"polls_choice"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "polls_choice";
SELECT setval(pg_get_serial_sequence('"polls_recordip"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "polls_recordip";
SELECT setval(pg_get_serial_sequence('"polls_recorduser"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "polls_recorduser";
SELECT setval(pg_get_serial_sequence('"comments_comment"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "comments_comment";
SELECT setval(pg_get_serial_sequence('"comments_commentflag"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "comments_commentflag";
SELECT setval(pg_get_serial_sequence('"comments_rootheader"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "comments_rootheader";
SELECT setval(pg_get_serial_sequence('"comments_userdiscussionattribute"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "comments_userdiscussionattribute";
SELECT setval(pg_get_serial_sequence('"wiki_page"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "wiki_page";

COMMIT;
