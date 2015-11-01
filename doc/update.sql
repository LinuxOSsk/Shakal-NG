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
-- Name: accounts_remembertoken; Type: TABLE; Schema: public; Owner: linuxos; Tablespace: 
--

CREATE TABLE accounts_remembertoken (
	token_hash character varying(255) NOT NULL,
	created timestamp with time zone NOT NULL,
	user_id integer NOT NULL
);


ALTER TABLE public.accounts_remembertoken OWNER TO linuxos;

