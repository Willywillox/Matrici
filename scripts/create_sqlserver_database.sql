-- Script per creare database SQL Server per Matrici
-- Eseguire in SQL Server Management Studio o con sqlcmd

-- Crea database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Matrici')
BEGIN
    CREATE DATABASE Matrici;
END
GO

USE Matrici;
GO

-- Tabella Anagrafica Operatori
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Anagrafica_Operatori')
BEGIN
    CREATE TABLE Anagrafica_Operatori (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Nome NVARCHAR(50) NOT NULL,
        Cognome NVARCHAR(50) NOT NULL,
        ID_SAP NVARCHAR(20) UNIQUE NOT NULL,
        Tipo_Contratto NVARCHAR(50),
        FTE FLOAT,
        Ore_Settimana FLOAT,
        ID_Turno NVARCHAR(20),
        Ora_Inizio_Turno TIME,
        Ora_Fine_Turno TIME,
        Ora_Inizio_Turno_Spezzato TIME,
        Ora_Fine_Turno_Spezzato TIME,
        Inizio_Strao_1 TIME,
        Fine_Strao_1 TIME,
        Inizio_Strao_2 TIME,
        Fine_Strao_2 TIME,
        Inizio_Strao_3 TIME,
        Fine_Strao_3 TIME,
        Inizio_Pausa_1 TIME,
        Fine_Pausa_1 TIME,
        Inizio_Pausa_2 TIME,
        Fine_Pausa_2 TIME,
        Inizio_Pausa_3 TIME,
        Fine_Pausa_3 TIME,
        Inizio_Pausa_4 TIME,
        Fine_Pausa_4 TIME,
        Inizio_Pausa_5 TIME,
        Fine_Pausa_5 TIME,
        Tipo_Giust_1 NVARCHAR(50),
        Inizio_Giust_1 TIME,
        Fine_Giust_1 TIME,
        Tipo_Giust_2 NVARCHAR(50),
        Inizio_Giust_2 TIME,
        Fine_Giust_2 TIME,
        Tipo_Giust_3 NVARCHAR(50),
        Inizio_Giust_3 TIME,
        Fine_Giust_3 TIME,
        Tipo_Giust_4 NVARCHAR(50),
        Inizio_Giust_4 TIME,
        Fine_Giust_4 TIME,
        Tipo_Giust_5 NVARCHAR(50),
        Inizio_Giust_5 TIME,
        Fine_Giust_5 TIME,
        Etichetta_Skill NVARCHAR(100),
        Data_Riferimento DATE NOT NULL,
        -- Campi per tracking multi-utente
        CreatedBy NVARCHAR(50) DEFAULT SYSTEM_USER,
        CreatedDate DATETIME DEFAULT GETDATE(),
        ModifiedBy NVARCHAR(50) DEFAULT SYSTEM_USER,
        ModifiedDate DATETIME DEFAULT GETDATE(),
        RowVersion ROWVERSION  -- Per ottimistic locking
    );

    CREATE INDEX IX_Anagrafica_Data ON Anagrafica_Operatori(Data_Riferimento);
    CREATE INDEX IX_Anagrafica_Skill ON Anagrafica_Operatori(Etichetta_Skill);
END
GO

