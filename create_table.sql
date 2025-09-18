CREATE TABLE message_data (
    pmkId int(10) NOT NULL AUTO_INCREMENT,
    timestamp varchar(50) NOT NULL,
    fldMessage varchar(1000),
    fldSource varchar(200),
    fldDestination varchar(200),
    PRIMARY KEY(pmkId)
);
