CREATE TABLE canal (
	id VARCHAR(30) NOT NULL,
	nombre VARCHAR(60) NOT NULL,
	tipo VARCHAR(30) NOT NULL,
	color VARCHAR(10) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE grupo_busqueda (
	id VARCHAR(20) NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	intencion VARCHAR(40) NOT NULL,
	elegible BOOLEAN NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE mercado (
	id VARCHAR(20) NOT NULL,
	nombre VARCHAR(80) NOT NULL,
	region VARCHAR(30) NOT NULL,
	tamano FLOAT NOT NULL,
	grupo VARCHAR(30) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE snapshot (
	id VARCHAR(60) NOT NULL,
	corte DATE NOT NULL,
	semilla INTEGER NOT NULL,
	version VARCHAR(30) NOT NULL,
	checksum VARCHAR(64) NOT NULL,
	manifiesto JSON NOT NULL,
	estado VARCHAR(20) NOT NULL,
	creado TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE busqueda_diaria (
	snapshot_id VARCHAR(60) NOT NULL,
	fecha DATE NOT NULL,
	mercado_id VARCHAR(20) NOT NULL,
	grupo_id VARCHAR(20) NOT NULL,
	fuente VARCHAR(8) NOT NULL,
	impresiones INTEGER NOT NULL,
	clics INTEGER NOT NULL,
	gasto_cent BIGINT NOT NULL,
	conversiones INTEGER,
	posicion FLOAT,
	competencia FLOAT NOT NULL,
	PRIMARY KEY (snapshot_id, fecha, mercado_id, grupo_id, fuente),
	CHECK (clics >= 0 AND clics <= impresiones AND gasto_cent >= 0),
	CHECK (fuente IN ('SEO', 'SEM')),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id),
	FOREIGN KEY(mercado_id) REFERENCES mercado (id),
	FOREIGN KEY(grupo_id) REFERENCES grupo_busqueda (id)
);

CREATE INDEX ix_busqueda_snapshot_fecha ON busqueda_diaria (snapshot_id, fecha, mercado_id);

CREATE TABLE campana (
	id VARCHAR(20) NOT NULL,
	canal_id VARCHAR(30) NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	categoria VARCHAR(30) NOT NULL,
	objetivo VARCHAR(40) NOT NULL,
	inicio DATE NOT NULL,
	fin DATE NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(canal_id) REFERENCES canal (id)
);

CREATE TABLE decision (
	id VARCHAR(50) NOT NULL,
	snapshot_id VARCHAR(60) NOT NULL,
	ejecucion_id VARCHAR(50) NOT NULL,
	estado VARCHAR(25) NOT NULL,
	motivo VARCHAR(1000) NOT NULL,
	evidencia JSON NOT NULL,
	creado TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (ejecucion_id),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id)
);

CREATE TABLE medios_diarios (
	snapshot_id VARCHAR(60) NOT NULL,
	fecha DATE NOT NULL,
	mercado_id VARCHAR(20) NOT NULL,
	canal_id VARCHAR(30) NOT NULL,
	gasto_cent BIGINT NOT NULL,
	impresiones BIGINT,
	clics INTEGER,
	conversiones INTEGER NOT NULL,
	ingresos_cent BIGINT NOT NULL,
	fuente VARCHAR(50) NOT NULL,
	ventana_dias INTEGER NOT NULL,
	PRIMARY KEY (snapshot_id, fecha, mercado_id, canal_id),
	CHECK (gasto_cent >= 0 AND conversiones >= 0 AND ingresos_cent >= 0),
	CHECK (clics IS NULL OR (clics >= 0 AND clics <= impresiones)),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id),
	FOREIGN KEY(mercado_id) REFERENCES mercado (id),
	FOREIGN KEY(canal_id) REFERENCES canal (id)
);

CREATE INDEX ix_medios_fecha_mercado ON medios_diarios (snapshot_id, fecha, mercado_id, canal_id);

CREATE TABLE negocio_diario (
	snapshot_id VARCHAR(60) NOT NULL,
	fecha DATE NOT NULL,
	mercado_id VARCHAR(20) NOT NULL,
	pedidos INTEGER NOT NULL,
	ventas_cent BIGINT NOT NULL,
	coste_cent BIGINT NOT NULL,
	margen_cent BIGINT NOT NULL,
	visitas INTEGER NOT NULL,
	promocion BOOLEAN NOT NULL,
	demanda_proxy FLOAT NOT NULL,
	PRIMARY KEY (snapshot_id, fecha, mercado_id),
	CHECK (pedidos >= 0 AND ventas_cent >= 0 AND coste_cent >= 0),
	CHECK (margen_cent = ventas_cent - coste_cent),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id),
	FOREIGN KEY(mercado_id) REFERENCES mercado (id)
);

CREATE INDEX ix_negocio_fecha_mercado ON negocio_diario (snapshot_id, fecha, mercado_id);

CREATE TABLE campana_diaria (
	snapshot_id VARCHAR(60) NOT NULL,
	fecha DATE NOT NULL,
	mercado_id VARCHAR(20) NOT NULL,
	campana_id VARCHAR(20) NOT NULL,
	gasto_cent BIGINT NOT NULL,
	PRIMARY KEY (snapshot_id, fecha, mercado_id, campana_id),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id),
	FOREIGN KEY(mercado_id) REFERENCES mercado (id),
	FOREIGN KEY(campana_id) REFERENCES campana (id)
);

CREATE TABLE creativo (
	id VARCHAR(20) NOT NULL,
	campana_id VARCHAR(20) NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	asset VARCHAR(150) NOT NULL,
	formato VARCHAR(40) NOT NULL,
	atributos JSON NOT NULL,
	licencia VARCHAR(120) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(campana_id) REFERENCES campana (id)
);

CREATE TABLE creatividad_diaria (
	snapshot_id VARCHAR(60) NOT NULL,
	fecha DATE NOT NULL,
	mercado_id VARCHAR(20) NOT NULL,
	creativo_id VARCHAR(20) NOT NULL,
	impresiones INTEGER NOT NULL,
	clics INTEGER NOT NULL,
	conversiones INTEGER NOT NULL,
	gasto_cent BIGINT NOT NULL,
	frecuencia FLOAT NOT NULL,
	PRIMARY KEY (snapshot_id, fecha, mercado_id, creativo_id),
	CHECK (clics >= 0 AND clics <= impresiones AND conversiones <= clics),
	FOREIGN KEY(snapshot_id) REFERENCES snapshot (id),
	FOREIGN KEY(mercado_id) REFERENCES mercado (id),
	FOREIGN KEY(creativo_id) REFERENCES creativo (id)
);

CREATE INDEX ix_creatividad_snapshot_fecha ON creatividad_diaria (snapshot_id, fecha, mercado_id);
