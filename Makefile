build:
	@echo "Building services..."
	docker compose -f docker-compose.yml --project-directory . build

run: down
	@echo "Starting services..."
	docker compose -f docker-compose.yml up -d --remove-orphans

down:
	@echo "Stopping services..."
	docker compose -f docker-compose.yml down
