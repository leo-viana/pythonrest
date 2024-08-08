USE master;
GO

IF EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = N'database_mapper_sqlserver')
    DROP DATABASE database_mapper_sqlserver;
GO

CREATE DATABASE database_mapper_sqlserver;
GO

USE database_mapper_sqlserver;
GO

SET QUOTED_IDENTIFIER ON;
GO

SET ANSI_NULLS ON;
GO

IF OBJECT_ID('variations_table', 'U') IS NOT NULL
    DROP TABLE [variations_table];
GO

CREATE TABLE [variations_table] (
    id_variations_table BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    not_null_col VARCHAR(10) NOT NULL,
    unique_col VARCHAR(20) NULL UNIQUE,
    binary_col VARBINARY(30) NULL,
    unsigned_col INT NULL,
    default_expression_bool_column TINYINT NULL DEFAULT 1,
    not_null_unique_col VARCHAR(50) NOT NULL UNIQUE,
    not_null_binary_col VARBINARY(60) NOT NULL,
    not_null_int_col INT NOT NULL,
    not_null_unique_varbinary_col VARBINARY(70) NOT NULL,
    not_null_unique_binary_generated_default_value_col VARCHAR(100) NULL DEFAULT 'DEFAULT',
    unique_varbinary_col VARBINARY(200) NULL UNIQUE,
    nullable_int_col INT NULL,
    datetime_default_value DATETIME NULL DEFAULT '1970-01-01 00:00:00'
);


IF OBJECT_ID('string_table', 'U') IS NOT NULL
    DROP TABLE [string_table];
GO

CREATE TABLE [string_table] (
    id_string_table UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    char_col CHAR(36) NULL UNIQUE,
    varchar_col VARCHAR(100) NULL UNIQUE,
    varchar_max_col VARCHAR(MAX) NULL,
    text_col TEXT,
    nchar_col NCHAR,
    nchar_fixed_col NCHAR(50),
    nvarchar_col NVARCHAR(100),
    nvarchar_max_col NVARCHAR(MAX),
    ntext_col NTEXT,
    binary_col BINARY(100),
    varbinary_col VARBINARY NULL UNIQUE,
    varbinary_fixed_col VARBINARY(1000) NULL UNIQUE,
    varbinary_max_col VARBINARY(MAX) NULL,
    image_col IMAGE,
    blob_col VARBINARY(MAX) NULL,
    enum_col VARCHAR(10) CHECK (enum_col IN ('enum1', 'enum2')) NULL,
    set_col VARCHAR(10) CHECK (set_col IN ('set1', 'set2')) NULL,
    variations_table_id BIGINT NOT NULL,
    CONSTRAINT fk_string_table_variations_table FOREIGN KEY (variations_table_id)
        REFERENCES [variations_table] (id_variations_table)
);

IF OBJECT_ID('numeric_table', 'U') IS NOT NULL
    DROP TABLE [numeric_table];
GO

CREATE TABLE [numeric_table] (
    id_numeric_table BIGINT NOT NULL PRIMARY KEY,
    bit_col BIT NULL,
    tinyint_col TINYINT NULL,
    smallint_col SMALLINT NULL,
    int_col INT NULL,
    bool_col TINYINT NULL,
    decimal_col DECIMAL(18, 2) NULL,
    numeric_col NUMERIC(18, 18) NULL,
    smallmoney_col SMALLMONEY,
    money_col MONEY,
    float_col FLOAT(3) NULL,
    real_col REAL NULL,
    variations_table_id BIGINT NOT NULL,
    CONSTRAINT fk_numeric_table_variations_table FOREIGN KEY (variations_table_id)
        REFERENCES [variations_table] (id_variations_table)
);

IF OBJECT_ID('date_and_time_table', 'U') IS NOT NULL
    DROP TABLE [date_and_time_table];
GO

CREATE TABLE [date_and_time_table] (
    id_date_and_time_table UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    datetime_col DATETIME NULL,
    datetime2_col DATETIME2,
    smalldatetime_col SMALLDATETIME,
    date_col DATE NULL,
    time_col TIME NULL,
    datetimeoffset_col DATETIMEOFFSET,
    timestamp_col TIMESTAMP NULL,
    variations_table_id BIGINT NULL,
    numeric_table_id BIGINT NOT NULL,
    CONSTRAINT fk_date_and_time_table_variations_table FOREIGN KEY (variations_table_id) 
        REFERENCES [variations_table] (id_variations_table),
    CONSTRAINT fk_date_and_time_table_numeric_table FOREIGN KEY (numeric_table_id) 
        REFERENCES [numeric_table] (id_numeric_table)
);

IF OBJECT_ID('spatial_table', 'U') IS NOT NULL
    DROP TABLE [spatial_table];
GO

CREATE TABLE [spatial_table] (
    id_spatial_table UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    linestring NVARCHAR(MAX) NULL,
    geometry NVARCHAR(MAX) NULL,
    geometrycollection NVARCHAR(MAX) NULL,
    point NVARCHAR(MAX) NULL,
    polygon NVARCHAR(MAX) NULL,
    multipoint NVARCHAR(MAX) NULL,
    multipolygon NVARCHAR(MAX) NULL,
    multilinestring NVARCHAR(MAX) NULL,
    variations_table_id BIGINT NOT NULL,
    CONSTRAINT fk_spatial_table_variations_table FOREIGN KEY (variations_table_id) 
        REFERENCES [variations_table] (id_variations_table)
);

IF OBJECT_ID('json_table', 'U') IS NOT NULL
    DROP TABLE [json_table];
GO

CREATE TABLE [json_table] (
    id_json_table UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    json_not_nullable_col NVARCHAR(MAX) NOT NULL,
    json_nvarcharmax_nullable_col NVARCHAR(MAX) NULL ,
    variations_table_id BIGINT NOT NULL,
    string_table_id UNIQUEIDENTIFIER NULL,
    spatial_table_id UNIQUEIDENTIFIER NOT NULL,
    CONSTRAINT fk_json_table_variations_table FOREIGN KEY (variations_table_id) 
        REFERENCES [variations_table] (id_variations_table),
    CONSTRAINT fk_json_table_string_table FOREIGN KEY (string_table_id) 
        REFERENCES [string_table] (id_string_table),
    CONSTRAINT fk_json_table_spatial_table FOREIGN KEY (spatial_table_id) 
        REFERENCES [spatial_table] (id_spatial_table)
);


IF OBJECT_ID('no_id_table', 'U') IS NOT NULL
    DROP TABLE [no_id_table];
GO

CREATE TABLE [no_id_table] (
    name VARCHAR(100) NULL,
    gender VARCHAR(20) NULL
);

IF OBJECT_ID('other_types_table', 'U') IS NOT NULL
    DROP TABLE [other_types_table];
GO

CREATE TABLE [other_types_table] (
    id INT PRIMARY KEY,
    geography_col GEOGRAPHY,
    geometry_col GEOMETRY,
    hierarchyid_col HIERARCHYID,
    rowversion_col ROWVERSION,
    sql_variant_col SQL_VARIANT,
    uniqueidentifier_col UNIQUEIDENTIFIER,
    xml_col XML
);