-- Tabella Cambio Skill
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Cambio_Skill')
BEGIN
    CREATE TABLE Cambio_Skill (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ID_SAP NVARCHAR(20) NOT NULL,
        Data_Riferimento DATE NOT NULL,
        Ora_Inizio TIME NOT NULL,
        Ora_Fine TIME NOT NULL,
        Skill_Temporaneo NVARCHAR(100) NOT NULL,
        Note NVARCHAR(255),
        CreatedBy NVARCHAR(50) DEFAULT SYSTEM_USER,
        CreatedDate DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_CambioSkill_Data ON Cambio_Skill(Data_Riferimento);
END
GO

-- Tabella Forecast
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Forecast')
BEGIN
    CREATE TABLE Forecast (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Data_Riferimento DATE NOT NULL,
        Fascia_Oraria DATETIME NOT NULL,
        Skill NVARCHAR(100) NOT NULL,
        Volumi_Attesi INT,
        Produttivita_Target FLOAT,
        FTE_Richiesti FLOAT,
        CreatedBy NVARCHAR(50) DEFAULT SYSTEM_USER,
        CreatedDate DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_Forecast_Data ON Forecast(Data_Riferimento, Fascia_Oraria);
END
GO

-- Tabella Skills
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Skills')
BEGIN
    CREATE TABLE Skills (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Codice_Skill NVARCHAR(50) UNIQUE NOT NULL,
        Descrizione NVARCHAR(255),
        Produttivita_Default FLOAT
    );
END
GO

-- Tabella Storico Turni
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Storico_Turni')
BEGIN
    CREATE TABLE Storico_Turni (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ID_SAP NVARCHAR(20) NOT NULL,
        Data_Riferimento DATE NOT NULL,
        Tipo_Turno NVARCHAR(20),
        Ora_Inizio TIME,
        Ora_Fine TIME,
        Skill NVARCHAR(100),
        Note NVARCHAR(255),
        Data_Inserimento DATETIME DEFAULT GETDATE()
    );
END
GO

-- Tabella Metadata per tracking modifiche
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Metadata')
BEGIN
    CREATE TABLE Metadata (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        TableName NVARCHAR(100) NOT NULL,
        LastModified DATETIME NOT NULL DEFAULT GETDATE(),
        ModifiedBy NVARCHAR(50) NOT NULL DEFAULT SYSTEM_USER
    );

    CREATE INDEX IX_Metadata_Table ON Metadata(TableName, LastModified);
END
GO

-- Tabella Utenti Attivi (per vedere chi è online)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Active_Users')
BEGIN
    CREATE TABLE Active_Users (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        UserID NVARCHAR(50) NOT NULL,
        ComputerName NVARCHAR(100),
        LastActivity DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UQ_ActiveUser UNIQUE (UserID, ComputerName)
    );
END
GO

-- Trigger per aggiornare ModifiedDate automaticamente
IF OBJECT_ID('TR_Anagrafica_Update', 'TR') IS NOT NULL
    DROP TRIGGER TR_Anagrafica_Update;
GO

CREATE TRIGGER TR_Anagrafica_Update
ON Anagrafica_Operatori
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Anagrafica_Operatori
    SET ModifiedDate = GETDATE(),
        ModifiedBy = SYSTEM_USER
    WHERE ID IN (SELECT ID FROM inserted);

    -- Aggiorna metadata
    INSERT INTO Metadata (TableName, LastModified, ModifiedBy)
    VALUES ('Anagrafica_Operatori', GETDATE(), SYSTEM_USER);
END
GO

-- Stored procedure per cleanup utenti inattivi
IF OBJECT_ID('sp_CleanupInactiveUsers', 'P') IS NOT NULL
    DROP PROCEDURE sp_CleanupInactiveUsers;
GO

CREATE PROCEDURE sp_CleanupInactiveUsers
AS
BEGIN
    -- Rimuovi utenti inattivi da più di 5 minuti
    DELETE FROM Active_Users
    WHERE DATEDIFF(MINUTE, LastActivity, GETDATE()) > 5;
END
GO

-- Inserisci skills di default
IF NOT EXISTS (SELECT * FROM Skills WHERE Codice_Skill = 'CUSTOMER_CARE')
BEGIN
    INSERT INTO Skills (Codice_Skill, Descrizione, Produttivita_Default)
    VALUES
        ('CUSTOMER_CARE', 'Assistenza clienti', 8.0),
        ('BACK_OFFICE', 'Back office', 12.0),
        ('TECHNICAL_SUPPORT', 'Supporto tecnico', 6.0);
END
GO

PRINT 'Database Matrici creato con successo!';
PRINT 'Tabelle create:';
PRINT '- Anagrafica_Operatori';
PRINT '- Cambio_Skill';
PRINT '- Forecast';
PRINT '- Skills';
PRINT '- Storico_Turni';
PRINT '- Metadata';
PRINT '- Active_Users';
PRINT '';
PRINT 'Trigger e stored procedures configurati.';
PRINT 'Database pronto per uso multi-utente!';
