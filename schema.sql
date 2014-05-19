CREATE TABLE format(
    id integer primary key autoincrement,
    nazov text
);

CREATE TABLE raw(
    cislo integer,
    nazov text,
    ucel text,
    prevadzkovatel text,
    institucia text,
    elektronizacia text,
    format text,
    rozsah text,
    aktualnost text,
    metadata text,
    zverejnitelnost text,
    odovodnenie text,
    plan text,
    vyjadrenie text
);

CREATE TABLE zverejnitelnost (
    id integer primary key autoincrement,
    nazov text
);

CREATE TABLE vyjadrenie(
    id integer primary key autoincrement,
    nazov text
);

CREATE TABLE dataset(
    id integer not null,
    nazov text not null,
    ucel text not null,
    prevadzkovatel text not null,
    institucia text not null,
    elektronicky integer not null,
    strukturovane integer not null,
    rozsah text not null,
    aktualnost text not null,
    metadata text not null,
    zverejnitelnost integer not null,
    odovodnenie text not null,
    plan text,
    vyjadrenie integer not null
);

CREATE TABLE dataset_format(
    dataset_id INT,
    format_id INT
);

CREATE TABLE elektronicky(
    id INT,
    stav TEXT
);

CREATE TABLE strukturovane(
    id INT,
    stav TEXT
);

CREATE TABLE ckan_dataset(
    ckan_id varchar(40) not null,
    ckan_name text not null,
    dataset_id integer references dataset (id)
);
