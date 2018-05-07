CREATE TABLE ms_tnt_version
(
  id serial,
  version character varying(255),
  description character varying(255),
  "timestamp" timestamp without time zone,
  CONSTRAINT ms_tnt_version_pkey PRIMARY KEY (id)
);

CREATE TABLE ms_lib_category
(
  id serial,
  categoryid integer,
  name character varying(255),
  CONSTRAINT ms_lib_category_pkey PRIMARY KEY (id)
);

INSERT INTO ms_lib_category(categoryid, name) VALUES
	(0, 'Uncategorized'),
	(1, 'Command'),
	(2, 'Product Related Conversation'),
	(3, 'General Conversation');

CREATE TABLE ms_lib_context
(
  id serial,
  contextid integer,
  name character varying(255),
  categoryid integer,
  CONSTRAINT ms_lib_context_pkey PRIMARY KEY (id)
);

INSERT INTO ms_lib_context(contextid, name, categoryid) VALUES
	(0, 'No Context', (SELECT id FROM ms_lib_category WHERE name = 'Uncategorized')),
	(0, 'No Context', (SELECT id FROM ms_lib_category WHERE name = 'Command')),
	(0, 'No Context', (SELECT id FROM ms_lib_category WHERE name = 'Product Related Conversation')),
	(0, 'No Context', (SELECT id FROM ms_lib_category WHERE name = 'General Conversation'));

CREATE TABLE ms_nn_network
(
  id serial,
  name character varying(255),
  learning_rate numeric(10,7),
  CONSTRAINT ms_nn_network_pkey PRIMARY KEY (id),
  CONSTRAINT ms_nn_network_unq_name UNIQUE (name)
);

CREATE TABLE tr_lib_rawword
(
  id serial,
  rawword character varying(255),
  wordid integer,
  CONSTRAINT tr_lib_rawword_pkey PRIMARY KEY (id)
);

CREATE TABLE tr_lib_record
(
  id serial,
  sentence character varying(255),
  contextid integer,
  intentid integer,
  recordtime timestamp without time zone,
  CONSTRAINT tr_lib_record_pkey PRIMARY KEY (id)
);

CREATE TABLE tr_lib_response
(
  id serial,
  sentence character varying(255),
  contextid integer,
  intentid integer,
  CONSTRAINT tr_lib_response_pkey PRIMARY KEY (id)
);

CREATE TABLE tr_lib_training
(
  id serial,
  recordid integer,
  contextid integer,
  intentid integer,
  CONSTRAINT tr_lib_training_pkey PRIMARY KEY (id)
);

CREATE TABLE tr_tnt_user
(
  id serial,
  username character varying(255),
  password_hash character varying(255),
  CONSTRAINT tr_tnt_user_pkey PRIMARY KEY (id)
);
