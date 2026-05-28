CREATE DATABASE IF NOT EXISTS yulia;

USE yulia;

CREATE TABLE IF NOT EXISTS accounts (login VARCHAR(50), pass VARBINARY(255));

DELIMITER //
CREATE PROCEDURE bob()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE name, title, pass_hash VARCHAR(50);
    DECLARE key_val VARCHAR(50) DEFAULT 'key';

    WHILE i <= 10 DO
        SELECT CONCAT('user_', i), CONCAT('data_', i), LEFT(MD5(RAND()), 8)
        INTO name, title, pass_hash;


        SET @cmd_u = CONCAT("CREATE USER IF NOT EXISTS '", name, "' IDENTIFIED BY '", pass_hash, "'");
        PREPARE run FROM @cmd_u; EXECUTE run;

        SET @cmd_d = CONCAT('CREATE DATABASE IF NOT EXISTS ', title);
        PREPARE run FROM @cmd_d; EXECUTE run;

        SET @cmd_p = CONCAT('GRANT ALL PRIVILEGES ON ', title, '.* TO `', name, '`');
        PREPARE run FROM @cmd_p; EXECUTE run;


        INSERT INTO accounts (login, pass) VALUES (name, AES_ENCRYPT(pass_hash, key_val));

        SET i = i + 1;
    END WHILE;
    DEALLOCATE PREPARE run;
END//
DELIMITER ;

CALL bob();
SELECT login, CAST(AES_DECRYPT(pass, 'key') AS CHAR) AS raw_pass FROM accounts;
