-- 由 scripts/generate_pg_schema.py 根据 ORM 模型自动生成, 请勿手改

CREATE TABLE "group" (
	id SERIAL NOT NULL, 
	open_id VARCHAR(32) NOT NULL, 
	admins JSON NOT NULL, 
	black_list JSON NOT NULL, 
	parent_open_id VARCHAR(32), 
	PRIMARY KEY (id), 
	UNIQUE (open_id), 
	FOREIGN KEY(parent_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_group_id ON "group" (id);

CREATE TABLE login_ip (
	id SERIAL NOT NULL, 
	ip TEXT NOT NULL, 
	city VARCHAR(32), 
	record_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	user_open_id VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_login_ip_id ON login_ip (id);
CREATE INDEX ix_login_ip_user_open_id ON login_ip (user_open_id);

CREATE TABLE login_uuid (
	id SERIAL NOT NULL, 
	uuid TEXT NOT NULL, 
	record_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	user_open_id VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_login_uuid_user_open_id ON login_uuid (user_open_id);
CREATE INDEX ix_login_uuid_id ON login_uuid (id);

CREATE TABLE statistic (
	id SERIAL NOT NULL, 
	key VARCHAR(32) NOT NULL, 
	value JSON NOT NULL, 
	PRIMARY KEY (id)
);


CREATE TABLE group_config (
	id SERIAL NOT NULL, 
	group_open_id VARCHAR(32) NOT NULL, 
	allow_default_getmapimage BOOLEAN NOT NULL, 
	allow_default_getmapfile BOOLEAN NOT NULL, 
	allow_default_getworldfile BOOLEAN NOT NULL, 
	show_ip_location BOOLEAN NOT NULL, 
	allow_admin_addadmin BOOLEAN NOT NULL, 
	disabled_whitelist_cooldown BOOLEAN NOT NULL, 
	disabled_show_playerlist BOOLEAN NOT NULL, 
	max_sign_coins INTEGER NOT NULL, 
	min_sign_coins INTEGER NOT NULL, 
	constant_sign_reward INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_group_config_id ON group_config (id);

CREATE TABLE server (
	id SERIAL NOT NULL, 
	group_open_id VARCHAR(32) NOT NULL, 
	token VARCHAR(36) NOT NULL, 
	ip TEXT NOT NULL, 
	port INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_server_group_open_id ON server (group_open_id);
CREATE INDEX ix_server_token ON server (token);
CREATE INDEX ix_server_id ON server (id);

CREATE TABLE shop_list (
	id SERIAL NOT NULL, 
	name VARCHAR(20) NOT NULL, 
	group_open_id VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_shop_list_id ON shop_list (id);

CREATE TABLE "user" (
	id SERIAL NOT NULL, 
	group_open_id VARCHAR(32) NOT NULL, 
	open_id VARCHAR(32) NOT NULL, 
	name VARCHAR(32), 
	money INTEGER NOT NULL, 
	sign_days INTEGER NOT NULL, 
	sign_consistency INTEGER NOT NULL, 
	last_login TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_sign TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	last_rename TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_user_group_open_id ON "user" (group_open_id);
CREATE INDEX ix_user_name ON "user" (name);
CREATE INDEX ix_user_id ON "user" (id);
CREATE INDEX ix_user_open_id ON "user" (open_id);

CREATE TABLE shop_item (
	id SERIAL NOT NULL, 
	name VARCHAR(20) NOT NULL, 
	type VARCHAR(10) NOT NULL, 
	item_id INTEGER NOT NULL, 
	item_stack INTEGER NOT NULL, 
	item_prefix INTEGER NOT NULL, 
	command VARCHAR(50) NOT NULL, 
	list_id INTEGER NOT NULL, 
	group_open_id VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(list_id) REFERENCES shop_list (id), 
	FOREIGN KEY(group_open_id) REFERENCES "group" (open_id)
);

CREATE INDEX ix_shop_item_id ON shop_item (id);
