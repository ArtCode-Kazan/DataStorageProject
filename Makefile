ROOT = /home/sigma-st-6/Temp
connect-to-db-container:
	docker run --name sigma_database -p 5433:5432 -e POSTGRES_PASSWORD=password -e PGDATA=/var/lib/postgresql/data/pgdata  -v "$(ROOT)":/var/lib/postgresql/data db_image