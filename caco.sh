
echo "POSTGRES_HOST='10.200.0.10'">backup.sh
echo "POSTGRES_PORT=5432">>backup.sh
echo "POSTGRES_DB='datauber'">>backup.sh
echo "POSTGRES_USER='uber'">>backup.sh
echo "export PGPASSWORD='mameluco02'">>backup.sh
echo "DtRef=\`date +%Y%m%d-%H%M\`">>backup.sh
echo "File=backup-\$POSTGRES_DB-\$DtRef.sql">>backup.sh
echo "pg_dump -h \$POSTGRES_HOST -p \$POSTGRES_PORT -U \$POSTGRES_USER -d \$POSTGRES_DB -f \$File " >>backup.sh
echo "ls /backup -liah" >>backup.sh
chmod +x backup.sh

echo "POSTGRES_HOST='10.200.0.10'">restore.sh
echo "POSTGRES_PORT=5432">>restore.sh
echo "POSTGRES_DB='datauber'">>restore.sh
echo "POSTGRES_USER='uber'">>restore.sh
echo "export PGPASSWORD='mameluco02'">>restore.sh
echo "echo  \"psql -h \$POSTGRES_HOST -p \$POSTGRES_PORT -U \$POSTGRES_USER -d \$POSTGRES_DB <\$1 \" ">>restore.sh
echo "psql -h \$POSTGRES_HOST -p \$POSTGRES_PORT -U \$POSTGRES_USER -d \$POSTGRES_DB <\$1 " >>restore.sh
chmod +x restore.sh

