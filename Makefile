container-run:
	docker run --name sigma_database -p 5433:5432 -e POSTGRES_PASSWORD=password -e PGDATA=/var/lib/postgresql/data/pgdata  -v "/home/sigma-st-6/Temp":/var/lib/postgresql/data db_image