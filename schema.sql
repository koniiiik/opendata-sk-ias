CREATE TABLE format(id integer primary key autoincrement, nazov text);
CREATE TABLE raw(cislo integer, nazov text, ucel text, prevadzkovatel text, institucia text, elektronizacia text, format text, rozsah text, aktualnost text, metadata text, zverejnitelnost text, odovodnenie text, plan text, vyjadrenie text);
CREATE TABLE zverejnitelnost (id integer primary key autoincrement, nazov text);
CREATE TABLE vyjadrenie(id integer primary key autoincrement, nazov text);
CREATE TABLE dataset(id integer not null, nazov text not null, ucel text not null, prevadzkovatel text not null, institucia text not null, elektronicky integer not null, strukturovane integer not null, rozsah text not null, aktualnost text not null, metadata text not null, zverejnitelnost integer not null, odovodnenie text not null, plan text, vyjadrenie integer not null);
CREATE TABLE dataset_format(dataset_id INT,format_id INT);
CREATE TABLE elektronicky(id INT,stav TEXT);
CREATE TABLE strukturovane(id INT,stav TEXT);
CREATE VIEW view_dataset_wide as select d.id, d.nazov, d.ucel, d.prevadzkovatel, d.institucia, e.stav as elektronicky, s.stav as strukturovane, f.formaty, d.rozsah, d.aktualnost, d.metadata, z.nazov as zverejnitelnost, d.odovodnenie, d.plan, v.nazov as vyjadrenie from dataset d inner join elektronicky e on e.id = d.elektronicky inner join strukturovane s on s.id = d.strukturovane inner join zverejnitelnost z on z.id = d.zverejnitelnost inner join vyjadrenie v on v.id = d.vyjadrenie inner join (select fd.dataset_id, group_concat(ff.nazov, ', ') as formaty from format ff inner join dataset_format fd on fd.format_id = ff.id group by fd.dataset_id) f on f.dataset_id = d.id;
CREATE VIEW view_dataset as select id, nazov, elektronicky, strukturovane, formaty, aktualnost, zverejnitelnost, plan, vyjadrenie from view_dataset_wide;
CREATE TABLE ckan_dataset(
    ckan_id varchar(40),
    ckan_name text,
    dataset_id integer references dataset (id));
CREATE TABLE ckan_resource(
    ckan_id varchar(40) not null,
    ckan_name text not null,
    status text,
    url text,
    star INT,
    guessed_ext varchar(20),
    content_type text
);
CREATE VIEW not_zverejnene as select d.* from view_dataset_wide d where not exists(select * from ckan_dataset c where c.dataset_id = d.id and c.ckan_id is not null);
