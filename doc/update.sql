--
-- Name: account_emailaddress; Type: TABLE; Schema: public; Owner: linuxos; Tablespace: 
--

CREATE TABLE account_emailaddress (
	id integer NOT NULL,
	email character varying(254) NOT NULL,
	verified boolean NOT NULL,
	"primary" boolean NOT NULL,
	user_id integer NOT NULL
);


ALTER TABLE public.account_emailaddress OWNER TO linuxos;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE; Schema: public; Owner: linuxos
--

CREATE SEQUENCE account_emailaddress_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MINVALUE
	NO MAXVALUE
	CACHE 1;


ALTER TABLE public.account_emailaddress_id_seq OWNER TO linuxos;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: linuxos
--

ALTER SEQUENCE account_emailaddress_id_seq OWNED BY account_emailaddress.id;



--
-- Name: account_emailconfirmation; Type: TABLE; Schema: public; Owner: linuxos; Tablespace: 
--

CREATE TABLE account_emailconfirmation (
	id integer NOT NULL,
	created timestamp with time zone NOT NULL,
	sent timestamp with time zone,
	key character varying(64) NOT NULL,
	email_address_id integer NOT NULL
);


ALTER TABLE public.account_emailconfirmation OWNER TO linuxos;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE; Schema: public; Owner: linuxos
--

CREATE SEQUENCE account_emailconfirmation_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MINVALUE
	NO MAXVALUE
	CACHE 1;


ALTER TABLE public.account_emailconfirmation_id_seq OWNER TO linuxos;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: linuxos
--

ALTER SEQUENCE account_emailconfirmation_id_seq OWNED BY account_emailconfirmation.id;

--
-- Name: attachment_attachmentimage; Type: TABLE; Schema: public; Owner: linuxos; Tablespace: 
--

CREATE TABLE attachment_attachmentimage (
	attachment_ptr_id integer NOT NULL,
	width integer NOT NULL,
	height integer NOT NULL
);


ALTER TABLE public.attachment_attachmentimage OWNER TO linuxos;

ALTER TABLE auth_remember_remembertoken ALTER COLUMN token_hash TYPE character varying(255);
ALTER TABLE auth_remember_remembertoken ADD CLUMN created_initial timestamp with time zone NOT NULL DEFAULT NOW();
ALTER TABLE auth_remember_remembertoken ALTER COLUMN created_initial DROP DEFAULT;
ALTER TABLE auth_permission ALTER COLUMN name TYPE character varying(255);

ALTER TABLE auth_user ALTER COLUMN last_login DROP NOT NULL;
ALTER TABLE auth_user ALTER COLUMN email TYPE character varying(254);
ALTER TABLE auth_user ALTER COLUMN filtered_info text NOT NULL;

ALTER TABLE django_content_type DROP COLUMN name;

--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: linuxos; Tablespace: 
--

CREATE TABLE django_migrations (
	id integer NOT NULL,
	app character varying(255) NOT NULL,
	name character varying(255) NOT NULL,
	applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO linuxos;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: linuxos
--

CREATE SEQUENCE django_migrations_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MINVALUE
	NO MAXVALUE
	CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO linuxos;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: linuxos
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;

DROP TABLE registration_registrationprofile;
DROP SEQUENCE registration_registrationprofile_id_seq;

ALTER TABLE reversion_revision ALTER COLUMN manager_slug TYPE character varying(191);

UPDATE threaded_comments_rootheader SET last_comment=NOW() WHERE last_comment IS NULL;
ALTER TABLE threaded_comments_rootheader ALTER COLUMN last_comment SET NOT NULL;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: linuxos
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);
