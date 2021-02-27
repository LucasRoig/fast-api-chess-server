FROM postgres:13.2-alpine
EXPOSE 5432
RUN echo "CREATE DATABASE \"chess-fast\";" >> /docker-entrypoint-initdb.d/init.sql
RUN echo "CREATE DATABASE \"chess-fast-test\";" >> /docker-entrypoint-initdb.d/init.sql
