-- Tables: SplitType, Class, Image, Label
-- Store Procedure: InsertClass, InsertImage, InsertLabel


-- Dataset Splits Table --
IF OBJECT_ID('dbo.SplitType', 'U') IS NULL
BEGIN
    CREATE TABLE SplitType(
        splitID    INT PRIMARY KEY,
        splitName VARCHAR(10) NOT NULL UNIQUE
    );
END;

IF NOT EXISTS (SELECT 1 FROM SplitType WHERE splitID = 0)
BEGIN
    INSERT INTO SplitType (splitID, splitName) VALUES
    (0, 'train'),
    (1, 'val'),
    (2, 'test');
END;

-- Class Table --
IF OBJECT_ID('dbo.Class', 'U') IS NULL
BEGIN
    CREATE TABLE Class(
        classID INT PRIMARY KEY,
        className VARCHAR(20) NOT NULL UNIQUE
    );
END;

-- Image Table --
IF OBJECT_ID('dbo.Image', 'U') IS NULL
BEGIN
    CREATE TABLE Image(
        imageID   INT IDENTITY(1,1) PRIMARY KEY,
        filePath  VARCHAR(500) NOT NULL,
        splitID   INT NOT NULL,
        CONSTRAINT FK_Image_SplitType FOREIGN KEY (splitID) REFERENCES SplitType(splitID)
    );
END;

-- Label Table --
IF OBJECT_ID('dbo.Label', 'U') IS NULL
BEGIN
    CREATE TABLE Label(
        imageID     INT NOT NULL,
        classID     INT NOT NULL,
        xCenter     FLOAT NOT NULL,
        yCenter     FLOAT NOT NULL,
        boxWidth    FLOAT NOT NULL,
        boxHeight   FLOAT NOT NULL,
        CONSTRAINT FK_Label_Image FOREIGN KEY (imageID) REFERENCES Image(imageID),
        CONSTRAINT FK_Label_Class FOREIGN KEY (classID) REFERENCES Class(classID)
    );
END;

-- Stored Procedure
EXEC('
-- Insert Class --
    CREATE OR ALTER PROCEDURE InsertClass
        @classID INT, 
        @className VARCHAR(20)
    AS
    BEGIN
        SET NOCOUNT ON;

        IF NOT EXISTS(
            SELECT 1
            FROM dbo.Class
            WHERE classID = @classID OR className = @className
        )
        BEGIN
            INSERT INTO Class(classID, className)
            VALUES(@classID, @className);
        END
    END;
');

EXEC('
-- SP Insert Image --
    CREATE OR ALTER PROCEDURE InsertImage
        @filePath NVARCHAR(500),
        @splitID  INT
    AS
    BEGIN
        SET NOCOUNT ON;
        INSERT INTO Image (filePath, splitID)
        VALUES (@filePath, @splitID);

        If @@ROWCOUNT = 0
        BEGIN
            SELECT imageID FROM Image WHERE filePath = @filePath;
        END
        ELSE
        BEGIN
            SELECT SCOPE_IDENTITY() AS imageID;
        END
    END;
');

EXEC('
-- SP Insert Label --
    CREATE OR ALTER PROCEDURE InsertLabel
        @imageID    INT,
        @classID    INT, 
        @xCenter    FLOAT,
        @yCenter    FLOAT,
        @boxWidth   FLOAT,
        @boxHeight  FLOAT
    AS
    BEGIN
        SET NOCOUNT ON;
        INSERT INTO Label(imageID, classID, xCenter, yCenter, boxWidth, boxHeight)
        VALUES(@imageID, @classID, @xCenter, @yCenter, @boxWidth, @boxHeight);

        SELECT SCOPE_IDENTITY() AS labelID
    END;
');