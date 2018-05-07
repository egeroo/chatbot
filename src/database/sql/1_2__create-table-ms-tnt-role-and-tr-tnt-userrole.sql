CREATE TABLE ms_tnt_role (
	id serial,
	name character varying(255),
	CONSTRAINT ms_tnt_role_pkey PRIMARY KEY (id)
);

INSERT INTO ms_tnt_role(id, name) VALUES
	(1, 'Super Admin'),
	(2, 'Admin'),
	(3, 'User');

CREATE TABLE tr_tnt_userrole (
	id serial,
	userid integer,
	roleid integer,
	CONSTRAINT tr_tnt_userrole_pkey PRIMARY KEY (id)
);

INSERT INTO tr_tnt_user (id, username, password_hash) VALUES
	(1, 'admin', '$6$rounds=656000$AcwCxALzR95ZbVpP$.OF.vkJDm.r77AJqcSZJBn5kHYRYQvYGUAqYULZwK/o5mbnSw9xIPtb9SzfMFClUX.i1lS/xwNOigtC9H6TpV/');

INSERT INTO tr_tnt_userrole(userid, roleid) VALUES
	(1, 1),
	(1, 2),
	(1, 3);