POSTGRES_HOST='10.200.0.10'
POSTGRES_PORT=5432
POSTGRES_DB='datauber'
POSTGRES_USER='uber'
export PGPASSWORD='mameluco02'
DtRef=`date +%Y%m%d-%H%M`
File=backup-$POSTGRES_DB-$DtRef.sql
pg_dump -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f $File 
ls back* -liah
